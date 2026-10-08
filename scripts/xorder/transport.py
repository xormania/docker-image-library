"""Verified byte transfer and extraction shared by publication and installation."""

import hashlib
import ipaddress
import os
import re
import shutil
import stat
import tarfile
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath, PureWindowsPath


CHUNK_BYTES = 128 * 1024
DOWNLOAD_TIMEOUT = 30


def _check_url(url, allow_local_http):
    parsed = urllib.parse.urlsplit(url)
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("download URLs must not contain credentials")
    if not parsed.hostname:
        raise ValueError("download URL has no hostname")
    if parsed.scheme == "https":
        return
    if parsed.scheme == "http" and allow_local_http:
        host = parsed.hostname.lower()
        try:
            loopback = ipaddress.ip_address(host).is_loopback
        except ValueError:
            loopback = host == "localhost"
        if loopback:
            return
    raise ValueError("downloads require HTTPS; local HTTP needs explicit opt-in")


class _VerifiedRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self, allow_local_http):
        self.allow_local_http = allow_local_http

    def redirect_request(self, request, response, code, message, headers, new_url):
        _check_url(new_url, self.allow_local_http)
        return super().redirect_request(request, response, code, message, headers, new_url)


def download(url, destination, expected_sha256, *, allow_local_http=False):
    """Replace destination atomically only after an exact SHA-256 match.

    Redirects follow the same HTTPS policy as the original URL. The local HTTP
    escape hatch is for explicit loopback test servers, never public artifacts.
    """
    if not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected_sha256):
        raise ValueError("expected_sha256 must be a 64-character SHA-256 hex digest")
    expected_sha256 = expected_sha256.lower()
    _check_url(url, allow_local_http)
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix="." + destination.name + ".download-", dir=destination.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as output:
            digest = hashlib.sha256()
            size = 0
            opener = urllib.request.build_opener(_VerifiedRedirect(allow_local_http))
            request = urllib.request.Request(url, headers={"User-Agent": "xorder-artifact-transfer"})
            with opener.open(request, timeout=DOWNLOAD_TIMEOUT) as response:
                _check_url(response.geturl(), allow_local_http)
                while chunk := response.read(CHUNK_BYTES):
                    output.write(chunk)
                    digest.update(chunk)
                    size += len(chunk)
            actual_sha256 = digest.hexdigest()
            if actual_sha256 != expected_sha256:
                raise ValueError(f"download checksum mismatch: expected {expected_sha256}, got {actual_sha256}")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, destination)
        return {"sha256": actual_sha256, "size_bytes": size}
    finally:
        temporary.unlink(missing_ok=True)


def _member_path(name):
    if not name or "\x00" in name or "\\" in name:
        raise ValueError(f"unsafe archive path: {name!r}")
    path = PurePosixPath(name)
    if path.is_absolute() or PureWindowsPath(name).drive or ".." in path.parts:
        raise ValueError(f"unsafe archive path: {name!r}")
    if not path.parts:
        raise ValueError(f"empty archive path: {name!r}")
    return path


def _normal_mode(mode):
    if mode & ~0o777:
        raise ValueError("special file permission bits are not supported")
    return mode


def _tar_members(archive):
    members = []
    paths = {}
    for member in archive.getmembers():
        path = _member_path(member.name)
        if path in paths:
            raise ValueError(f"duplicate archive path: {member.name!r}")
        if not member.isfile() and not member.isdir():
            raise ValueError(f"archive links and special files are not supported: {member.name!r}")
        _normal_mode(member.mode)
        paths[path] = member
        members.append((path, member))
    for path, member in members:
        for parent in path.parents:
            if parent in paths and not paths[parent].isdir():
                raise ValueError(f"archive file is also a parent directory: {str(parent)!r}")
    return members


def unpack(path, format, destination, filename=None):
    """Materialize verified bytes into a new owned directory; return that Path.

    TAR supports regular files and directories, preserving ordinary permissions.
    Links, devices, traversal, duplicate names and special permissions are rejected
    before materialization. Single files accept an explicit leaf filename because
    cache paths commonly use content hashes rather than the published filename.
    """
    path, destination = Path(path), Path(destination)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"extraction destination already exists: {destination}")
    if not path.is_file() or path.is_symlink():
        raise ValueError("artifact source must be a regular file")
    if format == "file":
        name = path.name if filename is None else filename
        leaf = _member_path(name)
        if len(leaf.parts) != 1 or name != leaf.name:
            raise ValueError("single-file artifacts require a leaf filename")
        mode = _normal_mode(stat.S_IMODE(path.stat().st_mode))
        destination.mkdir(parents=True)
        try:
            shutil.copyfile(path, destination / name)
            (destination / name).chmod(mode)
        except BaseException:
            shutil.rmtree(destination)
            raise
        return destination
    if format != "tar":
        raise ValueError(f"unsupported artifact format: {format!r}")
    if filename is not None:
        raise ValueError("filename applies only to single-file artifacts")
    with tarfile.open(path, mode="r:*") as archive:
        members = _tar_members(archive)
        destination.mkdir(parents=True)
        try:
            directories = []
            for relative, member in members:
                target = destination.joinpath(*relative.parts)
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                    directories.append((target, member.mode))
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with archive.extractfile(member) as source, target.open("xb") as output:
                        shutil.copyfileobj(source, output, length=CHUNK_BYTES)
                    target.chmod(member.mode)
            # Restrictive directory modes are applied after their children exist.
            for target, mode in sorted(directories, key=lambda item: len(item[0].parts), reverse=True):
                target.chmod(mode)
        except BaseException:
            shutil.rmtree(destination)
            raise
    return destination
