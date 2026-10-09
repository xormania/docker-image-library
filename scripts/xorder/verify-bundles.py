#!/usr/bin/env python3
"""Check the declared portable payloads after packaging and download."""

import configparser
import pathlib
import sys


def verify_editorconfig(root):
    payload = (root / "editorconfig").read_text(encoding="utf-8")
    # EditorConfig has top-level root before INI sections; parse that separately.
    preamble, sections = payload.split("[*]", 1)
    settings = configparser.ConfigParser(interpolation=None)
    settings.read_string("[root]\n" + preamble + "\n[*]" + sections)
    if not settings.getboolean("root", "root"):
        raise ValueError("EditorConfig must stop inherited parent settings")
    expected = {
        "charset": "utf-8",
        "end_of_line": "lf",
        "insert_final_newline": "true",
        "indent_style": "space",
        "indent_size": "4",
    }
    if any(settings["*"][key] != value for key, value in expected.items()):
        raise ValueError("Unexpected PHP/text formatting defaults")
    if settings["*.{json,yaml,yml}"]["indent_size"] != "2":
        raise ValueError("Structured files must use the advertised two-space indent")
    if settings.getboolean("*.md", "trim_trailing_whitespace"):
        raise ValueError("Markdown hard-break whitespace must be preserved")
    if settings["Makefile"]["indent_style"] != "tab":
        raise ValueError("Makefile recipes need tabs")


def verify_context(root):
    payload = (root / "project-guidance.md").read_text(encoding="utf-8")
    if not payload.startswith("# Project guidance (example)\n"):
        raise ValueError("Context must identify itself as an example")
    if "Current owner instructions govern the task." not in payload:
        raise ValueError("Example context must retain owner authority")
    if "not a statement of xor's\npersonal philosophy" not in payload:
        raise ValueError("Example context must not impersonate xor's philosophy")
    if len(payload.encode("utf-8")) >= 32 * 1024:
        raise ValueError("Example exceeds the documented default Codex guidance budget")


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: verify-bundles.py RESOURCE_ID EXTRACTED_DIRECTORY")
    verifiers = {
        "configuration/editorconfig": verify_editorconfig,
        "context/project-guidance": verify_context,
    }
    try:
        verifier = verifiers[sys.argv[1]]
        verifier(pathlib.Path(sys.argv[2]))
    except (KeyError, ValueError, OSError, configparser.Error) as error:
        raise SystemExit(f"Bundle verification failed: {error}") from error
    print(f"Verified {sys.argv[1]} payload and advertised scope")


if __name__ == "__main__":
    main()
