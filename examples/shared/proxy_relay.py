#!/usr/bin/env python3
"""Per-owner TCP relays. Authenticated local control avoids PID-based cleanup."""
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import select
import secrets
import socket
import socketserver
import stat
import subprocess
import sys
import tempfile
import threading
import time

_CHILDREN = {}
OWNER_LABEL = "dev.xorder.proxy-owner"


def owner_label(owner):
    return hashlib.sha256(owner.encode()).hexdigest()


def source_allowed(address, owner):
    """Authorize each new connection from current Docker state, never cached IPs."""
    try:
        ids = subprocess.check_output(
            ["docker", "ps", "-q", "--filter", f"label={OWNER_LABEL}={owner}"],
            text=True, stderr=subprocess.DEVNULL, timeout=5).split()
        if not ids:
            return False
        containers = json.loads(subprocess.check_output(
            ["docker", "inspect", "--type", "container", *ids],
            text=True, stderr=subprocess.DEVNULL, timeout=5))
        for container in containers:
            if (container["Config"]["Labels"].get(OWNER_LABEL) != owner
                    or not container["State"]["Running"]
                    or container["HostConfig"]["NetworkMode"] == "host"):
                continue
            for network in container["NetworkSettings"]["Networks"].values():
                if network.get("IPAddress") == address:
                    return True
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, TypeError, AttributeError):
        pass
    return False


def directory(owner):
    root = Path(tempfile.gettempdir()) / f"xorder-proxy-{os.getuid()}"
    root.mkdir(mode=0o700, exist_ok=True)
    info = root.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
        raise ValueError("Proxy state directory must be a private, owned directory")
    path = root / hashlib.sha256(owner.encode()).hexdigest()[:24]
    path.mkdir(mode=0o700, exist_ok=True)
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
        raise ValueError("Proxy owner directory must be private and owned")
    return path


def control(path, action="status"):
    state = json.loads((path / "state.json").read_text())
    with socket.create_connection(("127.0.0.1", state["control_port"]), timeout=2) as connection:
        connection.sendall(json.dumps({"token": state["token"], "action": action}).encode() + b"\n")
        with connection.makefile("rb") as stream:
            return json.loads(stream.readline(65536))


def running(path):
    try:
        return control(path)
    except (OSError, ValueError):
        return None


def halt(path):
    if running(path):
        control(path, "stop")
        deadline = time.monotonic() + 5
        while running(path):
            if time.monotonic() > deadline:
                raise ValueError("Proxy relay did not stop; retry cleanup")
            time.sleep(0.02)


def stop(owner):
    path = directory(owner)
    with (path / "lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        halt(path)
        (path / "state.json").unlink(missing_ok=True)
        child = _CHILDREN.pop(owner, None)
        if child:
            child.wait(timeout=5)


def ensure(owner, bind, targets, *, reconfigure=False, env=None):
    path = directory(owner)
    config = {"bind": bind, "targets": [list(target) for target in targets],
              "owner": owner_label(owner),
              "implementation": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    with (path / "lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        active = running(path)
        if active and active["config"] == config:
            return active["ports"]
        try:
            previous = json.loads((path / "state.json").read_text())
        except (OSError, ValueError):
            previous = None
        if previous and previous["config"] != config and not reconfigure:
            raise ValueError("Proxy settings changed; run up to recreate the container environment")
        halt(path)
        child = _CHILDREN.pop(owner, None)
        if child:
            child.wait(timeout=5)
        ports = previous["ports"] if previous and previous["config"] == config else [0] * len(targets)
        for target in targets:
            try:
                with socket.create_connection(target, timeout=3):
                    pass
            except OSError as error:
                raise ValueError("Host loopback proxy is unreachable; check the sandbox proxy") from error
        process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), str(path)],
                                   stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL, start_new_session=True, env=env)
        _CHILDREN[owner] = process
        process.stdin.write(json.dumps({"config": config, "ports": ports}).encode())
        process.stdin.close()
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            active = running(path)
            if active:
                return active["ports"]
            if process.poll() is not None:
                break
            time.sleep(0.02)
        process.terminate()
        process.wait(timeout=5)
        raise ValueError("Cannot bind the proxy relay on Docker's bridge (or restore its port); "
                         "verify the sandbox and Docker share this host, or configure a reachable proxy")


def pipe(client, upstream):
    readers = [client, upstream]
    while readers:
        ready, _, _ = select.select(readers, [], [], 60)
        if not ready:
            continue
        for source in ready:
            target = upstream if source is client else client
            data = source.recv(65536)
            if data:
                target.sendall(data)
            else:
                readers.remove(source)
                target.shutdown(socket.SHUT_WR)


class Relay(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


class Forward(socketserver.BaseRequestHandler):
    def handle(self):
        # Check before even opening the trusted loopback upstream. Docker's
        # labels and live addresses are the authority, not a client-supplied ID.
        if not source_allowed(self.client_address[0], self.server.owner):
            return
        try:
            with socket.create_connection(self.server.target, timeout=10) as upstream:
                upstream.settimeout(None)
                pipe(self.request, upstream)
        except OSError:
            pass


def serve(path):
    os.umask(0o077)
    state = json.load(sys.stdin)
    stopped = threading.Event()

    class Control(socketserver.StreamRequestHandler):
        def handle(self):
            self.request.settimeout(2)
            try:
                request = json.loads(self.rfile.readline(1024))
                if not secrets.compare_digest(request.get("token", ""), state["token"]):
                    return
            except (ValueError, TypeError, OSError):
                return
            self.wfile.write(json.dumps(state).encode() + b"\n")
            self.wfile.flush()
            if request.get("action") == "stop":
                stopped.set()

    with contextlib.ExitStack() as stack:
        for index, target in enumerate(state["config"]["targets"]):
            server = stack.enter_context(Relay((state["config"]["bind"], state["ports"][index]), Forward))
            server.target = tuple(target)
            server.owner = state["config"]["owner"]
            state["ports"][index] = server.server_address[1]
            threading.Thread(target=server.serve_forever, daemon=True).start()
        server = stack.enter_context(socketserver.TCPServer(("127.0.0.1", 0), Control))
        state.update(pid=os.getpid(), control_port=server.server_address[1], token=secrets.token_hex(32))
        temporary = path / "state.tmp"
        temporary.write_text(json.dumps(state))
        temporary.replace(path / "state.json")
        server.timeout = 0.2
        while not stopped.is_set():
            server.handle_request()


if __name__ == "__main__":
    serve(Path(sys.argv[1]))
