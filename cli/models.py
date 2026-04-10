"""Pure data types for lessons and exercises.

No I/O, no display, no business logic — just shapes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Union, Optional


# ---------------------------------------------------------------------------
# Exercise variants
# ---------------------------------------------------------------------------

@dataclass
class MultipleChoiceExercise:
    """A question with lettered options and a single correct answer."""
    id: str
    question: str
    options: list[str]
    correct: int          # 0-indexed
    explanation: str


@dataclass
class ShortAnswerExercise:
    """A free-text question graded against a list of acceptable answers."""
    id: str
    question: str
    accepted: list[str]   # pre-normalised (strip + lower) in lesson_loader
    explanation: str


@dataclass
class CodeExercise:
    """A coding challenge backed by an automated test suite."""
    id: str
    title: str
    description: str      # shown to the user (Markdown)
    starter_path: Path    # canonical starter in lessons/
    test_path: Path       # test functions file
    hint: str = ""


# Union type used in type annotations throughout the codebase
Exercise = Union[MultipleChoiceExercise, ShortAnswerExercise, CodeExercise]


class QuitLesson(Exception):
    """Raised from anywhere inside an exercise to exit back to the lesson runner.

    Progress written to disk before this is raised is preserved — the exception
    is purely a control-flow signal, not an error.
    """


# ---------------------------------------------------------------------------
# Lesson structure
# ---------------------------------------------------------------------------

@dataclass
class LessonSection:
    """One ## heading + its body text (Markdown)."""
    heading: str
    body: str


@dataclass
class Lesson:
    """A complete lesson: metadata + content + exercises."""
    slug: str
    title: str
    topic: str
    month: int
    week: int
    difficulty: str       # "easy" | "medium" | "hard"
    prerequisites: list[str]
    next_lesson: Optional[str]
    sections: list[LessonSection]
    exercises: list[Exercise]
    estimated_minutes: int
    path: Path            # absolute path to the lesson directory
