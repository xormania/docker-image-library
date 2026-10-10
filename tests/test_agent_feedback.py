"""Regression coverage for cache integrity, MCP shell sessions and host budgets."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "examples/shared"))
sys.path.insert(0, str(ROOT / "examples/serena"))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cache = load("dependency_cache", "examples/flowbite-xor/cache.py")
runtime = load("host_runtime", "examples/shared/runtime.py")
client = load("shell_serena", "examples/serena/client.py")
integration = load("serena_integration", "images/php-serena/integration.py")


class DependencySnapshotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.vendor = self.root / "one/demo/vendor"
        (self.vendor / "composer").mkdir(parents=True)
        (self.vendor / "composer/installed.json").write_text('{"dev":true,"packages":[]}')
        (self.vendor / "bin").mkdir()
        (self.vendor / "bin/tool").write_text("#!/bin/sh\nexit 0\n")
        (self.vendor / "bin/tool").chmod(0o755)
        self.vendor.joinpath("link").symlink_to("composer/installed.json")
        self.archive = self.root / "vendor.zip"
        cache.write_archive(self.vendor, self.archive, "proof")

    def test_restores_metadata_modes_and_links_in_another_worktree(self):
        target = self.root / "two/demo/vendor"
        self.assertTrue(cache.restore_archive(self.archive, target, "proof", self.root / "two"))
        self.assertEqual((target / "composer/installed.json").read_bytes(), (self.vendor / "composer/installed.json").read_bytes())
        self.assertEqual((target / "bin/tool").stat().st_mode & 0o777, 0o755)
        self.assertTrue((target / "link").is_symlink())
        self.assertFalse(cache.restore_archive(self.archive, target, "proof", self.root / "two"))

    def test_corrupt_snapshot_never_promotes_partial_dependencies(self):
        with zipfile.ZipFile(self.archive) as source:
            data = {name: source.read(name) for name in source.namelist()}
        data["files/composer/installed.json"] = b"corrupt"
        with zipfile.ZipFile(self.archive, "w") as output:
            for name, value in data.items():
                output.writestr(name, value)
        target = self.root / "two/demo/vendor"
        with self.assertRaisesRegex(ValueError, "checksum"):
            cache.restore_archive(self.archive, target, "proof", self.root / "two")
        self.assertFalse(target.exists())

    def test_lock_runtime_and_image_each_invalidate_reuse(self):
        project = self.vendor.parent
        (project / "composer.lock").write_text('{"packages":[]}')
        (project / "composer.json").write_text('{}')
        first = cache.identity(project, "vendor", "image:a", "8.5")
        self.assertNotEqual(first, cache.identity(project, "vendor", "image:b", "8.5"))
        self.assertNotEqual(first, cache.identity(project, "vendor", "image:a", "8.4"))
        (project / "composer.lock").write_text('{"packages":[{"version":"new"}]}')
        self.assertNotEqual(first, cache.identity(project, "vendor", "image:a", "8.5"))

    def test_archive_cannot_write_through_a_link_or_outside_workspace(self):
        for files in ({"../../escape": {"sha256": "bad", "mode": 0o644}},
                      {"link": {"link": "/tmp"}},
                      {"link": {"link": "composer"}, "link/file": {"sha256": "bad", "mode": 0o644}}):
            with self.subTest(files=files), zipfile.ZipFile(self.archive, "w") as output:
                output.writestr("manifest.json", json.dumps({"schema": 1, "identity": "proof", "files": files}))
            with self.assertRaises(ValueError):
                cache.restore_archive(self.archive, self.root / "two/demo/vendor", "proof", self.root / "two")


class HostBudgetTests(unittest.TestCase):
    def test_another_worktree_cannot_start_a_second_heavy_run(self):
        with tempfile.TemporaryDirectory() as directory:
            env = dict(os.environ, XDG_CACHE_HOME=directory, XORDER_TEST_MAX_RUNS="1")
            with runtime.heavy_run(Path(directory), env):
                script = "import sys; from pathlib import Path; import runtime;\nwith runtime.heavy_run(Path(sys.argv[1]), __import__('os').environ): pass"
                result = subprocess.run([sys.executable, "-c", script, directory],
                    env=dict(env, PYTHONPATH=str(ROOT / "examples/shared")), capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Another heavy test run", result.stderr)
            with runtime.heavy_run(Path(directory), env) as workers:
                self.assertGreaterEqual(workers, 1)

    def test_busy_host_reduces_worker_budget(self):
        facts = {"cpus": 8, "load": 7, "memory_available": 2 * 1024**3}
        with patch.object(runtime, "resources", return_value=facts):
            self.assertEqual(runtime.worker_budget(Path("."), {}), 1)


class ShellMCPTests(unittest.TestCase):
    def test_session_identity_and_execution_failure_are_machine_readable(self):
        result = integration.enrich({"result": {"content": [{"type": "text", "text": "Your Serena session id is `example`."}]}})
        self.assertEqual(result["result"]["structuredContent"]["session_id"], "example")
        error = integration.enrich({"result": {"content": [{"type": "text", "text": "RuntimeError: language server not running"}]}})
        self.assertTrue(error["result"]["isError"])

    def test_shell_client_reuses_one_protocol_session_and_does_not_hide_errors(self):
        source = '''import json,sys
for line in sys.stdin:
 m=json.loads(line)
 if 'id' not in m: continue
 p=m.get('params',{})
 if m['method']=='initialize': result={'protocolVersion':'2025-03-26','capabilities':{},'serverInfo':{'name':'fixture','version':'1'}}
 elif p.get('name')=='initial_instructions': result={'structuredContent':{'session_id':'fixture'},'content':[]}
 else:
  code=p['arguments']['code']; result={'content':[{'type':'text','text':'RuntimeError: failed' if code=='fail' else code}], 'isError':code=='fail'}
 print(json.dumps({'jsonrpc':'2.0','id':m['id'],'result':result}),flush=True)
'''
        service = client.MCP([sys.executable, "-u", "-c", source], timeout=5)
        try:
            self.assertTrue(service.repl("42")["ok"])
            result = service.repl("fail")
            self.assertFalse(result["ok"])
            self.assertEqual(result["session_id"], "fixture")
            service.process.terminate(); service.process.wait()
            with self.assertRaisesRegex(RuntimeError, "not running"):
                service.repl("again")
        finally:
            service.close()


if __name__ == "__main__":
    unittest.main()
