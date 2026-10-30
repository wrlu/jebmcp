---
name: jeb-hub
description: Use when analyzing APKs, JARs or DEX files with JEB Pro via the jeb-daemon. Triggers on JEB, decompilation, smali, Android manifest/components, exported activities/services/providers/receivers, permissions, method/field xrefs and callers, hardcoded strings, APK assets, rename refactoring, or running Jython inside JEB.
version: "1.0"
tags: [jeb-pro, android, apk, decompile, reverse-engineering]
---

# JEB Hub Skill

`jeb` is a CLI client that speaks the same JSON-RPC protocol as the existing
JEB MCP server. The **jeb-daemon (the MCP plugin running inside JEB) is
unchanged**; the MCP tools remain available. Use the CLI when you want a
shell-driven workflow, reproducible commands, or JSON output.

- Daemon endpoint: `http://127.0.0.1:16161/mcp` (JSON-RPC 2.0)
- Host/port/timeout override: `JEB_MCP_HOST`, `JEB_MCP_PORT`, `JEB_MCP_TIMEOUT`
- CLI source: `src/jeb_mcp/cli.py`

## When to Use

- User mentions JEB, APK/JAR/DEX analysis, decompilation, smali
- Need exported components, permissions, manifest or asset search
- Need method decompiled code, callers/xrefs, overrides, class hierarchy
- Need hardcoded strings, assets, or rename refactoring
- Need to run custom Jython 2.7 inside JEB

## When NOT to Use

- Analysis with IDA / Ghidra / Binary Ninja only
- The target is not an APK/JAR/DEX opened by JEB
- Pure static text processing that does not need JEB

## Setup

The daemon runs inside JEB. Start it once per JEB session:

> JEB menu: **Edit -> Scripts -> MCP**
> macOS: `Ctrl+Option+M`; other platforms: `Ctrl+Alt+M`

Then verify connectivity:

```bash
jeb ping
```

`jeb` is a symlink to `skills/jeb-hub/scripts/jeb` installed on `PATH`
(e.g. `~/.local/bin/jeb`). `ping` prints `Successfully connected to JEB Pro`
on success. If it fails, ask the user to start the MCP server in JEB; do not
retry blindly.

## Output

- String results (decompiled code, smali, exec-python output) are printed raw.
- Structured results are printed as pretty JSON.
- `--json` forces JSON for string results; `--compact` emits single-line JSON.
- `filepath` arguments must be absolute paths.

## Quick Start

```bash
jeb ping
jeb exported-activities /path/app.apk
jeb exported-services   /path/app.apk
jeb permissions         /path/app.apk
jeb search-manifest     /path/app.apk 'exported="true"'
jeb decompile           /path/app.apk 'Lcom/foo/A;->bar(I)V'
jeb method-callers      /path/app.apk 'Lcom/foo/A;->bar(I)V'
jeb strings             /path/app.apk '^https?://' --limit 50
jeb exec-python --file /tmp/probe.py
```

## Commands

| Command | Purpose |
|---|---|
| `ping` / `check-connection` | Check daemon connectivity |
| `search-manifest <apk> <regex>` | Search AndroidManifest (64-char context) |
| `search-assets <apk> <regex> [--limit N]` | Search files under `assets/` |
| `exported-activities <apk>` | Exported activities |
| `exported-services <apk>` | Exported services |
| `exported-receivers <apk>` | Exported receivers |
| `exported-providers <apk>` | Exported providers |
| `permissions <apk>` | Custom permissions defined by the app |
| `use-permissions <apk>` | Permissions requested by the app |
| `decompile <apk> <method_sig>` | Decompiled Java code |
| `smali <apk> <method_sig>` | Smali code |
| `method-callers <apk> <method_sig>` | Callers of a method |
| `field-callers <apk> <field_sig>` | Callers of a field |
| `method-overrides <apk> <method_sig>` | Overrides of a method |
| `superclass <apk> <class_sig>` | Superclass |
| `interfaces <apk> <class_sig>` | Implemented interfaces |
| `class-methods <apk> <class_sig>` | Declared methods |
| `class-fields <apk> <class_sig>` | Declared fields |
| `rename-class <apk> <class_sig> <new_name>` | Rename a class |
| `rename-method <apk> <class_sig> <method_sig> <new_name>` | Rename a method |
| `rename-field <apk> <class_sig> <field_sig> <new_name>` | Rename a field |
| `check-identifier <apk> <identifier>` | Resolve identifier kind (class/type/method/field) |
| `strings <apk> <regex> [--limit N]` | Hardcoded strings with xrefs |
| `exec-python --code C / --file F` | Run Python (Jython 2.7) inside JEB |
| `call <rpc_method> [args...]` | Call any JSON-RPC method directly |

## Signature Formats

DEX/Java internal names:

- Class: `Lcom/example/Foo;`
- Method: `Lcom/example/Foo;->bar(I[JLjava/lang/String;)V`
- Field: `Lcom/example/Foo;->flag1:Z`

## Workflows

### 1. APK triage

1. `exported-activities`, `exported-services`, `exported-providers`, `exported-receivers`
2. `permissions` and `use-permissions`
3. `search-manifest` for custom schemes, hosts, or exported flags

### 2. Decompile and pivot

1. `check-identifier <apk> <identifier>` to confirm what the identifier is
2. `decompile <apk> <method_sig>`
3. `method-callers` / `field-callers` to find entry points
4. `class-methods` / `superclass` / `interfaces` for the surrounding type

### 3. Strings and assets

- `strings <apk> '<regex>' --limit N` (0 = no limit)
- `search-assets <apk> '<regex>' --limit N`; binary matches are hex-encoded

### 4. Rename refactoring

`rename-class`, `rename-method`, `rename-field` mutate JEB state. Confirm the
target signature and new name with the user before running them.

### 5. Custom Jython

`exec-python` runs Python 2.7 inside JEB with the global `CTX` context. Prefer
`--file` (or `--file -` with stdin) over inline `--code` to avoid shell quoting
issues and preserve indentation.

## Error Handling

- `cannot reach JEB daemon ...` — the MCP plugin is not running. Ask the user
  to start it via **Edit -> Scripts -> MCP**, then retry `ping`.
- `JSON-RPC error ...` — the daemon rejected the request (bad path, signature,
  or unsupported operation). Report the message; do not guess a new signature.
- Executing Python in JEB is powerful; avoid destructive changes unless the
  user explicitly requests them.

## Relation to MCP

The daemon and `src/jeb_mcp/MCP.py` are unchanged. The existing MCP tools
(`jeb_*`) and this CLI are two front-ends to the same daemon; using one does
not disable the other.
