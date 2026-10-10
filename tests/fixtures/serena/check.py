#!/usr/bin/env python3
"""Exercise the public offline MCP runner on a disposable, pinned flowbite-xor checkout."""
import json
import os
import queue
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


class Client:
    def __init__(self, command, log):
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=log, text=True, bufsize=1)
        self.responses = queue.Queue()
        self.serial = 0
        def receive():
            for line in self.process.stdout:
                try:
                    self.responses.put(json.loads(line))
                except ValueError:
                    self.responses.put({"invalid_stdout": line})
            self.responses.put({"eof": True})
        threading.Thread(target=receive, daemon=True).start()
        try:
            self.call("initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
                                    "clientInfo": {"name": "xorder-serena-acceptance", "version": "1.0.0"}})
            self.send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        except BaseException:
            self.close()
            raise

    def send(self, message):
        self.process.stdin.write(json.dumps(message) + "\n")
        self.process.stdin.flush()

    def call(self, method, params=None):
        self.serial += 1
        self.send({"jsonrpc": "2.0", "id": self.serial, "method": method, "params": params or {}})
        while True:
            reply = self.responses.get(timeout=120)
            if "invalid_stdout" in reply or "eof" in reply:
                raise AssertionError(reply)
            if reply.get("id") == self.serial:
                if "error" in reply:
                    raise AssertionError(reply)
                return reply["result"]

    def repl(self, code, expected_error=False):
        reply = self.call("tools/call", {"name": "serena_repl", "arguments": {"code": code}})
        text = "\n".join(item["text"] for item in reply.get("content", []) if item["type"] == "text")
        if not expected_error:
            assert not reply.get("isError"), reply
            # Serena can encode execution errors inside a successful MCP reply.
            assert "Traceback (most recent call last)" not in text, text
        return text

    def close(self):
        self.process.stdin.close()
        try:
            self.process.wait(timeout=20)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            self.process.wait(timeout=10)


def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def main():
    image = sys.argv[1]
    fixture = json.loads(Path(__file__).with_name("consumer.json").read_text())
    with tempfile.TemporaryDirectory(prefix="xorder-serena-proof-") as directory:
        checkout = Path(directory) / "flowbite-xor"
        run("git", "init", "-q", str(checkout))
        run("git", "-C", str(checkout), "fetch", "--depth=1", fixture["repository"], fixture["commit"])
        run("git", "-C", str(checkout), "checkout", "--detach", "FETCH_HEAD")
        # Install the application's own lock, separately from the image's LSP.
        # No asset downloads, application scripts, browser, or server are needed.
        run("docker", "run", "--rm", "--mount", f"type=bind,src={checkout},dst=/workspace",
            "-e", f"PUID={os.getuid()}", "-e", f"PGID={os.getgid()}",
            "-w", "/workspace/demo", image, "composer", "install", "--no-interaction", "--prefer-dist",
            "--no-progress", "--no-scripts", "--no-plugins")
        command = [sys.executable, str(ROOT / "examples/serena/run.py"), str(checkout),
                   "--image", image, "--project", fixture["project"]]
        source = checkout / fixture["project"] / fixture["file"]
        original = source.read_text()
        evidence = {"consumer": fixture, "image": image, "checks": []}
        log_path = Path(directory) / "mcp.log"
        client = None
        try:
            with log_path.open("w") as log:
                client = Client(command, log)
                assert "serena_repl" in {tool["name"] for tool in client.call("tools/list")["tools"]}
                assert "42" in client.repl("xorder_answer = 42; xorder_answer")
                assert "42" in client.repl("xorder_answer")
                evidence["checks"].append("persistent-repl-state")
                overview = client.repl(f"s.lsp.get_symbols_overview({fixture['file']!r}, depth=1)")
                assert fixture["symbol"] in overview and "__toString" in overview, overview
                found = client.repl(f"s.lsp.find_symbol({fixture['symbol']!r}, relative_path={fixture['file']!r}, include_body=True)")
                assert "RequestStack" in found, found
                references = client.repl(f"s.lsp.find_referencing_symbols({fixture['symbol']!r}, {fixture['file']!r})")
                assert fixture["referencing_file"] in references, references
                evidence["checks"].append("php-symbols-and-cross-file-references")
                assert source.read_text() == original
                assert not (checkout / "demo/.serena").exists(), "Startup changed the project"
                client.repl(f"s.edit.replace_content({fixture['file']!r}, \"return '';\", \"return 'xorder-proof';\", 'literal')")
                assert "return 'xorder-proof';" in source.read_text()
                reread = client.repl(f"s.lsp.find_symbol('CspNonce/__toString', relative_path={fixture['file']!r}, include_body=True)")
                assert "xorder-proof" in reread, reread
                error = client.repl(f"s.edit.replace_content({fixture['file']!r}, 'xorder-proof', 'xorder-partial', 'literal')\nraise RuntimeError('xorder-expected-error')", expected_error=True)
                assert "xorder-expected-error" in error, error
                assert "xorder-partial" in source.read_text(), "Edit before error was lost"
                evidence["checks"].append("edit-read-and-partial-error")
                client.close()
                client = Client(command + ["--read-only"], log)
                assert "False" in client.repl("'xorder_answer' in globals()")
                assert "xorder-partial" in client.repl(f"s.lsp.find_symbol('CspNonce/__toString', relative_path={fixture['file']!r}, include_body=True)")
                blocked = client.repl("from pathlib import Path\nblocked = False\ntry:\n Path('/workspace/demo/src/Security/CspNonce.php').write_text('wrong')\nexcept OSError:\n blocked = True\nblocked")
                assert "True" in blocked, blocked
                assert "xorder-partial" in source.read_text()
                evidence["checks"].append("restart-loses-repl-state-preserves-source-and-readonly-mount")
                client.close()
                client = None
        except BaseException:
            print(log_path.read_text()[-16000:], file=sys.stderr)
            raise
        finally:
            if client:
                client.close()
        source.write_text(original)
        run("git", "-C", str(checkout), "diff", "--exit-code")
        output = ROOT / "out/serena"
        output.mkdir(parents=True, exist_ok=True)
        (output / "acceptance.json").write_text(json.dumps(evidence, indent=2) + "\n")
        print(json.dumps(evidence))


if __name__ == "__main__":
    main()
