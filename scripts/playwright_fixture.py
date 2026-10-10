#!/usr/bin/env python3
"""Resolve immutable application inputs for browser screenshot parity."""
import argparse
import json
import re
from pathlib import Path

from library import version


def application_image(catalog, identity=None):
    """Select once when authoring; validate the exact pin when running parity."""
    entries = [item for item in catalog["resources"]
               if item["id"] == "image/flowbite-xor-dev/8.5-trixie"
               and item["lifecycle"] == "available"
               and item["verification"]["status"] == "passed"
               and "linux/amd64" in item["targets"]]
    if identity is None:
        if not entries:
            raise ValueError("No accepted application image for browser parity")
        identity = max(entries, key=lambda item: version(item["version"]))["identity"]
    if not re.fullmatch(r"ghcr\.io/xormania/flowbite-xor-dev@sha256:[a-f0-9]{64}", identity):
        raise ValueError("Browser parity requires an exact application image digest")
    if not any(item["identity"] == identity for item in entries):
        raise ValueError("Pinned application image is not accepted for browser parity")
    return identity


def inputs(fixture, catalog):
    pin = fixture.get("application_image")
    if not isinstance(pin, str):
        raise ValueError("Browser parity requires an exact application image digest")
    image = application_image(catalog, pin)
    if not re.fullmatch(r"[a-f0-9]{40}", fixture["commit"]):
        raise ValueError("Browser parity requires an immutable consumer commit")
    version(fixture["playwright_version"])
    return (fixture["repository"], fixture["commit"], fixture["playwright_version"], image)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path)
    parser.add_argument("catalog", type=Path)
    args = parser.parse_args()
    print("\n".join(inputs(json.loads(args.fixture.read_text()), json.loads(args.catalog.read_text()))))
