# ──────────────────────────────────────────────────────────────────
#  Ultimate Python — Makefile
#  Default target (`make`) launches the interactive shell.
# ──────────────────────────────────────────────────────────────────

PYTHON   := python3
VENV_DIR := venv
REQ_FILE := requirements.txt

.PHONY: all run install test reset-progress lint clean help

# Default: just run the shell
all: run

# ──────────────────────────────────────────────────────────────────
#  Launch interactive shell
# ──────────────────────────────────────────────────────────────────
run:
	@$(PYTHON) main.py

# ──────────────────────────────────────────────────────────────────
#  Install dependencies
# ──────────────────────────────────────────────────────────────────
install:
	@echo "Installing dependencies..."
	@$(PYTHON) -m pip install --upgrade pip -q
	@$(PYTHON) -m pip install -r $(REQ_FILE) -q
	@echo "Done. Run 'make' to start."

# ──────────────────────────────────────────────────────────────────
#  Run the original ultimatepython module test suite
# ──────────────────────────────────────────────────────────────────
test:
	@$(PYTHON) runner.py

# ──────────────────────────────────────────────────────────────────
#  Wipe progress (JSON file only — no code is deleted)
# ──────────────────────────────────────────────────────────────────
reset-progress:
	@echo "Resetting progress..."
	@rm -f .progress/progress.json
	@echo "Progress cleared."

# ──────────────────────────────────────────────────────────────────
#  Lint (uses existing pyproject.toml config)
# ──────────────────────────────────────────────────────────────────
lint:
	@ruff check cli/ lessons/ main.py

# ──────────────────────────────────────────────────────────────────
#  Clean generated artefacts
# ──────────────────────────────────────────────────────────────────
clean:
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cleaned."

# ──────────────────────────────────────────────────────────────────
#  Help
# ──────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "  make              Launch the interactive learning shell"
	@echo "  make run          Same as make"
	@echo "  make install      Install Python dependencies"
	@echo "  make test         Run ultimatepython module tests (runner.py)"
	@echo "  make reset-progress  Wipe .progress/progress.json"
	@echo "  make lint         Run ruff on cli/ and lessons/"
	@echo "  make clean        Remove __pycache__ and .pyc files"
	@echo ""
