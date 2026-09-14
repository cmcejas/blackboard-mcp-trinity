# Trinity Blackboard MCP

A **private, read-only** MCP server for Carlos's Trinity College Dublin Blackboard Ultra data.

It is deliberately not a generic Blackboard integration and does not store a password, create coursework, submit assignments, modify grades, or write to Blackboard. It turns a local export of Carlos's signed-in Blackboard pages into tools for courses, work items, announcements, and a weekly worklist.

## Why local export first

Blackboard's public REST API is intended for institution-registered applications. TCD Blackboard Ultra uses TCD Microsoft SSO. This first version avoids putting credentials into a third-party service or repository: Carlos signs into Blackboard himself, produces a local JSON export, and the MCP reads that local file only.

The page exporter is intentionally the first validation point. Once we have real authenticated TCD Blackboard pages, we can refine the selectors and decide whether a browser-session adapter is reliable enough for automated daily refreshes.

## Setup

```bash
cd blackboard-mcp-trinity
uv venv
uv sync --extra test
```

1. Log in to `https://tcd.blackboard.com/` with your TCD account.
2. On the Blackboard Ultra dashboard and relevant course pages, open DevTools and run the contents of `scripts/export_blackboard.js`.
3. Save the downloaded file outside the repository at:

```text
~/.hermes/blackboard-mcp/blackboard-export.json
```

4. Check it:

```bash
uv run blackboard-mcp-trinity --check-export
```

## Hermes MCP configuration

Add this to `~/.hermes/config.yaml` after installation:

```yaml
mcp_servers:
  trinity_blackboard:
    command: "/absolute/path/to/blackboard-mcp-trinity/.venv/bin/blackboard-mcp-trinity"
    args: []
    timeout: 30
    sampling:
      enabled: false
```

Restart Hermes. The available tools are read-only:

- `blackboard_status`
- `list_courses`
- `list_work_items`
- `list_announcements`
- `weekly_worklist`

## Security

- Never commit Blackboard exports, cookies, passwords, tokens, or session files.
- The export is private academic data. Keep it owner-readable only.
- Treat the Blackboard page as the official source. The MCP summary can miss content until its selectors are checked against real TCD course pages.

## Development

```bash
uv run pytest -q
```

## Current limitation

This has a tested local data path but has **not yet been validated against an authenticated TCD Blackboard course**. That requires Carlos to log in through a browser session available to the development host. No credentials are requested or stored by this project.
