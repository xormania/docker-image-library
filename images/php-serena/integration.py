"""Narrow compatibility adapters for the pinned Serena/PHPactor pair."""
import json
import os
import re
from contextlib import ExitStack
from pathlib import Path

PHPACTOR_CONFIG = {
    "language_server_configuration.auto_config": False,
    "language_server_phpstan.enabled": False,
    "language_server_psalm.enabled": False,
    "language_server_php_cs_fixer.enabled": False,
}


def install(request_timeout):
    from solidlsp.language_servers.phpactor import PhpactorServer
    from solidlsp.language_servers.typescript_language_server import TypeScriptLanguageServer
    from solidlsp.ls_process import LanguageServerInterface, StdioLanguageServer

    base_initialize = PhpactorServer._create_base_initialize_params
    def initialize(self):
        params = base_initialize(self)
        params.setdefault("initializationOptions", {}).update(PHPACTOR_CONFIG)
        return params
    PhpactorServer._create_base_initialize_params = initialize
    PhpactorServer.DependencyProvider._create_launch_command = lambda self, core: [
        "php", core, "language-server", "--config-extra", json.dumps(PHPACTOR_CONFIG)]

    set_timeout = LanguageServerInterface.set_request_timeout
    LanguageServerInterface.set_request_timeout = lambda self, timeout: set_timeout(self, request_timeout)
    send = StdioLanguageServer.send_request
    def checked_send(self, method, params=None):
        if not self.is_running():
            raise RuntimeError("Language server not running; use s.lsp.restart_language_server() "
                               "or restart the Serena session before querying again")
        return send(self, method, params)
    StdioLanguageServer.send_request = checked_send

    language_id = TypeScriptLanguageServer._get_language_id_for_file
    def source_language(self, path):
        if path.endswith((".js", ".mjs", ".cjs")):
            return "javascript"
        return language_id(self, path)
    TypeScriptLanguageServer._get_language_id_for_file = source_language

    references = TypeScriptLanguageServer._send_references_request
    def workspace_references(self, path, line, column):
        # AssetMapper projects often have no jsconfig/tsconfig. tsserver's
        # inferred project knows opened files and forward imports, so unopened
        # consumers otherwise silently disappear from reverse references.
        # Hold eligible source buffers open until the reference request finishes;
        # never create configuration in the mounted checkout.
        with ExitStack() as opened:
            root = Path(self.repository_root_path)
            for directory, dirs, files in os.walk(root):
                parent = Path(directory)
                dirs[:] = sorted(name for name in dirs if not self.is_ignored_path(
                    (parent / name).relative_to(root).as_posix(), ignore_unsupported_files=False))
                for name in sorted(files):
                    relative = (parent / name).relative_to(root).as_posix()
                    if not self.is_ignored_path(relative):
                        opened.enter_context(self.open_file(relative))
            return references(self, path, line, column)
    TypeScriptLanguageServer._send_references_request = workspace_references


def enrich(reply):
    """Expose session identity and REPL execution errors without changing content."""
    result = reply.get("result")
    if not isinstance(result, dict) or "content" not in result:
        return reply
    text = "\n".join(item.get("text", "") for item in result["content"] if item.get("type") == "text")
    session = re.search(r"Your Serena session id is `([^`]+)`", text)
    if session:
        result.setdefault("structuredContent", {}).update(session_id=session.group(1))
    if re.match(r"^(?:[\w.]*Error|[\w.]*Exception):", text):
        result["isError"] = True
    return reply
