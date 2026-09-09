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

- [x] **Session 4 — MCP touchpoint, via LLM tool-calling (not a literal MCP server).** Scoping decision made explicit: literal MCP is a protocol layer (standardized tool schema, client-server boundary); what actually makes an edge agentic is the LLM deciding whether to act, which LangGraph's native tool-binding provides directly. Built accordingly — real MCP server noted as a productionization step, not required for the agentic property itself.
  - Replaced the fixed parse_diff → dependency_lookup edge with an LLM decision node (decide_dependency_check) using Gemini with a bound tool (check_dependencies). The LLM sees the real parsed CodeChange (file, change type, functions modified, diff) and decides whether to call the tool; the tool call itself carries only a reasoning string, the actual EndpointMapper call still runs on real state data, not anything the LLM constructs.
  - Hit a live model deprecation error (gemini-2.0-flash no longer available), resolved by switching to gemini-3.6-flash per the error message's own suggestion — same category of gotcha as the RAG project's model deprecation lesson.
  - Confirmed positive case: real change to the onboard_expert endpoint — Gemini called check_dependencies with independently generated reasoning about routing/business logic impact, routed to dependency_lookup, found the real endpoint, scored high risk, notify fired.
  - Confirmed negative case, the more important one: a comment-only addition above the same onboard_expert function (functions_modified identical to the positive case) — Gemini explicitly reasoned that a non-functional comment doesn't alter execution logic or API contracts, declined the tool call (tool_calls: []), routed straight to risk_score, empty dependencies, low risk, no notify. Same function name, opposite routing decision, driven by the model reading diff content rather than a rule matching on functions_modified. This is the concrete evidence that the edge is genuinely LLM-controlled, not just an LLM-flavored rule.
  - Honest scope note for interview framing: this is one genuinely agentic edge in an otherwise fixed graph, not an agent. The system still can't loop back, retry, or re-plan after seeing a tool result — decision-making at a single point, not full autonomy. Keep this distinction sharp; don't overclaim "agentic" to mean more than what was actually built.

- [ ] **Session 5 — EM synthesis.** When to hand orchestration control to an LLM versus keep it deterministic. Cost and reliability tradeoffs of LLM-controlled routing (token cost per decision, latency, non-determinism) versus a fixed threshold. Tie into interview narrative alongside the RAG lifecycle answers and the concrete known-limitation example from Session 3, plus the positive/negative tool-calling proof from Session 4.

---

## How to resume in a new thread

Paste this file back in, confirm which session to start from, and re-attach the Regression Analyzer document for grounding.
