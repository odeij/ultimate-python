"""All terminal display logic.

Single source of truth for visual output.  Nothing outside this module
should import `rich` directly — all formatting decisions live here.

Design choices:
  - `rich` for display: panels, markdown, tables, syntax highlighting.
  - Plain `input()` for prompts (no questionary/prompt_toolkit dependency).
    This maximises robustness across platforms and terminal emulators.
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

if TYPE_CHECKING:
    from cli.models import Lesson, LessonSection

# ---------------------------------------------------------------------------
# Colour palette — one place to change all colours
# ---------------------------------------------------------------------------

_TOPIC_COLORS: dict[str, str] = {
    "syntax":             "bright_cyan",
    "data_structures":    "bright_green",
    "classes":            "bright_yellow",
    "advanced":           "bright_magenta",
    "mastery/internals":  "bright_red",
    "mastery/algorithms": "bright_blue",
    "mastery/research":   "white",
}

_DIFFICULTY_COLORS: dict[str, str] = {
    "easy":   "green",
    "medium": "yellow",
    "hard":   "red",
}

_LETTERS = "ABCDEFGHIJ"


class Renderer:
    """Encapsulates all terminal I/O."""

    def __init__(self) -> None:
        self.console = Console()

    # ------------------------------------------------------------------
    # Application shell
    # ------------------------------------------------------------------

    def clear(self) -> None:
        self.console.clear()

    def show_main_header(self) -> None:
        self.console.clear()
        title = Text()
        title.append("  🐍  Ultimate Python", style="bold bright_green")
        title.append("  —  Interactive Shell", style="dim")
        self.console.print(Panel(
            title,
            subtitle="[dim italic]Master Python the way you mastered C[/dim italic]",
            border_style="bright_green",
            padding=(1, 4),
        ))
        self.console.print()

    def show_numbered_menu(
        self,
        title: str,
        options: list[tuple[str, str]],
        breadcrumb: str = "",
    ) -> None:
        """Print a clean numbered menu and return without reading input."""
        if breadcrumb:
            self.console.print(f"  [dim]{breadcrumb}[/dim]")
            self.console.print()
        self.console.print(f"  [bold]{title}[/bold]")
        self.console.print()
        for key, label in options:
            self.console.print(f"    [[bold cyan]{key}[/bold cyan]]  {label}")
        self.console.print()

    # ------------------------------------------------------------------
    # Lesson display
    # ------------------------------------------------------------------

    def show_lesson_header(self, lesson: "Lesson") -> None:
        self.console.clear()
        topic_col = _TOPIC_COLORS.get(lesson.topic, "white")
        diff_col  = _DIFFICULTY_COLORS.get(lesson.difficulty, "white")
        meta = (
            f"[{topic_col}]{lesson.topic.replace('/', ' › ')}[/{topic_col}]"
            f"  ·  [{diff_col}]{lesson.difficulty}[/{diff_col}]"
            f"  ·  [dim]~{lesson.estimated_minutes} min[/dim]"
        )
        self.console.print(Rule(f"[bold]{lesson.title}[/bold]", style="bright_green"))
        self.console.print(f"  {meta}")
        self.console.print()

    def show_section(
        self, section: "LessonSection", index: int, total: int
    ) -> None:
        """Render one theory section using rich Markdown."""
        self.console.print(Rule(
            f"[dim]Section {index}/{total}[/dim]  ·  [bold]{section.heading}[/bold]",
            style="dim",
        ))
        self.console.print()
        self.console.print(Markdown(section.body))
        self.console.print()

    def show_lesson_complete(self, lesson: "Lesson") -> None:
        next_hint = (
            f"\n  [dim]Next:[/dim] [bold]{lesson.next_lesson}[/bold]"
            if lesson.next_lesson else ""
        )
        self.console.print()
        self.console.print(Panel(
            f"[bold green]✅  Lesson complete![/bold green]{next_hint}",
            border_style="green",
            padding=(1, 4),
        ))
        self.console.print()

    # ------------------------------------------------------------------
    # Exercise display
    # ------------------------------------------------------------------

    def show_exercise_header(
        self, index: int, total: int, kind: str, title: str = ""
    ) -> None:
        _icons = {
            "multiple_choice": "✏️ ",
            "short_answer":    "💬",
            "code":            "💻",
        }
        icon  = _icons.get(kind, "▸")
        label = title or kind.replace("_", " ").title()
        self.console.print(Rule(
            f"{icon}  [bold]Exercise {index}/{total}[/bold]  ·  {label}",
            style="bright_cyan",
        ))
        self.console.print()

    def show_question(self, question: str) -> None:
        self.console.print(f"  [bold]{question}[/bold]")
        self.console.print()

    def show_options(self, options: list[str]) -> None:
        for i, opt in enumerate(options):
            self.console.print(f"    [bold cyan]{_LETTERS[i]})[/bold cyan]  {opt}")
        self.console.print()

    def show_correct(self, explanation: str) -> None:
        self.console.print("  [bold green]✅  Correct![/bold green]")
        self.console.print()
        self.console.print(f"  {explanation}")
        self.console.print()

    def show_incorrect(self, explanation: str) -> None:
        self.console.print("  [bold red]❌  Not quite.[/bold red]")
        self.console.print()
        self.console.print(f"  {explanation}")
        self.console.print()

    def show_already_completed(self) -> None:
        self.console.print("  [dim]✓  You've already completed this exercise.[/dim]")
        self.console.print()

    def show_code_exercise(self, description: str, solution_path: Path) -> None:
        self.console.print(Markdown(description))
        self.console.print()
        self.console.print("  [dim]Your solution file:[/dim]")
        self.console.print(f"  [bold cyan]➜  {solution_path}[/bold cyan]")
        self.console.print()
        self.console.print(
            "  [dim]Open it in your editor, implement the function, then return here.[/dim]"
        )
        self.console.print()

    def show_test_results(self, results: list[tuple[str, bool, str]]) -> None:
        """Display per-test pass/fail with final summary."""
        self.console.print(Rule(style="dim"))
        for name, passed, msg in results:
            if passed:
                self.console.print(f"  [green]✅  PASS[/green]  {name}")
            else:
                self.console.print(f"  [red]❌  FAIL[/red]  {name}")
                if msg:
                    # Trim long error messages to keep output readable
                    brief = msg.splitlines()[0][:120]
                    self.console.print(f"       [dim]{brief}[/dim]")

        self.console.print()
        self.console.print(Rule(style="dim"))
        passed_n = sum(1 for _, p, _ in results if p)
        total_n  = len(results)
        if passed_n == total_n:
            self.console.print(
                f"  [bold green]All {total_n} tests passed!  🎉[/bold green]"
            )
        else:
            self.console.print(
                f"  [yellow]{passed_n}/{total_n} tests passed.[/yellow]"
            )
        self.console.print()

    # ------------------------------------------------------------------
    # Progress dashboard
    # ------------------------------------------------------------------

    def show_dashboard(
        self, stats: dict, lessons: list["Lesson"], progress: object
    ) -> None:
        from cli.progress import ProgressTracker  # avoid circular at module level
        assert isinstance(progress, ProgressTracker)

        self.console.clear()
        self.console.print(Rule("[bold]Progress Dashboard[/bold]", style="bright_green"))
        self.console.print()

        # Summary row
        bar_filled = int(stats["percent"] / 5)
        bar = "[green]" + "█" * bar_filled + "[/green]" + "░" * (20 - bar_filled)
        summary = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        summary.add_column(style="dim", no_wrap=True)
        summary.add_column(style="bold")
        summary.add_row("Completed",   f"[green]{stats['completed']}[/green] / {stats['total']}")
        summary.add_row("In progress", f"[yellow]{stats['in_progress']}[/yellow]")
        summary.add_row("Not started", f"[dim]{stats['not_started']}[/dim]")
        summary.add_row("Progress",    f"{bar}  {stats['percent']}%")
        self.console.print(summary)
        self.console.print()

        # Per-lesson table
        tbl = Table(box=box.SIMPLE_HEAD, show_header=True, expand=False)
        tbl.add_column("#",      style="dim", width=3)
        tbl.add_column("Lesson", style="bold", no_wrap=True, max_width=46)
        tbl.add_column("Topic",  no_wrap=True)
        tbl.add_column("Status", no_wrap=True)

        for idx, lesson in enumerate(
            sorted(lessons, key=lambda l: (l.month, l.week)), start=1
        ):
            if progress.is_lesson_completed(lesson.slug):
                status = "[green]✓  Completed[/green]"
            elif progress.is_lesson_started(lesson.slug):
                status = "[yellow]⟳  In progress[/yellow]"
            else:
                status = "[dim]·  Not started[/dim]"

            tc = _TOPIC_COLORS.get(lesson.topic, "white")
            tbl.add_row(
                str(idx),
                lesson.title[:46],
                f"[{tc}]{lesson.topic}[/{tc}]",
                status,
            )

        self.console.print(tbl)
        self.console.print()

    # ------------------------------------------------------------------
    # Feedback helpers
    # ------------------------------------------------------------------

    def info(self, message: str) -> None:
        self.console.print(f"  [cyan]ℹ  {message}[/cyan]")
        self.console.print()

    def warning(self, message: str) -> None:
        self.console.print(f"  [yellow]⚠  {message}[/yellow]")
        self.console.print()

    def error(self, message: str) -> None:
        self.console.print(f"  [red]✗  {message}[/red]")
        self.console.print()

    def print(self, *args, **kwargs) -> None:  # noqa: A003
        self.console.print(*args, **kwargs)

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def prompt(self, text: str = "  ❯ ") -> str:
        """Read a line of input and strip whitespace."""
        try:
            return self.console.input(text).strip()
        except EOFError:
            return ""

    def wait(self, message: str = "  [dim][Press Enter to continue][/dim]") -> None:
        self.console.print(message)
        self.prompt("")
