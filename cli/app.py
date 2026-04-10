"""Main application controller.

Owns the navigation loop.  Every user-facing action routes through here.
No display logic lives in this file — all output goes through renderer.
"""
from __future__ import annotations

import sys
from pathlib import Path

from cli.exercise_runner import ExerciseRunner
from cli.lesson_loader import LessonLoader
from cli.models import Lesson
from cli.progress import ProgressTracker
from cli.renderer import Renderer
from cli.tester import Tester


class App:
    """Top-level controller: initialise subsystems, drive the main loop."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.renderer  = Renderer()
        self.progress  = ProgressTracker(repo_root / ".progress" / "progress.json")
        self.loader    = LessonLoader(repo_root / "lessons")
        self.workspace = repo_root / "user_workspace" / "solutions"
        self.runner    = ExerciseRunner(self.renderer, self.progress, self.workspace)
        self.tester    = Tester(self.renderer, self.progress, repo_root)
        self._lessons: list[Lesson] = []

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def run(self) -> None:
        try:
            self._lessons = self.loader.load_all()
            if not self._lessons:
                self.renderer.print(
                    "\n  [yellow]No lessons found under lessons/. "
                    "Make sure the repo is complete.[/yellow]\n"
                )
                sys.exit(1)
            self._main_loop()
        except KeyboardInterrupt:
            self.renderer.print("\n\n  [dim]Interrupted. Goodbye.[/dim]\n")
            sys.exit(0)

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def _main_loop(self) -> None:
        while True:
            self.renderer.show_main_header()
            choice = self._render_main_menu()
            dispatch = {
                "1": self._start_journey,
                "2": self._continue_progress,
                "3": self._browse_by_topic,
                "4": self._browse_by_month,
                "5": self._practice_exercises,
                "6": self._run_checkpoints,
                "7": self._show_dashboard,
                "8": self._reset_progress,
            }
            if choice in ("9", "q", "exit", "quit"):
                self.renderer.print("\n  [dim]Goodbye. Keep learning.[/dim]\n")
                sys.exit(0)
            action = dispatch.get(choice)
            if action:
                action()
            else:
                self.renderer.warning("Enter a number from 1–9.")

    def _render_main_menu(self) -> str:
        last_slug = self.progress.get_last_lesson()
        last_hint = ""
        if last_slug:
            last = self.loader.get_by_slug(last_slug, self._lessons)
            if last:
                title_short = last.title[:42]
                last_hint = f"  [dim](last: {title_short})[/dim]"

        stats = self.progress.get_stats(self._lessons)
        pct   = stats["percent"]
        bar   = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))

        self.renderer.print(f"  [dim]{bar}  {pct}% complete[/dim]")
        self.renderer.print()

        options = [
            ("1", "Start study journey"),
            ("2", f"Continue progress{last_hint}"),
            ("3", "Browse by topic"),
            ("4", "Browse by month / week"),
            ("5", "Practice exercises"),
            ("6", "Run checkpoints / tests"),
            ("7", "Progress dashboard"),
            ("8", "Reset progress"),
            ("9", "Exit"),
        ]
        self.renderer.show_numbered_menu("What would you like to do?", options)
        return self.renderer.prompt()

    # ------------------------------------------------------------------
    # Journey modes
    # ------------------------------------------------------------------

    def _start_journey(self) -> None:
        for lesson in self._lessons:
            if not self.progress.is_lesson_completed(lesson.slug):
                self._run_lesson(lesson)
                return
        self.renderer.info("🎉 You've completed all available lessons!")
        self.renderer.wait()

    def _continue_progress(self) -> None:
        last_slug = self.progress.get_last_lesson()
        if not last_slug:
            self.renderer.info("No progress yet — starting from the beginning.")
            self._start_journey()
            return
        lesson = self.loader.get_by_slug(last_slug, self._lessons)
        if lesson and not self.progress.is_lesson_completed(lesson.slug):
            self._run_lesson(lesson)
        else:
            self._start_journey()

    # ------------------------------------------------------------------
    # Browse by topic
    # ------------------------------------------------------------------

    def _browse_by_topic(self) -> None:
        topics = self.loader.get_topics(self._lessons)
        while True:
            self.renderer.show_main_header()
            opts = [(str(i + 1), t.replace("/", " › ")) for i, t in enumerate(topics)]
            opts.append(("b", "Back"))
            self.renderer.show_numbered_menu(
                "Browse by Topic", opts, "Main  ›  Browse by Topic"
            )
            choice = self.renderer.prompt()
            if choice.lower() == "b":
                return
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(topics):
                    self._lesson_list_menu(
                        self.loader.get_by_topic(topics[idx], self._lessons),
                        title=topics[idx],
                        breadcrumb=f"Main  ›  Topic: {topics[idx]}",
                    )
                else:
                    self.renderer.warning("Invalid selection.")
            except ValueError:
                self.renderer.warning("Enter a number or 'b' to go back.")

    # ------------------------------------------------------------------
    # Browse by month
    # ------------------------------------------------------------------

    def _browse_by_month(self) -> None:
        months = self.loader.get_months(self._lessons)
        while True:
            self.renderer.show_main_header()
            opts = [(str(m), f"Month {m}") for m in months]
            opts.append(("b", "Back"))
            self.renderer.show_numbered_menu(
                "Browse by Month", opts, "Main  ›  Browse by Month"
            )
            choice = self.renderer.prompt()
            if choice.lower() == "b":
                return
            try:
                month = int(choice)
                if month in months:
                    self._lesson_list_menu(
                        self.loader.get_by_month(month, self._lessons),
                        title=f"Month {month}",
                        breadcrumb=f"Main  ›  Month {month}",
                    )
                else:
                    self.renderer.warning("Invalid month.")
            except ValueError:
                self.renderer.warning("Enter a month number or 'b' to go back.")

    # ------------------------------------------------------------------
    # Shared lesson-list browser
    # ------------------------------------------------------------------

    def _lesson_list_menu(
        self, lessons: list[Lesson], title: str, breadcrumb: str = ""
    ) -> None:
        while True:
            self.renderer.show_main_header()
            opts: list[tuple[str, str]] = []
            for i, l in enumerate(lessons):
                done  = "[green]✓[/green] " if self.progress.is_lesson_completed(l.slug) else "  "
                opts.append((
                    str(i + 1),
                    f"{done}{l.title}  [dim](~{l.estimated_minutes}m · {l.difficulty})[/dim]",
                ))
            opts.append(("b", "Back"))
            self.renderer.show_numbered_menu(title, opts, breadcrumb)
            choice = self.renderer.prompt()
            if choice.lower() == "b":
                return
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(lessons):
                    self._run_lesson(lessons[idx])
                else:
                    self.renderer.warning("Invalid selection.")
            except ValueError:
                self.renderer.warning("Enter a number or 'b' to go back.")

    # ------------------------------------------------------------------
    # Practice exercises (reuse topic browser)
    # ------------------------------------------------------------------

    def _practice_exercises(self) -> None:
        self._browse_by_topic()

    # ------------------------------------------------------------------
    # Checkpoints
    # ------------------------------------------------------------------

    def _run_checkpoints(self) -> None:
        while True:
            self.renderer.show_main_header()
            opts = [
                ("1", "Run tests for a specific lesson"),
                ("2", "Run all ultimatepython module tests  [dim](runner.py)[/dim]"),
                ("b", "Back"),
            ]
            self.renderer.show_numbered_menu(
                "Checkpoints / Tests", opts, "Main  ›  Checkpoints"
            )
            choice = self.renderer.prompt()
            if choice.lower() == "b":
                return
            if choice == "1":
                self._checkpoint_pick_lesson()
            elif choice == "2":
                self.tester.run_module_suite()
                self.renderer.wait()
            else:
                self.renderer.warning("Invalid choice.")

    def _checkpoint_pick_lesson(self) -> None:
        while True:
            self.renderer.show_main_header()
            opts = [(str(i + 1), l.title) for i, l in enumerate(self._lessons)]
            opts.append(("b", "Back"))
            self.renderer.show_numbered_menu(
                "Choose a lesson to test", opts, "Main  ›  Checkpoints  ›  Pick Lesson"
            )
            choice = self.renderer.prompt()
            if choice.lower() == "b":
                return
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(self._lessons):
                    self.tester.run_for_lesson(self._lessons[idx])
                    self.renderer.wait()
                    return
            except ValueError:
                pass
            self.renderer.warning("Invalid selection.")

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def _show_dashboard(self) -> None:
        stats = self.progress.get_stats(self._lessons)
        self.renderer.show_dashboard(stats, self._lessons, self.progress)
        self.renderer.wait()

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def _reset_progress(self) -> None:
        self.renderer.warning("This will erase all progress and cannot be undone.")
        confirm = self.renderer.prompt("  Type 'yes' to confirm: ")
        if confirm.lower() == "yes":
            self.progress.reset()
            self.renderer.info("Progress reset.")
        else:
            self.renderer.info("Reset cancelled.")
        self.renderer.wait()

    # ------------------------------------------------------------------
    # Core lesson runner
    # ------------------------------------------------------------------

    def _run_lesson(self, lesson: Lesson) -> None:
        """Full lesson flow: header → sections → exercises → completion."""
        self.progress.mark_lesson_started(lesson.slug)
        self.renderer.show_lesson_header(lesson)

        # --- Theory sections ---
        for i, section in enumerate(lesson.sections, start=1):
            self.renderer.show_section(section, i, len(lesson.sections))
            cmd = self.renderer.prompt(
                "  [dim][Enter] next · [s] skip to exercises · [q] quit lesson[/dim]  ❯ "
            )
            if cmd.lower() == "q":
                return
            if cmd.lower() == "s":
                break

        # --- Exercises ---
        total = len(lesson.exercises)
        for i, exercise in enumerate(lesson.exercises, start=1):
            self.runner.run(exercise, lesson.slug, i, total)

        # --- Completion ---
        all_completed = all(
            self.progress.is_exercise_completed(lesson.slug, ex.id)
            for ex in lesson.exercises
        )
        if all_completed or not lesson.exercises:
            self.progress.mark_lesson_completed(lesson.slug)

        self.renderer.show_lesson_complete(lesson)

        # --- Offer next lesson ---
        if lesson.next_lesson:
            next_lesson = self.loader.get_by_slug(lesson.next_lesson, self._lessons)
            if next_lesson:
                go = self.renderer.prompt(
                    f"  Start next lesson  '{next_lesson.title}'? [y/n]: "
                )
                if go.lower() == "y":
                    self._run_lesson(next_lesson)
                    return

        self.renderer.wait("  [dim][Press Enter to return to menu][/dim]")
