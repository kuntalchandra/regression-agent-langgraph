# Agentic Workflow Study — Phase 2: Multi-Step Loops
## Progress Tracker

Goal: extend the single-decision-point graph from Phase 1 (regression-agent-langgraph) into a genuine planning → execution → reflection loop — the piece of the Regression Analyser doc's own definition of "agentic" that Phase 1 explicitly did not build.

Repo: regression-agent-langgraph (same repo, new branch or continued on main — decide at Session 1).

Grounding: Phase 1 built one LLM-controlled edge (decide whether to call dependency_lookup). Phase 2's target: when dependency_lookup returns low-confidence or ambiguous results, let the LLM decide to loop — re-examine the diff with different framing, try a different tool, or escalate — instead of always flowing straight to risk_score.
---

## Session-by-session plan

- [ ] **Session 1 — Concepts.** What actually distinguishes a loop from a single decision point. LangGraph's mechanism for cycles (edges that can route back to an earlier node, not just forward). What "reflection" means concretely — the LLM evaluating its own tool result quality, not just deciding whether to call a tool. Where this could go wrong: unbounded loops, cost blowup, the need for a max-iteration guard. Honest scoping check before building: is this genuinely a new capability, or just Session 4's single edge repeated — same rigor Phase 1 applied to "agentic" itself.

- [ ] **Session 2-3 — Build.** Add a reflection node after dependency_lookup that evaluates confidence of returned AffectedEndpoint results. If confidence is low across the board, let the LLM decide: retry with adjusted framing, accept the result as-is, or escalate to risk_score flagged as low-confidence. Add a hard iteration cap regardless of LLM preference, and log why.

- [ ] **Session 4 — Test against real and adversarial cases.** Confirm the loop actually triggers on genuinely ambiguous input (not just re-running Phase 1's clean examples). Test that the iteration cap actually stops runaway loops. Test cost: token count per full loop vs Phase 1's single-decision cost.

- [ ] **Session 5 — EM synthesis.** When does a loop earn its added cost and complexity over a single decision point? Extend Phase 1's four-axis framework with a fifth consideration specific to loops: bounded vs unbounded iteration, and how you'd justify a max-retry cap to someone worried about cost or latency in production. Tie into interview narrative alongside Phase 1's material.

---

## How to resume in a new thread

Paste this file back in, confirm which session to start from, re-attach the Regression Analyzer document, and paste Phase 1's agentic_workflow.md for grounding on what's already built.
