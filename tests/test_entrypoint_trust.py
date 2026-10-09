"""Exercise the actual entrypoint with real PEM parsing and isolated OS writes."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Only system mutation and account operations are replaced. OpenSSL and the
# entrypoint itself run normally; real client/system-store behavior is in the
# Docker trust fixture, called by verify-image.sh for every image family.
SYSTEM_COMMAND = r'''#!/usr/bin/env python3
import glob, json, os, pathlib, subprocess, sys
name = pathlib.Path(sys.argv[0]).name
args = sys.argv[1:]
trust_prefix = "/usr/local/share/ca-certificates"
def isolated(value):
    if value == trust_prefix or value.startswith(trust_prefix + "/"):
        return os.environ["TEST_TRUST"] + value[len(trust_prefix):]
    return value
if name == "id":
    print("1000" if "dev" in args else os.environ.get("TEST_UID", "0"))
    raise SystemExit(0)
record = {"command": name, "args": args}
if name == "install":
    sources = [pathlib.Path(arg) for arg in args if arg.endswith(".crt") and not arg.startswith(trust_prefix)]
    record["staged_modes"] = [path.stat().st_mode & 0o777 for path in sources]
with open(os.environ["TEST_MUTATIONS"], "a") as log:
    log.write(json.dumps(record) + "\n")
if name == "install":
    raise SystemExit(subprocess.call(["/usr/bin/install", *map(isolated, args)]))
if name == "rm":
    rewritten = []
    for arg in args:
        target = isolated(arg)
        rewritten.extend(glob.glob(target) or [target])
    raise SystemExit(subprocess.call(["/usr/bin/rm", *rewritten]))
if name == "gosu":
    os.execvp(args[1], args[1:])
'''


class EntrypointTrustTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificates = tempfile.TemporaryDirectory()
        cls.certs = []
        for index in range(2):
            root = Path(cls.certificates.name)
            path = root / f"ca-{index}.pem"
            subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
                            "-keyout", str(root / f"ca-{index}.key"), "-out", str(path), "-days", "1",
                            "-subj", f"/CN=XorderEntrypointFixture{index}",
                            "-addext", "basicConstraints=critical,CA:TRUE"],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            cls.certs.append(path.read_text())

    @classmethod
    def tearDownClass(cls):
        cls.certificates.cleanup()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        for name in ("id", "install", "rm", "update-ca-certificates", "chown", "gosu", "groupmod", "usermod"):
            command = self.bin / name
            command.write_text(SYSTEM_COMMAND)
            command.chmod(0o755)
        self.trust = self.root / "trust"
        self.trust.mkdir()
        self.staging = self.root / "staging"
        self.staging.mkdir()
        self.mutations = self.root / "mutations.jsonl"
        self.bundle = self.root / "bundle.pem"

    def invoke(self, bundle=None, **settings):
        env = {key: value for key, value in os.environ.items()
               if key not in ("LIBRARY_CA_FILE", "PUID", "PGID", "COMPOSER_CAFILE", "NODE_EXTRA_CA_CERTS")}
        env.update(PATH=str(self.bin) + os.pathsep + os.environ["PATH"],
                   TMPDIR=str(self.staging), TEST_TRUST=str(self.trust), TEST_MUTATIONS=str(self.mutations))
        if bundle is not None:
            self.bundle.write_text(bundle)
            env["LIBRARY_CA_FILE"] = str(self.bundle)
        env.update(settings)
        result = subprocess.run(["bash", str(ROOT / "images/shared/entrypoint.sh"), "python3", "-c",
                                 'import json,os; print(json.dumps({k:os.environ.get(k) for k in ("COMPOSER_CAFILE","NODE_EXTRA_CA_CERTS")}))'],
                                env=env, capture_output=True, text=True)
        self.assertEqual(list(self.staging.iterdir()), [], "Temporary PEM staging must be removed on every exit")
        return result

    def calls(self, name):
        calls = [json.loads(line) for line in self.mutations.read_text().splitlines()] if self.mutations.exists() else []
        return [call for call in calls if call["command"] == name]

    def installed(self):
        return sorted((self.trust / "library-proxy").glob("*.crt"))

    def test_single_and_multi_certificate_inputs_have_individual_system_trust_files(self):
        for certificates in (self.certs[:1], self.certs):
            with self.subTest(count=len(certificates)):
                bundle = "# Cloud gateway roots\n\n" + "\n".join(certificates)
                result = self.invoke(bundle.replace("\n", "\r\n"))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual([path.read_text() for path in self.installed()], certificates)
                self.assertTrue(all(path.stat().st_mode & 0o777 == 0o644 for path in self.installed()))
                settings = json.loads(result.stdout)
                self.assertEqual(settings, {"COMPOSER_CAFILE": "/etc/ssl/certs/ca-certificates.crt",
                                            "NODE_EXTRA_CA_CERTS": "/etc/ssl/certs/ca-certificates.crt"})
                self.assertEqual(self.calls("gosu")[-1]["args"][0], "1000:1000")
                self.assertEqual(self.calls("install")[-1]["staged_modes"], [0o600] * len(certificates))

    def test_replacement_removes_stale_managed_roots_and_preserves_unrelated_trust(self):
        legacy = self.trust / "library-proxy.crt"
        legacy.write_text(self.certs[1])
        unrelated = self.trust / "project-ca.crt"
        unrelated.write_text(self.certs[1])
        self.assertEqual(self.invoke("".join(self.certs)).returncode, 0)
        self.assertFalse(legacy.exists())
        self.assertEqual(len(self.installed()), 2)
        self.assertEqual(self.invoke(self.certs[0]).returncode, 0)
        snapshot = {path.name: path.read_bytes() for path in self.installed()}
        self.assertEqual(len(snapshot), 1)
        self.assertEqual(self.invoke(self.certs[0]).returncode, 0)
        self.assertEqual({path.name: path.read_bytes() for path in self.installed()}, snapshot)
        self.assertEqual(unrelated.read_text(), self.certs[1])
        self.assertEqual(len(self.calls("update-ca-certificates")), 3)
        self.assertEqual(self.invoke().returncode, 0)
        self.assertEqual({path.name: path.read_bytes() for path in self.installed()}, snapshot)
        self.assertEqual(len(self.calls("update-ca-certificates")), 3)

    def test_malformed_bundle_is_rejected_without_changing_trust_or_running_the_command(self):
        legacy = self.trust / "library-proxy.crt"
        legacy.write_text(self.certs[1])
        invalid_certificate = "-----BEGIN CERTIFICATE-----\nnot-base64\n-----END CERTIFICATE-----\n"
        cases = ["", "\n# No certificates\n", "invalid\n", invalid_certificate,
                 self.certs[0] + invalid_certificate,
                 self.certs[0] + "-----BEGIN CERTIFICATE-----\ntruncated\n",
                 "-----BEGIN CERTIFICATE-----\n" + self.certs[0],
                 self.certs[0] + "-----END CERTIFICATE-----\n",
                 self.certs[0] + "-----BEGIN PRIVATE KEY-----\nsecret\n-----END PRIVATE KEY-----\n"]
        for bundle in cases:
            with self.subTest(bundle=bundle[:40]):
                result = self.invoke(bundle)
                self.assertEqual(result.returncode, 64, result.stderr)
                self.assertIn("valid PEM certificates", result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertEqual(legacy.read_text(), self.certs[1])
                self.assertEqual(self.installed(), [])
                self.assertEqual(self.calls("update-ca-certificates"), [])
                self.assertEqual(self.calls("install"), [])
                self.assertEqual(self.calls("gosu"), [])

    def test_root_execution_and_explicit_tool_settings_remain_supported(self):
        result = self.invoke(self.certs[0], PUID="0", PGID="0", COMPOSER_CAFILE="/project/composer.pem",
                             NODE_EXTRA_CA_CERTS="/project/node.pem")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls("gosu")[-1]["args"][0], "0:0")
        self.assertEqual(json.loads(result.stdout), {"COMPOSER_CAFILE": "/project/composer.pem",
                                                   "NODE_EXTRA_CA_CERTS": "/project/node.pem"})

    def test_non_root_entrypoint_rejects_system_setup_but_can_use_tool_options(self):
        result = self.invoke(self.certs[0], TEST_UID="1000")
        self.assertEqual(result.returncode, 64)
        self.assertIn("needs the root entrypoint", result.stderr)
        self.assertEqual(self.calls("install"), [])
        result = self.invoke(TEST_UID="1000", COMPOSER_CAFILE="/project/composer.pem")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["COMPOSER_CAFILE"], "/project/composer.pem")
        self.assertEqual(self.calls("gosu"), [])

    def test_source_path_requires_an_absolute_readable_regular_file(self):
        for path in ("relative.pem", str(self.root / "missing.pem"), str(self.root)):
            with self.subTest(path=path):
                result = self.invoke(LIBRARY_CA_FILE=path)
                self.assertEqual(result.returncode, 64)
                self.assertIn("readable absolute PEM file", result.stderr)
                self.assertEqual(self.calls("install"), [])


if __name__ == "__main__":
    unittest.main()
