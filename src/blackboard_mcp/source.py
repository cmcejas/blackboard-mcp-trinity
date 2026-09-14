from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import Announcement, Course, WorkItem


class ExportError(ValueError):
    """The local Blackboard export is missing or malformed."""


def default_export_path() -> Path:
    configured = os.environ.get("BLACKBOARD_EXPORT_PATH")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".hermes" / "blackboard-mcp" / "blackboard-export.json"


class BlackboardExport:
    """Strictly local, read-only view over a browser-produced JSON export."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_export_path()

    def _payload(self) -> dict[str, Any]:
        if not self.path.is_file():
            raise ExportError(
                f"No Blackboard export at {self.path}. Run scripts/export_blackboard.js "
                "from a signed-in Blackboard page, then save the resulting JSON there."
            )
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ExportError(f"Invalid Blackboard export JSON: {exc.msg}") from exc
        if payload.get("schema_version") != 1:
            raise ExportError("Unsupported or missing Blackboard export schema_version.")
        return payload

    def status(self) -> dict[str, str | int]:
        payload = self._payload()
        return {
            "path": str(self.path),
            "exported_at": str(payload.get("exported_at", "")),
            "courses": len(payload.get("courses", [])),
            "work_items": len(payload.get("work_items", [])),
            "announcements": len(payload.get("announcements", [])),
        }

    def courses(self) -> list[Course]:
        return [Course(**row) for row in self._payload().get("courses", [])]

    def work_items(self, course: str | None = None) -> list[WorkItem]:
        rows = [WorkItem(**row) for row in self._payload().get("work_items", [])]
        if course:
            needle = course.casefold()
            rows = [row for row in rows if needle in row.course.casefold()]
        return sorted(rows, key=lambda row: row.due_at or "9999-12-31")

    def announcements(self, course: str | None = None) -> list[Announcement]:
        rows = [Announcement(**row) for row in self._payload().get("announcements", [])]
        if course:
            needle = course.casefold()
            rows = [row for row in rows if needle in row.course.casefold()]
        return sorted(rows, key=lambda row: row.posted_at or "", reverse=True)

    def weekly_briefing(self) -> dict[str, Any]:
        status = self.status()
        return {
            "generated_at": datetime.now(UTC).isoformat(),
            "export": status,
            "work_items": [item.to_dict() for item in self.work_items()],
            "announcements": [item.to_dict() for item in self.announcements()],
            "note": "This is a read-only local export. Dates without normalized ISO timestamps require manual review.",
        }
