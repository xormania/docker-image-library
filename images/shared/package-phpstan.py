#!/usr/bin/env python3
"""Filter the prepared native bundle before Composer's install layer is committed."""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def runtime(package):
    # Use the installed PHAR's platform/libc detection, not the Docker host or
    # Composer's config.platform.php (which describes dependency resolution).
    code = r'''
require $argv[1];
echo json_encode([
    'platform' => PHPStan\Turbo\TurboExtensionSelector::resolvePlatformDirectory(
        PHP_OS_FAMILY, php_uname('m'), PHPStan\Turbo\TurboExtensionSelector::isMusl()
    ),
    'php_minor' => PHP_MAJOR_VERSION . '.' . PHP_MINOR_VERSION,
    'zts' => (bool) PHP_ZTS,
    'debug' => (bool) PHP_DEBUG,
], JSON_THROW_ON_ERROR);
'''
    selector = 'phar://' + str(package / 'phpstan.phar') + '/src/Turbo/TurboExtensionSelector.php'
    return json.loads(subprocess.check_output(
        ['php', '-r', code, selector], text=True,
        env=dict(os.environ, XDEBUG_MODE='off'),
    ))


def package_tools(project):
    package = project.resolve() / 'vendor/phpstan/phpstan'
    native = package / 'turbo-ext'
    target = runtime(package)
    platform = target['platform']
    minor = target['php_minor']
    if target['debug'] or not isinstance(platform, str) or not re.fullmatch(r'linux-(gnu|musl)-(x86_64|arm64)', platform):
        raise ValueError(f'Unsupported prepared PHPStan runtime: {target}')
    if not re.fullmatch(r'\d+\.\d+', minor):
        raise ValueError(f'Invalid PHP minor version: {minor}')
    expected = f"{platform}/phpstan_turbo-{minor}{'-zts' if target['zts'] else ''}.so"

    # Validate the complete layout and selection before deleting any files.
    if native.is_symlink() or not native.is_dir():
        raise ValueError('Missing or symlinked PHPStan Turbo bundle')
    files = {}
    for path in native.rglob('*'):
        relative = path.relative_to(native).as_posix()
        if path.is_symlink() or not (path.is_file() or path.is_dir()):
            raise ValueError(f'Unexpected PHPStan Turbo entry: {relative}')
        if path.is_dir():
            continue
        if relative != '.version' and not re.fullmatch(r'[^/]+/phpstan_turbo-\d+\.\d+(?:-zts)?\.(?:so|dll)', relative):
            raise ValueError(f'Unexpected PHPStan Turbo file: {relative}')
        files[relative] = path
    if '.version' not in files or not files['.version'].read_text().strip():
        raise ValueError('Missing PHPStan Turbo version metadata')
    retained = expected if expected in files else None
    # The pinned upstream selector explicitly documents this Linux fallback.
    # A newly shipped matching ZTS binary is kept automatically; other missing
    # binaries are build failures so an upstream packaging change is reviewed.
    if retained is None and not (target['zts'] and minor in ('8.4', '8.5')):
        raise ValueError(f'Missing compatible PHPStan Turbo binary: {expected}')
    keep = {'.version'} | ({retained} if retained else set())
    before = sum(path.stat().st_size for path in files.values())
    digest = hashlib.sha256(files[retained].read_bytes()).hexdigest() if retained else None
    for relative, path in files.items():
        if relative not in keep:
            path.unlink()
    for path in sorted(native.rglob('*'), key=lambda path: len(path.parts), reverse=True):
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()
    after = sum(files[name].stat().st_size for name in keep)
    report = {
        'runtime': target,
        'turbo_version': files['.version'].read_text().strip(),
        'retained_binary': retained,
        'retained_sha256': digest,
        'before_bytes': before,
        'after_bytes': after,
        'removed_bytes': before - after,
    }
    (project / 'phpstan-packaging.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    try:
        print(json.dumps(package_tools(Path(sys.argv[1])), sort_keys=True))
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        sys.exit(f'PHPStan packaging failed: {error}')
