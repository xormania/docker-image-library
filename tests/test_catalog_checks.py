"""Public evidence gates and immutable ledger edits, without image builds."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import catalog_checks as checks
from test_library import record


class PublicEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.record = record("php-dev/8.4-trixie")
        self.durable = copy.deepcopy(self.record)
        self.release = {"draft": False, "tag_name": self.record["source_tag"],
                        "target_commitish": self.record["source_commit"],
                        "assets": [{"name": "record.json", "digest": "sha256:" + "e" * 64,
                                    "browser_download_url": "https://example.test/record.json"}]}
        self.remote = {"digest": self.record["publication"]["digest"], "platforms": {}}

    def verify(self):
        def transfer(url, destination, expected):
            self.assertEqual(url, "https://example.test/record.json")
            self.assertEqual(expected, "e" * 64)
            destination.write_text(json.dumps(self.durable))
        with patch.object(checks, "public_release", return_value=self.release), \
                patch.object(checks, "download", side_effect=transfer) as download, \
                patch.object(checks, "resolve", return_value=self.remote) as resolve:
            result = checks.verify_image_record(self.record, "xormania/xorder")
            download.assert_called_once()
            resolve.assert_called_once_with("ghcr.io/xormania/php-dev:8.4-trixie-v1.0.0")
            return result

    def test_single_manifest_and_index_resolve_public_digests(self):
        self.assertEqual(self.verify(), self.record)
        self.remote["platforms"] = {"linux/amd64": self.record["platforms"][0]["digest"]}
        self.assertEqual(self.verify(), self.record)

    def test_lifecycle_change_can_differ_from_original_durable_record(self):
        self.record.update(lifecycle="withdrawn", reason="Regression", replacement="v1.0.1",
                           lifecycle_date="2026-10-09")
        self.verify()

    def test_durable_facts_must_equal_proposed_facts(self):
        self.durable["resolved_base"] = "test@sha256:" + "f" * 64
        with self.assertRaisesRegex(RuntimeError, "durable Release asset"):
            self.verify()

    def test_missing_checksum_or_ambiguous_asset_rejected_before_download(self):
        for assets in ([], [{"name": "record.json"}], self.release["assets"] * 2):
            with self.subTest(assets=assets), \
                    patch.object(checks, "public_release", return_value={**self.release, "assets": assets}), \
                    patch.object(checks, "download") as download:
                with self.assertRaisesRegex(RuntimeError, "asset checksum"):
                    checks.verify_image_record(self.record, "xormania/xorder")
                download.assert_not_called()

    def test_draft_or_wrong_source_release_rejected(self):
        for change in ({"draft": True}, {"target_commitish": "f" * 40}, {"tag_name": "wrong"}):
            with self.subTest(change=change), \
                    patch.object(checks, "public_release", return_value={**self.release, **change}), \
                    patch.object(checks, "download") as download:
                with self.assertRaisesRegex(RuntimeError, "Source Release"):
                    checks.verify_image_record(self.record, "xormania/xorder")
                download.assert_not_called()

    def test_unavailable_or_wrong_exact_digest_rejected(self):
        for remote in (None, {"digest": "sha256:" + "f" * 64, "platforms": {}}):
            self.remote = remote
            with self.subTest(remote=remote), self.assertRaisesRegex(RuntimeError, "exact image digest"):
                self.verify()

    def test_wrong_or_missing_index_platform_rejected(self):
        for platforms in ({"linux/amd64": "sha256:" + "f" * 64},
                          {"linux/arm64": self.record["platforms"][0]["digest"]}):
            self.remote["platforms"] = platforms
            with self.subTest(platforms=platforms), self.assertRaisesRegex(RuntimeError, "platform digest"):
                self.verify()

    def test_corrupt_download_fails_before_registry_query(self):
        with patch.object(checks, "public_release", return_value=self.release), \
                patch.object(checks, "download", side_effect=ValueError("download checksum mismatch")), \
                patch.object(checks, "resolve") as resolve:
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                checks.verify_image_record(self.record, "xormania/xorder")
            resolve.assert_not_called()


class LedgerChangeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.git("init", "--initial-branch=master")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.test")
        self.original = record("php-dev/8.4-trixie")
        self.write(self.original)
        self.commit()
        self.base = self.git("rev-parse", "HEAD").strip()

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, text=True, stderr=subprocess.PIPE)

    def write(self, value, relative=None):
        relative = relative or f"release-records/{value['line_id']}/{value['version']}.json"
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value))

    def commit(self):
        self.git("add", ".")
        self.git("commit", "--allow-empty", "-m", "Fixture")

    def test_only_new_images_selected_from_mixed_records(self):
        new = record("php-dev/8.4-trixie", "1.0.1")
        self.write(new)
        self.write({"not": "an image"}, "release-records/artifacts/configuration/test/1.0.0.json")
        self.commit()
        self.assertEqual(list(checks.changed_image_records(self.base, self.root)), [new])

    def test_lifecycle_changes_do_not_reverify_unavailable_artifacts(self):
        changed = copy.deepcopy(self.original)
        changed.update(lifecycle="withdrawn", reason="Regression", replacement="v1.0.1",
                       lifecycle_date="2026-10-09")
        self.write(changed)
        self.commit()
        self.assertEqual(list(checks.changed_image_records(self.base, self.root)), [])

    def test_existing_evidence_cannot_change(self):
        changed = copy.deepcopy(self.original)
        changed["source_commit"] = "f" * 40
        self.write(changed)
        self.commit()
        with self.assertRaisesRegex(RuntimeError, "immutable"):
            list(checks.changed_image_records(self.base, self.root))

    def test_identity_must_match_record_path(self):
        self.write(record("php-dev/8.4-trixie", "1.0.1"), "release-records/other/1.0.1.json")
        self.commit()
        with self.assertRaisesRegex(RuntimeError, "path disagrees"):
            list(checks.changed_image_records(self.base, self.root))

    def test_manual_scan_checks_existing_records(self):
        self.assertEqual(list(checks.changed_image_records(None, self.root)), [self.original])
