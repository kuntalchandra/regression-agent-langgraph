# Agentic Workflow Study Plan — LangGraph
## Progress Tracker

Goal: hands-on understanding of agentic workflows, building directly on the completed RAG study plan, grounded in the Regression Analyzer's existing agent implementation.

Repo: regression-agent-langgraph — new repo, learning project only, does not modify the production Regression Analyzer codebase.

Environment: Chromebook, browser only. GitHub Codespaces for the project build.

---

## Session-by-session plan

- [x] **Session 1 — Concepts, in Colab/chat.** Agentic vs fixed pipeline: control of flow is the property, not LLM presence. Regression Analyzer today is a deterministic pipeline with an LLM reasoning step inside it, not an LLM deciding the steps. Comprehension check passed: control of flow is what changes if RegressionAnalyzerAgent decides whether to call EndpointMapper. Agentic comes in degrees — a single conditional edge is genuinely agentic, just narrow in scope, not "theoretically agentic."
- [x] **Session 2 — Build, in Codespaces.** Four-node graph implemented: parse_diff, dependency_lookup, risk_score, notify. Conditional edge after risk_score routes to notify on high risk, skips to END on low risk. Confirmed honestly: this branch is code-driven by a threshold, not yet LLM-driven — an if-statement in LangGraph's syntax, not agentic decision-making yet.
- [ ] **Session 3 — Test and harden.** Run both branches against mock diffs, confirm low risk skips notify and high risk hits it. Swap stub logic in parse_diff and dependency_lookup for real calls into CodeAnalyzer and EndpointMapper.
- [ ] **Session 4 — Stretch, MCP touchpoint.** Expose dependency_lookup as a tool the graph's LLM can choose to call rather than a hardcoded step. First point where the system earns real LLM-controlled routing.
- [ ] **Session 5 — EM synthesis.** When to hand orchestration control to an LLM versus keep it deterministic. Cost and reliability tradeoffs. Tie into interview narrative alongside the RAG lifecycle answers.

---

## How to resume in a new thread

Paste this file back in, confirm which session to start from, and re-attach the Regression Analyzer document for grounding.
