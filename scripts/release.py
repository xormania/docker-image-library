#!/usr/bin/env python3
"""Build/test/publish once, persist a verified record, and stage docs through a PR."""
import argparse
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from build import build, pinned, verify
from library import ROOT, definitions, encoded, fingerprint, read, records, validate_record, version
from registry import resolve


def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def gh(*args):
    return subprocess.check_output(["gh", *args], text=True)


def now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def exact_guard(current, intended):
    if current is not None and current != intended:
        raise RuntimeError(f"Refusing exact-tag reassignment: {current} != {intended}")


def alias_eligible(candidate, accepted):
    peers = [r for r in accepted if r["line_id"] == candidate["line_id"] and r["lifecycle"] == "available" and version(r["version"])[0] == version(candidate["version"])[0]]
    return bool(peers) and version(candidate["version"]) == max(version(r["version"]) for r in peers)


def release_asset(tag, destination):
    # --clobber is intentionally absent; assets define the durable release identity.
    result = subprocess.run(["gh", "release", "download", tag, "--pattern", "record.json", "--dir", str(destination)], capture_output=True, text=True)
    if result.returncode == 0:
        return validate_record(read(destination / "record.json"))
    # Inspect via the API so a missing asset is distinguished from an API failure.
    releases = json.loads(gh("api", "--paginate", "--slurp", f"repos/{os.environ['GITHUB_REPOSITORY']}/releases"))
    matching = [r for page in releases for r in page if r["tag_name"] == tag]
    if matching and any(a["name"] == "record.json" for a in matching[0]["assets"]):
        raise RuntimeError("A durable release record exists but could not be downloaded")
    return None


def publish(line, source, destination, parent=None):
    d = definitions()[line]
    prior = [r for r in records() if r["line_id"] == line and r["version"] == d["revision"]]
    fp = fingerprint(d)
    if parent:
        import hashlib
        fp = hashlib.sha256((fp + parent).encode()).hexdigest()
    if prior:
        if prior[0]["input_fingerprint"] != fp:
            raise RuntimeError(f"{line} changed without a new revision. Bump {d['revision']}.")
        return prior[0]
    source_tag = f"{line}/v{d['revision']}"
    destination.mkdir(parents=True, exist_ok=True)
    record = release_asset(source_tag, destination)
    if record:
        if record["input_fingerprint"] != fp:
            raise RuntimeError("Interrupted release has different inputs; use a new image revision")
        remote = resolve(record["publication"]["repository"] + "@" + record["publication"]["digest"])
        if not remote or remote["digest"] != record["publication"]["digest"]:
            raise RuntimeError("Recorded artifact is no longer publicly pullable")
        promote_exact(record)
        finalize_release(record)
        return record
    repository = "ghcr.io/xormania/" + d["family"]
    candidate = f"{repository}:{d['line']}-candidate-v{d['revision']}-{source}"
    # An existing exact tag without a durable record is ambiguous; never rebuild it.
    existing_exact = resolve(f"{repository}:{d['line']}-v{d['revision']}", authenticated=True)
    if existing_exact:
        raise RuntimeError("Exact tag exists without a durable record. Recover its record; do not rebuild.")
    existing = resolve(candidate, authenticated=True)
    inventory_path = destination / "inventory.json"
    resolved_base = parent or pinned(d["base"])
    if existing:
        artifact = repository + "@" + existing["digest"]
        run("docker", "pull", artifact)
        labels = json.loads(subprocess.check_output(["docker", "inspect", artifact, "--format", "{{json .Config.Labels}}"], text=True))
        if labels.get("org.opencontainers.image.revision") != source or labels.get("org.opencontainers.image.version") != d["revision"]:
            raise RuntimeError("Candidate metadata does not match this release")
        verify(line, artifact, inventory_path)
    else:
        build(line, candidate, source, parent, cache=line.replace("/", "-"))
        verify(line, candidate, inventory_path)
        run("docker", "push", candidate)
    published = resolve(candidate, authenticated=True)
    if not published:
        raise RuntimeError("Pushed candidate not found")
    digest = published["digest"]
    artifact = repository + "@" + digest
    # This lookup must work without any credential. New GHCR packages are private by default.
    try:
        public = resolve(artifact)
    except Exception as error:
        raise RuntimeError(f"Make GHCR package {d['family']} public, then rerun this workflow to reuse the candidate") from error
    if not public or public["digest"] != digest:
        raise RuntimeError("Anonymous registry resolution failed")
    with tempfile.TemporaryDirectory() as config:
        env = dict(os.environ, DOCKER_CONFIG=config)
        run("docker", "pull", "--platform", "linux/amd64", artifact, env=env)
        verify(line, artifact, inventory_path)
    evidence = f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}"
    date = now()
    record = {"schema_version": 1, "line_id": line, "version": d["revision"], "source_commit": source, "source_tag": source_tag,
              "created_at": date, "definition": d, "tools": read(ROOT / "images/tools.json"), "resolved_base": resolved_base,
              "input_fingerprint": fp, "lifecycle": "available",
              "platforms": [{"platform": "linux/amd64", "digest": published["platforms"].get("linux/amd64", digest), "inventory": read(inventory_path)}],
              "publication": {"repository": repository, "digest": digest, "exact_tag": f"{d['line']}-v{d['revision']}", "public_pull_verified_at": date, "evidence": evidence},
              "verification": {"status": "passed", "surface": "github-actions-linux-amd64", "completed_at": date, "evidence": evidence}}
    validate_record(record)
    (destination / "record.json").write_text(encoded(record))
    # Persist before exact promotion. A retry recovers this artifact, never rebuilds it.
    existing_release = json.loads(gh("api", "--paginate", "--slurp", f"repos/{os.environ['GITHUB_REPOSITORY']}/releases"))
    if not any(r["tag_name"] == source_tag for page in existing_release for r in page):
        run("gh", "release", "create", source_tag, "--target", source, "--draft", "--title", source_tag,
            "--notes", "Verified artifact recorded. Exact promotion and catalog writeback are in progress.")
    tagged = subprocess.check_output(["git", "ls-remote", "--tags", "origin", f"refs/tags/{source_tag}"], text=True).split()
    if tagged and tagged[0] != source:
        raise RuntimeError("Source tag already names a different commit")
    run("gh", "release", "upload", source_tag, str(destination / "record.json"), str(inventory_path))
    promote_exact(record)
    finalize_release(record)
    return record


def promote_exact(record):
    p = record["publication"]
    target = p["repository"] + ":" + p["exact_tag"]
    current = resolve(target, authenticated=True)
    exact_guard(current["digest"] if current else None, p["digest"])
    if not current:
        run("docker", "buildx", "imagetools", "create", "--prefer-index=false", "--tag", target, p["repository"] + "@" + p["digest"])
    verified = resolve(target)
    if not verified or verified["digest"] != p["digest"]:
        raise RuntimeError("Exact tag does not identify the tested public artifact")


def finalize_release(record):
    d = record["definition"]
    notes = "\n".join("- " + x for x in d["changes"])
    notes += f"\n\nMigration: {d['migration']}\n\nDigest: `{record['publication']['repository']}@{record['publication']['digest']}`"
    notes += f"\n\n[Verification]({record['verification']['evidence']}). Catalog update is staged through a protected-branch PR; the compatibility alias moves only after that PR lands."
    run("gh", "release", "edit", record["source_tag"], "--draft=false", "--notes", notes)


def aliases():
    # Workflow concurrency is repository-wide. Fetch the latest accepted ledger at execution time.
    run("git", "fetch", "origin", "master")
    run("git", "checkout", "--detach", "origin/master")
    accepted = records()
    groups = {}
    for r in accepted:
        p = r["publication"]
        alias = f"{p['repository']}:{r['definition']['line']}-v{version(r['version'])[0]}"
        groups.setdefault(alias, []).append(r)
    # Check every major before changing any aliases. A withdrawal must not leave
    # a stale recommendation silently successful, or delete a shared exact digest.
    blocked = [alias for alias, peers in groups.items()
               if not any(r["lifecycle"] == "available" for r in peers)
               and resolve(alias, authenticated=True) is not None]
    if blocked:
        raise RuntimeError("No available replacement for existing aliases: " + ", ".join(blocked)
                           + ". Restore a verified available release or retire these alias tags while preserving exact artifacts, then rerun.")
    for r in accepted:
        if not alias_eligible(r, accepted):
            continue
        p = r["publication"]
        if resolve(p["repository"] + ":" + p["exact_tag"])["digest"] != p["digest"]:
            raise RuntimeError("Accepted exact tag changed or is unavailable")
        alias = f"{p['repository']}:{r['definition']['line']}-v{version(r['version'])[0]}"
        run("docker", "buildx", "imagetools", "create", "--prefer-index=false", "--tag", alias, p["repository"] + "@" + p["digest"])
        if resolve(alias)["digest"] != p["digest"]:
            raise RuntimeError("Alias promotion verification failed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("line", nargs="?"); parser.add_argument("--source", default=os.environ.get("GITHUB_SHA"))
    parser.add_argument("--aliases", action="store_true")
    args = parser.parse_args()
    if args.aliases:
        aliases()
    else:
        d = definitions()[args.line]
        output = ROOT / "out" / args.line.replace("/", "-")
        record = publish(args.line, args.source, output)
        output.mkdir(parents=True, exist_ok=True)
        (output / "record.json").write_text(encoded(record))
        if d["family"] == "php-dev":
            browser = "php-browser/" + d["line"]
            parent = record["publication"]["repository"] + "@" + record["publication"]["digest"]
            browser_output = ROOT / "out" / browser.replace("/", "-")
            browser_record = publish(browser, args.source, browser_output, parent)
            browser_output.mkdir(parents=True, exist_ok=True)
            (browser_output / "record.json").write_text(encoded(browser_record))
