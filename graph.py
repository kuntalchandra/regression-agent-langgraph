from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
import os

os.environ["CODEBASE_ROOT"] = "./sample_codebase"

from regression_analyser.code_analyser import CodeAnalyzer
from regression_analyser.endpoint_mapper import EndpointMapper
from regression_analyser.models import CodeChange

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool


class RegressionState(TypedDict):
    pr_diff: str
    file_path: str
    changed_functions: list[str]
    dependencies: list
    risk_score: float
    risk_level: str
    notified: bool
    _code_change: Optional[CodeChange]
    _llm_decision: Optional[AIMessage]


code_analyzer = CodeAnalyzer()
endpoint_mapper = EndpointMapper()

llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0)


@tool
def check_dependencies(reasoning: str) -> str:
    """Call this if the code change could affect other API endpoints and
    dependencies should be traced against the codebase. Skip trivial changes
    like comments, logging, or docstrings. Provide brief reasoning."""
    return "dependency check triggered"


llm_with_tools = llm.bind_tools([check_dependencies])


def parse_diff(state: RegressionState) -> dict:
    change = code_analyzer.analyze_diff(state["file_path"], state["pr_diff"])
    return {"changed_functions": change.functions_modified, "_code_change": change}


def decide_dependency_check(state: RegressionState) -> dict:
    change = state["_code_change"]
    prompt = f"""A code change was made to {change.file_path}.
Change type: {change.change_type}
Functions modified: {change.functions_modified}
Classes modified: {change.classes_modified}
Lines added: {change.lines_added}, lines removed: {change.lines_removed}
Diff:
{change.diff}

Decide whether this change is significant enough to trace dependencies
against the codebase's API endpoints."""
    response = llm_with_tools.invoke([HumanMessage(content=prompt)])
    return {"_llm_decision": response}


def route_after_decision(state: RegressionState) -> str:
    decision = state["_llm_decision"]
    if decision.tool_calls:
        return "dependency_lookup"
    return "risk_score"


def dependency_lookup(state: RegressionState) -> dict:
    change = state["_code_change"]
    affected = endpoint_mapper.map_changes_to_endpoints([change])
    return {"dependencies": affected}


def risk_score(state: RegressionState) -> dict:
    deps = state["dependencies"]
    if not deps:
        return {"risk_score": 0.0, "risk_level": "low"}
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
graph.add_node("decide_dependency_check", decide_dependency_check)
graph.add_node("dependency_lookup", dependency_lookup)
graph.add_node("risk_score", risk_score)
graph.add_node("notify", notify)

graph.set_entry_point("parse_diff")
graph.add_edge("parse_diff", "decide_dependency_check")
graph.add_conditional_edges("decide_dependency_check", route_after_decision)
graph.add_edge("dependency_lookup", "risk_score")
graph.add_conditional_edges("risk_score", route_after_risk)

app = graph.compile()

if __name__ == "__main__":
    real_diff = """
+# TODO: refactor this later
+def onboard_expert(payload: dict):
      result = validate_and_create(payload)
      return result
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
        "_llm_decision": None,
    })
    print(result)
