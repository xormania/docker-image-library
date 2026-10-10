#!/opt/serena-env/bin/python
"""Start upstream Serena with session-local configuration and a prepared PHP LSP."""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def project_config(project, read_only, load_yaml):
    config = {}
    for name in ("project.yml", "project.local.yml"):
        source = project / ".serena" / name
        if source.is_file():
            config.update(load_yaml(source.read_text()) or {})
    config.setdefault("project_name", project.name)
    config.setdefault("language_servers", ["php_phpactor"])
    # A prepared profile must never silently download a different backend.
    if config["language_servers"] != ["php_phpactor"]:
        raise ValueError("This image prepares php_phpactor. Select language_servers: [php_phpactor] in the project's Serena configuration.")
    config.setdefault("ignored_paths", [".git", "node_modules", "var/cache", "var/log"])
    config["read_only"] = read_only or config.get("read_only", False)
    return config


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--read-only", action="store_true", help="Disable upstream editing APIs; mount source read-only as well for enforcement")
    parser.add_argument("--version", action="store_true")
    args = parser.parse_args()
    if args.version:
        from importlib.metadata import version
        print("Serena " + version("serena-agent") + " (b79e2a55, PHPactor 2025.12.21.1)")
        return
    project = args.project.resolve(strict=True)
    if not project.is_dir():
        parser.error("--project must be a directory")
    import yaml
    try:
        config = project_config(project, args.read_only, yaml.safe_load)
    except ValueError as exc:
        parser.error(str(exc))
    # Create the configured folder before Serena starts, avoiding its fallback
    # to a checkout's .serena directory. Each MCP process owns its temporary state.
    with tempfile.TemporaryDirectory(prefix="xorder-serena-") as temporary:
        home = Path(temporary)
        state = home / "project"
        state.mkdir()
        (state / "project.yml").write_text(json.dumps(config))
        (home / "serena_config.yml").write_text(json.dumps({
            "projects": [],
            "project_serena_folder_location": str(state),
            "agent_interface": "REPL", "language_backend": "LSP",
            "gui_log_window": False, "web_dashboard": False,
            "web_dashboard_open_on_launch": False,
        }))
        target = home / "language_servers/static/PhpactorServer/phpactor.phar"
        target.parent.mkdir(parents=True)
        shutil.copyfile("/opt/xorder/serena/phpactor.phar", target)
        os.environ["SERENA_HOME"] = str(home)
        os.environ["XDG_CACHE_HOME"] = str(home / "cache")
        # PHPactor accepts references before its background index is complete.
        # Finish the initial index in the same cache before serving MCP, so a
        # first query cannot silently miss cross-file usages on a cold checkout.
        print("Preparing PHPactor's project index before MCP startup...", file=sys.stderr)
        subprocess.run(["php", str(target), "index:build", "--no-interaction", "--quiet"],
                       cwd=project, stdout=sys.stderr, check=True)
        # Import after setting SERENA_HOME: upstream resolves paths at import time.
        from serena.cli import top_level
        top_level(args=[
            "start-mcp-server", "--project", str(project),
            "--agent-interface", "REPL", "--context", "desktop-app",
            "--mode", "editing", "--mode", "no-onboarding",
            "--enable-web-dashboard", "False", "--open-web-dashboard", "False",
            "--enable-gui-log-window", "False", "--tool-timeout", "90",
        ], prog_name="serena")


if __name__ == "__main__":
    main()
