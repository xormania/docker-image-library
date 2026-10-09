#!/usr/bin/env python3
"""Run independent PHPUnit/PHPStan tasks from the consuming project's lockfiles."""
import json
import os
import subprocess
import sys
from pathlib import Path


def tool(project, package, executable):
    """Reject missing/stale installs before using a project's own bin proxy."""
    project = Path(project).resolve(strict=True)
    locked = json.loads((project / "composer.lock").read_text())
    installed = json.loads((project / "vendor/composer/installed.json").read_text())
    wanted = next((item for item in locked.get("packages", []) + locked.get("packages-dev", [])
                   if item["name"] == package), None)
    actual = next((item for item in (installed["packages"] if isinstance(installed, dict) else installed)
                   if item["name"] == package), None)
    if wanted is None or actual is None:
        raise ValueError(f"{project}: {package} must be locked and installed with project development dependencies")
    if wanted["version"] != actual["version"]:
        raise ValueError(f"{project}: installed {package} {actual['version']} differs from lock {wanted['version']}")
    for origin in ("source", "dist"):
        reference = wanted.get(origin, {}).get("reference")
        if reference and reference != actual.get(origin, {}).get("reference"):
            raise ValueError(f"{project}: installed {package} {origin} reference differs from composer.lock")
    binary = project / "vendor/bin" / executable
    if not binary.is_file():
        raise ValueError(f"Missing project tool: {binary}; install project dependencies first")
    return project, binary, wanted["version"]


def configuration(name, project):
    value = os.environ.get(name)
    if not value:
        return []
    path = Path(value)
    if not path.is_absolute():
        path = project / path
    return ["--configuration", str(path.resolve(strict=True))]


def execute(task, arguments):
    if task not in ("phpunit", "coverage", "phpstan", "all"):
        raise ValueError("Task must be phpunit, coverage, phpstan, or all")
    if task == "all" and arguments:
        raise ValueError("Pass tool arguments to an individual task; use configuration environment variables for all")
    tools = {}
    if task in ("phpunit", "coverage", "all"):
        tools["phpunit"] = tool(os.environ.get("PHPUNIT_PROJECT", os.getcwd()), "phpunit/phpunit", "phpunit")
    if task in ("phpstan", "all"):
        tools["phpstan"] = tool(os.environ.get("PHPSTAN_PROJECT", os.getcwd()), "phpstan/phpstan", "phpstan")
    environment = os.environ.copy()
    environment["XDEBUG_MODE"] = "off"
    if task == "all":
        tasks = ["coverage", "phpstan"]
    else:
        tasks = [task]
    for selected in tasks:
        name = "phpunit" if selected == "coverage" else selected
        project, binary, version = tools[name]
        print(f"{selected}: {name} {version} from {project}/composer.lock", flush=True)
        command = ["php", "-d", "pcov.enabled=0", str(binary)]
        if name == "phpunit":
            command += configuration("PHPUNIT_CONFIGURATION", project)
            if selected == "coverage":
                driver = environment.get("COVERAGE_DRIVER", "pcov")
                if driver not in ("pcov", "xdebug"):
                    raise ValueError("COVERAGE_DRIVER must be pcov or xdebug")
                source = Path(environment.get("COVERAGE_SOURCE", str(project / "src" if (project / "src").is_dir() else project))).resolve(strict=True)
                environment["COVERAGE_SOURCE"] = str(source)
                output = Path(environment.get("COVERAGE_CLOVER", str(project / "var/coverage/clover.xml")))
                if not output.is_absolute():
                    output = project / output
                output.parent.mkdir(parents=True, exist_ok=True)
                command = ["library-php-coverage", driver, str(binary)] + configuration("PHPUNIT_CONFIGURATION", project)
                command += ["--coverage-clover", str(output.resolve())]
            else:
                command += ["--no-coverage"]
        else:
            workspace = Path(environment.get("PHPSTAN_WORKSPACE", os.getcwd())).resolve(strict=True)
            command += ["analyse", "--no-progress"] + configuration("PHPSTAN_CONFIGURATION", workspace)
            autoload = environment.get("PHPSTAN_AUTOLOAD_FILE")
            if autoload:
                autoload = Path(autoload)
                if not autoload.is_absolute():
                    autoload = workspace / autoload
                command += ["--autoload-file", str(autoload.resolve(strict=True))]
            paths = json.loads(environment.get("PHPSTAN_PATHS", "[]"))
            if not isinstance(paths, list) or any(not isinstance(path, str) or not path for path in paths):
                raise ValueError("PHPSTAN_PATHS must be a JSON array of paths")
            command += paths
        subprocess.run(command + arguments, env=environment,
                       cwd=workspace if name == "phpstan" else project, check=True)
    return 0


def main():
    if sys.argv[1:] == ["--version"]:
        print("xorder PHP test runner 1.0.0")
        return 0
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: library-php-tests phpunit|coverage|phpstan|all [TOOL_ARGS...]\n"
              "PHPUNIT_PROJECT and PHPSTAN_PROJECT select lock-owned project directories (default: cwd).\n"
              "PHPUNIT_CONFIGURATION and PHPSTAN_CONFIGURATION select project configuration files.\n"
              "PHPSTAN_WORKSPACE selects analysis cwd; PHPSTAN_AUTOLOAD_FILE/PHPSTAN_PATHS select app inputs.\n"
              "COVERAGE_DRIVER=pcov|xdebug; COVERAGE_SOURCE selects source; COVERAGE_CLOVER selects output.\n"
              "all runs coverage, then PHPStan. Project tools must already be installed.")
        return 0 if len(sys.argv) > 1 else 2
    try:
        return execute(sys.argv[1], sys.argv[2:])
    except subprocess.CalledProcessError as error:
        print("PHP tests: " + str(error), file=sys.stderr)
        return error.returncode if error.returncode >= 0 else 128 - error.returncode
    except (ValueError, KeyError, OSError) as error:
        print("PHP tests: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
