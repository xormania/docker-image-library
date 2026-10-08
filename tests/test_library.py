import copy
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from library import ROOT, affected, catalog, definitions, generated, select, validate_record
from release import alias_eligible, exact_guard
import release
from library import fingerprint, pending_releases
from unittest.mock import patch
import tempfile


def record(line, revision="1.0.0", digest="a"):
    d = copy.deepcopy(definitions()[line]); d["revision"] = revision
    inv = {"platform": "linux/amd64", "runtime_version": d["runtime_line"] + ".1",
           "os": {"VERSION_CODENAME": "trixie", "PRETTY_NAME": "Debian 13"},
           "extensions": {e: "test" for e in d["extensions"]}, "tools": {t: "test" for t in d["tools"]}}
    if "node" in d["capabilities"]:
        inv["tools"].update(node="v22.1.0", npm="10.1.0")
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

    def test_metadata_and_fixture_changes_select_only_their_consumers(self):
        defs = definitions()
        self.assertEqual(affected(["scripts/release.py", "scripts/writeback.py", "tests/test_library.py", "tests/requirements/php.json", ".github/workflows/refresh.yml"], defs), [])
        self.assertEqual(affected(["tests/fixtures/php/composer.lock"], defs), ["php-dev/8.4-trixie", "php-dev/8.5-trixie", "php-frankenphp/8.4-trixie", "php-frankenphp/8.5-trixie"])
        self.assertEqual(affected(["tests/fixtures/python/uv.lock"], defs), ["python-dev/3.14-trixie"])
        self.assertEqual(affected(["tests/fixtures/rust/Cargo.lock"], defs), ["rust-dev/1.99-trixie"])
        self.assertEqual(affected(["images/tools.json"], defs), ["php-dev/8.4-trixie", "php-dev/8.5-trixie", "php-frankenphp/8.4-trixie", "php-frankenphp/8.5-trixie", "python-dev/3.14-trixie"])
        self.assertEqual(len(affected(["scripts/new-build-helper.py"], defs)), 6)
        self.assertEqual(len(affected([".github/workflows/new-image-check.yml"], defs)), 6)

    def test_unrelated_tool_pins_do_not_change_release_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            import shutil
            shutil.copytree(ROOT / "images", root / "images")
            defs = definitions(root)
            before = {line: fingerprint(d, root) for line, d in defs.items()}
            path = root / "images/tools.json"
            tools = json.loads(path.read_text())
            tools["uv"]["digest"] = "sha256:" + "f" * 64
            path.write_text(json.dumps(tools))
            after = {line: fingerprint(d, root) for line, d in defs.items()}
            self.assertNotEqual(before["python-dev/3.14-trixie"], after["python-dev/3.14-trixie"])
            for line in ("php-dev/8.4-trixie", "php-browser/8.4-trixie", "rust-dev/1.99-trixie"):
                self.assertEqual(before[line], after[line])

    def test_tailwind_checksum_changes_only_the_project_profiles(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            import shutil
            shutil.copytree(ROOT / "images", root / "images")
            defs = definitions(root)
            before = {line: fingerprint(d, root) for line, d in defs.items()}
            path = root / "images/tools.json"
            tools = json.loads(path.read_text())
            tools["tailwind"]["sha256"] = "f" * 64
            path.write_text(json.dumps(tools))
            changed = [line for line, d in defs.items() if fingerprint(d, root) != before[line]]
            self.assertEqual(changed, ["flowbite-xor-dev/8.4-trixie", "flowbite-xor-dev/8.5-trixie"])

    def test_release_matrix_preserves_incomplete_peers_and_changed_input_guards(self):
        defs = definitions()
        accepted = []
        import hashlib
        for line, d in sorted(defs.items(), key=lambda item: bool(item[1]["base"].get("parent"))):
            r = record(line, d["revision"])
            fp = fingerprint(d)
            if d["base"].get("parent"):
                parent = next(p for p in accepted if p["line_id"] == d["base"]["parent"])
                ref = parent["publication"]["repository"] + "@" + parent["publication"]["digest"]
                fp = hashlib.sha256((fp + ref).encode()).hexdigest()
            r["input_fingerprint"] = fp
            accepted.append(r)
        self.assertEqual(pending_releases(defs, []), ["php-dev/8.4-trixie", "php-dev/8.5-trixie", "php-frankenphp/8.4-trixie", "php-frankenphp/8.5-trixie", "python-dev/3.14-trixie", "rust-dev/1.99-trixie"])
        self.assertEqual(pending_releases(defs, accepted), [])
        missing = [r for r in accepted if r["line_id"] != "php-browser/8.4-trixie"]
        self.assertEqual(pending_releases(defs, missing), ["php-dev/8.4-trixie"])
        changed = copy.deepcopy(accepted)
        next(r for r in changed if r["line_id"] == "rust-dev/1.99-trixie")["input_fingerprint"] = "0" * 64
        self.assertEqual(pending_releases(defs, changed), ["rust-dev/1.99-trixie"])

    def test_frankenphp_and_project_profile_selection_and_scope(self):
        defs = definitions()
        req = {"runtime_line": "8.5", "capabilities": ["frankenphp", "worker-server"], "extensions": ["intl", "apcu"]}
        cat = catalog([record("php-frankenphp/8.5-trixie"), record("flowbite-xor-dev/8.5-trixie", digest="e")])
        self.assertEqual(select(cat, req)["image"]["line_id"], "php-frankenphp/8.5-trixie")
        req["capabilities"].append("node")
        self.assertEqual(select(cat, req)["image"]["line_id"], "flowbite-xor-dev/8.5-trixie")
        self.assertEqual(select(catalog([]), req)["status"], "no_matching_image")
        self.assertEqual(affected(["examples/flowbite-xor/run.sh"], defs), ["php-frankenphp/8.4-trixie", "php-frankenphp/8.5-trixie"])
        self.assertEqual(affected(["images/flowbite-xor-dev/Dockerfile"], defs), ["php-frankenphp/8.4-trixie", "php-frankenphp/8.5-trixie"])
        from library import children
        self.assertEqual(children("php-frankenphp/8.5-trixie", defs), ["flowbite-xor-dev/8.5-trixie"])

    def test_project_requirements_select_cached_profiles_and_reject_the_old_image(self):
        older = record("flowbite-xor-dev/8.5-trixie", "1.0.0")
        older["definition"]["capabilities"].remove("tailwind-cli")
        older["definition"]["tools"].remove("tailwindcss")
        del older["platforms"][0]["inventory"]["tools"]["tailwindcss"]
        for runtime, fixture, revision in (("8.5", "flowbite-xor.json", "1.1.0"),
                                           ("8.4", "flowbite-xor-8.4.json", "1.0.0")):
            with self.subTest(runtime=runtime):
                req = json.loads((ROOT / "tests/requirements" / fixture).read_text())
                current = record("flowbite-xor-dev/" + runtime + "-trixie", revision, "e")
                selected = select(catalog([older, current]), req)["image"]
                self.assertEqual(selected["line_id"], current["line_id"])
                self.assertEqual(selected["version"], revision)
                self.assertEqual(select(catalog([older]), req)["status"], "no_matching_image")

    def test_generated_output_is_deterministic(self):
        self.assertEqual(generated(), generated())

    def test_node_input_and_inventory_are_scoped_to_the_project_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            import shutil
            shutil.copytree(ROOT / "images", root / "images")
            defs = definitions(root)
            before = {line: fingerprint(d, root) for line, d in defs.items()}
            path = root / "images/tools.json"
            tools = json.loads(path.read_text())
            tools["node"]["digest"] = "sha256:" + "f" * 64
            path.write_text(json.dumps(tools))
            changed = [line for line, d in defs.items() if fingerprint(d, root) != before[line]]
            self.assertEqual(changed, ["flowbite-xor-dev/8.4-trixie", "flowbite-xor-dev/8.5-trixie"])
        r = record("flowbite-xor-dev/8.5-trixie")
        r["platforms"][0]["inventory"]["tools"]["node"] = "v24.1.0"
        with self.assertRaisesRegex(AssertionError, "Node line must match CI"):
            validate_record(r)


class PromotionTests(unittest.TestCase):
    def test_project_publication_uses_the_exact_verified_parent(self):
        parent = record("php-frankenphp/8.5-trixie", digest="f")
        child = record("flowbite-xor-dev/8.5-trixie", digest="e")
        with tempfile.TemporaryDirectory() as tmp, patch.object(release, "ROOT", Path(tmp)), \
                patch.object(release, "publish", side_effect=[parent, child]) as publish:
            release.publish_tree("php-frankenphp/8.5-trixie", "b" * 40)
            self.assertEqual(publish.call_args_list[1].args[3], "ghcr.io/xormania/php-frankenphp@sha256:" + "f" * 64)
            self.assertEqual(json.loads((Path(tmp) / "out/flowbite-xor-dev-8.5-trixie/record.json").read_text()), child)

    def test_exact_tag_is_idempotent_but_never_reassigned(self):
        exact_guard(None, "a"); exact_guard("a", "a")
        with self.assertRaises(RuntimeError): exact_guard("a", "b")

    def test_old_job_cannot_advance_alias_over_newer_record(self):
        old = record("php-dev/8.4-trixie")
        new = record("php-dev/8.4-trixie", "1.1.0", "e")
        self.assertFalse(alias_eligible(old, [old, new]))
        self.assertTrue(alias_eligible(new, [old, new]))
        self.assertFalse(alias_eligible(new, [old]))  # unpublished candidate

    def test_last_withdrawn_or_deprecated_release_blocks_existing_alias(self):
        for lifecycle in ("withdrawn", "deprecated"):
            with self.subTest(lifecycle=lifecycle):
                r = record("php-dev/8.4-trixie")
                r["lifecycle"] = lifecycle
                with patch.object(release, "records", return_value=[r]), \
                        patch.object(release, "resolve", return_value={"digest": r["publication"]["digest"]}), \
                        patch.object(release, "run") as run:
                    with self.assertRaisesRegex(RuntimeError, "No available replacement.*php-dev:8.4-trixie-v1"):
                        release.aliases()
                    self.assertFalse(any(call.args[0] == "docker" for call in run.call_args_list))

    def test_retired_alias_that_is_already_absent_needs_no_promotion(self):
        r = record("php-dev/8.4-trixie")
        r["lifecycle"] = "withdrawn"
        with patch.object(release, "records", return_value=[r]), \
                patch.object(release, "resolve", return_value=None), \
                patch.object(release, "run") as run:
            release.aliases()
            self.assertFalse(any(call.args[0] == "docker" for call in run.call_args_list))

    def test_withdrawal_rolls_alias_back_to_available_revision(self):
        old = record("php-dev/8.4-trixie")
        withdrawn = record("php-dev/8.4-trixie", "1.0.1", "e")
        withdrawn["lifecycle"] = "withdrawn"
        with patch.object(release, "records", return_value=[old, withdrawn]), \
                patch.object(release, "resolve", return_value={"digest": old["publication"]["digest"]}), \
                patch.object(release, "run") as run:
            release.aliases()
            promotions = [call.args for call in run.call_args_list if call.args[0] == "docker"]
            self.assertEqual(len(promotions), 1)
            self.assertEqual(promotions[0][-1], old["publication"]["repository"] + "@" + old["publication"]["digest"])

    def test_blocked_major_is_detected_before_other_aliases_change(self):
        available = record("php-dev/8.4-trixie")
        withdrawn = record("php-dev/8.5-trixie")
        withdrawn["lifecycle"] = "withdrawn"
        with patch.object(release, "records", return_value=[available, withdrawn]), \
                patch.object(release, "resolve", return_value={"digest": withdrawn["publication"]["digest"]}), \
                patch.object(release, "run") as run:
            with self.assertRaises(RuntimeError):
                release.aliases()
            self.assertFalse(any(call.args[0] == "docker" for call in run.call_args_list))

    def test_retry_resumes_durable_artifact_without_rebuilding(self):
        r = record("php-dev/8.4-trixie")
        r["input_fingerprint"] = fingerprint(definitions()[r["line_id"]])
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(release, "records", return_value=[]), \
                patch.object(release, "release_asset", return_value=r), \
                patch.object(release, "resolve", return_value={"digest": r["publication"]["digest"]}), \
                patch.object(release, "build") as build, \
                patch.object(release, "promote_exact") as promote, \
                patch.object(release, "finalize_release") as finalize:
            self.assertEqual(release.publish(r["line_id"], "f" * 40, Path(tmp)), r)
            build.assert_not_called()
            promote.assert_called_once_with(r)
            finalize.assert_called_once_with(r)

    def test_changed_inputs_cannot_resume_old_revision(self):
        r = record("php-dev/8.4-trixie")
        r["input_fingerprint"] = "0" * 64
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(release, "records", return_value=[]), \
                patch.object(release, "release_asset", return_value=r), \
                patch.object(release, "build") as build:
            with self.assertRaisesRegex(RuntimeError, "different inputs"):
                release.publish(r["line_id"], "f" * 40, Path(tmp))
            build.assert_not_called()

    def test_ambiguous_existing_exact_tag_never_rebuilds(self):
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(release, "records", return_value=[]), \
                patch.object(release, "release_asset", return_value=None), \
                patch.object(release, "resolve", return_value={"digest": "sha256:" + "a" * 64}), \
                patch.object(release, "build") as build:
            with self.assertRaisesRegex(RuntimeError, "without a durable record"):
                release.publish("php-dev/8.4-trixie", "f" * 40, Path(tmp))
            build.assert_not_called()


if __name__ == "__main__":
    unittest.main()
