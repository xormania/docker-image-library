#!/usr/bin/env python3
"""Build a profile from locked inputs; browser requires an explicit parent."""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from library import ROOT, children, definitions, read, validate_inventory


def pinned(base):
    return base["tag"] + "@" + base["digest"]


def build(line, image, source, parent=None, cache=None):
    d = definitions()[line]
    tools = read(ROOT / "images/tools.json")
    args = {"BASE_IMAGE": parent or pinned(d["base"]), "SOURCE_COMMIT": source,
            "IMAGE_VERSION": d["revision"], "APT_REFRESH": d["revision"]}
    if d["family"] in ("php-dev", "php-frankenphp"):
        args.update(COMPOSER_IMAGE=pinned(tools["composer"]), REDIS_VERSION=tools["redis_version"],
                    XDEBUG_VERSION=tools["xdebug_version"], SYMFONY_URL=tools["symfony"]["url"], SYMFONY_SHA256=tools["symfony"]["sha256"])
    if d["family"] == "php-frankenphp":
        args["APCU_VERSION"] = tools["apcu_version"]
    if d["family"] == "flowbite-xor-dev":
        args["NODE_IMAGE"] = pinned(tools["node"])
    if d["family"] == "python-dev":
        args["UV_IMAGE"] = pinned(tools["uv"])
    local_parent = parent and parent.startswith("image-library-")
    cmd = ["docker", "buildx", "build", "--load", "--platform", "linux/amd64", "-t", image,
           "-f", f"images/{d['family']}/Dockerfile"]
    if local_parent:
        # The daemon's implicit builder shares its local image store. A custom
        # Docker context (as in CI) need not be named "default".
        context = subprocess.check_output(["docker", "context", "show"], text=True).strip()
        cmd += ["--builder", context]
    cache_path = None
    if cache and os.environ.get("LIBRARY_CACHE_DIR"):
        cache_path = Path(os.environ["LIBRARY_CACHE_DIR"]) / cache
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        if cache_path.exists():
            cmd += ["--cache-from", f"type=local,src={cache_path}"]
        shutil.rmtree(str(cache_path) + "-next", ignore_errors=True)
        cmd += ["--cache-to", f"type=local,dest={cache_path}-next,mode=max"]
    for name, value in args.items():
        cmd += ["--build-arg", f"{name}={value}"]
    subprocess.run(cmd + ["."], cwd=ROOT, check=True)
    if cache_path:
        shutil.rmtree(cache_path, ignore_errors=True)
        Path(str(cache_path) + "-next").rename(cache_path)


def image_facts(image):
    return json.loads(subprocess.check_output(["docker", "image", "inspect", image], text=True))[0]


def image_measurements(image):
    info = json.loads(subprocess.check_output(["docker", "info", "--format", "{{json .}}"], text=True))
    driver_type = dict(info.get("DriverStatus") or []).get("driver-type", "classic")
    return {"image_size_bytes": image_facts(image)["Size"],
            "size_method": "docker-image-inspect-size", "image_store": info["Driver"] + "/" + driver_type}


def cache_source(cache):
    """Describe the external cache input, without claiming a layer cache hit."""
    directory = os.environ.get("LIBRARY_CACHE_DIR")
    if not cache or not directory:
        return "disabled"
    return "restored" if (Path(directory) / cache / "index.json").is_file() else "empty"


def cache_probe(line, image, source, parent=None):
    """A new source label must reuse the tested filesystem layers."""
    before = image_facts(image)
    probe = image + "-cache-probe"
    start = time.monotonic()
    build(line, probe, source + "-cache-probe", parent)
    after = image_facts(probe)
    assert before["RootFS"]["Layers"] == after["RootFS"]["Layers"], "Source labels invalidated filesystem layers"
    assert after["Config"]["Labels"]["org.opencontainers.image.revision"] == source + "-cache-probe"
    subprocess.run(["docker", "image", "rm", probe], check=True)
    return round(time.monotonic() - start, 2)


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
    p.add_argument("--cache-probe", action="store_true")
    p.add_argument("--children", action="store_true", help="Build and verify immediate derived profiles with this exact local parent")
    a = p.parse_args()
    cache = cache_source(a.cache)
    start = time.monotonic()
    build(a.line, a.image, a.source, a.parent, a.cache)
    built = time.monotonic()
    verify(a.line, a.image, a.inventory)
    verified = time.monotonic()
    metrics = {"line": a.line, **image_measurements(a.image), "cache_source": cache,
               "build_seconds": round(built-start, 2), "verify_seconds": round(verified-built, 2)}
    if a.cache_probe:
        metrics["source_label_rebuild_seconds"] = cache_probe(a.line, a.image, a.source, a.parent)
    Path(a.inventory).with_suffix(".metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    print(json.dumps(metrics))
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as summary:
            summary.write(f"\n### {a.line}\n\nImage: {metrics['image_size_bytes']/1024**2:.1f} MiB; "
                          f"build: {metrics['build_seconds']}s; behavior/inventory: {metrics['verify_seconds']}s.\n")
            if a.cache_probe:
                summary.write(f"Source-label-only rebuild: {metrics['source_label_rebuild_seconds']}s; filesystem layers unchanged.\n")
    if a.children:
        for child in children(a.line, definitions()):
            family = definitions()[child]["family"]
            command = [sys.executable, __file__, child, "image-library-check:" + family,
                       "--source", a.source, "--parent", a.image, "--children",
                       "--inventory", str(Path(a.inventory).with_name(family + ".json"))]
            if a.cache:
                command += ["--cache", child.replace("/", "-")]
            if a.cache_probe:
                command += ["--cache-probe"]
            subprocess.run(command, check=True)
