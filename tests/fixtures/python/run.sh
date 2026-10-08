#!/usr/bin/env bash
set -euo pipefail
uv sync --locked
uv run --locked python -m image_library_fixture
python -m venv /tmp/fixture-venv
/tmp/fixture-venv/bin/python -m pip --version
