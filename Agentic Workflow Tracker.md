# Agentic Workflow Study Plan — LangGraph
## Progress Tracker

Goal: hands-on understanding of agentic workflows, building directly on the completed RAG study plan, grounded in the Regression Analyzer's existing agent implementation.

Repo: regression-agent-langgraph — new repo, learning project only, does not modify the production Regression Analyzer codebase.

Environment: Chromebook, browser only. GitHub Codespaces for the project build.

---

## Session-by-session plan

- [x] **Session 1 — Concepts, in chat.** Agentic vs fixed pipeline: control of flow is the property, not LLM presence. Regression Analyzer today is a deterministic pipeline with an LLM reasoning step inside it, not an LLM deciding the steps. Comprehension check passed: control of flow is what changes if RegressionAnalyzerAgent decides whether to call EndpointMapper. Corrected framing: agentic comes in degrees — a single conditional edge is genuinely agentic, just narrow in scope, not "theoretically agentic with practical limits."

- [x] **Session 2 — Build, in Codespaces.** Four-node graph implemented with stub logic: parse_diff, dependency_lookup, risk_score, notify. Conditional edge after risk_score routes to notify on high risk, skips to END on low risk. Both branches verified against mock data. Repo created (regression-agent-langgraph), pushed to GitHub after resolving divergent-histories merge.

- [x] **Session 3 — Real integration.** Swapped stub logic for actual CodeAnalyzer and EndpointMapper classes from the production Regression Analyzer codebase, pasted in unmodified. Built minimal local models.py/config.py/utils.py stand-ins (trimmed pydantic models, no GitHub/OpenAI dependency needed for this exercise) so the real classes could run standalone. Built a sample_codebase/experts/views.py fixture mirroring the doc's own Expert Onboarding API example, for EndpointMapper's AST indexer to walk.
  - Fixed a real bug surfaced by real data: initial risk_score stub used len(dependencies) as the signal, which misclassified a single high-confidence, high-impact endpoint change as low risk. Corrected to use max(confidence) and impact_level from the actual AffectedEndpoint objects.
  - Confirmed high-risk branch: a change to the routed onboard_expert endpoint was correctly detected (confidence 0.9, impact high), scored high risk, routed to notify, printed the real reasoning string.
  - Confirmed low-risk branch, two cases: an empty diff (trivially low risk), and a change to validate_and_create — a helper function called directly by onboard_expert but not itself a routed endpoint. EndpointMapper found zero dependencies for this change, since it only does direct name-matching against routed endpoints and cross-file import detection, not intra-file call-graph tracing. This reproduced, with a concrete example, the "known limitation" the Regression Analyzer doc itself names (complex import chains may not be fully traced) — a real blind spot, not a wiring mistake, useful as interview material on the system's actual limits.
  - Noted for future cleanup, not urgent: _code_change (a full CodeChange pydantic object) is passed through LangGraph state without being declared as a typed channel value beyond a bare type hint — works, but is a shortcut rather than a pattern to repeat.

- [ ] **Session 4 — Stretch, MCP touchpoint.** Expose dependency_lookup as a tool the graph's LLM can choose to call rather than a hardcoded step. First point where the system earns real LLM-controlled routing, per the Session 1 definition of agentic.

- [ ] **Session 5 — EM synthesis.** When to hand orchestration control to an LLM versus keep it deterministic. Cost and reliability tradeoffs. Tie into interview narrative alongside the RAG lifecycle answers and the concrete known-limitation example from Session 3.

---

## How to resume in a new thread

Paste this file back in, confirm which session to start from, and re-attach the Regression Analyzer document for grounding.
