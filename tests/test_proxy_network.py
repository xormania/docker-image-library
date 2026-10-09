import concurrent.futures
import importlib.util
import os
from pathlib import Path
import socket
import socketserver
import sys
import threading
import unittest
import uuid
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "examples/shared"))
import network
import proxy_relay


class Echo(socketserver.BaseRequestHandler):
    def handle(self):
        while data := self.request.recv(65536):
            self.request.sendall(data)


class ProxyNetworkTests(unittest.TestCase):
    def setUp(self):
        self.owner = "test:" + uuid.uuid4().hex
        self.server = socketserver.ThreadingTCPServer(("127.0.0.1", 0), Echo)
        self.server.daemon_threads = True
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.addCleanup(proxy_relay.stop, self.owner)
        self.target = self.server.server_address

    def roundtrip(self, port):
        with socket.create_connection(("127.0.0.2", port), timeout=2) as stream:
            payload = b"CONNECT permitted.example:443 HTTP/1.1\r\n\r\n"
            stream.sendall(payload)
            stream.shutdown(socket.SHUT_WR)
            self.assertEqual(stream.makefile("rb").read(), payload)

    def test_reuse_restart_and_parallel_owner_cleanup(self):
        def ensure():
            return proxy_relay.ensure(self.owner, "127.0.0.2", [self.target])[0]
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            ports = list(pool.map(lambda _: ensure(), range(4)))
        self.assertEqual(len(set(ports)), 1)
        self.roundtrip(ports[0])
        # A graceful relay exit without deleting its receipt simulates a restart.
        proxy_relay.halt(proxy_relay.directory(self.owner))
        self.assertEqual(ensure(), ports[0])
        self.roundtrip(ports[0])
        other = self.owner + ":other"
        self.addCleanup(proxy_relay.stop, other)
        second = proxy_relay.ensure(other, "127.0.0.2", [self.target])[0]
        proxy_relay.stop(self.owner)
        self.roundtrip(second)
        with self.assertRaises(OSError):
            socket.create_connection(("127.0.0.2", ports[0]), timeout=1)

    def test_mapping_preserves_credentials_host_environment_and_no_proxy(self):
        env = {"HTTPS_PROXY": f"http://name:p%40ss@127.0.0.1:{self.target[1]}", "NO_PROXY": "internal.example", "HTTP_PROXY": "http://remote:80"}
        original = dict(env)
        with patch.object(network, "bridge_address", return_value="127.0.0.2"):
            result = network.container_environment(env, self.owner, services=("php", "redis"))
        self.assertEqual(env, original)
        self.assertTrue(result["HTTPS_PROXY"].startswith("http://name:p%40ss@127.0.0.2:"))
        self.assertEqual(result["HTTP_PROXY"], env["HTTP_PROXY"])
        self.assertEqual(result["NO_PROXY"], "internal.example,localhost,127.0.0.1,::1,php,redis")
        self.assertNotIn("p%40ss", (proxy_relay.directory(self.owner) / "state.json").read_text())

    def test_loopback_spellings(self):
        for value in ("127.9.0.1:3128", "http://LOCALHOST.:3128", "http://[::1]:3128", "http://[::ffff:127.0.0.1]:3128"):
            self.assertIsNotNone(network.loopback_proxy(value, "HTTP_PROXY"))
        self.assertIsNone(network.loopback_proxy("http://remote:3128", "HTTP_PROXY"))

    def test_no_proxy_remote_proxy_and_explicit_modes_need_no_relay(self):
        with patch.object(network, "bridge_address", side_effect=AssertionError("Unexpected bridge lookup")):
            self.assertEqual(network.container_environment({}, self.owner)["HTTP_PROXY"], "")
            self.assertEqual(network.container_environment({"HTTP_PROXY": "http://remote:80"}, self.owner)["HTTP_PROXY"], "http://remote:80")
            self.assertEqual(network.container_environment({"HTTP_PROXY": "http://localhost:80", "PROXY_PASSTHROUGH": "0"}, self.owner)["HTTP_PROXY"], "")
            self.assertEqual(network.container_environment({"HTTP_PROXY": "http://localhost:80", "PROXY_PASSTHROUGH": "1"}, self.owner)["HTTP_PROXY"], "http://localhost:80")

    def test_changed_target_needs_up_and_unbindable_bridge_fails(self):
        proxy_relay.ensure(self.owner, "127.0.0.2", [self.target])
        with self.assertRaisesRegex(ValueError, "run up"):
            proxy_relay.ensure(self.owner, "127.0.0.3", [self.target])
        with self.assertRaisesRegex(ValueError, "Cannot bind"):
            proxy_relay.ensure(self.owner, "192.0.2.123", [self.target], reconfigure=True)

    def test_ephemeral_command_keeps_host_proxy_and_cleans_up_its_relay(self):
        upstream = f"http://127.0.0.1:{self.target[1]}"
        ports = []
        def command(arguments, env):
            self.assertEqual(env["HTTPS_PROXY"], upstream)
            forwarded = next(value for value in arguments if value.startswith("HTTPS_PROXY=http://127.0.0.2:"))
            ports.append(int(forwarded.rsplit(":", 1)[1]))
            self.roundtrip(ports[0])
            self.assertEqual(arguments[-3:], ["application", "-e", "HTTPS_PROXY"])
            return 7
        with patch.dict(os.environ, {"HTTPS_PROXY": upstream}, clear=True), \
             patch.object(network, "bridge_address", return_value="127.0.0.2"), \
             patch.object(network.subprocess, "call", side_effect=command):
            self.assertEqual(network.main(["docker", "run", "fixture", "application", "-e", "HTTPS_PROXY"]), 7)
        with self.assertRaises(OSError):
            socket.create_connection(("127.0.0.2", ports[0]), timeout=1)

    def test_real_tls_and_policy_rejection(self):
        spec = importlib.util.spec_from_file_location("proxy_fixture", ROOT / "tests/fixtures/network/check.py")
        fixture = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fixture)
        fixture.verify()
