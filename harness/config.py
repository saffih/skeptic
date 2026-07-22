"""Harness configuration constants."""

import os
from pathlib import Path

MODEL = "claude-sonnet-4-20250514"
TEMPERATURE = 0
MAX_TOKENS = 4096
CONCURRENCY = 5

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
