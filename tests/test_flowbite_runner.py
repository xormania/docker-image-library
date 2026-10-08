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
