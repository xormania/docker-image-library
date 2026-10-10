"""Local Dockerfile inputs and tool pins, shared by selection and fingerprints."""
import json
import re
import shlex
from pathlib import Path


TOOL_KEYS = {
    "php-dev": ("composer", "redis_version", "xdebug_version", "pcov_version", "symfony", "infection", "apt_indexes"),
    "php-frankenphp": ("composer", "redis_version", "xdebug_version", "pcov_version", "symfony", "apcu_version", "infection", "apt_indexes"),
    "flowbite-xor-dev": ("node", "tailwind"),
    "python-dev": ("uv", "apt_indexes"),
    "rust-dev": ("apt_indexes",),
    "php-browser": ("apt_indexes",),
    "php-serena": ("node",),
    "playwright-browser": ("apt_indexes",),
}


def sources(family, root):
    """Read COPY sources; stage copies are already represented by pinned inputs."""
    recipe = Path(root) / "images" / family / "Dockerfile"
    result = {str(recipe.relative_to(root)), ".dockerignore"}
    text = recipe.read_text().replace("\\\n", " ")
    for line in text.splitlines():
        instruction = re.match(r"^\s*(COPY|ADD)\s+(.+)$", line, re.I)
        if not instruction:
            continue
        if instruction[1].upper() == "ADD":
            raise ValueError("Use explicit COPY and pinned downloads for image inputs")
        value = instruction[2]
        flags = []
        while value.startswith("--"):
            flag, value = value.split(None, 1)
            flags.append(flag)
        if any(flag.startswith("--from=") for flag in flags):
            continue
        tokens = json.loads(value) if value.startswith("[") else shlex.split(value)
        for source in tokens[:-1]:
            if source.startswith("/") or ".." in Path(source).parts or "$" in source:
                raise ValueError(f"Unsupported COPY source: {source}")
            result.add(source.rstrip("/"))
    return sorted(result)


def consumes(family, path, root):
    return any(path == source or path.startswith(source + "/")
               or Path(path).match(source) for source in sources(family, root))


def files(family, root):
    result = set()
    for source in sources(family, root):
        for path in Path(root).glob(source):
            if path.is_dir():
                result.update(item for item in path.rglob("*") if item.is_file())
            elif path.is_file():
                result.add(path)
    return sorted(result)
