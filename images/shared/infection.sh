#!/usr/bin/env bash
set -euo pipefail
# The image supplies Infection; the consumer supplies PHPUnit and configuration.
# Xdebug activation is inherited by Infection's initial PHPUnit subprocess.
exec library-php-coverage xdebug /opt/xorder/infection/infection.phar "$@"
