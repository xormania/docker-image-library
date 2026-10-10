#!/usr/bin/env python3
"""Shell access to the same Serena MCP service: one-shot queries or a private daemon."""
import argparse
import json
import os
from pathlib import Path
import queue
import re
import signal
import socket
import socketserver
import subprocess
import sys
import threading
import time

from run import command


class MCP:
    def __init__(self, argv, timeout=600):
        self.timeout, self.serial = timeout, 0
        self.responses = queue.Queue()
        self.process = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        self.lock = threading.Lock()
        threading.Thread(target=self.read, daemon=True).start()
        try:
            self.call("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                                     "clientInfo": {"name": "xorder-shell", "version": "1.0.0"}})
            self.send({"jsonrpc": "2.0", "method": "notifications/initialized"})
            result = self.call("tools/call", {"name": "initial_instructions", "arguments": {}})
            self.session = result.get("structuredContent", {}).get("session_id")
            if not self.session:
                match = re.search(r"Your Serena session id is `([^`]+)`", self.content(result))
                if match:
                    self.session = match.group(1)
            if not self.session or result.get("isError"):
                raise RuntimeError("Serena initialization failed: " + self.content(result))
        except BaseException:
            self.close()
            raise

    @staticmethod
    def content(result):
        return "\n".join(part.get("text", "") for part in result.get("content", []) if part.get("type") == "text")

    def read(self):
        try:
            for line in self.process.stdout:
                self.responses.put(json.loads(line))
        except (OSError, ValueError) as error:
            self.responses.put({"reader_error": str(error)})
        finally:
            self.responses.put({"eof": True})

    def send(self, message):
        self.process.stdin.write(json.dumps(message) + "\n")
        self.process.stdin.flush()

    def call(self, method, params=None):
        with self.lock:
            if self.process.poll() is not None:
                raise RuntimeError("Serena process not running; restart the session")
            self.serial += 1
            self.send({"jsonrpc": "2.0", "id": self.serial, "method": method, "params": params or {}})
            deadline = time.monotonic() + self.timeout
            while True:
                try:
                    reply = self.responses.get(timeout=max(0, deadline - time.monotonic()))
                except queue.Empty:
                    # Execution may have edited source; do not automatically replay.
                    self.close()
                    raise TimeoutError("Serena response timed out; session stopped. Inspect source edits before retrying")
                if reply.get("eof") or "reader_error" in reply:
                    raise RuntimeError("Serena process stopped; restart the session")
                if "method" in reply and "id" in reply:
                    self.send({"jsonrpc": "2.0", "id": reply["id"], "error": {"code": -32601, "message": "Unsupported client request"}})
                if reply.get("id") == self.serial:
                    if "error" in reply:
                        raise RuntimeError(str(reply["error"]))
                    return reply["result"]

    def repl(self, code):
        result = self.call("tools/call", {"name": "serena_repl", "arguments": {"session": self.session, "code": code}})
        text = self.content(result)
        return {"session_id": self.session, "ok": not result.get("isError", False) and not
                bool(re.match(r"^(?:[\w.]*Error|[\w.]*Exception):", text)), "result": result}

    def close(self):
        if self.process.stdin and not self.process.stdin.closed:
            try:
                self.process.stdin.close()
            except BrokenPipeError:
                pass
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        if self.process.stdout and not self.process.stdout.closed:
            self.process.stdout.close()


def request(path, value, timeout=600):
    with socket.socket(socket.AF_UNIX) as connection:
        connection.settimeout(timeout)
        connection.connect(str(path))
        connection.sendall(json.dumps(value).encode() + b"\n")
        with connection.makefile("rb") as stream:
            return json.loads(stream.readline())


def serve(path, argv, timeout):
    path = path.absolute()
    path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    if path.parent.stat().st_uid != os.getuid() or path.parent.stat().st_mode & 0o077:
        raise ValueError("Socket directory must be owned by this user and mode 0700")
    # Do not unlink another active daemon's socket.
    if path.exists():
        raise ValueError("Socket already exists; stop its daemon or remove a confirmed stale socket")
    client = MCP(argv, timeout)
    class Handler(socketserver.StreamRequestHandler):
        def handle(self):
            try:
                value = json.loads(self.rfile.readline(4 * 1024 * 1024))
                action = value.get("action", "call")
                if action == "stop":
                    result = {"ok": True, "stopping": True}
                    threading.Thread(target=self.server.shutdown, daemon=True).start()
                elif action == "status":
                    result = {"ok": client.process.poll() is None, "session_id": client.session,
                              "access": "write" if "--write" in argv else "read-only"}
                elif action == "call":
                    result = client.repl(value["code"])
                else:
                    raise ValueError("Unknown action")
            except Exception as error:
                result = {"ok": False, "error": str(error)}
            self.wfile.write(json.dumps(result).encode() + b"\n")
    class Server(socketserver.ThreadingUnixStreamServer):
        daemon_threads = True
        block_on_close = False
    try:
        with Server(str(path), Handler) as server:
            path.chmod(0o600)
            def stop(_signum, _frame):
                threading.Thread(target=server.shutdown, daemon=True).start()
            signal.signal(signal.SIGTERM, stop)
            signal.signal(signal.SIGINT, stop)
            print(json.dumps({"ok": True, "socket": str(path), "session_id": client.session}), flush=True)
            server.serve_forever()
    finally:
        client.close()
        path.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["query", "serve", "call", "status", "stop"])
    parser.add_argument("operation", nargs="?", choices=["find_symbol", "find_referencing_symbols", "get_symbols_overview", "repl"])
    parser.add_argument("name", nargs="?")
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--project", default=".")
    parser.add_argument("--image")
    parser.add_argument("--path")
    parser.add_argument("--code", help="Python cell; source edits require a write-capable session")
    parser.add_argument("--socket", type=Path)
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--languages")
    parser.add_argument("--request-timeout", type=float, default=180)
    parser.add_argument("--startup-timeout", type=float, default=600)
    access = parser.add_mutually_exclusive_group()
    access.add_argument("--write", dest="read_only", action="store_false")
    access.add_argument("--read-only", dest="read_only", action="store_true")
    parser.set_defaults(read_only=True)
    args = parser.parse_args(argv)
    if args.request_timeout <= 0 or args.startup_timeout <= 0:
        parser.error("Timeouts must be positive")
    if args.action == "query" and not args.code:
        if args.operation == "get_symbols_overview" and args.path:
            args.code = f"s.lsp.get_symbols_overview({args.path!r}, depth=1)"
        elif args.operation == "find_symbol" and args.name:
            args.code = f"s.lsp.find_symbol({args.name!r}, relative_path={args.path or ''!r}, include_body=True)"
        elif args.operation == "find_referencing_symbols" and args.name and args.path:
            args.code = f"s.lsp.find_referencing_symbols({args.name!r}, {args.path!r})"
    if args.action in {"query", "call"} and not args.code:
        parser.error("Supply --code or a query operation with its name/--path")
    if args.action in {"serve", "call", "status", "stop"} and not args.socket:
        parser.error("This action requires --socket")
    if args.action in {"call", "status", "stop"}:
        result = request(args.socket, {"action": args.action, "code": args.code}, args.startup_timeout)
    else:
        if not args.workspace:
            parser.error("Supply --workspace")
        argv = command(args)
        if args.action == "serve":
            serve(args.socket, argv, max(args.startup_timeout, args.request_timeout + 30))
            return 0
        client = MCP(argv, max(args.startup_timeout, args.request_timeout + 30))
        try:
            result = client.repl(args.code)
        finally:
            client.close()
    print(json.dumps(result), flush=True)
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, TimeoutError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        sys.exit(1)
