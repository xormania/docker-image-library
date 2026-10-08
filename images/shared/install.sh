#!/usr/bin/env bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends \
  bash ca-certificates curl git gh jq ripgrep unzip zip xz-utils tar \
  build-essential autoconf file re2c pkg-config libssl-dev libpq-dev postgresql-client \
  gosu python3 procps
rm -rf /var/lib/apt/lists/*
groupadd --gid 1000 dev
useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash dev
mkdir -p /workspace /home/dev/.cache /home/dev/.composer /home/dev/.cargo
chown -R dev:dev /workspace /home/dev
