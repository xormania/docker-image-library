"""Compact review context derived from verified records and accepted catalogs."""
import subprocess
from urllib.error import URLError

from catalog_checks import github_json
from library import read, version


def proposed_records(root, base="origin/master"):
    paths = subprocess.check_output(
        ["git", "diff", "--name-only", "--diff-filter=AM", base, "HEAD", "--", "release-records"],
        cwd=root, text=True).splitlines()
    return [read(root / path) for path in paths if path.endswith(".json")]


def source_prs(records, repository):
    result = {}
    for source in sorted({record["source_commit"] for record in records}):
        try:
            pulls = github_json(repository, f"commits/{source}/pulls")
            result[source] = [(pull["number"], pull["html_url"]) for pull in pulls
                              if pull["merged_at"] and pull["base"]["repo"]["full_name"] == repository]
        except (URLError, ValueError) as error:
            # Source/verification links remain sufficient if optional enrichment
            # is unavailable. Never turn a missing PR lookup into a release gate.
            print(f"Source PR lookup unavailable for {source}: {error}")
    return result


def latest(items, identity):
    peers = [item for item in items if item["lifecycle"] == "available"
             and (item.get("line_id") or item.get("id")) == identity]
    return max(peers, key=lambda item: version(item["version"])) if peers else None


def image_size(record):
    metrics = record["platforms"][0].get("metrics")
    if not metrics:
        return "Not measured"
    size = metrics["image_size_bytes"] / 1024**2
    text = f"{size:,.1f} MiB"
    baseline = metrics.get("baseline")
    if baseline:
        delta = (metrics["image_size_bytes"] - baseline["image_size_bytes"]) / 1024**2
        percentage = (metrics["image_size_bytes"] / baseline["image_size_bytes"] - 1) * 100
        text += f"; {delta:+,.1f} MiB ({percentage:+.1f}%, v{baseline['version']})"
    return text


def catalog_body(records, previous_images, previous_resources, repository, associated_prs=None):
    associated_prs = associated_prs or {}
    images = [record for record in records if record["schema_version"] == 1]
    resources = [record for record in records if record["schema_version"] == 2]
    body = f"Accepts **{len(images)} verified image releases** and **{len(resources)} verified downloadable resource releases**, with regenerated catalogs and documentation."
    families = sorted({r["definition"]["family"] for r in images}
                      - {r["definition"]["family"] for r in previous_images})
    if families:
        body += "\n\nNew image families: " + ", ".join(f"`{family}`" for family in families) + "."
    body += "\n\n| Resource | Previously accepted | Proposed revision | Measured size/change | Alias after acceptance |\n| --- | --- | --- | --- | --- |\n"
    for record in sorted(records, key=lambda r: (r.get("line_id") or r["id"], version(r["version"]))):
        image = record["schema_version"] == 1
        identity = record["line_id"] if image else record["id"]
        previous = latest(previous_images if image else previous_resources, identity)
        prior = previous["version"] if previous else "New line" if image else "New resource"
        size = image_size(record) if image else f"{record['publication']['size_bytes']:,} bytes"
        alias = "None"
        if image:
            major = version(record["version"])[0]
            compatible = [r for r in previous_images + images
                          if r["line_id"] == identity and r["lifecycle"] == "available"
                          and version(r["version"])[0] == major]
            target = max(compatible, key=lambda r: version(r["version"]))
            alias = f"`{record['publication']['repository']}:{record['definition']['line']}-v{major}` → {target['version']}"
        release = f"https://github.com/{repository}/releases/tag/{record['source_tag']}"
        body += f"| [{identity}]({release}) | {prior} | {record['version']} | {size} | {alias} |\n"
    body += "\n### Source and verification\n\n"
    for source in sorted({record["source_commit"] for record in records}):
        links = associated_prs.get(source, [])
        pulls = "; " + ", ".join(f"[PR #{number}]({url})" for number, url in links) if links else ""
        body += f"- [Source `{source[:12]}`](https://github.com/{repository}/commit/{source}){pulls}.\n"
    for evidence in sorted({record["verification"]["evidence"] for record in records}):
        body += f"- [Passed public-artifact verification]({evidence}).\n"
    body += "\nThis PR accepts already-published artifacts. It does not rebuild images. After merge, the alias workflow selects the newest accepted available revision in each compatible major line; exact tags and digest pins stay unchanged."
    return body
