import json
import os
import subprocess
import socket
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WorktreeRunnerTests(unittest.TestCase):
    def run_fixture(self, relative=False, enabled=True, action=None):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            main, workspace = root / 'main "repo', root / "linked checkout"
            subprocess.run(["git", "init", "-q", str(main)], check=True)
            (main / "example").write_text("fixture\n")
            subprocess.run(["git", "-C", str(main), "add", "example"], check=True)
            subprocess.run(["git", "-C", str(main), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.test",
                            "commit", "-qm", "fixture"], check=True)
            subprocess.run(["git", "-C", str(main), "worktree", "add", "-q", "--detach", str(workspace)], check=True)
            (workspace / "package.json").write_text(json.dumps({"devDependencies": {"@playwright/test": "1.58.2"}}))
            (workspace / "package-lock.json").write_text(json.dumps({"packages": {"node_modules/@playwright/test": {"version": "1.58.2"}}}))
            pointer = workspace / ".git"
            private = pointer.read_text().removeprefix("gitdir: ").strip()
            if relative:
                pointer.write_text("gitdir: " + os.path.relpath(private, workspace) + "\n")
            original = pointer.read_bytes()
            commands = root / "commands.jsonl"
            docker = root / "docker"
            docker.write_text('''#!/usr/bin/env python3
import json, os, pathlib, sys
args = sys.argv[1:]
if args[0] == "run":
    print("1.58.2", end="")
else:
    record = {"args": args}
    # A fourth file is the generated worktree overlay.
    positions = [i for i, arg in enumerate(args) if arg == "-f"]
    if len(positions) == 4:
        record["overlay"] = json.loads(pathlib.Path(args[positions[-1]+1]).read_text())
        mounts = record["overlay"]["services"]["php"]["volumes"]
        record["pointer"] = pathlib.Path(mounts[1]["source"]).read_text()
    with open(os.environ["COMMANDS"], "a") as output:
        output.write(json.dumps(record) + "\\n")
''')
            docker.chmod(0o755)
            env = dict(os.environ, PATH=str(root) + os.pathsep + os.environ["PATH"],
                       WORKSPACE=str(workspace), IMAGE="fixture:test", WORKTREE_GIT=str(int(enabled)),
                       XDG_CACHE_HOME=str(root / "cache"), COMMANDS=str(commands), PHPUNIT_XDEBUG_MODE="coverage")
            subprocess.run(["bash", str(ROOT / "examples/flowbite-xor/run.sh"), *(action or ["exec", "git", "status"])],
                           env=env, check=True, capture_output=True, text=True)
            self.assertEqual(pointer.read_bytes(), original)
            calls = [json.loads(line) for line in commands.read_text().splitlines()]
            if enabled:
                mounts = calls[0]["overlay"]["services"]["php"]["volumes"]
                self.assertEqual(mounts[0]["source"], str(main / ".git"))
                self.assertEqual(mounts[0]["target"], str(main / ".git"))
                self.assertEqual(mounts[1]["target"], "/app/.git")
                self.assertTrue(all(mount["read_only"] and not mount["bind"]["create_host_path"] for mount in mounts))
                self.assertEqual(calls[0]["pointer"], "gitdir: " + private + "\n")
                self.assertTrue(Path(mounts[1]["source"]).is_file(), "Pointer must survive runner exit for restarts")
            else:
                self.assertNotIn("overlay", calls[0])
            return calls

    def test_absolute_and_relative_linked_worktree_pointers(self):
        for relative in (False, True):
            with self.subTest(relative=relative):
                self.run_fixture(relative=relative)

    def test_worktree_mount_requires_opt_in(self):
        self.run_fixture(enabled=False)

    def test_coverage_is_enabled_on_the_phpunit_exec_process(self):
        call = self.run_fixture(action=["phpunit", "--coverage-clover", "var/coverage.xml"])[0]["args"]
        self.assertIn("XDEBUG_MODE=coverage", call)
        self.assertIn("APP_ENV=test", call)
        self.assertIn("CREATE_SNAPSHOTS=false", call)
        self.assertEqual(call[-5:], ["php", "php", "bin/phpunit", "--coverage-clover", "var/coverage.xml"])
        self.assertEqual(call[call.index("-w") + 1], "/app/demo")


class ProfileOrchestrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.workspace = self.directory / "project"
        (self.workspace / "demo").mkdir(parents=True)
        (self.workspace / "package.json").write_text(json.dumps({"devDependencies": {"@playwright/test": "1.58.2"}}))
        (self.workspace / "package-lock.json").write_text(json.dumps({"packages": {"node_modules/@playwright/test": {"version": "1.58.2"}}}))
        for filename in ("compose.yaml", "compose.override.yaml"):
            (self.workspace / "demo" / filename).write_text("services: {}\n")
        self.commands = self.directory / "commands.jsonl"
        self.docker = self.directory / "docker"
        self.docker.write_text('''#!/usr/bin/env python3
import hashlib, json, os, pathlib, sys
args = sys.argv[1:]
statefile = pathlib.Path(os.environ["MOCK_STATE"])
state = json.loads(statefile.read_text()) if statefile.exists() else {"containers": [], "node": False, "generation": 0}
keys = ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "PROXY_PASSTHROUGH", "PLAYWRIGHT_VERSION", "PUID", "PGID", "HTTP_PORT", "HTTPS_PORT", "HTTP3_PORT", "XORDER_INPUT_FINGERPRINT", "FLOWBITE_PROJECT", "WORKSPACE", "IMAGE"]
record = {"args": args, "env": {key: os.environ.get(key) for key in keys}}
positions = [i for i, arg in enumerate(args) if arg == "-f"]
if len(positions) == 4:
    record["overlay"] = json.loads(pathlib.Path(args[positions[-1] + 1]).read_text())
with open(os.environ["COMMANDS"], "a") as output:
    output.write(json.dumps(record) + "\\n")
if args[0] == "info":
    sys.exit(1 if os.environ.get("MOCK_DAEMON_FAIL") == "1" else 0)
if args[0] == "ps":
    project = args[-1].rsplit("=", 1)[1]
    if not state["containers"] and os.environ.get("MOCK_RESERVED_PORTS") == "1":
        print("port-reservation")
        sys.exit(0)
    print("\\n".join(c["Id"] for c in state["containers"] if c["Config"]["Labels"]["com.docker.compose.project"] == project))
elif args[0] == "inspect":
    if "port-reservation" in args:
        print(json.dumps([{"Id": "port-reservation", "Config": {"Labels": {"com.docker.compose.project": os.environ["FLOWBITE_PROJECT"], "com.docker.compose.service": "php", "dev.xorder.workspace": os.environ["WORKSPACE"]}}, "NetworkSettings": {"Ports": {"80/tcp": [{"HostPort": os.environ["HTTP_PORT"]}], "443/tcp": [{"HostPort": os.environ["HTTPS_PORT"]}], "443/udp": [{"HostPort": os.environ["HTTP3_PORT"]}]}}}]))
        sys.exit(0)
    print(json.dumps([c for c in state["containers"] if c["Id"] in args[1:]]))
elif args[0] == "exec":
    sys.exit(22 if os.environ.get("MOCK_APP_FAIL") == "1" else 0)
elif "config" in args:
    print(json.dumps(record["env"], sort_keys=True))
elif "up" in args:
    if os.environ.get("MOCK_UP_FAIL") == "1": sys.exit(1)
    if state.get("inputs") != os.environ.get("XORDER_INPUT_FINGERPRINT") or not state["containers"]:
        state["generation"] += 1
    state["inputs"] = os.environ.get("XORDER_INPUT_FINGERPRINT")
    state["containers"] = [{"Id": service + str(state["generation"]), "Config": {"Labels": {"com.docker.compose.project": os.environ["FLOWBITE_PROJECT"], "com.docker.compose.service": service, "dev.xorder.workspace": os.environ["WORKSPACE"]}}, "State": {"Running": True, "Status": "running", "Health": {"Status": "healthy"}}, "NetworkSettings": {"Ports": {"80/tcp": [{"HostPort": os.environ["HTTP_PORT"]}], "443/tcp": [{"HostPort": os.environ["HTTPS_PORT"]}], "443/udp": [{"HostPort": os.environ["HTTP3_PORT"]}]}}} for service in ("php", "browser")]
elif "exec" in args:
    if args[-1] == "verify":
        if not state["node"]: sys.exit(1)
        print("node-ready")
    elif args[-1] == "record":
        state["node"] = True
        print("node-ready")
    elif args[-1] == "var/xorder/composer-ready":
        print("composer-ready")
    elif "curl" in args:
        if os.environ.get("MOCK_APP_FAIL") == "1": sys.exit(22)
statefile.write_text(json.dumps(state))
''')
        self.docker.chmod(0o755)
        self.env = {key: value for key, value in os.environ.items() if key not in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "PROXY_PASSTHROUGH", "COMPOSER_CACHE_DIR", "WORKTREE_GIT", "FLOWBITE_PROJECT", "HTTP_PORT", "HTTPS_PORT", "HTTP3_PORT")}
        self.env.update(PATH=str(self.directory) + os.pathsep + os.environ["PATH"], WORKSPACE=str(self.workspace), IMAGE="fixture:test", COMMANDS=str(self.commands), MOCK_STATE=str(self.directory / "state.json"), XDG_CACHE_HOME=str(self.directory / "cache"))
        # Keep kernel-allocated TCP/UDP sockets reserved for this mocked profile.
        # The Docker mock reports those reservations as project-owned ports, so
        # unrelated local services cannot make orchestration fixtures flaky.
        # The occupied-port test opts out and exercises the real bind probe.
        def reserve_tcp(start):
            for port in range(start, 20000):
                listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    listener.bind(("127.0.0.1", port))
                except OSError:
                    listener.close()
                    continue
                self.addCleanup(listener.close)
                return listener
            self.fail("No free test TCP port below 20000")

        http = reserve_tcp(10000)
        candidate = http.getsockname()[1] + 1
        while candidate < 20000:
            https = reserve_tcp(candidate)
            http3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                http3.bind(("127.0.0.1", https.getsockname()[1]))
            except OSError:
                candidate = https.getsockname()[1] + 1
                https.close()
                http3.close()
                continue
            self.addCleanup(http3.close)
            break
        else:
            self.fail("No free paired test TCP/UDP port below 20000")
        self.env.update(HTTP_PORT=str(http.getsockname()[1]), HTTPS_PORT=str(https.getsockname()[1]),
                        HTTP3_PORT=str(http3.getsockname()[1]))

    def run_profile(self, *arguments, **environment):
        selected = dict(self.env, **environment)
        selected = {key: value for key, value in selected.items() if value is not None}
        selected.setdefault("MOCK_RESERVED_PORTS", "1" if "up" in arguments else "0")
        result = subprocess.run(["bash", str(ROOT / "examples/flowbite-xor/run.sh"), *arguments],
                                env=selected, capture_output=True, text=True)
        self.calls = [json.loads(line) for line in self.commands.read_text().splitlines()] if self.commands.exists() else []
        self.last_result = result
        return result

    def assertEqual(self, first, second, msg=None):
        if first != second and hasattr(self, "last_result"):
            msg = (msg or "") + "\nProfile stdout:\n" + self.last_result.stdout + "\nProfile stderr:\n" + self.last_result.stderr
        super().assertEqual(first, second, msg)

    def test_filters_all_loopback_proxy_spellings_and_preserves_remote(self):
        for value in ("http://127.0.0.1:3128", "http://127.9.0.1:3128", "localhost:3128", "http://LOCALHOST.:3128", "http://[::1]:3128", "http://[::ffff:127.0.0.1]:3128"):
            with self.subTest(value=value):
                self.assertEqual(self.run_profile("up", HTTP_PROXY=value, https_proxy=value, HTTPS_PROXY="http://proxy.example:8080").returncode, 0)
                for call in self.calls:
                    self.assertEqual(call["env"]["HTTP_PROXY"], "")
                    self.assertEqual(call["env"]["https_proxy"], "")
                    self.assertEqual(call["env"]["HTTPS_PROXY"], "http://proxy.example:8080")
                self.commands.unlink()

    def test_proxy_opt_out_and_explicit_passthrough(self):
        self.assertEqual(self.run_profile("exec", "true", HTTP_PROXY="http://remote:3128", PROXY_PASSTHROUGH="0").returncode, 0)
        self.assertEqual(self.calls[-1]["env"]["HTTP_PROXY"], "")
        self.assertEqual(self.run_profile("exec", "true", HTTP_PROXY="http://[::1]:3128", PROXY_PASSTHROUGH="1").returncode, 0)
        self.assertEqual(self.calls[-1]["env"]["HTTP_PROXY"], "http://[::1]:3128")
        self.assertEqual(self.run_profile("exec", "true", PROXY_PASSTHROUGH="maybe").returncode, 64)

    def test_host_cache_is_mounted_outside_home_and_never_created_implicitly(self):
        cache = self.directory / "Composer cache"
        cache.mkdir()
        self.assertEqual(self.run_profile("up", COMPOSER_CACHE_DIR=str(cache), PUID="0", PGID="0").returncode, 0)
        mount = next(call["overlay"] for call in self.calls if "overlay" in call)["services"]["php"]["volumes"][0]
        self.assertEqual(mount["target"], "/run/composer-cache")
        self.assertFalse(mount["bind"]["create_host_path"])
        self.assertEqual(self.calls[0]["env"]["PUID"], "0")
        absent = cache / "absent"
        self.assertEqual(self.run_profile("up", COMPOSER_CACHE_DIR=str(absent)).returncode, 64)
        self.assertFalse(absent.exists())

    def test_up_prepares_dependencies_then_test_cache_then_served_page(self):
        self.assertEqual(self.run_profile("up").returncode, 0)
        args = [call["args"] for call in self.calls if call["args"][0] == "compose"]
        start = next(i for i, arguments in enumerate(args) if "up" in arguments)
        self.assertIn("--wait", args[start])
        self.assertIn("--prepare", args[start + 1])
        npm = next(i for i, arguments in enumerate(args) if arguments[-3:] == ["php", "npm", "ci"])
        warmup = next(i for i, arguments in enumerate(args) if "cache:warmup" in arguments)
        page = next(i for i, arguments in enumerate(args) if "curl" in arguments)
        self.assertLess(start, npm)
        self.assertLess(npm, warmup)
        self.assertLess(warmup, page)
        self.assertEqual(args[page][-1], "https://localhost/")
        self.assertTrue(all(call["env"]["PLAYWRIGHT_VERSION"] == "1.58.2" for call in self.calls))
        self.assertFalse(any(arguments[0] == "run" for arguments in args))

    def test_failed_start_stops_setup_and_does_not_run_npm(self):
        self.assertEqual(self.run_profile("up", MOCK_UP_FAIL="1").returncode, 1)
        self.assertFalse(any("exec" in call["args"] for call in self.calls))

    def test_inexact_browser_pin_is_rejected_before_docker(self):
        (self.workspace / "package.json").write_text(json.dumps({"devDependencies": {"@playwright/test": "^1.58.2"}}))
        self.assertEqual(self.run_profile("up").returncode, 64)
        self.assertEqual(self.calls, [])

    def test_repeated_up_reconciles_compose_and_reuses_verified_setup(self):
        self.assertEqual(self.run_profile("up").returncode, 0)
        self.commands.unlink()
        self.assertEqual(self.run_profile("up").returncode, 0)
        self.assertTrue(any("up" in call["args"] for call in self.calls))
        self.assertTrue(any("--prepare" in call["args"] for call in self.calls))
        self.assertTrue(any("verify" == call["args"][-1] for call in self.calls))
        self.assertFalse(any(call["args"][-2:] == ["npm", "ci"] or "cache:warmup" in call["args"] for call in self.calls))
        self.assertTrue(any("curl" in call["args"] for call in self.calls))

    def test_source_or_configuration_change_invalidates_setup_receipt(self):
        self.assertEqual(self.run_profile("up").returncode, 0)
        (self.workspace / "demo/config.yaml").write_text("changed: true\n")
        self.commands.unlink()
        self.assertEqual(self.run_profile("up").returncode, 0)
        self.assertTrue(any("cache:warmup" in call["args"] for call in self.calls))
        self.commands.unlink()
        self.assertEqual(self.run_profile("up", HTTPS_PROXY="http://remote-proxy:3128").returncode, 0)
        self.assertTrue(any("cache:warmup" in call["args"] for call in self.calls))

    def test_stable_names_slot_ports_and_explicit_overrides(self):
        self.assertEqual(self.run_profile("--slot", "2", "exec", "true", HTTP_PORT=None, HTTPS_PORT=None, HTTP3_PORT=None).returncode, 0)
        first = self.calls[-1]
        self.assertEqual(first["env"]["HTTP_PORT"], "20004")
        self.assertEqual(first["env"]["HTTPS_PORT"], "20005")
        self.assertEqual(first["env"]["HTTP3_PORT"], "20005")
        project = first["env"]["FLOWBITE_PROJECT"]
        self.assertEqual(self.run_profile("exec", "--slot", "3", "true", HTTP_PORT="28001", HTTPS_PORT="28002", HTTP3_PORT=None).returncode, 0)
        self.assertEqual(self.calls[-1]["env"]["FLOWBITE_PROJECT"], project)
        self.assertEqual(self.calls[-1]["env"]["HTTP_PORT"], "28001")
        self.assertEqual(self.calls[-1]["env"]["HTTP3_PORT"], "28002")
        self.assertEqual(self.run_profile("exec", "true", FLOWBITE_PROJECT="explicit-project").returncode, 0)
        self.assertEqual(self.calls[-1]["env"]["FLOWBITE_PROJECT"], "explicit-project")

    def test_default_workspace_project_and_ports_are_stable(self):
        defaults = dict(HTTP_PORT=None, HTTPS_PORT=None, HTTP3_PORT=None)
        self.assertEqual(self.run_profile("exec", "true", **defaults).returncode, 0)
        first = self.calls[-1]["env"]
        self.assertEqual(self.run_profile("exec", "true", **defaults).returncode, 0)
        second = self.calls[-1]["env"]
        for key in ("FLOWBITE_PROJECT", "HTTP_PORT", "HTTPS_PORT", "HTTP3_PORT"):
            self.assertEqual(first[key], second[key])
        self.assertTrue(20000 <= int(first["HTTP_PORT"]) <= 29998)
        self.assertEqual(int(first["HTTPS_PORT"]), int(first["HTTP_PORT"]) + 1)
        self.assertEqual(first["HTTP3_PORT"], first["HTTPS_PORT"])

    def test_occupied_port_fails_before_compose_up(self):
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            listener.listen()
            port = listener.getsockname()[1]
            self.assertEqual(self.run_profile("up", HTTP_PORT=str(port), MOCK_RESERVED_PORTS="0").returncode, 64)
        self.assertFalse(any("up" in call["args"] for call in self.calls))

    def test_status_needs_neither_image_nor_lock_and_starts_no_container(self):
        self.assertEqual(self.run_profile("up").returncode, 0)
        self.commands.unlink()
        (self.workspace / "package-lock.json").unlink()
        result = self.run_profile("status", IMAGE="")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("application: ready", result.stdout)
        self.assertFalse(any(call["args"][0] in ("compose", "run") for call in self.calls))
        result = self.run_profile("status", IMAGE="", MOCK_DAEMON_FAIL="1")
        self.assertEqual(result.returncode, 1)
        self.assertIn("daemon: unavailable", result.stdout)
        result = self.run_profile("status", IMAGE="", MOCK_APP_FAIL="1")
        self.assertEqual(result.returncode, 1)
        self.assertIn("application: not ready", result.stdout)

    def test_absent_status_and_existing_project_owner_conflict(self):
        self.assertEqual(self.run_profile("status", IMAGE="").returncode, 1)
        self.assertEqual(self.run_profile("up", FLOWBITE_PROJECT="shared").returncode, 0)
        statepath = self.directory / "state.json"
        state = json.loads(statepath.read_text())
        state["containers"][0]["Config"]["Labels"]["dev.xorder.workspace"] = "/another/worktree"
        statepath.write_text(json.dumps(state))
        self.commands.unlink()
        result = self.run_profile("up", FLOWBITE_PROJECT="shared")
        self.assertEqual(result.returncode, 64)
        self.assertIn("another workspace", result.stderr)
        self.assertFalse(any("up" in call["args"] for call in self.calls))

    def test_running_unhealthy_browser_is_not_ready(self):
        self.assertEqual(self.run_profile("up").returncode, 0)
        statepath = self.directory / "state.json"
        state = json.loads(statepath.read_text())
        state["containers"][1]["State"]["Health"]["Status"] = "unhealthy"
        statepath.write_text(json.dumps(state))
        result = self.run_profile("status")
        self.assertEqual(result.returncode, 1)
        self.assertIn("browser: running, health=unhealthy", result.stdout)


class StartupBootstrapTests(unittest.TestCase):
    def run_startup(self, mode="--application", build_failure=False):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            profile, demo = root / "profile", root / "app/demo"
            (demo / "frankenphp").mkdir(parents=True)
            profile.mkdir()
            commands = root / "commands"
            # Remap only the container's fixed filesystem prefix for this
            # executable bootstrap test; preserve its actual shell control flow.
            source = (ROOT / "examples/flowbite-xor/startup.sh").read_text()
            (profile / "startup.sh").write_text(source.replace("/app/", str(root / "app") + "/"))
            (profile / "verify-composer.php").write_text("fixture")
            server = demo / "frankenphp/docker-entrypoint.sh"
            server.write_text('''#!/bin/sh
set -eu
test -s var/tailwind/app.built.css
printf 'server %s\n' "$*" >> "$STARTUP_COMMANDS"
''')
            executable = root / "php"
            executable.write_text('''#!/usr/bin/env python3
import os, pathlib, sys
args = sys.argv[1:]
with open(os.environ["STARTUP_COMMANDS"], "a") as log:
    log.write("php " + " ".join(args) + "\\n")
if args[-1] == "fingerprint":
    print("composer-ready")
if "tailwind:build" in args:
    if os.environ.get("BUILD_FAILURE") == "1": sys.exit(1)
    path = pathlib.Path("var/tailwind/app.built.css")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("compiled-css")
''')
            executable.chmod(0o755)
            for command in ("composer", "flowbite-prime-tailwind"):
                path = root / command
                path.write_text('#!/bin/sh\nprintf "%s\\n" "' + command + ' $*" >> "$STARTUP_COMMANDS"\n')
                path.chmod(0o755)
            result = subprocess.run(["bash", str(profile / "startup.sh"), mode, "frankenphp", "run"],
                                    env=dict(os.environ, PATH=str(root) + os.pathsep + os.environ["PATH"],
                                             STARTUP_COMMANDS=str(commands), BUILD_FAILURE=str(int(build_failure))),
                                    capture_output=True, text=True)
            return result, commands.read_text().splitlines()

    def test_application_compiles_css_after_priming_before_server(self):
        result, commands = self.run_startup()
        self.assertEqual(result.returncode, 0, result.stderr)
        prime = next(i for i, command in enumerate(commands) if command.startswith("flowbite-prime-tailwind"))
        build = next(i for i, command in enumerate(commands) if "tailwind:build" in command)
        server = next(i for i, command in enumerate(commands) if command.startswith("server "))
        self.assertLess(prime, build)
        self.assertLess(build, server)
        self.assertEqual(commands[server], "server frankenphp run")

    def test_failed_css_build_stops_before_starting_server(self):
        result, commands = self.run_startup(build_failure=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(any(command.startswith("server ") for command in commands))

    def test_retained_service_prepare_does_not_rebuild_or_launch_server(self):
        result, commands = self.run_startup(mode="--prepare")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(any("tailwind:build" in command or command.startswith("server ") for command in commands))
