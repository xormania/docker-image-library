#!/usr/bin/env python3
"""Local Compose orchestration; dependencies and application hooks stay project-owned."""
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit

PROFILE = Path(__file__).resolve().parent


def call(arguments, env, capture=False, check=True):
    return subprocess.run(arguments, env=env, check=check, text=True,
                          stdout=subprocess.PIPE if capture else None,
                          stderr=subprocess.PIPE if capture else None)


def proxies(env):
    mode = env.get("PROXY_PASSTHROUGH", "auto")
    if mode not in ("auto", "0", "1"):
        raise ValueError("PROXY_PASSTHROUGH must be auto, 0 (disable), or 1 (forward unchanged)")
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        value = env.get(key, "")
        loopback = False
        if value:
            try:
                host = urlsplit(value if "://" in value else "http://" + value).hostname
                loopback = host and host.rstrip(".").lower() == "localhost"
                try:
                    address = ipaddress.ip_address(host or "")
                    loopback = loopback or address.is_loopback or (address.version == 6 and address.ipv4_mapped and address.ipv4_mapped.is_loopback)
                except ValueError:
                    pass
            except ValueError as error:
                raise ValueError(f"Invalid {key} URL") from error
        if mode == "0" or (mode == "auto" and loopback):
            env[key] = ""
            if value:
                print(f"Ignoring {key}: {'disabled' if mode == '0' else 'loopback proxy is local to the host'}", file=sys.stderr)
    return env


def playwright(workspace):
    package = json.loads((workspace / "package.json").read_text())
    lock = json.loads((workspace / "package-lock.json").read_text())
    version = lock["packages"]["node_modules/@playwright/test"]["version"]
    if not re.fullmatch(r"\d+\.\d+\.\d+", version) or package.get("devDependencies", {}).get("@playwright/test") != version:
        raise ValueError("Pin @playwright/test to the same exact version in package.json and package-lock.json")
    return version


def php_exec(compose, env, *arguments, cwd="/app"):
    return call([*compose, "exec", "-T", "--user", f'{env["PUID"]}:{env["PGID"]}', "-w", cwd, "php", *arguments], env)


def main(arguments):
    if not arguments:
        raise ValueError("Usage: run.sh up|test|phpunit|exec|logs|down [arguments]")
    action, *extra = arguments
    if action not in ("up", "test", "phpunit", "exec", "logs", "down"):
        raise ValueError(f"Unknown action: {action}")
    env = dict(os.environ)
    workspace = Path(env["WORKSPACE"]).resolve(strict=True)
    if not workspace.is_dir():
        raise ValueError("WORKSPACE must be a directory")
    env.update(WORKSPACE=str(workspace), PUID=env.get("PUID", str(os.getuid())),
               PGID=env.get("PGID", str(os.getgid())), FLOWBITE_PROFILE_DIR=str(PROFILE),
               HTTP_PORT=env.get("HTTP_PORT", "8084"), HTTPS_PORT=env.get("HTTPS_PORT", "8444"),
               HTTP3_PORT=env.get("HTTP3_PORT", "8444"), CONTAINER_CA_FILE="")
    if not env.get("IMAGE"):
        raise ValueError("Select IMAGE from the verified flowbite-xor-dev catalog")
    ca = env.get("CA_CERTIFICATE")
    if ca:
        if not Path(ca).is_absolute() or not os.access(ca, os.R_OK):
            raise ValueError("CA_CERTIFICATE must be a readable absolute PEM path")
        env["CONTAINER_CA_FILE"] = "/run/library-proxy.pem"
    env = proxies(env)
    env["PLAYWRIGHT_VERSION"] = playwright(workspace)
    preference = env.get("COMPOSER_INSTALL_PREFERENCE", "dist")
    if preference not in ("dist", "source"):
        raise ValueError("COMPOSER_INSTALL_PREFERENCE must be dist or source")
    compose = ["docker", "compose", "--project-directory", str(workspace / "demo"), "-p", env.get("FLOWBITE_PROJECT", "flowbite-xor-library"),
               "-f", str(workspace / "demo/compose.yaml"), "-f", str(workspace / "demo/compose.override.yaml"), "-f", str(PROFILE / "compose.yaml")]
    overlay = {"services": {"php": {"volumes": []}}}
    cache = env.get("COMPOSER_CACHE_DIR")
    if cache:
        host_cache = Path(cache)
        if not host_cache.is_absolute() or not host_cache.is_dir():
            raise ValueError("COMPOSER_CACHE_DIR must be an existing absolute host cache directory")
        overlay["services"]["php"]["volumes"].append({"type": "bind", "source": str(host_cache), "target": "/home/dev/.cache/composer", "bind": {"create_host_path": False}})
    # The image owns HOME and recursively adjusts its UID. Keep a host bind cache
    # outside HOME so that shared entrypoint cannot change host cache ownership.
    if cache:
        overlay["services"]["php"]["environment"] = {"COMPOSER_CACHE_DIR": "/run/composer-cache"}
        overlay["services"]["php"]["volumes"][-1]["target"] = "/run/composer-cache"
    if env.get("WORKTREE_GIT", "0") == "1" and (workspace / ".git").is_file():
        common = call(["git", "-C", str(workspace), "rev-parse", "--path-format=absolute", "--git-common-dir"], env, capture=True).stdout.strip()
        private = call(["git", "-C", str(workspace), "rev-parse", "--absolute-git-dir"], env, capture=True).stdout.strip()
        key = hashlib.sha256(str(workspace).encode()).hexdigest()
        pointer = Path(env.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))) / "xorder/worktrees" / key / "git-pointer"
        pointer.parent.mkdir(parents=True, exist_ok=True)
        pointer.write_text(f"gitdir: {private}\n")
        pointer.chmod(0o644)
        overlay["services"]["php"].setdefault("environment", {})["GIT_OPTIONAL_LOCKS"] = "0"
        for source, target in ((common, common), (str(pointer), "/app/.git")):
            overlay["services"]["php"]["volumes"].append({"type": "bind", "source": source, "target": target, "read_only": True, "bind": {"create_host_path": False}})
    with tempfile.TemporaryDirectory(prefix="xorder-compose-") as directory:
        if overlay["services"]["php"]["volumes"]:
            filename = Path(directory) / "overlay.json"
            filename.write_text(json.dumps(overlay))
            compose += ["-f", str(filename)]
        if action == "up":
            call([*compose, "up", "--wait", "--wait-timeout", "600", "--no-build"], env)
            # Recheck lockfiles even when Compose retained an existing container.
            php_exec(compose, env, "bash", "/run/xorder/startup.sh", "--prepare", cwd="/app/demo")
            php_exec(compose, env, "npm", "ci")
            # Establish test cache readiness explicitly, separate from the server.
            php_exec(compose, env, "php", "bin/console", "cache:warmup", "--env=test", cwd="/app/demo")
            php_exec(compose, env, "curl", "--fail", "--silent", "--show-error", "--insecure", "--noproxy", "*", "--max-time", "15", "https://localhost" + env.get("APP_READY_PATH", "/"))
        elif action == "test":
            php_exec(compose, env, "npx", "playwright", "test", *extra)
        elif action == "phpunit":
            call([*compose, "exec", "-T", "--user", f'{env["PUID"]}:{env["PGID"]}', "-w", "/app/demo",
                  "-e", "XDEBUG_MODE=" + env.get("PHPUNIT_XDEBUG_MODE", "off"), "-e", "APP_ENV=test", "-e", "APP_DEBUG=1",
                  "-e", "CREATE_SNAPSHOTS=false", "php", "php", "bin/phpunit", *extra], env)
        elif action == "exec":
            php_exec(compose, env, *extra)
        else:
            call([*compose, action, *extra], env)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        print(f"xorder flowbite: {error}", file=sys.stderr)
        sys.exit(64)
    except subprocess.CalledProcessError as error:
        if error.stderr:
            print(error.stderr, file=sys.stderr, end="")
        sys.exit(error.returncode)
