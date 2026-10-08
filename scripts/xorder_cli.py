#!/usr/bin/env python3
"""Optional xorder discovery helper; Python 3 and requirements-ci.txt are required."""
import argparse
import hashlib
from pathlib import Path

from xorder import model
from xorder.resolve import resolve


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=model.ROOT, help="repository root")
    sub = parser.add_subparsers(dest="command", required=True)
    listing = sub.add_parser("list")
    listing.add_argument("--kind", choices=("image",) + model.KINDS)
    listing.add_argument("--all", action="store_true", help="include withdrawn/deprecated releases")
    sub.add_parser("show").add_argument("id")
    resolution = sub.add_parser("resolve")
    resolution.add_argument("profile", help="local profile JSON path")
    resolution.add_argument("--target", required=True, help="JSON with observed target facts")
    resolution.add_argument("--pins", help="previous lock JSON; pins are preserved")
    resolution.add_argument("--overlay", help="explicit private local overlay JSON")
    sub.add_parser("generate")
    sub.add_parser("check")
    args = parser.parse_args()
    if args.command == "generate":
        from library import generated
        for path, content in generated(args.root).items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        return
    if args.command == "check":
        model.check(args.root)
        return
    cat = model.catalog(args.root)
    if args.command == "list":
        result = {"schema_version": 2, "resources": [item for item in cat["resources"]
                  if (not args.kind or item["kind"] == args.kind)
                  and (args.all or item["lifecycle"] == "available")]}
    elif args.command == "show":
        result = {"id": args.id, "resources": [item for item in cat["resources"] if item["id"] == args.id]}
        if not result["resources"]:
            print(model.encoded({"status": "resource_unavailable", "id": args.id}), end="")
            raise SystemExit(2)
    else:
        profile = Path(args.profile)
        overlay = Path(args.overlay) if args.overlay else None
        result = resolve(model.read(profile), cat, model.read(args.target),
                         pins=model.read(args.pins) if args.pins else None,
                         overlay=model.read(overlay) if overlay else None,
                         profile_sha256=hashlib.sha256(profile.read_bytes()).hexdigest(),
                         overlay_sha256=hashlib.sha256(overlay.read_bytes()).hexdigest() if overlay else None,
                         root=args.root)
    print(model.encoded(result), end="")
    if result.get("status") == "resolution_failed":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
