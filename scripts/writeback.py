#!/usr/bin/env python3
"""Stage generated changes through a PR; never push to protected master."""
import argparse
import json
import os
import subprocess
from pathlib import Path
from library import ROOT, encoded, generated, read, validate_record
from registry import resolve


def run(*args, **kwargs):
    return subprocess.run(args, cwd=ROOT, check=True, **kwargs)


def output(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--refresh", action="store_true")
args = parser.parse_args()
release_inputs = [validate_record(read(p)) for p in (ROOT / "out/releases").rglob("record.json")]
if not args.refresh and not release_inputs:
    print("No completed records to stage. Inspect the publication jobs for the incomplete step.")
    raise SystemExit(0)
run("git", "config", "user.name", "image-library automation")
run("git", "config", "user.email", "image-library@users.noreply.github.com")
branch = "automation/" + ("refresh" if args.refresh else "catalog") + "-" + os.environ["GITHUB_RUN_ID"]
if not args.refresh:
    run("git", "fetch", "origin", "master")
    exists = output("git", "ls-remote", "--heads", "origin", branch).strip()
    if exists:
        run("git", "fetch", "origin", branch)
        run("git", "checkout", "-B", branch, "FETCH_HEAD")
        run("git", "merge", "origin/master", "--no-edit")
    else:
        run("git", "checkout", "-b", branch, "origin/master")
    for record in release_inputs:
        p = record["publication"]
        remote = resolve(p["repository"] + ":" + p["exact_tag"])
        if not remote or remote["digest"] != p["digest"]:
            print(f"Skipping incomplete exact promotion for {record['line_id']}")
            continue
        release = json.loads(output("gh", "release", "view", record["source_tag"], "--json", "isDraft,targetCommitish"))
        if release["isDraft"] or release["targetCommitish"] != record["source_commit"]:
            print(f"Skipping unfinished source release for {record['line_id']}")
            continue
        path = ROOT / "release-records" / record["line_id"] / (record["version"] + ".json")
        if path.exists() and read(path) != record:
            raise RuntimeError("Existing release identity differs from the publication record")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(encoded(record))
    for path, content in generated().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
else:
    run("git", "checkout", "-b", branch)
run("git", "add", "images", "release-records", "catalog.json", "README.md", "docs")
if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode == 0:
    print("Already current; no writeback needed.")
    raise SystemExit(0)
title = "Refresh development image inputs" if args.refresh else "Catalog verified public image releases"
run("git", "commit", "-m", title)
run("git", "push", "origin", branch)
body = ("Updates locked inputs and allocates fresh patch revisions, including apt refreshes. Image behavior is validated by PR CI before publication."
        if args.refresh else "Adds only anonymously verified exact references and measured inventories. Regenerates the README, catalog, capability docs and release notes. After this PR is merged, the alias workflow promotes the latest accepted compatible revisions.")
body += "\n\nMaster requires PRs and automatic merge is currently disabled. Merge through the repository's permitted merge method. If this PR was created with GITHUB_TOKEN, its creation does not trigger other Actions workflows; use LIBRARY_BOT_TOKEN or run validation manually."
prs = json.loads(output("gh", "pr", "list", "--head", branch, "--state", "open", "--json", "number"))
body_path = ROOT / "out" / "pr-body.md"
body_path.parent.mkdir(parents=True, exist_ok=True)
body_path.write_text(body)
if prs:
    run("gh", "pr", "edit", str(prs[0]["number"]), "--title", title, "--body-file", str(body_path))
else:
    run("gh", "pr", "create", "--base", "master", "--head", branch, "--title", title, "--body-file", str(body_path))
