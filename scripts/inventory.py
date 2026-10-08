#!/usr/bin/env python3
"""Run inside the tested container; collect facts, not declared capabilities."""
import json
import platform
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


def run(*command):
    return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT).strip()


family = sys.argv[1]
tools = {}
commands = {"bash": ["bash", "--version"], "git": ["git", "--version"], "gh": ["gh", "--version"],
            "curl": ["curl", "--version"], "jq": ["jq", "--version"], "rg": ["rg", "--version"],
            "psql": ["psql", "--version"]}
extensions = {}
if family.startswith("php"):
    runtime = run("php", "-r", "echo PHP_VERSION;")
    extensions = json.loads(run("php", "-r", '$out=[]; foreach(get_loaded_extensions() as $e) {$out[strtolower($e)]=phpversion($e) ?: "bundled";} echo json_encode($out);'))
    commands.update({"php": ["php", "--version"], "composer": ["composer", "--version"], "symfony": ["symfony", "version"]})
    if family == "php-browser":
        commands.update({"chromium": ["chromium", "--version"], "chromedriver": ["chromedriver", "--version"]})
elif family == "python-dev":
    runtime = run("python", "-c", "import platform; print(platform.python_version())")
    commands.update({"python": ["python", "--version"], "uv": ["uv", "--version"], "pip": ["python", "-m", "pip", "--version"]})
elif family == "rust-dev":
    runtime = run("rustc", "--version").split()[1]
    commands.update({"rustc": ["rustc", "--version"], "cargo": ["cargo", "--version"], "rustfmt": ["rustfmt", "--version"], "clippy": ["cargo", "clippy", "--version"], "rustup": ["rustup", "--version"]})
else:
    raise SystemExit("Unknown family")
for tool, command in commands.items():
    tools[tool] = run(*command).splitlines()[0]
os_release = {}
for line in Path("/etc/os-release").read_text().splitlines():
    if "=" in line:
        k, v = line.split("=", 1)
        os_release[k] = shlex.split(v)[0]
result = {"platform": "linux/" + {"x86_64": "amd64", "aarch64": "arm64"}[platform.machine()],
          "runtime_version": runtime, "tools": tools, "extensions": extensions,
          "os": os_release, "packages": run("dpkg-query", "-W", "-f=${Package}=${Version}\\n").splitlines()}
if family == "rust-dev":
    result["rust_targets"] = run("rustup", "target", "list", "--installed").splitlines()
print(json.dumps(result, indent=2, sort_keys=True))
