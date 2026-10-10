"""Narrow compatibility adapters for the pinned Serena/PHPactor pair."""
import json
import re

PHPACTOR_CONFIG = {
    "language_server_configuration.auto_config": False,
    "language_server_phpstan.enabled": False,
    "language_server_psalm.enabled": False,
    "language_server_php_cs_fixer.enabled": False,
}


def install(request_timeout):
    from solidlsp.language_servers.phpactor import PhpactorServer
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
