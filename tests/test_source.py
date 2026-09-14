import json
from pathlib import Path

import pytest

from blackboard_mcp.source import BlackboardExport, ExportError


@pytest.fixture
def export_path(tmp_path: Path) -> Path:
    path = tmp_path / "blackboard-export.json"
    path.write_text(json.dumps({
        "schema_version": 1,
        "exported_at": "2026-09-13T15:00:00Z",
        "source": "Trinity College Dublin Blackboard Ultra",
        "courses": [{"id": "course-1", "title": "CS101", "url": "https://tcd.blackboard.com/ultra/courses/course-1"}],
        "work_items": [
            {"title": "Problem set", "course": "CS101", "due_at": "2026-09-20T17:00:00+01:00", "url": "https://example.test/work", "details": "Submit online"},
            {"title": "Essay", "course": "History", "due_at": "", "url": "", "details": "Date to be confirmed"},
        ],
        "announcements": [{"title": "Read chapter 2", "course": "CS101", "posted_at": "2026-09-12T10:00:00Z", "body": "Before Tuesday", "url": "https://example.test/announcement"}],
    }), encoding="utf-8")
    return path


def test_reads_and_filters_export(export_path: Path) -> None:
    source = BlackboardExport(export_path)
    assert source.status()["courses"] == 1
    assert [course.title for course in source.courses()] == ["CS101"]
    assert [item.title for item in source.work_items("cs101")] == ["Problem set"]
    assert [item.title for item in source.announcements("CS101")] == ["Read chapter 2"]


def test_weekly_briefing_keeps_ambiguous_dates_visible(export_path: Path) -> None:
    briefing = BlackboardExport(export_path).weekly_briefing()
    assert briefing["work_items"][0]["title"] == "Problem set"
    assert any(item["title"] == "Essay" and not item["due_at"] for item in briefing["work_items"])


def test_missing_export_has_actionable_error(tmp_path: Path) -> None:
    with pytest.raises(ExportError, match="Run scripts/export_blackboard.js"):
        BlackboardExport(tmp_path / "missing.json").status()
