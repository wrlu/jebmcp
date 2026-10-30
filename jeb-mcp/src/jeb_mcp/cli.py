#!/usr/bin/env python3
"""jeb — CLI client for the JEB Pro MCP plugin (jeb-daemon).

This speaks the same JSON-RPC protocol as the existing MCP wrapper
(server.py -> POST http://127.0.0.1:16161/mcp), so the MCP architecture keeps
working unchanged. The CLI is the interface used by the jeb-hub-skill.

Examples:
  jeb ping
  jeb search-manifest /path/app.apk 'exported="true"'
  jeb exported-activities /path/app.apk
  jeb decompile /path/app.apk 'Lcom/foo/A;->bar(I)V'
  jeb method-callers /path/app.apk 'Lcom/foo/A;->bar(I)V'
  jeb strings /path/app.apk '^https?://' --limit 50
  jeb exec-python --file script.py
  jeb call get_class_methods /path/app.apk 'Lcom/foo/A;'
"""

from __future__ import annotations

import argparse
import http.client
import json
import os
import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple

DEFAULT_HOST = os.getenv("JEB_MCP_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.getenv("JEB_MCP_PORT", "16161"))
DEFAULT_TIMEOUT = float(os.getenv("JEB_MCP_TIMEOUT", "60"))


class CliError(Exception):
    """User-facing CLI/RPC failure."""


# --------------------------------------------------------------------------- #
# JSON-RPC client (same protocol as server.py)
# --------------------------------------------------------------------------- #

def rpc(method: str, *params: Any, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT,
        timeout: float = DEFAULT_TIMEOUT) -> Any:
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": list(params),
        "id": 1,
    }
    conn = http.client.HTTPConnection(host, port, timeout=timeout)
    try:
        conn.request(
            "POST",
            "/mcp",
            json.dumps(payload),
            {"Content-Type": "application/json"},
        )
        response = conn.getresponse()
        raw = response.read().decode("utf-8", "replace")
    except OSError as exc:
        raise CliError(
            f"cannot reach JEB daemon at {host}:{port}: {exc}\n"
            "Start it in JEB: Edit -> Scripts -> MCP "
            "(Ctrl+Option+M on macOS, Ctrl+Alt+M on other platforms)."
        ) from exc
    finally:
        conn.close()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CliError(f"invalid JSON-RPC response from JEB: {raw[:500]}") from exc

    if not isinstance(data, dict):
        raise CliError(f"unexpected JSON-RPC response: {raw[:500]}")

    if "error" in data:
        error = data["error"] or {}
        message = error.get("message", "unknown error")
        code = error.get("code")
        if code == -1:
            raise CliError(str(message))
        detail = f"JSON-RPC error {code}: {message}"
        if error.get("data"):
            detail += "\n" + str(error["data"])
        raise CliError(detail)

    return data.get("result")


# --------------------------------------------------------------------------- #
# Command table
# --------------------------------------------------------------------------- #
# (cli name, rpc method, positional argument names, optional arguments)
# optional argument: (flag, dest, type, default, help)
Spec = Tuple[str, str, List[str], List[Tuple[str, str, type, Any, str]]]

SPECS: List[Spec] = [
    ("search-manifest", "search_manifest",
     ["filepath", "regex_pattern"], []),
    ("search-assets", "search_assets",
     ["filepath", "regex_pattern"],
     [("--limit", "limit", int, 100, "max files with matches; 0 = no limit")]),
    ("exported-activities", "get_all_exported_activities", ["filepath"], []),
    ("exported-services", "get_all_exported_services", ["filepath"], []),
    ("exported-receivers", "get_all_exported_receivers", ["filepath"], []),
    ("exported-providers", "get_all_exported_providers", ["filepath"], []),
    ("permissions", "get_permissions", ["filepath"], []),
    ("use-permissions", "get_use_permissions", ["filepath"], []),
    ("decompile", "get_method_decompiled_code",
     ["filepath", "method_signature"], []),
    ("smali", "get_method_smali_code",
     ["filepath", "method_signature"], []),
    ("method-callers", "get_method_callers",
     ["filepath", "method_signature"], []),
    ("field-callers", "get_field_callers",
     ["filepath", "field_signature"], []),
    ("method-overrides", "get_method_overrides",
     ["filepath", "method_signature"], []),
    ("superclass", "get_superclass", ["filepath", "class_signature"], []),
    ("interfaces", "get_interfaces", ["filepath", "class_signature"], []),
    ("class-methods", "get_class_methods", ["filepath", "class_signature"], []),
    ("class-fields", "get_class_fields", ["filepath", "class_signature"], []),
    ("rename-class", "rename_class_name",
     ["filepath", "class_signature", "new_class_name"], []),
    ("rename-method", "rename_method_name",
     ["filepath", "class_signature", "method_signature", "new_method_name"], []),
    ("rename-field", "rename_class_field",
     ["filepath", "class_signature", "field_signature", "new_field_name"], []),
    ("check-identifier", "check_java_identifier",
     ["filepath", "identifier"], []),
    ("strings", "get_strings",
     ["filepath", "regex_pattern"],
     [("--limit", "limit", int, 100, "max strings; 0 = no limit")]),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jeb",
        description="CLI client for the JEB Pro MCP plugin (jeb-daemon).",
    )
    parser.add_argument("--host", default=DEFAULT_HOST, help="daemon host")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="daemon port")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT,
                        help="request timeout in seconds")
    parser.add_argument("--json", action="store_true",
                        help="always emit JSON (even for string results)")
    parser.add_argument("--compact", action="store_true", help="compact JSON output")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("ping", help="check daemon connectivity")
    sub.add_parser("check-connection", help="alias for ping")

    for cli_name, _method, positionals, options in SPECS:
        command = sub.add_parser(cli_name)
        for name in positionals:
            command.add_argument(name)
        for flag, dest, value_type, default, help_text in options:
            command.add_argument(flag, dest=dest, type=value_type,
                                 default=default, help=help_text)

    exec_parser = sub.add_parser(
        "exec-python",
        help="execute arbitrary Python (Jython 2.7) inside JEB",
    )
    source = exec_parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--code", help="inline Python code")
    source.add_argument("--file", help="read code from a file ('-' for stdin)")

    call_parser = sub.add_parser(
        "call",
        help="call any JSON-RPC method directly (escape hatch for new methods)",
    )
    call_parser.add_argument("method", help="JSON-RPC method name")
    call_parser.add_argument(
        "params", nargs="*",
        help="JSON literal when parseable, otherwise passed as a string",
    )

    return parser


def emit(result: Any, force_json: bool, compact: bool) -> None:
    if isinstance(result, str) and not force_json:
        sys.stdout.write(result)
        if not result.endswith("\n"):
            sys.stdout.write("\n")
        return
    print(json.dumps(result, ensure_ascii=False,
                     indent=None if compact else 2,
                     separators=(",", ":") if compact else None))


def parse_param(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def read_python_source(args: argparse.Namespace) -> str:
    if args.code is not None:
        return args.code
    if args.file == "-":
        return sys.stdin.read()
    try:
        with open(args.file, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError as exc:
        raise CliError(f"cannot read {args.file}: {exc}") from exc


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    common: Dict[str, Any] = {
        "host": args.host,
        "port": args.port,
        "timeout": args.timeout,
    }

    try:
        if args.command in ("ping", "check-connection"):
            rpc("ping", **common)
            print("Successfully connected to JEB Pro")
            return 0

        if args.command == "exec-python":
            result = rpc("execute_python_code", read_python_source(args), **common)
        elif args.command == "call":
            result = rpc(args.method, *[parse_param(item) for item in args.params],
                         **common)
        else:
            _cli_name, method, positionals, options = next(
                spec for spec in SPECS if spec[0] == args.command)
            params: List[Any] = [getattr(args, name) for name in positionals]
            params.extend(getattr(args, dest) for _flag, dest, *_ in options)
            result = rpc(method, *params, **common)
    except CliError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    emit(result, force_json=args.json, compact=args.compact)
    return 0


if __name__ == "__main__":
    sys.exit(main())
