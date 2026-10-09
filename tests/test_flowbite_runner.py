import json
import os
import subprocess
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
import json, os, pathlib, sys
args = sys.argv[1:]
record = {"args": args, "env": {key: os.environ.get(key) for key in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "PROXY_PASSTHROUGH", "PLAYWRIGHT_VERSION", "PUID", "PGID", "HTTP_PORT", "HTTPS_PORT", "HTTP3_PORT"]}}
positions = [i for i, arg in enumerate(args) if arg == "-f"]
if len(positions) == 4:
    record["overlay"] = json.loads(pathlib.Path(args[positions[-1] + 1]).read_text())
with open(os.environ["COMMANDS"], "a") as output:
    output.write(json.dumps(record) + "\\n")
if "up" in args and os.environ.get("MOCK_UP_FAIL") == "1":
    sys.exit(1)
''')
        self.docker.chmod(0o755)
        self.env = {key: value for key, value in os.environ.items() if key not in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "PROXY_PASSTHROUGH", "COMPOSER_CACHE_DIR", "WORKTREE_GIT", "FLOWBITE_PROJECT", "HTTP_PORT", "HTTPS_PORT", "HTTP3_PORT")}
        self.env.update(PATH=str(self.directory) + os.pathsep + os.environ["PATH"], WORKSPACE=str(self.workspace), IMAGE="fixture:test", COMMANDS=str(self.commands), XDG_CACHE_HOME=str(self.directory / "cache"))

    def run_profile(self, *arguments, **environment):
        result = subprocess.run(["bash", str(ROOT / "examples/flowbite-xor/run.sh"), *arguments],
                                env=dict(self.env, **environment), capture_output=True, text=True)
        self.calls = [json.loads(line) for line in self.commands.read_text().splitlines()] if self.commands.exists() else []
        return result

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
        mount = self.calls[0]["overlay"]["services"]["php"]["volumes"][0]
        self.assertEqual(mount["target"], "/run/composer-cache")
        self.assertFalse(mount["bind"]["create_host_path"])
        self.assertEqual(self.calls[0]["env"]["PUID"], "0")
        absent = cache / "absent"
        self.assertEqual(self.run_profile("up", COMPOSER_CACHE_DIR=str(absent)).returncode, 64)
        self.assertFalse(absent.exists())

    def test_up_prepares_dependencies_then_test_cache_then_served_page(self):
        self.assertEqual(self.run_profile("up").returncode, 0)
        args = [call["args"] for call in self.calls]
        self.assertIn("--wait", args[0])
        self.assertIn("--prepare", args[1])
        self.assertEqual(args[2][-3:], ["php", "npm", "ci"])
        self.assertEqual(args[3][-3:], ["bin/console", "cache:warmup", "--env=test"])
        self.assertEqual(args[4][-1], "https://localhost/")
        self.assertTrue(all(call["env"]["PLAYWRIGHT_VERSION"] == "1.58.2" for call in self.calls))
        self.assertFalse(any("run" == args[0] for args in args))

    def test_failed_start_stops_setup_and_does_not_run_npm(self):
        self.assertEqual(self.run_profile("up", MOCK_UP_FAIL="1").returncode, 1)
        self.assertEqual(len(self.calls), 1)

    def test_inexact_browser_pin_is_rejected_before_docker(self):
        (self.workspace / "package.json").write_text(json.dumps({"devDependencies": {"@playwright/test": "^1.58.2"}}))
        self.assertEqual(self.run_profile("up").returncode, 64)
        self.assertEqual(self.calls, [])
