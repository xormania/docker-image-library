#!/usr/bin/env python3
"""Resolve moving upstream inputs into reviewable pins and fresh revisions."""
import json
import urllib.request
from library import ROOT, encoded, read, version
from registry import resolve


tools_path = ROOT / "images/tools.json"
tools = read(tools_path)
for name in ("composer", "uv"):
    tools[name]["digest"] = resolve(tools[name]["tag"])["digest"]
for name in ("redis", "xdebug"):
    with urllib.request.urlopen(f"https://pecl.php.net/rest/r/{name}/stable.txt", timeout=60) as response:
        tools[name + "_version"] = response.read().decode().strip()
with urllib.request.urlopen("https://api.github.com/repos/symfony-cli/symfony-cli/releases/latest", timeout=60) as response:
    release = json.load(response)
asset = next(a for a in release["assets"] if a["name"] == "symfony-cli_linux_amd64.tar.gz")
assert asset.get("digest", "").startswith("sha256:"), "No upstream artifact checksum"
tools["symfony"] = {"version": release["tag_name"].removeprefix("v"), "url": asset["browser_download_url"], "sha256": asset["digest"].removeprefix("sha256:")}
tools_path.write_text(encoded(tools))
for path in (ROOT / "images").glob("*/definition.json"):
    d = read(path)
    for name, line in d["lines"].items():
        if "tag" in line["base"]:
            line["base"]["digest"] = resolve(line["base"]["tag"])["digest"]
        major, minor, patch = version(line["revision"])
        line["revision"] = f"{major}.{minor}.{patch + 1}"
        line["changes"] = ["Refresh locked upstream inputs and Debian packages; preserve the advertised development contract."]
        line["migration"] = "Compatible refresh. Update the digest deliberately after project validation; retain the previous exact release for rollback."
    path.write_text(encoded(d))
print("Resolved upstream pins and fresh patch revisions. Apt package versions are measured from the resulting artifact, not assumed from unchanged Dockerfile text.")
