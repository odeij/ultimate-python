"""
cli/ — Interactive terminal shell for Ultimate Python.

Architecture:
  app.py          Navigation controller (main loop + all menu state)
  renderer.py     All display logic via `rich` (panels, markdown, tables)
  models.py       Pure data: Lesson, LessonSection, Exercise variants
  lesson_loader.py Discover and parse lessons from lessons/ directory
  exercise_runner.py Run exercises, manage user workspace, grade answers
  tester.py       Run checkpoint tests (lesson tests + full module suite)
  progress.py     JSON-backed progress persistence
"""
