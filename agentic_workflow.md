# Agentic Workflow Study — LangGraph
## Progress Tracker

Goal: hands-on understanding of agentic workflows, grounded in the Regression Analyzer's existing deterministic pipeline. Full detail lives here; README.md has the project overview only.

---

## Session-by-session plan

- [x] **Session 1 — Concepts.** Agentic vs fixed pipeline: control of flow is the property, not LLM presence. Regression Analyzer today runs an LLM reasoning step inside a deterministic pipeline — the LLM doesn't decide the steps. Corrected framing: agentic comes in degrees. A single conditional edge is genuinely agentic, just narrow in scope, not "theoretical."

- [x] **Session 2 — Build.** Four-node graph with stub logic: parse_diff, dependency_lookup, risk_score, notify. Conditional edge after risk_score routes to notify on high risk, skips on low. Both branches verified against mock data.

- [x] **Session 3 — Real integration.** Swapped stubs for the real CodeAnalyzer and EndpointMapper classes, unmodified, plus a sample_codebase fixture for EndpointMapper's AST indexer to walk. Fixed a real bug the stub logic masked: len(dependencies) misclassified a single high-confidence, high-impact change as low risk — corrected to use max(confidence) and impact_level from real AffectedEndpoint objects. Reproduced, with a concrete example, EndpointMapper's known limitation: it can't trace intra-file call-graph dependencies, only direct name matches and cross-file imports.

- [x] **Session 4 — LLM-controlled routing.** Scoped honestly: this is agentic via LangGraph tool-binding, not a literal MCP server — MCP is a protocol layer around this same decision, not required for the agentic property itself. Replaced the fixed parse_diff → dependency_lookup edge with an LLM decision node using Gemini. Tested two diffs modifying the identical function name — a real logic change and a comment-only addition — and the LLM correctly distinguished them, something a name-matching rule couldn't do. risk_score → notify stays deterministic; it's a threshold, no judgment for a model to add.

- [x] **Session 5 — EM synthesis.** Four-axis framework for agentic vs deterministic: context-dependence, cost/reversibility of a wrong decision, per-decision LLM cost at volume, testability. Applied to this graph: the parse_diff → dependency_lookup edge earned being agentic on all four axes; risk_score → notify correctly stayed deterministic.
  - Reversibility, refined under pressure-testing: the original framing ("cheap failure, human review catches it") missed that PR review always happens regardless of what notify decides — so the real question isn't whether review happens, but what the reviewer knows going in. A wrong LLM decision to skip dependency_lookup doesn't cause a broken deploy, but it does silently revert that one PR to the exact baseline risk the tool exists to reduce — no worse than not having the tool, but not neutral either. The sharper line: a safe-to-automate decision degrades to baseline on failure; an unsafe one (auto-merge, skipping a security scan) actively creates risk beyond baseline. That distinction, not "someone eventually looks at it," is what actually determines whether a decision is safe to hand to a model.
  - Testability named as an open gap, not solved: a threshold is trivially unit-testable, same input same output. An LLM-controlled edge isn't guaranteed to route the same diff the same way twice, and the existing deterministic testing philosophy has no answer for that yet.
  - Final answer drafted and stress-tested through three revision passes — moved from asserting the distinction abstractly, to citing the same-function-name test as evidence, to correcting a factual error about which edge the LLM actually controls, to fixing the reversibility argument after it was shown to conflate "review happens" with "review is informed."