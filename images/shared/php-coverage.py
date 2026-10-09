#!/usr/bin/env python3
"""Enable exactly one coverage driver for a CLI process, preserving PHP settings."""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def without_xdebug(text):
    """Remove loader directives, preserving other settings in the same file."""
    return "".join(line for line in text.splitlines(keepends=True)
                   if not re.match(r"^\s*zend_extension\s*=.*xdebug", line, re.IGNORECASE))


def run(driver, arguments, source=None):
    if driver not in ("pcov", "xdebug"):
        raise ValueError("Coverage driver must be pcov or xdebug")
    if not arguments:
        raise ValueError("Supply a PHP script or PHP CLI arguments")
    environment = os.environ.copy()
    if driver == "xdebug":
        environment["XDEBUG_MODE"] = "coverage"
        command = ["php", "-d", "pcov.enabled=0"]
        check = 'if (!extension_loaded("xdebug") || !in_array("coverage", xdebug_info("mode"), true)) {fwrite(STDERR, "Xdebug coverage unavailable\\n"); exit(1);}'
        subprocess.run(command + ["-r", check], env=environment, check=True)
        return subprocess.call(command + arguments, env=environment)

    source = Path(source or environment.get("COVERAGE_SOURCE", ".")).resolve(strict=True)
    if not source.is_dir():
        raise ValueError("COVERAGE_SOURCE must identify a source directory")
    # PCOV's executor hooks are incompatible with a loaded Xdebug. Copy the
    # actual CLI configuration for this invocation and remove only its loader.
    # Never rename/unload an extension globally in a running app container.
    configuration = json.loads(subprocess.check_output([
        "php", "-d", "pcov.enabled=0", "-r",
        "echo json_encode(['main'=>php_ini_loaded_file(), 'scanned'=>php_ini_scanned_files()]);"
    ], text=True))
    with tempfile.TemporaryDirectory(prefix="xorder-pcov-") as temporary:
        directory = Path(temporary)
        main = directory / "main.ini"
        main.write_text(without_xdebug(Path(configuration["main"]).read_text())
                        if configuration["main"] else "")
        scanned = directory / "conf.d"
        scanned.mkdir()
        # php_ini_scanned_files() returns files in their actual load order,
        # including directories supplied through PHP_INI_SCAN_DIR.
        files = (configuration["scanned"] or "").strip().split(",")
        for number, filename in enumerate(files):
            if filename.strip():
                (scanned / f"{number:05d}.ini").write_text(
                    without_xdebug(Path(filename.strip()).read_text()))
        environment.update(PHP_INI_SCAN_DIR=str(scanned), XDEBUG_MODE="off")
        command = ["php", "-c", str(main), "-d", "pcov.enabled=1",
                   "-d", "pcov.directory=" + str(source)]
        check = 'if (!extension_loaded("pcov") || extension_loaded("xdebug") || !ini_get("pcov.enabled")) {fwrite(STDERR, "PCOV unavailable or Xdebug still loaded\\n"); exit(1);}'
        subprocess.run(command + ["-r", check], env=environment, check=True)
        return subprocess.call(command + arguments, env=environment)


def main():
    if sys.argv[1:] == ["--version"]:
        print("xorder PHP coverage runner 1.0.0")
        return 0
    if len(sys.argv) < 3 or sys.argv[1] in ("-h", "--help"):
        print("Usage: library-php-coverage pcov|xdebug PHP_SCRIPT [PHP_ARGS...]\n"
              "COVERAGE_SOURCE selects the source directory for PCOV (default: cwd).")
        return 0 if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help") else 2
    try:
        return run(sys.argv[1], sys.argv[2:])
    except subprocess.CalledProcessError as error:
        print("PHP coverage: " + str(error), file=sys.stderr)
        return error.returncode
    except (ValueError, OSError) as error:
        print("PHP coverage: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    status = main()
    sys.exit(status if status >= 0 else 128 - status)
