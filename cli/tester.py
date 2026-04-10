"""Checkpoint testing: run code-exercise tests for one or all lessons,
and optionally run the full ultimatepython module suite via runner.py.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from cli.exercise_runner import run_tests

if TYPE_CHECKING:
    from cli.models import Lesson
    from cli.progress import ProgressTracker
    from cli.renderer import Renderer


class Tester:
    """Runs checkpoint tests and displays formatted results."""

    def __init__(
        self,
        renderer: "Renderer",
        progress: "ProgressTracker",
        repo_root: Path,
    ) -> None:
        self.renderer  = renderer
        self.progress  = progress
        self.repo_root = repo_root
        self._workspace = repo_root / "user_workspace" / "solutions"

    # ------------------------------------------------------------------
    # Per-lesson checkpoint
    # ------------------------------------------------------------------

    def run_for_lesson(self, lesson: "Lesson") -> None:
        from cli.models import CodeExercise

        code_exercises = [ex for ex in lesson.exercises if isinstance(ex, CodeExercise)]
        if not code_exercises:
            self.renderer.info(f"No code exercises in '{lesson.title}'.")
            return

        self.renderer.print(f"\n  [bold]Checkpoint: {lesson.title}[/bold]\n")

        any_solution = False
        for ex in code_exercises:
            solution_path = self._workspace / lesson.slug / f"{ex.id}.py"
            if not solution_path.exists():
                self.renderer.warning(
                    f"  {ex.id}: no solution file yet — work through the exercise first."
                )
                continue

            any_solution = True
            self.renderer.print(f"  [bold]{ex.title}[/bold]")
            results = run_tests(ex.test_path, solution_path)
            self.renderer.show_test_results(results)

            if all(p for _, p, _ in results):
                self.progress.mark_exercise_completed(lesson.slug, ex.id)

        if not any_solution:
            self.renderer.info(
                "No solution files found yet. Start the lesson and attempt the exercises."
            )

    # ------------------------------------------------------------------
    # Full module suite (the existing runner.py)
    # ------------------------------------------------------------------

    def run_module_suite(self) -> None:
        """Run runner.py and stream output to the terminal."""
        runner = self.repo_root / "runner.py"
        if not runner.exists():
            self.renderer.error("runner.py not found.")
            return

        self.renderer.print(
            "\n  [bold]Running all ultimatepython module tests (runner.py)...[/bold]\n"
        )
        result = subprocess.run(
            [sys.executable, str(runner)],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )

        if result.stdout:
            self.renderer.print(result.stdout)
        if result.returncode == 0:
            self.renderer.info("All ultimatepython modules passed. ✅")
        else:
            self.renderer.error("Some modules failed.")
            if result.stderr:
                self.renderer.print(f"[dim]{result.stderr[:800]}[/dim]")
