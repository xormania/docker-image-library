# flowbite-xor-dev/8.4-trixie v1.1.0

- Add opt-in PCOV coverage and reusable lock-owned PHPUnit/PHPStan tasks while retaining Xdebug coverage and default-disabled coverage hooks.
- Accept a mounted multi-certificate PEM CA bundle; validate all certificates before replacing managed trust and retain single-certificate and root/user behavior.

Migration: Compatible additive update. Select a verified new digest before using library-php-tests; PHPUnit/PHPStan versions and configuration continue to come from the consuming project. Set COVERAGE_DRIVER=xdebug for Xdebug coverage. LIBRARY_CA_FILE accepts either a single certificate or a complete validated PEM bundle.

Source: `ea9133bbb23d222c1e0ff800250ccbb98066f254` (`flowbite-xor-dev/8.4-trixie/v1.1.0`).

Artifact: `ghcr.io/xormania/flowbite-xor-dev@sha256:68979e1105bdadb6a3a784a8944f86ffe8f54f0e8d475dc2bbea0c18a00b2cca`.

Base/parent: `ghcr.io/xormania/php-frankenphp@sha256:6c5edb921d745e5dbc8fdff454c557360c5a789d5a82aa7b351b6419176050e8`.

[Verification](https://github.com/xormania/xorder/actions/runs/37884893194).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,426.1 MiB (1,495,325,659 bytes) |
| Build, cache export and image load | 26.95s |
| Public-artifact behavior and inventory verification | 108.97s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/37884893194); 2026-10-09T04:49:05.827746Z.

Plan about **3 GiB free for a cold pull**, plus space for project dependencies and test output. This estimate is twice the measured unpacked image size, rounded up; shared layers may lower it, while the image store, temporary files and sandbox quotas can increase the requirement. Check free space on the Docker data filesystem; it may differ from the checkout filesystem.

External build cache at start: `restored`. This does not assert that every layer was a cache hit.

Size baseline: v1.0.0, `ghcr.io/xormania/flowbite-xor-dev@sha256:39d0dfa2cae629a9bc65e09d3cd44b5e1a3b92b54c55fb111286f4c4e2a4b374`; 1,168.4 MiB in the same image store. Change: **+22.0%**. [Baseline measurement](https://github.com/xormania/docker-image-library/actions/runs/37852642503); 2026-10-08T22:27:17.513207Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
