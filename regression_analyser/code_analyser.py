"""Analyzes code changes from PR diffs."""

import re
from typing import List, Set
from pathlib import Path
import logging

from regression_analyser.models import CodeChange
from regression_analyser.config import Config

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """Analyzes code changes to extract functions, classes, and dependencies."""

    def __init__(self):
        self.function_pattern = re.compile(r"^[\s]*(?:async\s+)?def\s+(\w+)\s*\(", re.MULTILINE)
        self.class_pattern = re.compile(r"^[\s]*class\s+(\w+)", re.MULTILINE)
        self.import_pattern = re.compile(r"^[\s]*(?:from\s+(\S+)\s+)?import\s+", re.MULTILINE)

    def analyze_diff(self, file_path: str, diff: str) -> CodeChange:
        """Analyze a diff to extract code changes."""
        lines_added = diff.count("\n+") - diff.count("\n+++")
        lines_removed = diff.count("\n-") - diff.count("\n---")

        # Extract functions and classes from diff
        functions_modified = self._extract_functions_from_diff(diff)
        classes_modified = self._extract_classes_from_diff(diff)

        # Determine change type
        change_type = self._determine_change_type(diff, file_path)

        return CodeChange(
            file_path=file_path,
            change_type=change_type,
            lines_added=lines_added,
            lines_removed=lines_removed,
            diff=diff,
            functions_modified=functions_modified,
            classes_modified=classes_modified,
        )

    def _extract_functions_from_diff(self, diff: str) -> List[str]:
        """Extract function names from diff."""
        functions = set()

        # Look for function definitions in added/modified lines
        for line in diff.split("\n"):
            if line.startswith("+") or (line.startswith(" ") and "def " in line):
                clean_line = line.lstrip("+- ")
                match = self.function_pattern.search(clean_line)
                if match:
                    functions.add(match.group(1))

        return list(functions)

    def _extract_classes_from_diff(self, diff: str) -> List[str]:
        """Extract class names from diff."""
        classes = set()

        for line in diff.split("\n"):
            if line.startswith("+") or (line.startswith(" ") and "class " in line):
                clean_line = line.lstrip("+- ")
                match = self.class_pattern.search(clean_line)
                if match:
                    classes.add(match.group(1))

        return list(classes)

    def _determine_change_type(self, diff: str, file_path: str) -> str:
        """Determine the type of change."""
        file_lower = file_path.lower()

        if "views.py" in file_lower:
            return "endpoint_modified"
        elif "service.py" in file_lower:
            return "service_modified"
        elif "models.py" in file_lower:
            return "model_modified"
        elif "schemas.py" in file_lower:
            return "schema_modified"
        elif "config" in file_lower or "settings" in file_lower:
            return "config_modified"
        else:
            return "dependency_modified"

    def analyze_file_changes(self, file_path: str, old_content: str, new_content: str) -> CodeChange:
        """Analyze changes between old and new file content."""
        # Simple diff simulation - in production, use proper diff library
        old_lines = set(old_content.split("\n"))
        new_lines = set(new_content.split("\n"))

        added = new_lines - old_lines
        removed = old_lines - new_lines

        diff_lines = []
        for line in removed:
            diff_lines.append(f"-{line}")
        for line in added:
            diff_lines.append(f"+{line}")

        diff = "\n".join(diff_lines)

        return self.analyze_diff(file_path, diff)

