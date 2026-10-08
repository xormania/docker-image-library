#!/usr/bin/env python3
"""Build a profile from locked inputs; browser requires an explicit parent."""
import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
from library import ROOT, definitions, read, validate_inventory


def pinned(base):
    return base["tag"] + "@" + base["digest"]


def build(line, image, source, parent=None, cache=None):
    d = definitions()[line]
    tools = read(ROOT / "images/tools.json")
    args = {"BASE_IMAGE": parent or pinned(d["base"]), "SOURCE_COMMIT": source, "IMAGE_VERSION": d["revision"]}
    if d["family"] == "php-dev":
        args.update(COMPOSER_IMAGE=pinned(tools["composer"]), REDIS_VERSION=tools["redis_version"],
                    XDEBUG_VERSION=tools["xdebug_version"], SYMFONY_URL=tools["symfony"]["url"], SYMFONY_SHA256=tools["symfony"]["sha256"])
    if d["family"] == "python-dev":
        args["UV_IMAGE"] = pinned(tools["uv"])
    local_parent = parent and parent.startswith("image-library-")
    cmd = ["docker", "buildx", "build", "--load", "--platform", "linux/amd64", "-t", image,
           "-f", f"images/{d['family']}/Dockerfile"]
    if local_parent:
        cmd += ["--builder", "default"]
    cache_path = None
    if cache and not local_parent and os.environ.get("LIBRARY_CACHE_DIR"):
        cache_path = Path(os.environ["LIBRARY_CACHE_DIR"]) / cache
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        if cache_path.exists():
            cmd += ["--cache-from", f"type=local,src={cache_path}"]
        cmd += ["--cache-to", f"type=local,dest={cache_path}-next,mode=max"]
    for name, value in args.items():
        cmd += ["--build-arg", f"{name}={value}"]
    subprocess.run(cmd + ["."], cwd=ROOT, check=True)
    if cache_path:
        shutil.rmtree(cache_path, ignore_errors=True)
        Path(str(cache_path) + "-next").rename(cache_path)


def inspect(line, image, destination):
    cmd = ["docker", "run", "--rm", "--mount", f"type=bind,src={ROOT / 'scripts'},dst=/inventory,readonly", image,
           "python3", "/inventory/inventory.py", line.split("/")[0]]
    result = subprocess.check_output(cmd, text=True)
    Path(destination).parent.mkdir(parents=True, exist_ok=True)
    try:
        validate_inventory(definitions()[line], json.loads(result))
    except (ValueError, AssertionError):
        Path(str(destination) + ".stdout").write_text(result)
        raise
    Path(destination).write_text(result)


def verify(line, image, destination):
    subprocess.run(["bash", str(ROOT / "scripts/verify-image.sh"), line, image], check=True)
    inspect(line, image, destination)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("line"); p.add_argument("image")
    p.add_argument("--source", default="local"); p.add_argument("--parent"); p.add_argument("--cache")
    p.add_argument("--inventory", default="out/inventory.json")
    a = p.parse_args()
    build(a.line, a.image, a.source, a.parent, a.cache)
    verify(a.line, a.image, a.inventory)
