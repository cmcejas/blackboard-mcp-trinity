from __future__ import annotations

import argparse
import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from .source import BlackboardExport, ExportError

mcp = FastMCP("trinity-blackboard", instructions=(
    "Private, read-only assistant for Trinity College Dublin Blackboard Ultra. "
    "Never create, submit, edit, or delete Blackboard content. Treat the exported Blackboard page as the source of truth and flag ambiguous due dates."
))


def _call(operation: str, course: str | None = None) -> Any:
    source = BlackboardExport()
    try:
        if operation == "status":
            return source.status()
        if operation == "courses":
            return [course_item.to_dict() for course_item in source.courses()]
        if operation == "work_items":
            return [item.to_dict() for item in source.work_items(course)]
        if operation == "announcements":
            return [item.to_dict() for item in source.announcements(course)]
        return source.weekly_briefing()
    except ExportError as exc:
        return {"error": str(exc)}


@mcp.tool()
def blackboard_status() -> dict[str, Any]:
    """Confirm that the private local Blackboard export is available and current."""
    return _call("status")


@mcp.tool()
def list_courses() -> list[dict[str, str]] | dict[str, str]:
    """List courses visible in Carlos's latest Blackboard export."""
    return _call("courses")


@mcp.tool()
def list_work_items(course: str | None = None) -> list[dict[str, str]] | dict[str, str]:
    """List upcoming or mentioned work items, optionally filtering by course name."""
    return _call("work_items", course)


@mcp.tool()
def list_announcements(course: str | None = None) -> list[dict[str, str]] | dict[str, str]:
    """List lecturer announcements, optionally filtering by course name."""
    return _call("announcements", course)


@mcp.tool()
def weekly_worklist() -> dict[str, Any]:
    """Return a read-only digest of work items and announcements from Blackboard."""
    return _call("briefing")


def main() -> None:
    parser = argparse.ArgumentParser(description="Trinity Blackboard read-only MCP")
    parser.add_argument("--check-export", action="store_true", help="Validate and print local export status")
    args = parser.parse_args()
    if args.check_export:
        print(json.dumps(_call("status"), indent=2))
        return
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
