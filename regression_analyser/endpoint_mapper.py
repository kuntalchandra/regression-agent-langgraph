"""Maps code changes to API endpoints."""

import ast
import re
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
import logging

from regression_analyser.models import AffectedEndpoint, CodeChange, ChangeType
from regression_analyser.config import Config

logger = logging.getLogger(__name__)


class EndpointMapper:
    """Maps code changes to affected API endpoints."""

    def __init__(self, codebase_root: str = None):
        self.codebase_root = Path(codebase_root or Config.CODEBASE_ROOT)
        self.endpoint_cache: Dict[str, List[Dict]] = {}
        self._build_endpoint_index()

    def _build_endpoint_index(self) -> None:
        """Build index of all API endpoints in codebase."""
        logger.debug("Building endpoint index...")
        views_files = list(self.codebase_root.glob(Config.VIEWS_PATTERN))

        for views_file in views_files:
            try:
                endpoints = self._extract_endpoints_from_file(views_file)
                if endpoints:
                    self.endpoint_cache[str(views_file)] = endpoints
            except Exception as e:
                logger.warning(f"Failed to parse {views_file}: {e}")

        logger.debug(f"Indexed {len(self.endpoint_cache)} view files")

    def _extract_endpoints_from_file(self, file_path: Path) -> List[Dict]:
        """Extract API endpoints from a views.py file."""
        endpoints = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content, filename=str(file_path))
        except Exception as e:
            logger.debug(f"Failed to parse {file_path}: {e}")
            return endpoints

        # Find router definition
        router_name = None
        router_prefix = None

        for node in ast.walk(tree):
            # Find router creation: router = APIRouter(...)
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and "router" in target.id.lower():
                        router_name = target.id
                        # Try to find prefix in router creation
                        if isinstance(node.value, ast.Call):
                            for keyword in node.value.keywords:
                                if keyword.arg == "prefix":
                                    if isinstance(keyword.value, ast.Constant):
                                        router_prefix = keyword.value.value

            # Find route decorators: @router.get("/path")
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Attribute):
                            # Check if it's router.get, router.post, etc.
                            if isinstance(decorator.func.value, ast.Name):
                                if decorator.func.value.id == router_name or "router" in decorator.func.value.id.lower():
                                    method = decorator.func.attr.upper()
                                    path = self._extract_path_from_decorator(decorator)
                                    if path:
                                        full_path = f"{router_prefix or ''}{path}".replace("//", "/")
                                        endpoints.append({
                                            "method": method,
                                            "path": full_path,
                                            "function": node.name,
                                            "line": node.lineno,
                                        })

        return endpoints

    def _extract_path_from_decorator(self, decorator: ast.Call) -> Optional[str]:
        """Extract path from route decorator."""
        if decorator.args:
            arg = decorator.args[0]
            if isinstance(arg, ast.Constant):
                return arg.value
            elif isinstance(arg, ast.JoinedStr):  # f-strings
                # Try to extract static parts
                parts = []
                for value in arg.values:
                    if isinstance(value, ast.Constant):
                        parts.append(value.value)
                return "".join(parts) if parts else None
        return None

    def map_changes_to_endpoints(
        self, code_changes: List[CodeChange]
    ) -> List[AffectedEndpoint]:
        """Map code changes to affected endpoints."""
        affected_endpoints = []
        changed_files = {change.file_path for change in code_changes}
        changed_functions = set()
        changed_classes = set()

        # Collect all changed functions and classes
        for change in code_changes:
            changed_functions.update(change.functions_modified)
            changed_classes.update(change.classes_modified)

        # Find endpoints in changed files
        for change in code_changes:
            file_path = Path(change.file_path)
            if file_path.name == "views.py":
                endpoints = self._get_endpoints_in_file(file_path)
                for endpoint in endpoints:
                    if self._is_endpoint_affected(endpoint, change, changed_functions, changed_classes):
                        affected_endpoints.append(
                            AffectedEndpoint(
                                method=endpoint["method"],
                                path=endpoint["path"],
                                function_name=endpoint["function"],
                                file_path=str(file_path),
                                confidence=0.9,  # High confidence for direct changes
                                reasoning=f"Endpoint function '{endpoint['function']}' was modified in {file_path.name}",
                                impact_level="high",
                                change_type=ChangeType.ENDPOINT_MODIFIED,
                            )
                        )

        # Find endpoints that use changed services/models
        affected_endpoints.extend(
            self._find_indirect_affected_endpoints(changed_files, changed_functions, changed_classes)
        )

        return affected_endpoints

    def _get_endpoints_in_file(self, file_path: Path) -> List[Dict]:
        """Get endpoints from a views file."""
        file_str = str(file_path)
        if file_str in self.endpoint_cache:
            return self.endpoint_cache[file_str]
        return []

    def _is_endpoint_affected(
        self,
        endpoint: Dict,
        change: CodeChange,
        changed_functions: Set[str],
        changed_classes: Set[str],
    ) -> bool:
        """Check if endpoint is directly affected by change."""
        # Direct match
        if endpoint["function"] in change.functions_modified:
            return True

        # Check if endpoint function is in the diff
        if endpoint["function"] in change.diff:
            return True

        return False

    def _find_indirect_affected_endpoints(
        self,
        changed_files: Set[str],
        changed_functions: Set[str],
        changed_classes: Set[str],
    ) -> List[AffectedEndpoint]:
        """Find endpoints indirectly affected through service/model dependencies."""
        affected = []
        changed_services = {f for f in changed_files if "service.py" in f}
        changed_models = {f for f in changed_files if "models.py" in f or "schemas.py" in f}

        # Check all endpoints for dependencies on changed services/models
        for file_path, endpoints in self.endpoint_cache.items():
            if file_path in changed_files:
                continue  # Already handled as direct changes

            for endpoint in endpoints:
                # Check if endpoint file imports changed services/models
                if self._file_imports_changed_modules(file_path, changed_services, changed_models):
                    affected.append(
                        AffectedEndpoint(
                            method=endpoint["method"],
                            path=endpoint["path"],
                            function_name=endpoint["function"],
                            file_path=file_path,
                            confidence=0.6,  # Medium confidence for indirect changes
                            reasoning=f"Endpoint may be affected by changes to imported services/models",
                            impact_level="medium",
                            change_type=ChangeType.SERVICE_MODIFIED,
                        )
                    )

        return affected

    def _file_imports_changed_modules(
        self, file_path: str, changed_services: Set[str], changed_models: Set[str]
    ) -> bool:
        """Check if file imports any changed services or models."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content, filename=file_path)
        except Exception:
            return False

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    module_path = node.module.replace(".", "/")
                    # Check if imported module matches changed files
                    for changed in changed_services:
                        if changed.replace(".py", "") in module_path or module_path in changed.replace(".py", ""):
                            return True
                    for changed in changed_models:
                        if changed.replace(".py", "") in module_path or module_path in changed.replace(".py", ""):
                            return True

        return False

