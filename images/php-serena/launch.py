#!/opt/serena-env/bin/python
"""Start upstream Serena with session-local configuration and a prepared PHP LSP."""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import hashlib
import fcntl
import threading
from contextlib import ExitStack
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from integration import PHPACTOR_CONFIG, enrich


def project_config(project, read_only, load_yaml, languages=None):
    config = {}
    for name in ("project.yml", "project.local.yml"):
        source = project / ".serena" / name
        if source.is_file():
            data = load_yaml(source.read_text()) or {}
            if not isinstance(data, dict):
                raise ValueError(f"{source} must contain a configuration mapping")
            config.update(data)
    config.setdefault("project_name", project.name)
    if languages:
        config["language_servers"] = languages
    config.setdefault("language_servers", ["php_phpactor"])
    # A prepared profile must never silently download a different backend.
    if not config["language_servers"] or not set(config["language_servers"]) <= {"php_phpactor", "typescript"}:
        raise ValueError("This image prepares php_phpactor and typescript (JavaScript/TypeScript). Select those language_servers only.")
    settings = config.get("ls_specific_settings") or {}
    if not isinstance(settings, dict) or any(not isinstance(value, dict) for value in settings.values()):
        raise ValueError("ls_specific_settings must map language servers to settings mappings")
    for options in settings.values():
        if {"phpactor_version", "ls_path"}.intersection(options):
            raise ValueError("Remove phpactor_version and ls_path overrides: this image uses its prepared PHPactor binary.")
    # Mounted project files do not authorize activation commands or dependency
    # overrides. Keep ordinary project preferences, but strip trust-gated fields.
    for key in ("activation_command", "ls_specific_settings"):
        if config.pop(key, None):
            print(f"Ignoring repository-provided {key} in the prepared profile", file=sys.stderr)
    config.setdefault("ignored_paths", [".git", "node_modules", "var/cache", "var/log"])
    config["read_only"] = read_only
    return config


def index_fingerprint(project, config):
    """Bind a complete index to current source, installed dependencies and settings."""
    digest = hashlib.sha256(json.dumps({key: value for key, value in config.items() if key != "read_only"}, sort_keys=True).encode())
    digest.update(Path("/opt/xorder/serena/phpactor.phar").read_bytes())
    root = Path("/workspace") if project.is_relative_to(Path("/workspace")) else project
    for directory, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in {".git", ".serena", "node_modules", "var", "assets"})
        for name in sorted(files):
            path = Path(directory) / name
            if path.is_symlink():
                digest.update(str(path.relative_to(root)).encode() + os.readlink(path).encode())
            elif path.suffix in {".php", ".json", ".lock", ".yaml", ".yml"}:
                digest.update(str(path.relative_to(root)).encode() + b"\0" + path.read_bytes())
    return digest.hexdigest()


def proxy():
    """Keep stdio MCP compatible while adding machine-readable session identity."""
    process = subprocess.Popen([sys.executable, __file__, *sys.argv[1:], "--upstream"],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    def forward():
        try:
            for line in sys.stdin:
                process.stdin.write(line)
                process.stdin.flush()
        except (BrokenPipeError, OSError):
            pass
        finally:
            process.stdin.close()
    threading.Thread(target=forward, daemon=True).start()
    try:
        for line in process.stdout:
            print(json.dumps(enrich(json.loads(line))), flush=True)
        return process.wait()
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path.cwd())
    access = parser.add_mutually_exclusive_group()
    access.add_argument("--read-only", dest="read_only", action="store_true", default=True,
                        help="Disable upstream editing APIs (default); use the runner for mount enforcement")
    access.add_argument("--write", dest="read_only", action="store_false", help="Enable source editing for a trusted checkout")
    parser.add_argument("--version", action="store_true")
    parser.add_argument("--request-timeout", type=float, default=180)
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--languages", default=None, help="Comma-separated php_phpactor,typescript")
    parser.add_argument("--upstream", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.version:
        from importlib.metadata import version
        print("Serena " + version("serena-agent") + " (b79e2a55, PHPactor 2025.12.21.1)")
        return
    if args.request_timeout <= 0:
        parser.error("--request-timeout must be positive")
    if not args.upstream:
        sys.exit(proxy())
    project = args.project.resolve(strict=True)
    if not project.is_dir():
        parser.error("--project must be a directory")
    import yaml
    try:
        config = project_config(project, args.read_only, yaml.safe_load,
                                args.languages.split(",") if args.languages else None)
    except ValueError as exc:
        parser.error(str(exc))
    # Create the configured folder before Serena starts, avoiding its fallback
    # to a checkout's .serena directory. Each MCP process owns its temporary state.
    with ExitStack() as stack:
        temporary = stack.enter_context(tempfile.TemporaryDirectory(prefix="xorder-serena-"))
        home = Path(temporary)
        state = home / "project"
        state.mkdir()
        (state / "project.yml").write_text(json.dumps(config))
        (home / "serena_config.yml").write_text(json.dumps({
            "projects": [],
            "trusted_project_path_patterns": [],
            "project_serena_folder_location": str(state),
            "agent_interface": "REPL", "language_backend": "LSP",
            "gui_log_window": False, "web_dashboard": False,
            "web_dashboard_open_on_launch": False,
        }))
        target = home / "language_servers/static/PhpactorServer/phpactor.phar"
        target.parent.mkdir(parents=True)
        shutil.copyfile("/opt/xorder/serena/phpactor.phar", target)
        ts = home / "language_servers/static/TypeScriptLanguageServer/ts-lsp"
        ts.parent.mkdir(parents=True)
        ts.symlink_to("/opt/xorder/serena/javascript", target_is_directory=True)
        os.environ["SERENA_HOME"] = str(home)
        cache = args.cache_dir or home / "cache"
        cache.mkdir(parents=True, exist_ok=True)
        if args.cache_dir:
            lock = stack.enter_context((cache / "index.lock").open("a"))
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                parser.error("This worktree index is in use; reuse its shell daemon or choose another --cache-dir")
        os.environ["XDG_CACHE_HOME"] = str(cache)
        # PHPactor accepts references before its background index is complete.
        # Finish the initial index in the same cache before serving MCP, so a
        # first query cannot silently miss cross-file usages on a cold checkout.
        if "php_phpactor" in config["language_servers"]:
            fingerprint = index_fingerprint(project, config)
            marker = cache / "complete-index"
            if not marker.is_file() or marker.read_text() != fingerprint:
                marker.unlink(missing_ok=True)
                print("Preparing PHPactor's complete project index...", file=sys.stderr)
                subprocess.run(["php", str(target), "index:build", "--config-extra", json.dumps(PHPACTOR_CONFIG),
                                "--no-interaction", "--quiet"], cwd=project, stdout=sys.stderr, check=True)
                marker.write_text(fingerprint)
            else:
                print("Reusing complete PHPactor index for unchanged sources and dependencies", file=sys.stderr)
        # Import after setting SERENA_HOME: upstream resolves paths at import time.
        from serena.cli import top_level
        from integration import install
        install(args.request_timeout)
        top_level(args=[
            "start-mcp-server", "--project", str(project),
            "--agent-interface", "REPL", "--context", "desktop-app",
            "--mode", "editing", "--mode", "no-onboarding",
            "--enable-web-dashboard", "False", "--open-web-dashboard", "False",
            "--enable-gui-log-window", "False", "--tool-timeout", str(args.request_timeout + 15),
        ], prog_name="serena")


if __name__ == "__main__":
    main()
