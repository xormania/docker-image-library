#!/usr/bin/env python3
"""Stage generated changes through a PR; never push to protected master."""
import argparse
import json
import os
import subprocess
from library import ROOT, encoded, generated, read, validate_record
from registry import resolve
from refresh import refresh as refresh_inputs


def run(*args, **kwargs):
    return subprocess.run(args, cwd=ROOT, check=True, **kwargs)


def output(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True)


def prepare_branch(branch):
    run("git", "fetch", "origin", "master")
    exists = output("git", "ls-remote", "--heads", "origin", branch).strip()
    if exists:
        run("git", "fetch", "origin", branch)
        run("git", "checkout", "-B", branch, "FETCH_HEAD")
        run("git", "merge", "origin/master", "--no-edit")
    else:
        run("git", "checkout", "-b", branch, "origin/master")


def main(refresh=False):
    release_inputs = [validate_record(read(p)) for p in (ROOT / "out/releases").rglob("record.json")]
    if not refresh and not release_inputs:
        print("No completed records to stage. Inspect the publication jobs for the incomplete step.")
        return
    run("git", "config", "user.name", "image-library automation")
    run("git", "config", "user.email", "image-library@users.noreply.github.com")
    branch = "automation/" + ("refresh" if refresh else "catalog") + "-" + os.environ["GITHUB_RUN_ID"]
    prepare_branch(branch)
    if refresh:
        # Resolve after checkout. Allocate from master so a rerun of the same
        # pending refresh does not increment the proposal's revision again.
        refresh_inputs(base_ref="origin/master")
    else:
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
    for path, content in generated(ROOT).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    run("git", "add", "images", "release-records", "catalog.json", "README.md", "docs")
    changed = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode != 0
    if not changed and output("git", "rev-list", "--count", "origin/master..HEAD").strip() == "0":
        print("Already current; no writeback needed.")
        return
    title = "Refresh development image inputs" if refresh else "Catalog verified public image releases"
    if changed:
        run("git", "commit", "-m", title)
    # An unchanged recovered branch may still need its missing PR created.
    run("git", "push", "origin", branch)
    body = ("Updates locked inputs and allocates fresh patch revisions, including apt refreshes. Image behavior is validated by PR CI before publication."
            if refresh else "Adds only anonymously verified exact references and measured inventories. Regenerates the README, catalog, capability docs and release notes. After this PR is merged, the alias workflow promotes the latest accepted compatible revisions.")
    body += "\n\nMaster requires PRs and automatic merge is currently disabled. Merge through the repository's permitted merge method. If this PR was created with GITHUB_TOKEN, its creation does not trigger other Actions workflows; use LIBRARY_BOT_TOKEN or run validation manually."
    prs = json.loads(output("gh", "pr", "list", "--head", branch, "--state", "open", "--json", "number"))
    body_path = ROOT / "out" / "pr-body.md"
    body_path.parent.mkdir(parents=True, exist_ok=True)
    body_path.write_text(body)
    if prs:
        run("gh", "pr", "edit", str(prs[0]["number"]), "--title", title, "--body-file", str(body_path))
    else:
        run("gh", "pr", "create", "--base", "master", "--head", branch, "--title", title, "--body-file", str(body_path))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    main(refresh=parser.parse_args().refresh)
