# regression-agent-langgraph

A learning project: rebuilding the real logic of a production CI/CD tool, the Regression Analyser, as a LangGraph graph, to move from a fully deterministic pipeline toward genuine LLM-controlled routing.

This repo does not modify or replace the production Regression Analyser. It reuses two of its own classes, `CodeAnalyzer` and `EndpointMapper`, unmodified, against a small sample codebase, so the graph's decisions run on real logic rather than stubs.

## What's here

- `graph.py` — a five-node LangGraph graph: `parse_diff → decide_dependency_check → dependency_lookup → risk_score → notify`
- `regression_analyser/` — the real `CodeAnalyzer` and `EndpointMapper` classes, plus trimmed local `models.py`/`config.py`/`utils.py` stand-ins so they run standalone without the production repo's GitHub/OpenAI dependencies
- `sample_codebase/` — a small fixture API for `EndpointMapper`'s AST indexer to walk

## The core result

One edge in this graph is genuinely agentic: an LLM decides whether to run `dependency_lookup` based on the actual content of a diff, not a rule matching on function names. Tested against two diffs modifying the identical function — a real logic change and a comment-only edit — the LLM correctly told them apart. The remaining edges stay deterministic, on purpose — see agentic_workflow_phase1.md for the single-decision-edge build, and agentic_workflow_phase2.md for the multi-step loop extension.

## Setup

```bash
pip install -r requirements.txt
export GOOGLE_API_KEY="your-key-here"
python graph.py
```
