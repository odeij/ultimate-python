"""Runs exercises interactively and records progress.

Three exercise modes:
  MultipleChoiceExercise  — lettered options, single correct answer
  ShortAnswerExercise     — free text graded against normalised list
  CodeExercise            — copy starter → workspace → test against solution

Test protocol for code exercises:
  Each test file exposes TEST_CASES: list[tuple[str, Callable[[Path], None]]]
  where the string is the display name and the callable receives the path to
  the user's solution file.  A raised AssertionError counts as a failure.
  If TEST_CASES is absent the runner falls back to calling every test_* function.
"""
from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cli.models import CodeExercise, Exercise, MultipleChoiceExercise, ShortAnswerExercise
    from cli.progress import ProgressTracker
    from cli.renderer import Renderer

_LETTERS = "ABCDEFGHIJ"
_QUIT_TOKENS = {"q", "quit", "exit", ":q"}   # anything in this set quits the lesson


class ExerciseRunner:
    """Orchestrates the interactive exercise loop."""

    def __init__(
        self,
        renderer: "Renderer",
        progress: "ProgressTracker",
        workspace_root: Path,
    ) -> None:
        self.renderer  = renderer
        self.progress  = progress
        self.workspace = workspace_root

    # ------------------------------------------------------------------
    # Quit helper — replaces bare renderer.wait() calls so that typing
    # 'q' at the "press Enter" prompt also triggers a clean exit.
    # ------------------------------------------------------------------

    def _wait_or_quit(self) -> None:
        """Show a continue prompt that also accepts 'q' to quit the lesson."""
        from cli.models import QuitLesson
        val = self.renderer.prompt(
            "  [dim][Enter] continue  ·  [q] save & quit lesson[/dim]  ❯ "
        )
        if val.lower() in _QUIT_TOKENS:
            raise QuitLesson()

    def run(
        self,
        exercise: "Exercise",
        lesson_slug: str,
        index: int,
        total: int,
    ) -> None:
        from cli.models import CodeExercise, MultipleChoiceExercise, ShortAnswerExercise

        if isinstance(exercise, MultipleChoiceExercise):
            self._run_multiple_choice(exercise, lesson_slug, index, total)
        elif isinstance(exercise, ShortAnswerExercise):
            self._run_short_answer(exercise, lesson_slug, index, total)
        elif isinstance(exercise, CodeExercise):
            self._run_code(exercise, lesson_slug, index, total)

    # ------------------------------------------------------------------
    # Multiple choice
    # ------------------------------------------------------------------

    def _run_multiple_choice(
        self,
        ex: "MultipleChoiceExercise",
        lesson_slug: str,
        index: int,
        total: int,
    ) -> None:
        self.renderer.show_exercise_header(index, total, "multiple_choice")

        already = self.progress.is_exercise_completed(lesson_slug, ex.id)
        if already:
            self.renderer.show_already_completed()

        self.renderer.show_question(ex.question)
        self.renderer.show_options(ex.options)

        from cli.models import QuitLesson

        valid = _LETTERS[: len(ex.options)]
        while True:
            raw = self.renderer.prompt(
                f"  Your answer ({'/'.join(valid)})  [dim]or [q] to quit[/dim]: "
            ).upper()

            if raw.lower() in _QUIT_TOKENS:
                raise QuitLesson()

            if not raw or raw[0] not in valid:
                self.renderer.warning(f"Enter one of: {', '.join(valid)}  (or q to quit)")
                continue

            chosen = _LETTERS.index(raw[0])
            self.progress.record_attempt(lesson_slug, ex.id)

            if chosen == ex.correct:
                self.renderer.show_correct(ex.explanation)
                self.progress.mark_exercise_completed(lesson_slug, ex.id)
                break
            else:
                self.renderer.show_incorrect(ex.explanation)
                retry = self.renderer.prompt("  Try again? [y/n/q]: ").lower()
                if retry in _QUIT_TOKENS:
                    raise QuitLesson()
                if retry == "y":
                    self.renderer.show_question(ex.question)
                    self.renderer.show_options(ex.options)
                    continue
                break

        self._wait_or_quit()

    # ------------------------------------------------------------------
    # Short answer
    # ------------------------------------------------------------------

    def _run_short_answer(
        self,
        ex: "ShortAnswerExercise",
        lesson_slug: str,
        index: int,
        total: int,
    ) -> None:
        self.renderer.show_exercise_header(index, total, "short_answer")

        already = self.progress.is_exercise_completed(lesson_slug, ex.id)
        if already:
            self.renderer.show_already_completed()

        self.renderer.show_question(ex.question)

        from cli.models import QuitLesson

        while True:
            answer = self.renderer.prompt(
                "  Your answer  [dim]or [q] to quit[/dim]: "
            ).strip()

            if answer.lower() in _QUIT_TOKENS:
                raise QuitLesson()

            if not answer:
                continue

            self.progress.record_attempt(lesson_slug, ex.id)

            if answer.lower() in ex.accepted:
                self.renderer.show_correct(ex.explanation)
                self.progress.mark_exercise_completed(lesson_slug, ex.id)
                break
            else:
                self.renderer.show_incorrect(ex.explanation)
                retry = self.renderer.prompt("  Try again? [y/n/q]: ").lower()
                if retry in _QUIT_TOKENS:
                    raise QuitLesson()
                if retry == "y":
                    self.renderer.show_question(ex.question)
                    continue
                break

        self._wait_or_quit()

    # ------------------------------------------------------------------
    # Code exercise
    # ------------------------------------------------------------------

    def _run_code(
        self,
        ex: "CodeExercise",
        lesson_slug: str,
        index: int,
        total: int,
    ) -> None:
        self.renderer.show_exercise_header(index, total, "code", ex.title)

        solution_path = self._setup_workspace(ex, lesson_slug)
        self.renderer.show_code_exercise(ex.description, solution_path)

        if self.progress.is_exercise_completed(lesson_slug, ex.id):
            self.renderer.show_already_completed()

        from cli.models import QuitLesson

        options: list[tuple[str, str]] = [("1", "Run tests against my solution")]
        if ex.hint:
            options.append(("2", "Show hint"))
        options.append(("s", "Skip this exercise"))
        options.append(("q", "Save and quit lesson"))

        while True:
            self.renderer.show_numbered_menu("What would you like to do?", options)
            choice = self.renderer.prompt()

            if choice == "1":
                self.progress.record_attempt(lesson_slug, ex.id)
                results = run_tests(ex.test_path, solution_path)
                self.renderer.show_test_results(results)

                if all(passed for _, passed, _ in results):
                    self.progress.mark_exercise_completed(lesson_slug, ex.id)
                    self._wait_or_quit()
                    return

                # Failed — allow retry (user edits file externally, then re-runs)
                self.renderer.info("Edit your solution file and try again.")

            elif choice == "2" and ex.hint:
                self.renderer.info(f"Hint: {ex.hint}")

            elif choice.lower() == "s":
                self.renderer.info("Exercise skipped.")
                return

            elif choice.lower() in _QUIT_TOKENS:
                raise QuitLesson()

            else:
                self.renderer.warning("Invalid choice.")

    def _setup_workspace(self, ex: "CodeExercise", lesson_slug: str) -> Path:
        """Copy starter file to user workspace (once) and return the path."""
        dest_dir = self.workspace / lesson_slug
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f"{ex.id}.py"
        if not dest.exists():
            shutil.copy(ex.starter_path, dest)
        return dest


# ---------------------------------------------------------------------------
# Public test runner (also used by tester.py)
# ---------------------------------------------------------------------------

def run_tests(
    test_path: Path, solution_path: Path
) -> list[tuple[str, bool, str]]:
    """Import *test_path* and run its test functions against *solution_path*.

    Returns a list of (display_name, passed, error_message).

    Test files should expose:
      TEST_CASES: list[tuple[str, Callable[[Path], None]]]

    Fallback: any callable whose name starts with ``test_`` is called with
    ``solution_path`` as its sole argument.
    """
    spec = importlib.util.spec_from_file_location("_lesson_tests", test_path)
    if spec is None or spec.loader is None:
        return [("Load test file", False, f"Cannot load {test_path}")]

    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
    except Exception as exc:
        return [("Import test module", False, f"{type(exc).__name__}: {exc}")]

    # Prefer explicit TEST_CASES list
    if hasattr(mod, "TEST_CASES"):
        cases = mod.TEST_CASES
    else:
        cases = [
            (name, getattr(mod, name))
            for name in sorted(dir(mod))
            if name.startswith("test_") and callable(getattr(mod, name))
        ]

    if not cases:
        return [("No tests found", False, f"No TEST_CASES or test_* in {test_path.name}")]

    results: list[tuple[str, bool, str]] = []
    for display_name, func in cases:
        try:
            func(solution_path)
            results.append((display_name, True, ""))
        except AssertionError as exc:
            results.append((display_name, False, str(exc)))
        except Exception as exc:
            results.append((display_name, False, f"{type(exc).__name__}: {exc}"))

    return results
