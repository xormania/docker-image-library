import argparse
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runner = load('serena_runner', 'examples/serena/run.py')
launcher = load('serena_launcher', 'images/php-serena/launch.py')
acceptance = load('serena_acceptance', 'tests/fixtures/serena/check.py')


class SerenaTests(unittest.TestCase):
    def test_textual_repl_error_cannot_pass_as_successful_mcp(self):
        client = acceptance.Client.__new__(acceptance.Client)
        client.call = lambda *args: {'content': [{'type': 'text', 'text': 'RuntimeError: failed\n  line 1: answer = 42'}]}
        with self.assertRaisesRegex(AssertionError, 'RuntimeError'):
            client.repl('answer = 42')
        self.assertIn('RuntimeError', client.repl('answer = 42', expected_error=True))

    def test_runner_keeps_sibling_sources_visible_and_enforces_readonly(self):
        with tempfile.TemporaryDirectory(prefix='serena checkout ') as directory:
            root = Path(directory)
            (root / 'demo').mkdir()
            args = argparse.Namespace(workspace=root, project='demo', image='local:proof', read_only=True)
            command = runner.command(args)
            self.assertIn(f'type=bind,src={root},dst=/workspace,readonly', command)
            self.assertEqual(command[-3:], ['--project', '/workspace/demo', '--read-only'])
            self.assertIn('--network=none', command)
            self.assertIn('--pull=never', command)
            self.assertNotIn('--tty', command)
            args.project = '..'
            with self.assertRaisesRegex(ValueError, 'inside'):
                runner.command(args)

    def test_project_configuration_is_preserved_and_conflicts_are_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / '.serena').mkdir()
            source = root / '.serena/project.yml'
            source.write_text(json.dumps({'project_name': 'consumer', 'ignored_paths': ['generated']}))
            original = source.read_bytes()
            config = launcher.project_config(root, True, json.loads)
            self.assertEqual(config['language_servers'], ['php_phpactor'])
            self.assertEqual(config['ignored_paths'], ['generated'])
            self.assertTrue(config['read_only'])
            self.assertEqual(source.read_bytes(), original)
            (root / '.serena/project.local.yml').write_text('{"language_servers": ["php"]}')
            with self.assertRaisesRegex(ValueError, 'php_phpactor'):
                launcher.project_config(root, False, json.loads)

    def test_serena_inputs_select_only_the_php85_parent_tree(self):
        from library import affected, definitions
        for path in ('images/php-serena/Dockerfile', 'images/php-serena/requirements-build.txt',
                     'examples/serena/run.py', 'tests/fixtures/serena/check.py',
                     'tests/fixtures/serena/consumer.json'):
            with self.subTest(path=path):
                self.assertEqual(affected([path], definitions()), ['php-dev/8.5-trixie'])


if __name__ == '__main__':
    unittest.main()
