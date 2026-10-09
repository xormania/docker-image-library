#!/usr/bin/env python3
"""Sanitize host proxy variables before launching container orchestration."""
import ipaddress
import os
import sys
from urllib.parse import urlsplit


def sanitize(env):
    mode = env.get("PROXY_PASSTHROUGH", "auto")
    if mode not in ("auto", "0", "1"):
        raise ValueError("PROXY_PASSTHROUGH must be auto, 0 (disable), or 1 (forward unchanged)")
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"):
        value = env.get(key, "")
        loopback = False
        if value:
            try:
                host = urlsplit(value if "://" in value else "http://" + value).hostname
                loopback = host and host.rstrip(".").lower() == "localhost"
                try:
                    address = ipaddress.ip_address(host or "")
                    loopback = loopback or address.is_loopback or (address.version == 6 and address.ipv4_mapped and address.ipv4_mapped.is_loopback)
                except ValueError:
                    pass
            except ValueError as error:
                raise ValueError(f"Invalid {key} URL") from error
        if mode == "0" or (mode == "auto" and loopback):
            env[key] = ""
            if value:
                print(f"Ignoring {key}: {'disabled' if mode == '0' else 'loopback proxy is local to the host'}", file=sys.stderr)
    return env


if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            raise ValueError("Usage: network.py COMMAND [ARGS...]")
        os.execvpe(sys.argv[1], sys.argv[1:], sanitize(dict(os.environ)))
    except (ValueError, OSError) as error:
        print(f"xorder network: {error}", file=sys.stderr)
        sys.exit(64)
