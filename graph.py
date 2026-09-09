from langgraph.graph import StateGraph, END
from typing import TypedDict
import os

os.environ["CODEBASE_ROOT"] = "./sample_codebase"

from regression_analyser.code_analyser import CodeAnalyzer
from regression_analyser.endpoint_mapper import EndpointMapper
from regression_analyser.models import CodeChange


class RegressionState(TypedDict):
    pr_diff: str
    file_path: str
    changed_functions: list[str]
    dependencies: list
    risk_score: float
    risk_level: str
    notified: bool
    _code_change: CodeChange


code_analyzer = CodeAnalyzer()
endpoint_mapper = EndpointMapper()


def parse_diff(state: RegressionState) -> dict:
    change = code_analyzer.analyze_diff(state["file_path"], state["pr_diff"])
    return {"changed_functions": change.functions_modified, "_code_change": change}


def dependency_lookup(state: RegressionState) -> dict:
    change = state["_code_change"]
    affected = endpoint_mapper.map_changes_to_endpoints([change])
    return {"dependencies": affected}


def risk_score(state: RegressionState) -> dict:
    deps = state["dependencies"]
    if not deps:
        return {"risk_score": 0.0, "risk_level": "low"}

    # Use the real signal the analyzer actually produces: confidence + impact_level,
    # not how many endpoints happened to come back.
    max_confidence = max(ep.confidence for ep in deps)
    has_high_impact = any(ep.impact_level == "high" for ep in deps)

    score = max_confidence if has_high_impact else max_confidence * 0.5
    level = "high" if score >= 0.5 else "low"
    return {"risk_score": score, "risk_level": level}


def notify(state: RegressionState) -> dict:
    for ep in state["dependencies"]:
        print(f"NOTIFY: {ep.method} {ep.path} — {ep.reasoning} (confidence {ep.confidence})")
    return {"notified": True}


def route_after_risk(state: RegressionState) -> str:
    if state["risk_level"] == "high":
        return "notify"
    return END


graph = StateGraph(RegressionState)
graph.add_node("parse_diff", parse_diff)
graph.add_node("dependency_lookup", dependency_lookup)
graph.add_node("risk_score", risk_score)
graph.add_node("notify", notify)

graph.set_entry_point("parse_diff")
graph.add_edge("parse_diff", "dependency_lookup")
graph.add_edge("dependency_lookup", "risk_score")
graph.add_conditional_edges("risk_score", route_after_risk)

app = graph.compile()

if __name__ == "__main__":
    real_diff = """
+def validate_and_create(payload: dict):
+    payload["validated"] = True
+    return {"status": "created"}
"""
    result = app.invoke({
        "pr_diff": real_diff,
        "file_path": "sample_codebase/experts/views.py",
        "changed_functions": [],
        "dependencies": [],
        "risk_score": 0.0,
        "risk_level": "",
        "notified": False,
        "_code_change": None,
    })
    print(result)
