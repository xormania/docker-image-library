import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from library import ROOT, affected, catalog, definitions, generated, select, validate_record
from release import alias_eligible, exact_guard


def record(line, revision="1.0.0", digest="a"):
    d = copy.deepcopy(definitions()[line]); d["revision"] = revision
    inv = {"platform": "linux/amd64", "runtime_version": d["runtime_line"] + ".1",
           "os": {"VERSION_CODENAME": "trixie", "PRETTY_NAME": "Debian 13"},
           "extensions": {e: "test" for e in d["extensions"]}, "tools": {t: "test" for t in d["tools"]}}
    if d["family"] == "php-browser":
        inv["tools"].update(chromium="Chromium 140.0", chromedriver="ChromeDriver 140.0")
    return {"schema_version": 1, "line_id": line, "version": revision, "source_commit": "b" * 40,
            "source_tag": line + "/v" + revision, "created_at": "2026-01-01T00:00:00Z", "definition": d,
            "resolved_base": "test@sha256:" + "c" * 64, "tools": {}, "input_fingerprint": "d" * 64,
            "lifecycle": "available", "platforms": [{"platform": "linux/amd64", "digest": "sha256:" + digest * 64, "inventory": inv}],
            "publication": {"repository": "ghcr.io/xormania/" + d["family"], "digest": "sha256:" + digest * 64,
                            "exact_tag": d["line"] + "-v" + revision, "public_pull_verified_at": "2026-01-01T00:00:00Z", "evidence": "https://example.test/ci"},
            "verification": {"status": "passed", "surface": "github-actions-linux-amd64", "completed_at": "2026-01-01T00:00:00Z", "evidence": "https://example.test/ci"}}


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.cat = catalog([record("php-dev/8.4-trixie"), record("php-browser/8.4-trixie", digest="e")])

    def test_empty_catalog_does_not_offer_definitions(self):
        self.assertEqual(catalog([])["images"], [])
        self.assertEqual(select(catalog([]), {"runtime_line": "8.4"})["status"], "no_matching_image")

    def test_mock_requirements_have_independent_expected_outcomes(self):
        for name, expected in [("php", "php-dev/8.4-trixie"), ("browser", "php-browser/8.4-trixie"), ("missing-runtime", None), ("missing-capability", None)]:
            with self.subTest(name=name):
                requirements = json.loads((ROOT / "tests/requirements" / (name + ".json")).read_text())
                result = select(self.cat, requirements)
                if expected:
                    self.assertEqual(result["image"]["line_id"], expected)
                else:
                    self.assertEqual(result["status"], "no_matching_image")

    def test_preserve_existing_pin_even_when_new_revision_available(self):
        newer = record("php-dev/8.4-trixie", "1.0.1", "f")
        cat = catalog([record("php-dev/8.4-trixie"), newer])
        req = {"runtime_line": "8.4", "pinned_digest": cat["images"][0]["digest_reference"]}
        result = select(cat, req)
        self.assertTrue(result["preserved_pin"])
        self.assertEqual(result["image"]["version"], "1.0.0")
        req["pinned_digest"] = "unknown"
        self.assertEqual(select(cat, req)["status"], "pin_unverified_or_incompatible")

    def test_unverified_inventory_and_withdrawal_are_rejected(self):
        r = record("php-dev/8.4-trixie")
        del r["platforms"][0]["inventory"]["extensions"]["intl"]
        with self.assertRaises(AssertionError): validate_record(r)
        r = record("php-dev/8.4-trixie"); r["lifecycle"] = "withdrawn"
        with self.assertRaises(AssertionError): validate_record(r)

    def test_docs_only_change_has_no_image_builds(self):
        self.assertEqual(affected(["README.md", "docs/usage.md", "catalog.json", "release-records/php-dev/8.4-trixie/1.0.0.json"], definitions()), [])
        self.assertEqual(affected(["images/php-browser/Dockerfile"], definitions()), ["php-dev/8.4-trixie", "php-dev/8.5-trixie"])
        self.assertIn("rust-dev/1.99-trixie", affected(["images/shared/install.sh"], definitions()))

    def test_generated_output_is_deterministic(self):
        self.assertEqual(generated(), generated())


class PromotionTests(unittest.TestCase):
    def test_exact_tag_is_idempotent_but_never_reassigned(self):
        exact_guard(None, "a"); exact_guard("a", "a")
        with self.assertRaises(RuntimeError): exact_guard("a", "b")

    def test_old_job_cannot_advance_alias_over_newer_record(self):
        old = record("php-dev/8.4-trixie")
        new = record("php-dev/8.4-trixie", "1.1.0", "e")
        self.assertFalse(alias_eligible(old, [old, new]))
        self.assertTrue(alias_eligible(new, [old, new]))
        self.assertFalse(alias_eligible(new, [old]))  # unpublished candidate


if __name__ == "__main__":
    unittest.main()
