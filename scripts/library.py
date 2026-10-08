#!/usr/bin/env python3
"""Definitions, verified records, deterministic discovery, and affected builds."""
import argparse
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIGEST = re.compile(r"^sha256:[a-f0-9]{64}$")
SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")


def read(path):
    return json.loads(Path(path).read_text())


def validate_schemas(root=ROOT):
    import jsonschema
    for path in (root / "images").glob("*/definition.json"):
        jsonschema.validate(read(path), read(root / "schemas/definition.schema.json"))
    for path in (root / "release-records").rglob("*.json"):
        jsonschema.validate(read(path), read(root / "schemas/release-record.schema.json"))
    jsonschema.validate(read(root / "catalog.json"), read(root / "schemas/catalog.schema.json"))


def encoded(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def version(value):
    if not SEMVER.fullmatch(value):
        raise ValueError(f"Invalid image revision: {value}")
    return tuple(map(int, value.split(".")))


def definitions(root=ROOT):
    result = {}
    for path in sorted((root / "images").glob("*/definition.json")):
        definition = read(path)
        assert definition["schema_version"] == 1
        family = definition["family"]
        assert family == path.parent.name
        for line, inputs in definition["lines"].items():
            version(inputs["revision"])
            assert inputs["platforms"] == ["linux/amd64"], "Add platform build/test support before advertising it"
            base = inputs["base"]
            assert "parent" in base or DIGEST.fullmatch(base["digest"])
            item = copy.deepcopy(definition)
            del item["lines"]
            item.update(inputs)
            item["line_id"] = f"{family}/{line}"
            item["line"] = line
            result[item["line_id"]] = item
    for item in result.values():
        parent = item["base"].get("parent")
        if parent:
            assert parent in result
            for key in ("capabilities", "extensions", "tools", "limitations"):
                item[key] = sorted(set(item[key] + result[parent][key]))
    return result


def validate_inventory(definition, inventory):
    assert inventory["platform"] in definition["platforms"]
    assert inventory["os"]["VERSION_CODENAME"] == "trixie"
    assert set(definition["extensions"]) <= set(inventory["extensions"])
    assert set(definition["tools"]) <= set(inventory["tools"])
    assert inventory["runtime_version"].startswith(definition["runtime_line"] + ".")
    if definition["family"] == "php-browser":
        browser = re.search(r"\d+", inventory["tools"]["chromium"])[0]
        driver = re.search(r"\d+", inventory["tools"]["chromedriver"])[0]
        assert browser == driver, "Chromium and driver major versions differ"
    if "wasm32-unknown-unknown" in definition["capabilities"]:
        assert "wasm32-unknown-unknown" in inventory["rust_targets"]


def validate_record(record):
    assert record["schema_version"] == 1
    version(record["version"])
    assert re.fullmatch(r"[a-f0-9]{40}", record["source_commit"])
    assert record["lifecycle"] in ("available", "deprecated", "withdrawn")
    if record["lifecycle"] != "available":
        assert record.get("reason") and record.get("replacement") and record.get("lifecycle_date")
    pub = record["publication"]
    assert DIGEST.fullmatch(pub["digest"])
    assert pub["public_pull_verified_at"] and pub["evidence"]
    assert record["verification"]["status"] == "passed"
    assert record["verification"]["surface"] == "github-actions-linux-amd64"
    assert record["definition"]["line_id"] == record["line_id"]
    assert record["definition"]["revision"] == record["version"]
    expected = f"{record['definition']['line']}-v{record['version']}"
    assert pub["exact_tag"] == expected
    assert record["source_tag"] == f"{record['line_id']}/v{record['version']}"
    assert record["platforms"], "No tested platforms"
    assert [p["platform"] for p in record["platforms"]] == record["definition"]["platforms"]
    for platform in record["platforms"]:
        assert DIGEST.fullmatch(platform["digest"])
        inventory = platform["inventory"]
        assert inventory["platform"] == platform["platform"]
        validate_inventory(record["definition"], inventory)
    return record


def records(root=ROOT):
    result = []
    for path in sorted((root / "release-records").rglob("*.json")):
        result.append(validate_record(read(path)))
    identities = [(r["line_id"], r["version"]) for r in result]
    assert len(identities) == len(set(identities)), "Duplicate release identity"
    return result


def catalog(releases):
    entries = []
    for r in sorted(releases, key=lambda r: (r["line_id"], version(r["version"]))):
        pub = r["publication"]
        item = copy.deepcopy(r)
        item["digest_reference"] = f"{pub['repository']}@{pub['digest']}"
        item["exact_reference"] = f"{pub['repository']}:{pub['exact_tag']}"
        item["documentation"] = f"docs/images/{r['line_id'].replace('/', '-')}.md"
        entries.append(item)
    return {"schema_version": 1, "generated_at": max((r["created_at"] for r in releases), default=None), "images": entries}


def select(cat, requirements):
    def compatible(item):
        d = item["definition"]
        platforms = [p["platform"] for p in item["platforms"]]
        return (item["lifecycle"] == "available"
                and d["runtime_line"] == requirements["runtime_line"]
                and (not requirements.get("family") or d["family"] == requirements["family"])
                and requirements.get("platform", "linux/amd64") in platforms
                and set(requirements.get("capabilities", [])) <= set(d["capabilities"])
                and set(requirements.get("extensions", [])) <= set(d["extensions"]))
    matches = [i for i in cat["images"] if compatible(i)]
    if requirements.get("pinned_digest"):
        pinned = [i for i in matches if i["digest_reference"] == requirements["pinned_digest"]]
        if pinned:
            return {"status": "selected", "preserved_pin": True, "image": pinned[0]}
        return {"status": "pin_unverified_or_incompatible", "reason": "The existing pin is absent, withdrawn, or does not meet these requirements. Do not replace it silently."}
    if not matches:
        return {"status": "no_matching_image", "requirements": requirements, "reason": "No verified available release satisfies every runtime, platform, capability, and extension requirement."}
    # Choose the smallest suitable capability profile, then latest revision in that line.
    minimum = min(len(i["definition"]["capabilities"]) for i in matches)
    matches = [i for i in matches if len(i["definition"]["capabilities"]) == minimum]
    chosen = sorted(matches, key=lambda i: (version(i["version"]), i["line_id"]), reverse=True)[0]
    return {"status": "selected", "preserved_pin": False, "image": chosen}


def generated(root=ROOT):
    defs = definitions(root)
    releases = records(root)
    cat = catalog(releases)
    latest = {}
    for item in cat["images"]:
        if item["lifecycle"] == "available":
            latest[item["line_id"]] = item
    rows = ["| Line | Revision | Verified platform | Exact reference |", "| --- | --- | --- | --- |"]
    for line, item in sorted(latest.items()):
        rows.append(f"| [{line}]({item['documentation']}) | {item['version']} | {', '.join(p['platform'] for p in item['platforms'])} | `{item['exact_reference']}` |")
    table = "\n".join(rows) if latest else "No verified public releases yet. Definitions are build inputs, not available images."
    readme = (root / "README.md").read_text()
    readme = re.sub(r"(?s)(<!-- catalog:start -->\n).*?(\n<!-- catalog:end -->)", lambda m: m[1] + table + m[2], readme)
    outputs = {root / "catalog.json": encoded(cat), root / "README.md": readme}
    for line, d in defs.items():
        item = latest.get(line)
        if item:
            d = item["definition"]
        text = f"# {line}\n\n{d['purpose']}\n\n"
        if item:
            text += f"Available revision: **{item['version']}**. Pin:\n\n```text\n{item['digest_reference']}\n```\n\n"
            text += f"[Verification evidence]({item['verification']['evidence']}); {item['verification']['completed_at']}.\n\n"
            for platform in item["platforms"]:
                inv = platform["inventory"]
                text += f"## Measured inventory — {platform['platform']}\n\nRuntime: {inv['runtime_version']}; OS: {inv['os']['PRETTY_NAME']}.\n\n"
                text += "| Tool | Version |\n| --- | --- |\n" + "\n".join(f"| {k} | {v.replace('|', '/')} |" for k, v in sorted(inv["tools"].items())) + "\n\n"
                if inv["extensions"]:
                    text += "Extensions: " + ", ".join(f"`{e}`" for e in sorted(inv["extensions"])) + ".\n\n"
            text += f"[Release notes](../releases/{line.replace('/', '-')}-v{item['version']}.md).\n\n"
        else:
            text += "**Not available:** no verified public release. The following capabilities describe the intended profile.\n\n"
        text += "Capabilities: " + ", ".join(f"`{c}`" for c in d["capabilities"]) + ".\n\n"
        text += "Workspace `/workspace`, HOME `/home/dev`, default UID/GID 1000; configure `PUID` and `PGID`.\n\n"
        text += "[Usage](../usage.md) · [Selection](../selection.md) · [Compatibility evidence](../compatibility.md)\n\n"
        text += "## Limitations\n\n" + "\n".join(f"- {x}" for x in d["limitations"]) + "\n"
        outputs[root / "docs" / "images" / (line.replace("/", "-") + ".md")] = text
    for item in cat["images"]:
        d = item["definition"]
        text = f"# {item['line_id']} v{item['version']}\n\n" + "\n".join(f"- {c}" for c in d["changes"]) + "\n\n"
        text += f"Migration: {d['migration']}\n\nSource: `{item['source_commit']}` (`{item['source_tag']}`).\n\nArtifact: `{item['digest_reference']}`.\n\n"
        text += f"Base/parent: `{item['resolved_base']}`.\n\n[Verification]({item['verification']['evidence']}).\n\n"
        text += "The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.\n"
        outputs[root / "docs" / "releases" / f"{item['line_id'].replace('/', '-')}-v{item['version']}.md"] = text
    return outputs


def affected(changed, defs):
    result = set()
    metadata_scripts = {"scripts/release.py", "scripts/writeback.py", "scripts/refresh.py", "scripts/registry.py"}
    for path in changed:
        families = set()
        if path == "images/tools.json":
            families = {"php-dev", "php-browser", "python-dev"}
        elif path.startswith(("tests/fixtures/php/", "examples/php/")):
            families = {"php-dev", "php-browser", "python-dev"} if path.startswith("examples/php/") else {"php-dev", "php-browser"}
        elif path.startswith("tests/fixtures/python/"):
            families = {"python-dev"}
        elif path.startswith("tests/fixtures/rust/"):
            families = {"rust-dev"}
        elif path.startswith("tests/test_") or path in metadata_scripts:
            continue
        elif path.startswith(".github/workflows/") and path != ".github/workflows/validate.yml":
            continue
        elif path.startswith(("images/shared/", "scripts/", "schemas/", "tests/", "examples/")) or path == ".github/workflows/validate.yml":
            result.update(defs)
            continue
        else:
            families = {d["family"] for d in defs.values() if path.startswith(f"images/{d['family']}/")}
        result.update(line for line, d in defs.items() if d["family"] in families)
    for line, d in defs.items():
        if d["base"].get("parent") in result:
            result.add(line)
    # The PHP root job builds/tests its matching derived browser line too.
    result |= {defs[line]["base"]["parent"] for line in list(result) if defs[line]["family"] == "php-browser"}
    return sorted(line for line in result if defs[line]["family"] != "php-browser")


def fingerprint(d, root=ROOT):
    paths = list((root / "images" / d["family"]).glob("*")) + list((root / "images" / "shared").glob("*"))
    h = hashlib.sha256(encoded(d).encode())
    tools = read(root / "images" / "tools.json")
    keys = {"php-dev": ("composer", "redis_version", "xdebug_version", "symfony"),
            "python-dev": ("uv",)}.get(d["family"], ())
    h.update(encoded({key: tools[key] for key in keys}).encode())
    for path in sorted(paths):
        if path.is_file() and path.name != "definition.json":
            h.update(str(path.relative_to(root)).encode())
            h.update(path.read_bytes())
    return h.hexdigest()


def cache_key(line, defs):
    # One CI job owns the PHP parent and browser caches. Neither source commit
    # nor unrelated tool pins belong in their immutable Actions cache key.
    peers = [line]
    if defs[line]["family"] == "php-dev":
        peers.append("php-browser/" + defs[line]["line"])
    return hashlib.sha256("".join(fingerprint(defs[peer]) for peer in peers).encode()).hexdigest()


def pending_releases(defs, accepted):
    """Skip accepted inputs, but retain missing browser peers and guard failures."""
    current = {(r["line_id"], r["version"]): r for r in accepted}
    pending = set()
    for line, d in defs.items():
        fp = fingerprint(d)
        parent_line = d["base"].get("parent")
        if parent_line:
            parent = current.get((parent_line, defs[parent_line]["revision"]))
            if not parent:
                pending.add(parent_line)
                continue
            parent_ref = parent["publication"]["repository"] + "@" + parent["publication"]["digest"]
            fp = hashlib.sha256((fp + parent_ref).encode()).hexdigest()
        prior = current.get((line, d["revision"]))
        if not prior or prior["input_fingerprint"] != fp:
            pending.add(parent_line or line)
    return sorted(pending)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("generate")
    sub.add_parser("check")
    s = sub.add_parser("select"); s.add_argument("requirements"); s.add_argument("--catalog", default=str(ROOT / "catalog.json"))
    a = sub.add_parser("affected"); a.add_argument("--base"); a.add_argument("--all", action="store_true")
    sub.add_parser("cache-key").add_argument("line")
    sub.add_parser("release-matrix")
    sub.add_parser("definitions")
    args = parser.parse_args()
    if args.command in ("generate", "check"):
        if args.command == "check":
            validate_schemas()
        errors = []
        for path, content in generated().items():
            if args.command == "generate":
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            elif not path.exists() or path.read_text() != content:
                errors.append(str(path.relative_to(ROOT)))
        if errors:
            raise SystemExit("Stale generated files: " + ", ".join(errors))
    elif args.command == "definitions":
        print(encoded(definitions()), end="")
    elif args.command == "select":
        result = select(read(args.catalog), read(args.requirements))
        print(encoded(result), end="")
        if result["status"] != "selected":
            raise SystemExit(2)
    elif args.command == "affected":
        changed = subprocess.check_output(["git", "diff", "--name-only", args.base, "HEAD"], cwd=ROOT, text=True).splitlines() if args.base and not args.all else ["images/shared/"]
        print(json.dumps({"line": affected(changed, definitions())}))
    elif args.command == "cache-key":
        print(cache_key(args.line, definitions()))
    elif args.command == "release-matrix":
        print(json.dumps({"line": pending_releases(definitions(), records())}))


if __name__ == "__main__":
    main()
