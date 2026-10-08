"""Resource discovery and resolution contracts, independent of publication fixtures."""
import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import library
from xorder import model
from xorder.resolve import resolve, validate_lock


def definition(name="composer", kind="binary", revision="1.0.0"):
    details = {"upstream_version": "2.0.0", "source_url": "https://example.test/composer.phar",
               "sha256": "a" * 64, "filename": "composer.phar", "executable": "bin/composer.phar"}
    if kind != "binary":
        details = {"files": [{"source": "example.txt", "destination": f"{name}/example.txt"}]}
        if kind == "environment":
            details["backend"] = "devenv"
        elif kind == "configuration":
            details["target_application"] = "editor"
        else:
            details["audience"] = "coding-agents"
    return {"schema_version": 2, "id": f"{kind}/{name}", "kind": kind, "name": name,
            "revision": revision, "purpose": "Controlled test resource",
            "capabilities": ["package-management"], "targets": ["linux/amd64"],
            "prerequisites": {"commands": ["php"] if kind == "binary" else []},
            "documentation": f"docs/resources/{kind}-{name}.md", "details": details,
            "verification": {"command": ["python3", "scripts/test-verifier.py"]}}


def record(d):
    return {"schema_version": 2, "id": d["id"], "version": d["revision"],
            "source_commit": "b" * 40, "source_tag": f"{d['id']}/v{d['revision']}",
            "created_at": "2026-01-01T00:00:00Z", "input_fingerprint": "c" * 64,
            "lifecycle": "available", "definition": copy.deepcopy(d),
            "publication": {"url": "https://example.test/releases/test.tar", "sha256": "a" * 64,
                            "filename": d["details"].get("filename", "test.tar"), "size_bytes": 10,
                            "format": "file" if d["kind"] == "binary" else "tar",
                            "public_download_verified_at": "2026-01-01T00:00:00Z",
                            "evidence": "https://example.test/public-download"},
            "verification": {"status": "passed", "surface": "controlled-fixture",
                             "evidence": "https://example.test/verification",
                             "commands": [["python3", "scripts/test-verifier.py", "/staged"]]}}


def profile(*ids):
    return {"schema_version": 2, "id": "profile/test", "revision": "1.0.0",
            "purpose": "Controlled profile",
            "roles": [{"name": f"role-{index}", "alternatives": [{"id": ident}]} for index, ident in enumerate(ids)]}


class ResourceContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(model.ROOT / "schemas", self.root / "schemas")
        self.target = {"platform": "linux/amd64", "commands": ["php"], "scope": "project", "harness": "codex"}

    def add(self, d, released=True):
        path = self.root / "artifacts" / d["id"] / "definition.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(model.encoded(d))
        if released:
            release = self.root / "release-records/artifacts" / d["id"] / f"{d['revision']}.json"
            release.parent.mkdir(parents=True, exist_ok=True)
            release.write_text(model.encoded(record(d)))

    def cat(self):
        return model.catalog(self.root, image_records=[])

    def resolve(self, p, **kwargs):
        return resolve(p, self.cat(), kwargs.pop("target", self.target), root=self.root, **kwargs)

    def test_existing_image_view_preserves_every_record_and_exact_identity(self):
        ledger = library.records()
        self.assertEqual(model.encoded(library.catalog(ledger)), (model.ROOT / "catalog.json").read_text())
        cat = model.catalog(image_records=ledger)
        expected = {(r["line_id"], r["version"]): r for r in ledger}
        for entry in cat["resources"]:
            if entry["kind"] != "image":
                continue
            release = expected[(entry["id"][len("image/"):], entry["version"])]
            self.assertEqual(entry["identity"], release["publication"]["repository"] + "@" + release["publication"]["digest"])
            self.assertNotIn("inventory", json.dumps(entry))
            self.assertEqual(entry["targets"], [p["platform"] for p in release["platforms"]])
        self.assertLess(len(model.encoded(cat)), len(model.encoded(library.catalog(ledger))))

    def test_authored_intent_never_becomes_an_available_catalog_entry(self):
        self.add(definition(), released=False)
        self.assertIn("binary/composer", model.definitions(self.root))
        self.assertEqual(self.cat()["resources"], [])

    def test_new_records_do_not_enter_legacy_image_ledger(self):
        self.add(definition())
        self.assertEqual(library.records(self.root), [])
        self.assertEqual(self.cat()["resources"][0]["identity"], "sha256:" + "a" * 64)

    def test_catalog_generation_is_deterministic_and_compact(self):
        self.add(definition("second"))
        self.add(definition("first"))
        cat = self.cat()
        self.assertEqual(cat, self.cat())
        self.assertEqual([item["id"] for item in cat["resources"]], ["binary/first", "binary/second"])
        self.assertNotIn("definition", cat["resources"][0])
        self.assertNotIn("source_commit", cat["resources"][0])
        model.validate_schema(cat, "catalog-v2.schema.json", self.root)

    def test_record_snapshot_and_upstream_bytes_cannot_disagree(self):
        r = record(definition())
        r["definition"]["revision"] = "1.1.0"
        with self.assertRaisesRegex(ValueError, "snapshot"):
            model.validate_record(r, self.root)
        r = record(definition())
        r["publication"]["sha256"] = "d" * 64
        with self.assertRaisesRegex(ValueError, "reviewed source bytes"):
            model.validate_record(r, self.root)

    def test_unavailable_record_requires_lifecycle_reason(self):
        r = record(definition())
        r["lifecycle"] = "withdrawn"
        with self.assertRaisesRegex(ValueError, "reason"):
            model.validate_record(r, self.root)

    def test_file_mappings_cannot_escape_or_overlap(self):
        for source, destination in [("../secret", "safe"), ("safe", "/etc/config"), ("safe", "a/../../config")]:
            d = definition("guide", "context")
            d["details"]["files"] = [{"source": source, "destination": destination}]
            with self.subTest(source=source, destination=destination), self.assertRaises(ValueError):
                model.validate_definition(d, self.root)
        d = definition("guide", "context")
        d["details"]["files"] += [{"source": "second.txt", "destination": "guide/example.txt/child"}]
        with self.assertRaisesRegex(ValueError, "Overlapping"):
            model.validate_definition(d, self.root)

    def test_fingerprint_tracks_payload_and_referenced_verification(self):
        d = definition("guide", "context")
        self.add(d, released=False)
        payload = self.root / "artifacts/context/guide/payload/example.txt"
        payload.parent.mkdir()
        payload.write_text("first")
        verifier = self.root / "scripts/test-verifier.py"
        verifier.parent.mkdir()
        verifier.write_text("first")
        before = model.fingerprint(d, self.root)
        payload.write_text("second")
        after_payload = model.fingerprint(d, self.root)
        self.assertNotEqual(before, after_payload)
        verifier.write_text("second")
        self.assertNotEqual(after_payload, model.fingerprint(d, self.root))
        after_verifier = model.fingerprint(d, self.root)
        runtime_cache = payload.parent / ".devenv/runtime-state"
        runtime_cache.parent.mkdir()
        runtime_cache.write_text("not an authored input")
        self.assertEqual(after_verifier, model.fingerprint(d, self.root))

    def test_available_resource_index_is_generated_from_verified_releases(self):
        self.add(definition(), released=False)
        self.assertIn("No verified", model.resource_index(self.cat()))
        self.add(definition())
        index = model.resource_index(self.cat())
        self.assertIn("binary/composer v1.0.0", index)
        self.assertIn("`php`", index)
        self.assertIn("../../release-records/artifacts/binary/composer/1.0.0.json", index)
        self.assertIn("docs/resources/binary-composer.md", model.availability_table(self.cat()))

    def test_resolve_exact_verified_resources(self):
        self.add(definition())
        result = self.resolve(profile("binary/composer"))
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["lock"]["resources"][0]["identity"], "sha256:" + "a" * 64)
        self.assertEqual(result["lock"]["target"], self.target)

    def test_missing_commands_and_unknown_target_facts_are_distinct(self):
        self.add(definition())
        for target, expected in [({"platform": "linux/amd64", "commands": []}, "missing_prerequisite"),
                                 ({"platform": "linux/amd64"}, "target_fact_missing"),
                                 ({"commands": ["php"]}, "target_fact_missing"),
                                 ({"platform": "linux/arm64", "commands": ["php"]}, "untested_target")]:
            with self.subTest(expected=expected):
                result = self.resolve(profile("binary/composer"), target=target)
                self.assertEqual(result["status"], "resolution_failed")
                self.assertEqual(result["gaps"][0]["mismatches"][0]["reasons"][0]["code"], expected)
                self.assertNotIn("lock", result)

    def test_a_newer_version_never_silently_replaces_a_pin(self):
        self.add(definition())
        p = profile("binary/composer")
        prior = self.resolve(p)["lock"]
        self.add(definition(revision="1.1.0"))
        self.assertEqual(self.resolve(p)["lock"]["resources"][0]["version"], "1.1.0")
        self.assertEqual(self.resolve(p, pins=prior)["lock"]["resources"][0]["version"], "1.0.0")
        p["roles"][0]["alternatives"][0]["version"] = "1.1.0"
        result = self.resolve(p, pins=prior)
        self.assertEqual(result["gaps"][0]["code"], "pin_unverified_or_incompatible")

    def test_multiple_compatible_variants_need_an_explicit_choice(self):
        self.add(definition("composer"))
        self.add(definition("alternative"))
        p = profile("binary/composer")
        p["roles"][0]["alternatives"].append({"id": "binary/alternative"})
        result = self.resolve(p)
        self.assertEqual(result["gaps"][0]["code"], "ambiguous_resources")

    def test_conditions_deliver_only_matching_roles(self):
        self.add(definition("guide", "context"))
        p = profile("context/guide")
        p["roles"][0]["when"] = {"harness": ["claude"], "scope": "project"}
        result = self.resolve(p)
        self.assertEqual(result["lock"]["resources"], [])
        result = self.resolve(p, target={"platform": "linux/amd64", "commands": [], "scope": "project"})
        self.assertEqual(result["gaps"][0]["code"], "target_fact_missing")

    def test_overlay_is_explicit_pinned_and_cannot_override_unknown_roles(self):
        self.add(definition("guide", "context"))
        p = profile("context/unpublished")
        overlay = {"roles": {"role-0": {"alternatives": [{"id": "context/guide"}]}}, "target": {"harness": "claude"}}
        before = copy.deepcopy(p)
        result = self.resolve(p, overlay=overlay, profile_sha256="f" * 64, overlay_sha256="e" * 64)
        self.assertEqual(result["lock"]["profile"]["sha256"], "f" * 64)
        self.assertEqual(result["lock"]["profile"]["overlay_sha256"], "e" * 64)
        self.assertEqual(result["lock"]["target"]["harness"], "claude")
        self.assertEqual(p, before)
        with self.assertRaisesRegex(ValueError, "unknown roles"):
            self.resolve(p, overlay={"roles": {"unknown": {}}})

    def test_optional_unavailable_resources_do_not_fabricate_releases(self):
        p = profile("context/unpublished")
        p["roles"][0]["optional"] = True
        result = self.resolve(p)
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["lock"]["resources"], [])
        self.assertEqual(len(result["skipped"]), 1)

    def test_dependency_order_cycles_and_conflicting_versions(self):
        child = definition("guide", "context")
        parent = definition("editor", "configuration")
        parent["prerequisites"]["resources"] = [{"id": child["id"], "version": "1.0.0"}]
        self.add(child)
        self.add(parent)
        result = self.resolve(profile(parent["id"]))
        self.assertEqual([item["id"] for item in result["lock"]["resources"]], [child["id"], parent["id"]])
        lock_without_dependency = copy.deepcopy(result["lock"])
        lock_without_dependency["resources"] = lock_without_dependency["resources"][1:]
        with self.assertRaisesRegex(ValueError, "Missing required dependency"):
            validate_lock(lock_without_dependency, self.cat(), self.root)
        self.add(definition("guide", "context", "2.0.0"))
        p = profile(parent["id"], child["id"])
        p["roles"][1]["alternatives"][0]["version"] = "2.0.0"
        result = self.resolve(p)
        self.assertEqual(result["gaps"][0]["code"], "conflicting_resources")
        child["prerequisites"]["resources"] = [{"id": parent["id"]}]
        self.add(child)
        result = self.resolve(profile(parent["id"]))
        self.assertEqual(result["gaps"][0]["code"], "dependency_cycle")

    def test_destination_collisions_fail_before_a_lock_is_returned(self):
        first = definition("first", "context")
        second = definition("second", "context")
        second["details"]["files"][0]["destination"] = first["details"]["files"][0]["destination"]
        self.add(first)
        self.add(second)
        result = self.resolve(profile(first["id"], second["id"]))
        self.assertEqual(result["gaps"][0]["code"], "file_destination_conflict")
        self.assertNotIn("lock", result)

    def test_editing_lock_payload_metadata_is_not_accepted(self):
        self.add(definition())
        lock = self.resolve(profile("binary/composer"))["lock"]
        lock["resources"][0]["details"]["executable"] = "bin/other"
        with self.assertRaisesRegex(ValueError, "metadata disagrees"):
            validate_lock(lock, self.cat(), self.root)


if __name__ == "__main__":
    unittest.main()
