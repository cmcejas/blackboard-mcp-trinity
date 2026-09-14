from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Course:
    id: str
    title: str
    url: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class WorkItem:
    title: str
    course: str
    due_at: str = ""
    url: str = ""
    details: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class Announcement:
    title: str
    course: str
    posted_at: str = ""
    body: str = ""
    url: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)
