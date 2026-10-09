import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('package_phpstan', ROOT / 'images/shared/package-phpstan.py')
packaging = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packaging)


class PhpstanPackagingTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.project = Path(temporary.name)
        self.package = self.project / 'vendor/phpstan/phpstan'
        self.native = self.package / 'turbo-ext'
        self.native.mkdir(parents=True)
        for name, payload in {
            '.version': b'0.12.0\n',
            'linux-gnu-x86_64/phpstan_turbo-8.4.so': b'php84',
            'linux-gnu-x86_64/phpstan_turbo-8.5.so': b'php85',
            'linux-gnu-x86_64/phpstan_turbo-8.6-zts.so': b'php86zts',
            'linux-gnu-arm64/phpstan_turbo-8.5.so': b'arm85',
            'linux-musl-x86_64/phpstan_turbo-8.5.so': b'musl85',
            'windows-x86_64/phpstan_turbo-8.5-zts.dll': b'windows',
            'macos-arm64/phpstan_turbo-8.5.so': b'macos',
        }.items():
            self.write_native(name, payload)
        self.untouched = {}
        for name in ('phpstan.phar', 'LICENSE', 'composer.json'):
            path = self.package / name
            path.write_bytes(name.encode())
            self.untouched[path] = path.read_bytes()
        self.target = {'platform': 'linux-gnu-x86_64', 'php_minor': '8.5', 'zts': False, 'debug': False}

    def write_native(self, name, payload):
        path = self.native / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)

    def inventory(self):
        return {path.relative_to(self.native).as_posix(): path.read_bytes()
                for path in self.native.rglob('*') if path.is_file()}

    def package_tools(self):
        with patch.object(packaging, 'runtime', return_value=self.target):
            return packaging.package_tools(self.project)

    def test_matches_runtime_abi_and_preserves_other_package_files(self):
        for platform, minor in (('linux-gnu-x86_64', '8.5'), ('linux-gnu-x86_64', '8.4'),
                                ('linux-gnu-arm64', '8.5'), ('linux-musl-x86_64', '8.5')):
            with self.subTest(platform=platform, minor=minor):
                # Each case needs the original cross-platform bundle.
                before = self.inventory()
                self.target.update(platform=platform, php_minor=minor)
                report = self.package_tools()
                expected = f'{platform}/phpstan_turbo-{minor}.so'
                self.assertEqual(self.inventory(), {name: before[name] for name in ('.version', expected)})
                self.assertEqual(report['retained_sha256'], hashlib.sha256(before[expected]).hexdigest())
                self.assertEqual(report['before_bytes'], sum(map(len, before.values())))
                self.assertEqual(report['removed_bytes'], report['before_bytes'] - report['after_bytes'])
                self.assertEqual(json.loads((self.project / 'phpstan-packaging.json').read_text()), report)
                for path, payload in self.untouched.items():
                    self.assertEqual(path.read_bytes(), payload)
                for name, payload in before.items():
                    self.write_native(name, payload)

    def test_zts_fallback_and_future_compatible_binary(self):
        for minor in ('8.4', '8.5'):
            with self.subTest(minor=minor):
                before = self.inventory()
                self.target.update(php_minor=minor, zts=True)
                report = self.package_tools()
                self.assertIsNone(report['retained_binary'])
                self.assertEqual(self.inventory(), {'.version': before['.version']})
                for name, payload in before.items():
                    self.write_native(name, payload)
        self.write_native('linux-gnu-x86_64/phpstan_turbo-8.5-zts.so', b'future-zts')
        report = self.package_tools()
        self.assertEqual(report['retained_binary'], 'linux-gnu-x86_64/phpstan_turbo-8.5-zts.so')
        self.assertEqual(len(self.inventory()), 2)

    def test_missing_supported_binary_fails_before_deletion(self):
        (self.native / 'linux-gnu-x86_64/phpstan_turbo-8.5.so').unlink()
        before = self.inventory()
        with self.assertRaisesRegex(ValueError, 'Missing compatible'):
            self.package_tools()
        self.assertEqual(self.inventory(), before)
        self.assertFalse((self.project / 'phpstan-packaging.json').exists())

    def test_unknown_layout_and_missing_metadata_fail_before_deletion(self):
        self.write_native('README', b'new layout')
        before = self.inventory()
        with self.assertRaisesRegex(ValueError, 'Unexpected PHPStan Turbo file'):
            self.package_tools()
        self.assertEqual(self.inventory(), before)
        (self.native / 'README').unlink()
        (self.native / '.version').unlink()
        before = self.inventory()
        with self.assertRaisesRegex(ValueError, 'version metadata'):
            self.package_tools()
        self.assertEqual(self.inventory(), before)

    def test_debug_and_unknown_platform_do_not_silently_lose_acceleration(self):
        before = self.inventory()
        for change in ({'debug': True}, {'platform': None}, {'php_minor': '8.7', 'zts': True}):
            with self.subTest(change=change), patch.object(packaging, 'runtime', return_value=self.target | change):
                with self.assertRaises(ValueError):
                    packaging.package_tools(self.project)
        self.assertEqual(self.inventory(), before)

    def test_symlinked_bundle_entries_are_rejected_before_deletion(self):
        before = self.inventory()
        link = self.native / 'linked-platform'
        link.symlink_to(self.native / 'linux-gnu-x86_64', target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Unexpected PHPStan Turbo entry'):
            self.package_tools()
        link.unlink()
        self.assertEqual(self.inventory(), before)

    def test_selection_uses_installed_phar_and_disables_xdebug(self):
        with patch.object(packaging.subprocess, 'check_output', return_value=json.dumps(self.target)) as run:
            self.assertEqual(packaging.runtime(self.package), self.target)
        self.assertEqual(run.call_args.args[0][-1],
                         'phar://' + str(self.package / 'phpstan.phar') + '/src/Turbo/TurboExtensionSelector.php')
        self.assertEqual(run.call_args.kwargs['env']['XDEBUG_MODE'], 'off')

    def test_filter_selects_only_php_parent_validation_jobs(self):
        import sys
        sys.path.insert(0, str(ROOT / 'scripts'))
        from library import affected, definitions
        self.assertEqual(affected(['images/shared/package-phpstan.py'], definitions()), [
            'php-dev/8.4-trixie', 'php-dev/8.5-trixie',
            'php-frankenphp/8.4-trixie', 'php-frankenphp/8.5-trixie',
        ])
