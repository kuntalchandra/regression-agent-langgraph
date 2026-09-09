"""Configuration for Regression Analyser — trimmed for learning repo."""

import os


class Config:
    CODEBASE_ROOT: str = os.getenv("CODEBASE_ROOT", "./sample_codebase")
    VIEWS_PATTERN: str = "**/views.py"
    SERVICE_PATTERN: str = "**/service.py"
