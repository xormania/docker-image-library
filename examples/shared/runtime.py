"""Host resource observations, daemon recovery and cooperative heavy-run limits."""
from contextlib import contextmanager
import fcntl
import json
import math
import os
from pathlib import Path
import shlex
import shutil
import subprocess


def state_root(env):
    root = Path(env.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))) / "xorder"
    root.mkdir(parents=True, exist_ok=True)
    return root


def resources(workspace):
    cpus = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count() or 1
    try:
        quota, period = Path("/sys/fs/cgroup/cpu.max").read_text().split()
        if quota != "max":
            cpus = min(cpus, max(1, math.ceil(int(quota) / int(period))))
    except (OSError, ValueError):
        pass
    available = None
    try:
        entries = dict(line.split(":", 1) for line in Path("/proc/meminfo").read_text().splitlines())
        available = int(entries["MemAvailable"].split()[0]) * 1024
        limit = Path("/sys/fs/cgroup/memory.max").read_text().strip()
        if limit != "max":
            available = min(available, max(0, int(limit) - int(Path("/sys/fs/cgroup/memory.current").read_text())))
    except (OSError, ValueError, KeyError):
        pass
    load = os.getloadavg()[0] if hasattr(os, "getloadavg") else 0
    disk = shutil.disk_usage(workspace)
    return {"cpus": cpus, "load": round(load, 2), "memory_available": available,
            "disk_total": disk.total, "disk_free": disk.free, "disk_used": disk.used}


def print_resources(workspace, env=None):
    facts = resources(workspace)
    threshold = float((env or os.environ).get("XORDER_DISK_WARN_GIB", "3"))
    if not math.isfinite(threshold) or threshold < 0:
        raise ValueError("XORDER_DISK_WARN_GIB must be a finite nonnegative number")
    print(f"disk: {facts['disk_free']/1024**3:.1f} GiB free, {facts['disk_used']/1024**3:.1f} GiB used "
          "(filesystem accounting; sandbox quota may differ)")
    if facts["disk_free"] < threshold * 1024**3:
        print(f"disk warning: below {threshold:g} GiB free; reclaim space before pulling images or running tests")
    memory = f", {facts['memory_available']/1024**3:.1f} GiB available" if facts['memory_available'] is not None else ""
    print(f"load: {facts['load']:.2f}, CPU budget {facts['cpus']}{memory}")


def ensure_daemon(env):
    def reachable():
        return subprocess.run(["docker", "info"], env=env, stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL, timeout=15).returncode == 0
    if reachable():
        return
    from network import local_engine
    if not local_engine(env):
        raise ValueError("Remote Docker daemon unavailable; restore the selected engine")
    explicit = env.get("XORDER_DOCKER_START_COMMAND")
    commands = [shlex.split(explicit)] if explicit else ([
        ["systemctl", "start", "docker"], ["service", "docker", "start"]
    ] if os.getuid() == 0 else [["systemctl", "--user", "start", "docker"]])
    for command in commands:
        if not command or not shutil.which(command[0]):
            continue
        print("Docker unavailable; attempting configured service recovery", flush=True)
        subprocess.run(command, env=env, check=False, timeout=30,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if reachable():
            return
    raise ValueError("Docker daemon unavailable. Start Docker or set XORDER_DOCKER_START_COMMAND, then run up")


def worker_budget(workspace, env):
    facts = resources(workspace)
    cpu_budget = max(1, int(facts["cpus"] - facts["load"]))
    memory_budget = max(1, facts["memory_available"] // (1024**3)) if facts["memory_available"] else 1
    maximum = int(env.get("XORDER_TEST_MAX_WORKERS", "4"))
    if maximum < 1:
        raise ValueError("XORDER_TEST_MAX_WORKERS must be positive")
    return min(cpu_budget, memory_budget, maximum)


@contextmanager
def heavy_run(workspace, env):
    count = int(env.get("XORDER_TEST_MAX_RUNS", "1"))
    if not 1 <= count <= 64:
        raise ValueError("XORDER_TEST_MAX_RUNS must be between 1 and 64")
    folder = state_root(env) / "test-runs"
    folder.mkdir(parents=True, exist_ok=True)
    lock = None
    for slot in range(count):
        candidate = (folder / f"{slot}.lock").open("a+")
        try:
            fcntl.flock(candidate, fcntl.LOCK_EX | fcntl.LOCK_NB)
            lock = candidate
            break
        except BlockingIOError:
            candidate.close()
    if lock is None:
        raise ValueError("Another heavy test run holds the host budget. Retry when it finishes "
                         "or deliberately increase XORDER_TEST_MAX_RUNS")
    try:
        lock.seek(0); lock.truncate()
        lock.write(json.dumps({"workspace": str(workspace), "pid": os.getpid()})); lock.flush()
        yield worker_budget(workspace, env)
    finally:
        lock.seek(0); lock.truncate()
        lock.close()


def referenced_images(containers, images, keep=()):
    """Protect direct images and local ancestors, including BuildKit's layer-only ancestry."""
    aliases = {alias: image["Id"] for image in images
               for alias in [image["Id"], *(image.get("RepoTags") or []), *(image.get("RepoDigests") or [])]}
    used = {aliases.get(value, value) for value in keep}
    for container in containers:
        for value in (container.get("Image"), container.get("Config", {}).get("Image")):
            if value:
                used.add(aliases.get(value, value))
    by_id = {image["Id"]: image for image in images}
    pending = list(used)
    while pending:
        image = by_id.get(pending.pop())
        if not image:
            continue
        layers = image.get("RootFS", {}).get("Layers", [])
        parents = {image.get("Parent")}
        # Docker's Parent is often empty for OCI/BuildKit images. RootFS diff-ID
        # prefixes also establish ancestors; equal layers conservatively protect
        # configuration-only derivatives and aliases of the same filesystem.
        parents.update(other["Id"] for other in images
                       if (prior := other.get("RootFS", {}).get("Layers", []))
                       and len(prior) <= len(layers) and layers[:len(prior)] == prior)
        for parent in parents - used - {None, ""}:
            used.add(parent)
            pending.append(parent)
    return used


def gc(env, apply=False, runner_copies=(), keep=()):
    """Remove only stopped xorder-labelled containers and unused xorder image IDs."""
    def docker(*args):
        return subprocess.check_output(["docker", *args], env=env, text=True).strip()
    ids = docker("ps", "-aq") .split()
    containers = json.loads(docker("inspect", *ids)) if ids else []
    stopped = [item for item in containers if item.get("Config", {}).get("Labels", {}).get("dev.xorder.workspace")
               and not item.get("State", {}).get("Running")]
    image_ids = docker("image", "ls", "-aq", "--no-trunc").split()
    images = json.loads(docker("image", "inspect", *dict.fromkeys(image_ids))) if image_ids else []
    # Resolve exact local identities before planning. An unknown keep reference
    # stops cleanup instead of silently ignoring a misspelling or a missing pull.
    kept = [image["Id"] for image in json.loads(docker("image", "inspect", *keep))] if keep else []
    used = referenced_images(containers, images, kept)
    unused = [item for item in images if item["Id"] not in used and
              item.get("Config", {}).get("Labels", {}).get("org.opencontainers.image.source") == "https://github.com/xormania/xorder"]
    result = {"dry_run": not apply, "stopped_containers": [item["Id"] for item in stopped],
              "unused_images": [item["Id"] for item in unused], "kept_images": kept,
              "old_runner_state": [], "old_runner_copies": []}
    for value in runner_copies:
        path = Path(value).resolve(strict=True)
        current = Path(env["XORDER_RUNNER_ROOT"]).resolve()
        workspace = Path(env["WORKSPACE"]).resolve()
        if (not path.is_dir() or (path / ".git").exists() or current.is_relative_to(path)
                or workspace.is_relative_to(path) or path.is_relative_to(workspace)
                or not (path / "catalog-v2.json").is_file()
                or not (path / "examples/flowbite-xor/runner.py").is_file()):
            raise ValueError("Runner-copy cleanup needs an explicitly selected unpacked xorder copy outside the checkout and current runner")
        if any(Path(mount.get("Source", "/")).is_relative_to(path)
               for container in containers for mount in container.get("Mounts", []) if mount.get("Type") == "bind"):
            raise ValueError("Runner copy is still mounted by a stack; stop and remove that stack first")
        result["old_runner_copies"].append(str(path))
    # Receipts and generated git pointers are reconstructable. Never delete repositories.
    root = state_root(env)
    for folder in (root / "worktrees", root / "flowbite"):
        if folder.exists():
            for item in folder.glob("*/workspace.json"):
                try:
                    workspace = Path(json.loads(item.read_text())["workspace"])
                    if not workspace.exists():
                        result["old_runner_state"].append(str(item.parent))
                except (OSError, ValueError, KeyError):
                    pass
    print(json.dumps(result, indent=2))
    if apply:
        for item in stopped:
            # Reinspect: never remove a container which became running since planning.
            if json.loads(docker("inspect", item["Id"]))[0]["State"].get("Running"):
                continue
            subprocess.run(["docker", "rm", item["Id"]], env=env, check=True)
        for image in unused:
            current_ids = docker("ps", "-aq").split()
            current_containers = json.loads(docker("inspect", *current_ids)) if current_ids else []
            current_image_ids = docker("image", "ls", "-aq", "--no-trunc").split()
            current_images = json.loads(docker("image", "inspect", *dict.fromkeys(current_image_ids))) if current_image_ids else []
            if image["Id"] in referenced_images(current_containers, current_images, kept):
                print(f"Skipped image now referenced: {image['Id']}")
                continue
            # No --force: Docker protects references that appeared since planning.
            subprocess.run(["docker", "image", "rm", image["Id"]], env=env, check=False)
        for path in result["old_runner_state"]:
            shutil.rmtree(path)
        for path in result["old_runner_copies"]:
            # Recheck mounts immediately before removing the selected copy.
            current_ids = docker("ps", "-aq").split()
            current_containers = json.loads(docker("inspect", *current_ids)) if current_ids else []
            if any(Path(mount.get("Source", "/")).is_relative_to(Path(path))
                   for container in current_containers for mount in container.get("Mounts", []) if mount.get("Type") == "bind"):
                raise ValueError("Runner copy acquired a stack reference; cleanup stopped")
            shutil.rmtree(path)
    return 0
