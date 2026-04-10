"""JSON-backed progress persistence.

Stored at .progress/progress.json (gitignored).  One flat dict:

{
  "lessons": {
    "variables": {
      "started_at":  "2024-01-01T10:00:00+00:00",
      "completed_at": null,
      "exercises_completed": ["q1", "q2"],
      "attempts": {"q3": 3}
    }
  },
  "last_lesson": "variables",
  "last_updated": "2024-01-01T10:05:00+00:00"
}
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from cli.models import Lesson


class ProgressTracker:
    """All read/write access to progress state goes through this class."""

    def __init__(self, progress_file: Path):
        self._file = progress_file
        self._data = self._load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self) -> dict:
        if self._file.exists():
            try:
                return json.loads(self._file.read_text())
            except (json.JSONDecodeError, OSError):
                pass
        return self._empty_state()

    def _empty_state(self) -> dict:
        return {"lessons": {}, "last_lesson": None, "last_updated": None}

    def _save(self) -> None:
        self._file.parent.mkdir(parents=True, exist_ok=True)
        self._data["last_updated"] = _utc_now()
        self._file.write_text(json.dumps(self._data, indent=2))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _lesson_record(self, slug: str) -> dict:
        """Return the mutable dict for a lesson, creating it if needed."""
        return self._data["lessons"].setdefault(slug, {
            "started_at": None,
            "completed_at": None,
            "exercises_completed": [],
            "attempts": {},
        })

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def is_lesson_started(self, slug: str) -> bool:
        rec = self._data["lessons"].get(slug, {})
        return bool(rec.get("started_at"))

    def is_lesson_completed(self, slug: str) -> bool:
        rec = self._data["lessons"].get(slug, {})
        return bool(rec.get("completed_at"))

    def is_exercise_completed(self, lesson_slug: str, exercise_id: str) -> bool:
        rec = self._data["lessons"].get(lesson_slug, {})
        return exercise_id in rec.get("exercises_completed", [])

    def get_last_lesson(self) -> Optional[str]:
        return self._data.get("last_lesson")

    def get_stats(self, all_lessons: list["Lesson"]) -> dict:
        total = len(all_lessons)
        completed = sum(1 for l in all_lessons if self.is_lesson_completed(l.slug))
        in_progress = sum(
            1 for l in all_lessons
            if self.is_lesson_started(l.slug) and not self.is_lesson_completed(l.slug)
        )
        not_started = total - completed - in_progress
        pct = round(completed / total * 100) if total > 0 else 0
        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "not_started": not_started,
            "percent": pct,
        }

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------

    def mark_lesson_started(self, slug: str) -> None:
        rec = self._lesson_record(slug)
        if not rec["started_at"]:
            rec["started_at"] = _utc_now()
        self._data["last_lesson"] = slug
        self._save()

    def mark_lesson_completed(self, slug: str) -> None:
        rec = self._lesson_record(slug)
        rec["completed_at"] = _utc_now()
        self._data["last_lesson"] = slug
        self._save()

    def mark_exercise_completed(self, lesson_slug: str, exercise_id: str) -> None:
        rec = self._lesson_record(lesson_slug)
        if exercise_id not in rec["exercises_completed"]:
            rec["exercises_completed"].append(exercise_id)
        self._save()

    def record_attempt(self, lesson_slug: str, exercise_id: str) -> None:
        rec = self._lesson_record(lesson_slug)
        rec["attempts"][exercise_id] = rec["attempts"].get(exercise_id, 0) + 1
        self._save()

    def reset(self) -> None:
        self._data = self._empty_state()
        self._save()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
