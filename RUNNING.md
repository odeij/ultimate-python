# Running the Interactive Shell Locally

## Prerequisites

- Python 3.10 or higher
- pip
- A terminal (macOS Terminal, iTerm2, VS Code integrated terminal all work)

Check your Python version:
```bash
python3 --version
```

---

## 1. Clone the repo (if you haven't already)

```bash
git clone https://github.com/odeij/ultimate-python.git
cd ultimate-python
```

---

## 2. Install dependencies

The shell requires two packages: `rich` (display) and `PyYAML` (lesson parsing).

```bash
make install
```

Or manually:
```bash
pip install rich PyYAML
```

---

## 3. Launch the shell

```bash
make
```

That's it. You should see the main menu.

Alternatively:
```bash
python main.py
# or
make run
```

---

## What you will see

When the shell starts:

```
╭────────────────────────────────────────────────────╮
│   🐍  Ultimate Python  —  Interactive Shell         │
│                                                     │
│   Master Python the way you mastered C              │
╰────────────────────────────────────────────────────╯

  ░░░░░░░░░░░░░░░░░░░░  0% complete

  What would you like to do?

    [1]  Start study journey
    [2]  Continue progress
    [3]  Browse by topic
    [4]  Browse by month / week
    [5]  Practice exercises
    [6]  Run checkpoints / tests
    [7]  Progress dashboard
    [8]  Reset progress
    [9]  Exit

  ❯
```

Type a number and press Enter to navigate.

---

## 4. Working through a lesson

### Recommended first path

Press `1` (Start study journey). It will open the first lesson: **Variables & References**.

The lesson has two parts:

**Theory** — reads like a textbook section. Each `## heading` is its own screen.
- Press **Enter** to go to the next section
- Type `s` + Enter to skip theory and jump straight to exercises
- Type `q` + Enter to quit the lesson and return to the menu

**Exercises** — three per lesson:
1. Multiple choice — type `A`, `B`, `C`, or `D` and press Enter
2. Short answer — type your answer and press Enter
3. Code challenge — see section below

---

## 5. Doing the code exercise

When you reach Exercise 3 (the code challenge), the shell will:

1. Show you the problem description
2. Copy a starter file to `user_workspace/solutions/<lesson>/q3.py`
3. Tell you the exact path of that file

**You then open a second terminal** (or your editor) and edit the file:
```bash
# In a second terminal tab / your editor:
code user_workspace/solutions/variables/q3.py
# or
vim user_workspace/solutions/variables/q3.py
# or whatever editor you use
```

Implement the function in that file. Save it.

**Come back to the shell** and press `1` (Run tests). The shell will run the automated tests against your solution and show pass/fail for each test case.

If tests fail, edit your file again, save, then press `1` again. Repeat until all tests pass.

---

## 6. Available lessons right now

| # | Slug | Title | Exercises |
|---|------|-------|-----------|
| 1 | `variables` | Variables & References: Names, Not Boxes | MCQ + short answer + `is_same_object()` |
| 2 | `conditionals` | Conditionals: Truthiness & Short-Circuit | MCQ + short answer + `safe_divide()` |
| 3 | `functions` | Functions: First-Class Objects & the Mutable Default Trap | MCQ + short answer + `build_history()` |

---

## 7. Testing without going through the menu

You can run the tests for any lesson directly from the terminal:

```bash
# Run the full ultimatepython module suite (runner.py)
make test

# Or directly:
python runner.py
```

To test your solution for a specific exercise outside the shell:

```bash
python -c "
from cli.exercise_runner import run_tests
from pathlib import Path

results = run_tests(
    Path('lessons/syntax/variables/exercises/q3_tests.py'),
    Path('user_workspace/solutions/variables/q3.py')
)
for name, passed, msg in results:
    print('PASS' if passed else 'FAIL', name)
    if msg: print(' ', msg)
"
```

---

## 8. Resetting progress

Your progress is saved in `.progress/progress.json`. To wipe it:

```bash
make reset-progress
```

Or from inside the shell: menu option `8` (Reset progress).

---

## 9. All Makefile targets

```bash
make              # launch the shell (default)
make run          # same as make
make install      # pip install rich PyYAML
make test         # run runner.py (all ultimatepython module tests)
make reset-progress  # delete .progress/progress.json
make lint         # run ruff on cli/ and lessons/
make clean        # remove __pycache__ and .pyc files
make help         # print this list
```

---

## 10. Troubleshooting

**`ModuleNotFoundError: No module named 'rich'`**
```bash
pip install rich PyYAML
```

**`Python 3.10+ required`**
```bash
# macOS with Homebrew:
brew install python@3.12
python3.12 main.py
```

**`No lessons found under lessons/`**
Make sure you are running from the repo root (the directory containing `main.py`):
```bash
cd ultimate-python
python main.py
```

**Shell looks broken / garbled characters**
The shell uses Unicode box-drawing characters. Make sure your terminal font supports them.
iTerm2, macOS Terminal with a modern font, and VS Code terminal all work fine.

**Progress not saving**
The `.progress/` directory is created automatically on first run. Make sure the repo directory is writable.
