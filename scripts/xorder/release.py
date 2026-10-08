"""Publish HTTP resources, verify anonymous retrieved bytes, and persist evidence."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

from . import model
from .transport import download
from .verify import exercise, prepare

ROOT = Path(__file__).resolve().parents[2]


def run(*args):
    return subprocess.run(args, cwd=ROOT, check=True)


def gh(*args):
    return subprocess.check_output(["gh", *args], cwd=ROOT, text=True)


def now():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def release_info(tag):
    # Listing successfully distinguishes absence from auth/network/API failure.
    pages = json.loads(gh("api", "--paginate", "--slurp", f"repos/{os.environ['GITHUB_REPOSITORY']}/releases"))
    matches = [release for page in pages for release in page if release["tag_name"] == tag]
    if len(matches) > 1:
        raise RuntimeError("Duplicate namespaced release tag")
    return matches[0] if matches else None


def tag_guard(tag, source):
    output = subprocess.check_output(["git", "ls-remote", "--tags", "origin", f"refs/tags/{tag}", f"refs/tags/{tag}^{{}}"], cwd=ROOT, text=True)
    tags = dict(line.split()[::-1] for line in output.splitlines())
    resolved = tags.get(f"refs/tags/{tag}^{{}}", tags.get(f"refs/tags/{tag}"))
    if resolved is not None and resolved != source:
        raise RuntimeError("Exact source tag names a different commit; recover using its original source")


def asset_named(release, filename):
    matches = [asset for asset in release["assets"] if asset["name"] == filename]
    if len(matches) > 1:
        raise RuntimeError("Duplicate release asset filename")
    return matches[0] if matches else None


def download_asset(tag, filename, directory):
    run("gh", "release", "download", tag, "--pattern", filename, "--dir", str(directory))
    path = Path(directory) / filename
    if not path.is_file():
        raise RuntimeError(f"Durable asset is missing: {filename}")
    return path


def public_artifact(definition, publication, directory, root=ROOT):
    artifact = Path(directory) / publication["filename"]
    facts = download(publication["url"], artifact, publication["sha256"])
    if facts["size_bytes"] != publication["size_bytes"]:
        raise RuntimeError("Public artifact size differs from its recorded identity")
    command = exercise(definition, artifact, publication["format"], root)
    return command


def pending(defs, accepted, root=ROOT):
    current = {(record["id"], record["version"]): record for record in accepted}
    result = []
    for key, definition in sorted(defs.items()):
        record = current.get((key, definition["revision"]))
        # Keep changed-input errors in the matrix so publication explains them.
        if record is None or record["input_fingerprint"] != model.fingerprint(definition, root):
            result.append(key)
    return result


def publish(resource_id, source, destination, root=ROOT):
    definition = model.definitions(root)[resource_id]
    fingerprint = model.fingerprint(definition, root)
    prior = [record for record in model.records(root) if (record["id"], record["version"]) == (resource_id, definition["revision"])]
    if prior:
        if prior[0]["input_fingerprint"] != fingerprint:
            raise RuntimeError(f"{resource_id} changed without a new revision")
        return prior[0]
    if not source or not re.fullmatch(r"[a-f0-9]{40}", source):
        raise ValueError("Publication requires the exact source commit")
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    tag = f"{resource_id}/v{definition['revision']}"
    release = release_info(tag)
    record_asset = asset_named(release, "record.json") if release else None
    if record_asset:
        with tempfile.TemporaryDirectory(prefix="xorder-record-") as temporary:
            record = model.validate_record(model.read(download_asset(tag, "record.json", temporary)), root)
        if (record["id"], record["version"], record["input_fingerprint"]) != (resource_id, definition["revision"], fingerprint):
            raise RuntimeError("Interrupted resource release has different inputs; allocate a new revision")
        tag_guard(tag, record["source_commit"])
        if release["draft"]:
            raise RuntimeError("Verified HTTP record belongs to a draft release; recover publication explicitly")
        payload_asset = asset_named(release, record["publication"]["filename"])
        if payload_asset is None or payload_asset["browser_download_url"] != record["publication"]["url"]:
            raise RuntimeError("Recorded release payload is absent")
        with tempfile.TemporaryDirectory(prefix="xorder-public-") as temporary:
            public_artifact(definition, record["publication"], temporary, root)
        (destination / "record.json").write_text(model.encoded(record))
        return record
    # A retry without a record can reuse an existing candidate only at its
    # original source commit. No exact tag or payload asset is ever replaced.
    tag_guard(tag, source)
    if release and release["target_commitish"] != source:
        raise RuntimeError("Existing release source differs; recover using its original commit")
    artifact, facts = prepare(definition, destination, root)
    if not release:
        run("gh", "release", "create", tag, "--target", source, "--draft", "--title", tag,
            "--notes", "Candidate resource. Public retrieval verification and catalog acceptance are pending.")
        release = release_info(tag)
        if release is None:
            raise RuntimeError("Candidate release creation was not observable")
    tag_guard(tag, source)
    payload_asset = asset_named(release, facts["filename"])
    if payload_asset:
        with tempfile.TemporaryDirectory(prefix="xorder-candidate-") as temporary:
            existing = download_asset(tag, facts["filename"], temporary)
            if (hashlib.sha256(existing.read_bytes()).hexdigest(), existing.stat().st_size) != (facts["sha256"], facts["size_bytes"]):
                raise RuntimeError("Exact resource asset already contains different bytes")
    else:
        run("gh", "release", "upload", tag, str(artifact))
    # Unlike registry candidates, GitHub draft assets are not public. Publication
    # exposes bytes, while the merged verified ledger alone makes them selectable.
    if release["draft"]:
        run("gh", "release", "edit", tag, "--draft=false")
    release = release_info(tag)
    payload_asset = asset_named(release, facts["filename"])
    if release["draft"] or payload_asset is None:
        raise RuntimeError("Published resource asset is not observable")
    publication = {**facts, "url": payload_asset["browser_download_url"]}
    with tempfile.TemporaryDirectory(prefix="xorder-public-") as temporary:
        command = public_artifact(definition, publication, temporary, root)
    evidence = f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}"
    completed = now()
    publication.update(public_download_verified_at=completed, evidence=evidence)
    record = {"schema_version": 2, "id": resource_id, "version": definition["revision"],
              "source_commit": source, "source_tag": tag, "created_at": completed,
              "input_fingerprint": fingerprint, "lifecycle": "available", "definition": definition,
              "publication": publication,
              "verification": {"status": "passed", "surface": "github-actions-linux-amd64", "completed_at": completed,
                               "evidence": evidence, "commands": [command]}}
    model.validate_record(record, root)
    record_path = destination / "record.json"
    record_path.write_text(model.encoded(record))
    run("gh", "release", "upload", tag, str(record_path))
    notes = "\n".join("- " + change for change in definition.get("changes", ["Published independently versioned resource."]))
    notes += f"\n\nMigration: {definition.get('migration', 'See the resource usage documentation.')}\n\nSHA256: `{facts['sha256']}`\n\n[Verification]({evidence}). Catalog acceptance is staged through a protected-branch PR."
    run("gh", "release", "edit", tag, "--notes", notes)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("id", nargs="?")
    parser.add_argument("--source", default=os.environ.get("GITHUB_SHA"))
    parser.add_argument("--matrix", action="store_true")
    args = parser.parse_args()
    if args.matrix:
        defs = model.definitions()
        ids = pending(defs, model.records())
        print(json.dumps({"resource": [key for key in ids if defs[key]["kind"] != "environment"], "environment": [key for key in ids if defs[key]["kind"] == "environment"]}))
    else:
        if args.id is None:
            parser.error("resource id is required")
        publish(args.id, args.source, ROOT / "out" / "resources" / args.id)


if __name__ == "__main__":
    main()
