#!/usr/bin/env python3
"""Real HTTPS CONNECT through a loopback proxy, with an explicit deny result."""
import http.server
import os
from pathlib import Path
import socket
import socketserver
import ssl
import subprocess
import sys
import tempfile
import threading
import uuid
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "examples/shared"))
import network
from proxy_relay import pipe, stop


class Origin(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        content = b"allowed through original proxy\n"
        self.send_response(200)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, *args):
        pass


class Proxy(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            request = b""
            while not request.endswith(b"\r\n\r\n") and len(request) < 8192:
                chunk = self.request.recv(1)
                if not chunk:
                    return
                request += chunk
            line = request.split(b"\r\n")[0]
            self.server.requests.append(line)
            if line != b"CONNECT allowed.test:443 HTTP/1.1":
                self.request.sendall(b"HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\n\r\n")
                return
            with socket.create_connection(self.server.origin, timeout=5) as upstream:
                self.request.sendall(b"HTTP/1.1 200 Connection established\r\n\r\n")
                pipe(self.request, upstream)
        except OSError:
            pass


class Server(socketserver.ThreadingTCPServer):
    daemon_threads = True


def verify(image=None):
    owner = "network-fixture:" + uuid.uuid4().hex
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary)
        subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1",
                        "-subj", "/CN=allowed.test", "-addext", "subjectAltName=DNS:allowed.test",
                        "-keyout", str(path / "key.pem"), "-out", str(path / "ca.pem")],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with http.server.ThreadingHTTPServer(("127.0.0.1", 0), Origin) as origin, Server(("127.0.0.1", 0), Proxy) as proxy:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(path / "ca.pem", path / "key.pem")
            origin.socket = context.wrap_socket(origin.socket, server_side=True)
            proxy.origin = origin.server_address
            proxy.requests = []
            for server in (origin, proxy):
                threading.Thread(target=server.serve_forever, daemon=True).start()
            env = {key: value for key, value in os.environ.items() if key not in (*network.PROXIES, "NO_PROXY", "no_proxy", "PROXY_PASSTHROUGH")}
            env["HTTPS_PROXY"] = f"http://127.0.0.1:{proxy.server_address[1]}"
            try:
                if image:
                    settings = network.container_environment(env, owner)
                else:
                    with patch.object(network, "bridge_address", return_value="127.0.0.2"):
                        settings = network.container_environment(env, owner)
                if image:
                    command = ["docker", "run", "--rm", "--dns", "192.0.2.1",
                               "--mount", f"type=bind,src={path / 'ca.pem'},dst=/proxy-ca.pem,readonly"]
                    command += [part for key, value in settings.items() for part in ("-e", key + "=" + value)]
                    command += [image, "curl", "--cacert", "/proxy-ca.pem"]
                else:
                    command = ["curl", "--cacert", str(path / "ca.pem")]
                for host, expected in (("allowed.test", 0), ("denied.test", 56), ("allowed.test", 0)):
                    result = subprocess.run([*command, "--fail", "--silent", "--show-error", "--max-time", "15", f"https://{host}/"],
                                            env=dict(env, **settings) if not image else env, capture_output=True, text=True)
                    if expected == 0:
                        assert result.returncode == 0, result.stderr
                        assert "allowed through original proxy" in result.stdout
                    else:
                        assert result.returncode != 0 and "403" in result.stderr, result.stderr
                assert b"CONNECT denied.test:443 HTTP/1.1" in proxy.requests
                assert proxy.requests.count(b"CONNECT allowed.test:443 HTTP/1.1") == 2
                print("HTTPS trusted; upstream allow/deny preserved; repeated connection passed")
            finally:
                stop(owner)
                origin.shutdown()
                proxy.shutdown()


if __name__ == "__main__":
    verify(sys.argv[1] if len(sys.argv) > 1 else None)
