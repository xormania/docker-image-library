#!/usr/bin/env python3
"""Verified dependency snapshots, portable between worktrees and CI artifact jobs."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tempfile
import zipfile


def sha(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def identity(project, kind, image="", runtime=None):
    runtime = runtime or subprocess.check_output(["php", "-r",
        '$e=get_loaded_extensions(); sort($e); echo json_encode([PHP_VERSION,PHP_OS_FAMILY,PHP_INT_SIZE,$e]);'], text=True)
    files = ["composer.json", "composer.lock"]
    if kind == "importmap":
        files.append(os.environ.get("IMPORTMAP_FILE", "importmap.php"))
    facts = {"schema": 1, "kind": kind, "runtime": runtime, "image": image,
             "inputs": {name: sha(project / name) for name in files}}
    return hashlib.sha256(json.dumps(facts, sort_keys=True).encode()).hexdigest()


def tree_manifest(folder):
    result = {}
    for directory, dirs, files in os.walk(folder):
        # Directory links belong in the manifest, but are never traversed.
        links = [name for name in dirs if (Path(directory) / name).is_symlink()]
        dirs[:] = sorted(name for name in dirs if name not in links)
        for name in sorted(files + links):
            path = Path(directory) / name
            relative = path.relative_to(folder).as_posix()
            if path.is_symlink():
                result[relative] = {"link": os.readlink(path)}
            elif path.is_file():
                result[relative] = {"sha256": sha(path), "mode": path.stat().st_mode & 0o777}
    return result


def write_archive(folder, archive, key):
    manifest = tree_manifest(folder)
    if not manifest:
        return False
    if archive.is_file():
        try:
            with zipfile.ZipFile(archive) as existing:
                if json.loads(existing.read("manifest.json")) == {"schema": 1, "identity": key, "files": manifest}:
                    return True
        except (OSError, ValueError, KeyError, zipfile.BadZipFile):
            pass
    archive.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=archive.parent, delete=False) as stream:
        temporary = Path(stream.name)
    try:
        with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, compresslevel=3) as output:
            output.writestr("manifest.json", json.dumps({"schema": 1, "identity": key, "files": manifest}))
            for name, entry in manifest.items():
                if "link" not in entry:
                    output.write(folder / name, "files/" + name)
        temporary.replace(archive)
    finally:
        temporary.unlink(missing_ok=True)
    return True


def restore_archive(archive, folder, key, workspace):
    if folder.exists() or folder.is_symlink():
        return False
    with zipfile.ZipFile(archive) as source:
        manifest = json.loads(source.read("manifest.json"))
        if manifest.get("schema") != 1 or manifest.get("identity") != key:
            raise ValueError("Dependency cache identity differs from project/runtime inputs")
        entries = manifest["files"]
        links = {name for name, entry in entries.items() if "link" in entry}
        for name, entry in entries.items():
            parts = PurePosixPath(name).parts
            if not parts or name.startswith("/") or ".." in parts or "\\" in name:
                raise ValueError("Unsafe dependency archive path")
            if any(PurePosixPath(name).is_relative_to(PurePosixPath(link)) and name != link for link in links):
                raise ValueError("Dependency archive contains files below a symlink")
            if "link" in entry:
                target = Path(os.path.normpath(str(folder / name / ".." / entry["link"])))
                if Path(entry["link"]).is_absolute() or not target.is_relative_to(workspace):
                    raise ValueError("Dependency symlink leaves the mounted workspace")
        folder.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=folder.parent, prefix=".xorder-restore-") as directory:
            staged = Path(directory) / "payload"
            staged.mkdir()
            for name, entry in entries.items():
                path = staged / name
                path.parent.mkdir(parents=True, exist_ok=True)
                if "link" in entry:
                    path.symlink_to(entry["link"])
                else:
                    with source.open("files/" + name) as incoming, path.open("wb") as output:
                        shutil.copyfileobj(incoming, output)
                    if sha(path) != entry["sha256"]:
                        raise ValueError("Dependency snapshot checksum mismatch")
                    path.chmod(entry["mode"] & 0o777)
            staged.rename(folder)
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["restore", "store", "export", "import"])
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--cache", type=Path, default=Path(os.environ.get("XORDER_DEPENDENCY_CACHE", "/run/xorder-cache")))
    parser.add_argument("--image", default=os.environ.get("XORDER_CACHE_IMAGE", ""))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--input", type=Path)
    args = parser.parse_args(argv)
    project = args.project.resolve()
    if not args.cache.is_dir():
        if args.action in {"restore", "store"}:
            return 0
        parser.error("Cache directory is unavailable")
    if args.action == "export" and not args.output or args.action == "import" and not args.input:
        parser.error("export needs --output; import needs --input")
    vendor = os.environ.get("IMPORTMAP_VENDOR_DIR", "assets/vendor")
    folders = {"vendor": project / "vendor", "importmap": project / vendor}
    for folder in folders.values():
        if not folder.resolve().is_relative_to(project):
            raise ValueError("Dependency directory must be inside the project")
    with (args.cache / "snapshots.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if args.action == "import":
            with zipfile.ZipFile(args.input) as bundle:
                for kind in folders:
                    key = identity(project, kind, args.image)
                    name = kind + "-" + key + ".zip"
                    if name in bundle.namelist():
                        destination = args.cache / name
                        temporary = destination.with_suffix(".tmp")
                        try:
                            with bundle.open(name) as incoming, temporary.open("wb") as output:
                                shutil.copyfileobj(incoming, output)
                            # Validate all bytes in isolation before promoting an imported cache.
                            with tempfile.TemporaryDirectory(dir=project) as directory:
                                restore_archive(temporary, Path(directory) / kind, key, project.parent)
                            temporary.replace(destination)
                        finally:
                            temporary.unlink(missing_ok=True)
        selected = []
        for kind, folder in folders.items():
            if kind == "importmap" and not (project / os.environ.get("IMPORTMAP_FILE", "importmap.php")).is_file():
                continue
            key = identity(project, kind, args.image)
            archive = args.cache / (kind + "-" + key + ".zip")
            if args.action in {"store", "export"} and folder.is_dir():
                write_archive(folder, archive, key)
            if args.action in {"restore", "import"} and archive.is_file():
                try:
                    if restore_archive(archive, folder, key, project.parent):
                        print(f"Restored verified {kind} snapshot")
                except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
                    print(f"Ignoring unusable {kind} snapshot: {error}", file=__import__('sys').stderr)
            if archive.is_file():
                selected.append(archive)
        if args.action == "export":
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(args.output, "w", zipfile.ZIP_STORED) as bundle:
                for archive in selected:
                    bundle.write(archive, archive.name)
            print("Exported dependency snapshots to " + str(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
