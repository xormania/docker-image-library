import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "images/shared" / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


coverage = module("php-coverage")
testing = module("php-tests")


class PhpTestingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name)
        (self.project / "src").mkdir()
        (self.project / "vendor/composer").mkdir(parents=True)
        (self.project / "vendor/bin").mkdir()
        self.packages = [{"name": "phpunit/phpunit", "version": "13.4.0", "source": {"reference": "unit"}},
                         {"name": "phpstan/phpstan", "version": "2.3.0", "dist": {"reference": "stan"}}]
        (self.project / "composer.lock").write_text(json.dumps({"packages": [], "packages-dev": self.packages}))
        (self.project / "vendor/composer/installed.json").write_text(json.dumps({"packages": self.packages}))
        for name in ("phpunit", "phpstan"):
            (self.project / "vendor/bin" / name).write_text("<?php\n")

    def test_rejects_stale_tool_version_and_reference_before_execution(self):
        for change in ("version", "reference"):
            with self.subTest(change=change):
                packages = json.loads(json.dumps(self.packages))
                if change == "version":
                    packages[0]["version"] = "12.0.0"
                else:
                    packages[0]["source"]["reference"] = "old"
                (self.project / "vendor/composer/installed.json").write_text(json.dumps({"packages": packages}))
                with self.assertRaisesRegex(ValueError, "differs from"):
                    testing.tool(self.project, "phpunit/phpunit", "phpunit")

    def test_all_requires_both_tools_before_creating_coverage_output(self):
        (self.project / "vendor/bin/phpstan").unlink()
        with patch.dict(os.environ, {"PHPUNIT_PROJECT": str(self.project), "PHPSTAN_PROJECT": str(self.project)}), \
                patch.object(testing.subprocess, "run") as run:
            with self.assertRaisesRegex(ValueError, "Missing project tool"):
                testing.execute("all", [])
        run.assert_not_called()
        self.assertFalse((self.project / "var/coverage").exists())

    def test_all_routes_locked_tools_and_preserves_separate_configuration(self):
        (self.project / "phpunit.xml").touch()
        (self.project / "phpstan.neon").touch()
        environment = {"PHPUNIT_PROJECT": str(self.project), "PHPSTAN_PROJECT": str(self.project),
                       "PHPSTAN_WORKSPACE": str(self.project),
                       "PHPUNIT_CONFIGURATION": "phpunit.xml", "PHPSTAN_CONFIGURATION": "phpstan.neon",
                       "COVERAGE_DRIVER": "pcov", "COVERAGE_CLOVER": "reports/clover.xml"}
        with patch.dict(os.environ, environment), patch.object(testing.subprocess, "run") as run:
            testing.execute("all", [])
        self.assertEqual(run.call_count, 2)
        first, second = run.call_args_list
        self.assertEqual(first.args[0][:3], ["library-php-coverage", "pcov", str(self.project / "vendor/bin/phpunit")])
        self.assertIn(str(self.project / "reports/clover.xml"), first.args[0])
        self.assertEqual(first.kwargs["env"]["COVERAGE_SOURCE"], str(self.project / "src"))
        self.assertEqual(second.args[0][:4], ["php", "-d", "pcov.enabled=0", str(self.project / "vendor/bin/phpstan")])
        self.assertIn(str(self.project / "phpstan.neon"), second.args[0])
        self.assertEqual(second.kwargs["cwd"], self.project)

    def test_phpstan_failure_propagates_and_xdebug_driver_is_explicit(self):
        import subprocess
        with patch.dict(os.environ, {"PHPUNIT_PROJECT": str(self.project), "COVERAGE_DRIVER": "xdebug"}), \
                patch.object(testing.subprocess, "run") as run:
            testing.execute("coverage", ["--filter", "behavior"])
        self.assertEqual(run.call_args.args[0][1], "xdebug")
        self.assertEqual(run.call_args.args[0][-2:], ["--filter", "behavior"])
        with patch.dict(os.environ, {"PHPSTAN_PROJECT": str(self.project)}), \
                patch.object(testing.subprocess, "run", side_effect=subprocess.CalledProcessError(1, "phpstan")):
            with self.assertRaises(subprocess.CalledProcessError):
                testing.execute("phpstan", [])

    def test_analysis_workspace_and_autoloader_are_independent_of_tool_install(self):
        workspace = self.project / "app"
        workspace.mkdir()
        (workspace / "phpstan.neon").touch()
        (workspace / "autoload.php").touch()
        environment = {"PHPSTAN_PROJECT": str(self.project), "PHPSTAN_WORKSPACE": str(workspace),
                       "PHPSTAN_CONFIGURATION": "phpstan.neon", "PHPSTAN_AUTOLOAD_FILE": "autoload.php",
                       "PHPSTAN_PATHS": '["src", "demo/tests"]'}
        with patch.dict(os.environ, environment), patch.object(testing.subprocess, "run") as run:
            testing.execute("phpstan", [])
        self.assertEqual(run.call_args.kwargs["cwd"], workspace)
        self.assertIn(str(workspace / "phpstan.neon"), run.call_args.args[0])
        self.assertIn(str(workspace / "autoload.php"), run.call_args.args[0])
        self.assertEqual(run.call_args.args[0][-2:], ["src", "demo/tests"])

    def test_pcov_removes_xdebug_loader_only_and_cleans_process_configuration(self):
        main = self.project / "php.ini"
        main.write_text('memory_limit=1G\nzend_extension="/usr/lib/xdebug.so"\ndate.timezone=UTC\n')
        scan = self.project / "scan.ini"
        scan.write_text('extension=pcov.so\n zend_extension = xdebug\n\n')
        configuration = json.dumps({"main": str(main), "scanned": str(scan) + ",\n"})
        captured = {}

        def check(command, **kwargs):
            captured["environment"] = kwargs["env"]
            copied_main = Path(command[2])
            copied_scan = Path(kwargs["env"]["PHP_INI_SCAN_DIR"]) / "00000.ini"
            self.assertEqual(copied_main.read_text(), 'memory_limit=1G\ndate.timezone=UTC\n')
            self.assertEqual(copied_scan.read_text(), 'extension=pcov.so\n\n')

        with patch.object(coverage.subprocess, "check_output", return_value=configuration), \
                patch.object(coverage.subprocess, "run", side_effect=check), \
                patch.object(coverage.subprocess, "call", return_value=0) as call:
            self.assertEqual(coverage.run("pcov", ["test.php"], self.project / "src"), 0)
        self.assertIn("pcov.enabled=1", call.call_args.args[0])
        self.assertFalse(Path(captured["environment"]["PHP_INI_SCAN_DIR"]).exists())
        self.assertIn("zend_extension", main.read_text())

    def test_xdebug_disables_pcov_without_rewriting_existing_scan_configuration(self):
        with patch.dict(os.environ, {"PHP_INI_SCAN_DIR": "/original/scan"}), \
                patch.object(coverage.subprocess, "run"), patch.object(coverage.subprocess, "call", return_value=0) as call:
            coverage.run("xdebug", ["test.php"])
        self.assertEqual(call.call_args.args[0], ["php", "-d", "pcov.enabled=0", "test.php"])
        self.assertEqual(call.call_args.kwargs["env"]["XDEBUG_MODE"], "coverage")
        self.assertEqual(call.call_args.kwargs["env"]["PHP_INI_SCAN_DIR"], "/original/scan")
