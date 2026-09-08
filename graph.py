from langgraph.graph import StateGraph, END
from typing import TypedDict

class RegressionState(TypedDict):
    pr_diff: str
    changed_functions: list[str]
    dependencies: list[str]
    risk_score: float
    risk_level: str
    notified: bool

def parse_diff(state: RegressionState) -> dict:
    changed = ["EndpointX.handler", "ServiceY.compute"]
    return {"changed_functions": changed}

def dependency_lookup(state: RegressionState) -> dict:
    deps = [f"{fn}_dependent_endpoint" for fn in state["changed_functions"]]
    return {"dependencies": deps}

def risk_score(state: RegressionState) -> dict:
    score = 0.8 if len(state["dependencies"]) > 1 else 0.2
    level = "high" if score >= 0.5 else "low"
    return {"risk_score": score, "risk_level": level}

def notify(state: RegressionState) -> dict:
    print(f"NOTIFY: risk={state['risk_level']}, deps={state['dependencies']}")
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
    result = app.invoke({
        "pr_diff": "mock diff content",
        "changed_functions": [],
        "dependencies": [],
        "risk_score": 0.0,
        "risk_level": "",
        "notified": False,
    })
    print(result)
