"""Human review summaries for mixed publication and recovered branches."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import catalog_summary as summary
from library import affected, definitions
from test_library import record
from test_resources import definition, record as resource_record


class CatalogSummaryTests(unittest.TestCase):
    def test_mixed_summary_has_versions_new_families_sizes_aliases_and_evidence(self):
        old = record("php-dev/8.4-trixie")
        new = record("php-dev/8.4-trixie", "1.0.1")
        new["platforms"][0]["metrics"] = {
            "image_size_bytes": 200 * 1024**2,
            "baseline": {"image_size_bytes": 100 * 1024**2, "version": "1.0.0"}}
        browser = record("php-browser/8.4-trixie")
        downloadable = resource_record(definition())
        body = summary.catalog_body([browser, new, downloadable], [old], [], "xormania/xorder",
                                    {new["source_commit"]: [(22, "https://github.com/xormania/xorder/pull/22")]})
        self.assertIn("**2 verified image releases**", body)
        self.assertIn("**1 verified downloadable resource releases**", body)
        self.assertIn("New image families: `php-browser`", body)
        self.assertIn("| 1.0.0 | 1.0.1 | 200.0 MiB; +100.0 MiB (+100.0%, v1.0.0)", body)
        self.assertIn("ghcr.io/xormania/php-dev:8.4-trixie-v1` → 1.0.1", body)
        self.assertIn("New line | 1.0.0 | Not measured", body)
        self.assertIn("New resource | 1.0.0 | 10 bytes | None", body)
        self.assertIn("releases/tag/php-dev/8.4-trixie/v1.0.1", body)
        self.assertIn("commit/" + new["source_commit"], body)
        self.assertIn("[PR #22]", body)
        self.assertIn("https://example.test/ci", body)

    def test_alias_targets_newest_available_revision_in_compatible_major(self):
        pending = record("php-dev/8.4-trixie", "1.0.1")
        newer = record("php-dev/8.4-trixie", "1.0.2")
        withdrawn = record("php-dev/8.4-trixie", "1.0.3")
        withdrawn["lifecycle"] = "withdrawn"
        other_major = record("php-dev/8.4-trixie", "2.0.0")
        body = summary.catalog_body([pending], [newer, withdrawn, other_major], [], "xormania/xorder")
        self.assertIn("8.4-trixie-v1` → 1.0.2", body)

    def test_source_pr_lookup_deduplicates_commits_and_filters_unmerged_or_other_repo(self):
        def pull(number, merged=True, repo="xormania/xorder"):
            return {"number": number, "html_url": f"https://github.com/{repo}/pull/{number}",
                    "merged_at": "2026-10-09" if merged else None, "base": {"repo": {"full_name": repo}}}
        records = [record("php-dev/8.4-trixie"), record("php-browser/8.4-trixie")]
        with patch.object(summary, "github_json", return_value=[pull(22), pull(23, False), pull(24, repo="other/repo")]) as api:
            result = summary.source_prs(records, "xormania/xorder")
            api.assert_called_once()
            self.assertEqual(result, {records[0]["source_commit"]: [(22, "https://github.com/xormania/xorder/pull/22")]})

    def test_optional_pr_lookup_failure_keeps_source_and_verification_links(self):
        new = record("php-dev/8.4-trixie")
        with patch.object(summary, "github_json", side_effect=URLError("unavailable")), patch("builtins.print"):
            pulls = summary.source_prs([new], "xormania/xorder")
        body = summary.catalog_body([new], [], [], "xormania/xorder", pulls)
        self.assertIn("commit/" + new["source_commit"], body)
        self.assertIn(new["verification"]["evidence"], body)

    def test_recovered_branch_summary_includes_earlier_records(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            def git(*args):
                return subprocess.check_output(["git", *args], cwd=root, text=True, stderr=subprocess.PIPE)
            def commit_record(item):
                path = root / "release-records" / item["line_id"] / (item["version"] + ".json")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(item))
                git("add", ".")
                git("commit", "-m", "Record")
            git("init", "--initial-branch=master")
            git("config", "user.name", "Fixture")
            git("config", "user.email", "fixture@example.test")
            commit_record(record("php-dev/8.4-trixie"))
            base = git("rev-parse", "HEAD").strip()
            first = record("php-dev/8.4-trixie", "1.0.1")
            second = record("php-browser/8.4-trixie")
            commit_record(first)
            commit_record(second)
            proposed = summary.proposed_records(root, base)
            self.assertEqual({item["line_id"] for item in proposed}, {first["line_id"], second["line_id"]})
            self.assertEqual(len(proposed), 2)

    def test_catalog_evidence_changes_do_not_request_image_builds(self):
        self.assertEqual(affected(["scripts/catalog_checks.py", "scripts/catalog_summary.py",
                                   ".github/workflows/catalog.yml"], definitions()), [])
