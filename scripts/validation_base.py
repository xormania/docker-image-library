#!/usr/bin/env python3
"""Reuse successful validation for an ancestral head of the same PR and base."""
import json
import os
import re
import subprocess
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def ancestor(commit, head):
    return subprocess.run(["git", "merge-base", "--is-ancestor", commit, head],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def select(runs, number, head, base, is_ancestor=ancestor):
    for run in runs:
        if run.get("event") != "pull_request" or run.get("conclusion") != "success":
            continue
        commit = run.get("head_sha", "")
        if not re.fullmatch(r"[0-9a-f]{40}", commit):
            continue
        if not any(pr.get("number") == number and pr.get("base", {}).get("sha") == base
                   for pr in run.get("pull_requests", [])):
            continue
        if is_ancestor(commit, head):
            return commit
    return base


def main():
    base = os.environ.get("BASE_SHA", "")
    number = os.environ.get("PR_NUMBER", "")
    token = os.environ.get("GITHUB_TOKEN", "")
    if not (base and number and token):
        print(base)
        return
    repository = os.environ["GITHUB_REPOSITORY"]
    request = Request(f"https://api.github.com/repos/{repository}/actions/workflows/validate.yml/runs?event=pull_request&status=success&per_page=100",
                      headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json"})
    try:
        with urlopen(request, timeout=20) as response:
            runs = json.load(response)["workflow_runs"]
        print(select(runs, int(number), os.environ["HEAD_SHA"], base))
    except (HTTPError, URLError, TimeoutError, ValueError, KeyError) as error:
        print(f"Previous validation unavailable ({type(error).__name__}); checking the full PR", file=sys.stderr)
        print(base)


if __name__ == "__main__":
    main()
