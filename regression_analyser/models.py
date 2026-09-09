"""Data models for Regression Analyser."""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class ImpactLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class ChangeType(str, Enum):
    ENDPOINT_MODIFIED = "endpoint_modified"
    SERVICE_MODIFIED = "service_modified"
    MODEL_MODIFIED = "model_modified"
    SCHEMA_MODIFIED = "schema_modified"
    DEPENDENCY_MODIFIED = "dependency_modified"
    CONFIG_MODIFIED = "config_modified"


class AffectedEndpoint(BaseModel):
    method: str
    path: str
    function_name: str
    file_path: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    impact_level: str
    change_type: ChangeType
    test_recommendations: List[str] = Field(default_factory=list)


class CodeChange(BaseModel):
    file_path: str
    change_type: str
    lines_added: int
    lines_removed: int
    diff: str
    functions_modified: List[str] = Field(default_factory=list)
    classes_modified: List[str] = Field(default_factory=list)
