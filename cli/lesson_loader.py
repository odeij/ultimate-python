"""Discovers and parses lessons from the lessons/ directory.

Lesson layout on disk:
  lessons/<topic>/<slug>/
    lesson.yaml      — metadata + exercises (inline YAML)
    theory.md        — theory content, split by ## headings
    exercises/
      q3_starter.py  — starter code handed to the user
      q3_tests.py    — test functions (TEST_CASES list)

The loader is the only place that knows about the on-disk format.
Everything above this layer works with cli.models types only.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import yaml

from cli.models import (
    CodeExercise,
    Exercise,
    Lesson,
    LessonSection,
    MultipleChoiceExercise,
    ShortAnswerExercise,
)


class LessonLoader:
    """Discovers and loads all lessons under a root directory."""

    def __init__(self, lessons_dir: Path) -> None:
        self.lessons_dir = lessons_dir
        self._cache: dict[str, Lesson] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_all(self) -> list[Lesson]:
        """Return all lessons sorted by (month, week)."""
        lessons: list[Lesson] = []
        for yaml_path in sorted(self.lessons_dir.glob("**/lesson.yaml")):
            try:
                lesson = self._load_from_dir(yaml_path.parent)
                lessons.append(lesson)
            except Exception as exc:
                # Don't crash the whole app if one lesson is malformed
                print(f"  [warning] Could not load lesson at {yaml_path}: {exc}")
        return sorted(lessons, key=lambda l: (l.month, l.week))

    def get_by_slug(self, slug: str, lessons: list[Lesson]) -> Optional[Lesson]:
        for lesson in lessons:
            if lesson.slug == slug:
                return lesson
        return None

    def get_topics(self, lessons: list[Lesson]) -> list[str]:
        seen: list[str] = []
        for lesson in lessons:
            if lesson.topic not in seen:
                seen.append(lesson.topic)
        return seen

    def get_by_topic(self, topic: str, lessons: list[Lesson]) -> list[Lesson]:
        return [l for l in lessons if l.topic == topic]

    def get_months(self, lessons: list[Lesson]) -> list[int]:
        return sorted({l.month for l in lessons})

    def get_by_month(self, month: int, lessons: list[Lesson]) -> list[Lesson]:
        return [l for l in lessons if l.month == month]

    # ------------------------------------------------------------------
    # Internal loading
    # ------------------------------------------------------------------

    def _load_from_dir(self, lesson_dir: Path) -> Lesson:
        """Parse a single lesson directory into a Lesson model."""
        slug = lesson_dir.name
        if slug in self._cache:
            return self._cache[slug]

        raw = yaml.safe_load((lesson_dir / "lesson.yaml").read_text())

        theory_file = lesson_dir / raw.get("theory_file", "theory.md")
        sections = _parse_theory_md(theory_file) if theory_file.exists() else []

        exercises: list[Exercise] = [
            _parse_exercise(ex_data, lesson_dir)
            for ex_data in raw.get("exercises", [])
        ]

        lesson = Lesson(
            slug=raw["slug"],
            title=raw["title"],
            topic=raw["topic"],
            month=int(raw.get("month", 1)),
            week=int(raw.get("week", 1)),
            difficulty=raw.get("difficulty", "easy"),
            prerequisites=raw.get("prerequisites", []),
            next_lesson=raw.get("next_lesson"),
            sections=sections,
            exercises=exercises,
            estimated_minutes=int(raw.get("estimated_minutes", 20)),
            path=lesson_dir,
        )
        self._cache[slug] = lesson
        return lesson


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def _parse_theory_md(path: Path) -> list[LessonSection]:
    """Split a Markdown file on ## headings → list[LessonSection]."""
    text = path.read_text()
    # Split on lines that start with exactly "## "
    parts = re.split(r"^## (.+)$", text, flags=re.MULTILINE)
    # parts = [preamble, heading1, body1, heading2, body2, ...]
    sections: list[LessonSection] = []
    i = 1
    while i + 1 <= len(parts) - 1:
        heading = parts[i].strip()
        body    = parts[i + 1].strip()
        if heading:
            sections.append(LessonSection(heading=heading, body=body))
        i += 2
    return sections


def _parse_exercise(data: dict, lesson_dir: Path) -> Exercise:
    """Dispatch to the correct Exercise dataclass based on 'type'."""
    ex_type = data["type"]

    if ex_type == "multiple_choice":
        return MultipleChoiceExercise(
            id=data["id"],
            question=data["question"],
            options=data["options"],
            correct=int(data["correct"]),
            explanation=data["explanation"],
        )

    if ex_type == "short_answer":
        return ShortAnswerExercise(
            id=data["id"],
            question=data["question"],
            # Normalise accepted answers once at load time
            accepted=[str(a).lower().strip() for a in data["accepted"]],
            explanation=data["explanation"],
        )

    if ex_type == "code":
        return CodeExercise(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            starter_path=lesson_dir / data["starter_file"],
            test_path=lesson_dir / data["test_file"],
            hint=data.get("hint", ""),
        )

    raise ValueError(f"Unknown exercise type: {ex_type!r}")
