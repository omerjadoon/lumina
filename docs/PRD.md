# Product Requirements Document
## Legal Investigation Agent

---

## Problem Statement

Legal professionals conducting acquisition due diligence must manually review large volumes of documents — contracts, corporate filings, IP assignments, litigation records — to answer a single high-level question. This is slow, error-prone, and fails to adapt when evidence is missing or contradictory. Existing document review tools follow fixed pipelines; they do not reason about what to look for next.

---

## Goal

Build a minimal AI agent that accepts a high-level legal investigation goal, plans its own investigation across a corpus of local documents, adapts when evidence is missing or conflicting, and produces a structured report — demonstrating genuine plan-act-observe-adapt behaviour throughout.

---

## Target User

An AI engineering reviewer evaluating whether the candidate can build a real agent loop, measure it honestly, and exercise sound engineering judgment under time pressure.

Secondary: A legal professional who needs to answer an acquisition feasibility question from a folder of documents, without writing queries or navigating a UI.

---

## Scope

- Single-session CLI agent
- One high-level investigation goal per run (e.g. "Can Company A safely acquire Company B?")
- Local document corpus only (plain text / markdown files)
- Agent generates its own investigation plan
- Agent executes plan using local tools, observing results after each step
- Agent adapts: re-plans when a document is missing, re-investigates when findings conflict
- Agent produces a structured final report
- Runnable evaluation harness with pre-defined hidden rubric
- README documenting decisions, trade-offs, and time allocation

---

## Out of Scope

- Web search or any external API calls beyond the LLM
- Multi-agent or orchestrator/worker architectures
- Persistent memory across sessions
- User authentication or multi-user support
- GUI or web interface
- Streaming output or real-time UI updates
- Support for PDF, Word, or binary document formats
- Production deployment, containerisation, or cloud infrastructure
- Legal correctness — this is a demonstration of agent behaviour, not legal advice

---

## Functional Requirements

### FR-1: Goal Ingestion
The agent accepts a natural-language investigation goal from the user via CLI.

### FR-2: Plan Generation
Given the goal, the agent produces a structured investigation plan — a prioritised list of questions it needs to answer and the documents or document types it expects to consult.

### FR-3: Tool Execution
The agent executes its plan using a small, fixed set of local tools. Each tool call is logged with its input, output, and the agent's interpretation.

### FR-4: Adaptive Re-planning
When a tool returns no useful result (document missing, clause absent, conflicting evidence), the agent explicitly decides: continue with partial information, seek an alternative document, or flag the gap. This decision is logged and visible.

### FR-5: State Tracking
The agent maintains a running investigation state — what has been established, what is still open, what has been flagged — and uses this state to inform each subsequent decision.

### FR-6: Final Report
On completion, the agent produces a structured report covering: findings, gaps, conflicts, and a conclusion addressing the original goal.

### FR-7: Evaluation Harness
A separate, runnable harness executes the agent against a suite of test scenarios and scores each run against the hidden rubric. Results are written to a file.

---

## Non-Functional Requirements

### NFR-1: Observability
Every agent decision — plan step, tool call, observation, re-plan — must be printed to stdout in a readable, structured format. A reviewer must be able to follow the agent's reasoning without reading the source code.

### NFR-2: Simplicity
The agent loop must be readable in a single sitting. No unnecessary abstraction layers. Total implementation target: under 500 lines of Python excluding eval harness.

### NFR-3: Robustness
The agent must not crash on tool failure. It must handle missing documents, empty results, and unexpected content without raising unhandled exceptions.

### NFR-4: Determinism of Eval
The evaluation harness must produce the same scores on repeated runs against the same document corpus. Scoring criteria are defined before implementation and do not change based on what the agent produces.

### NFR-5: Reproducibility
A reviewer must be able to clone the repo, run one setup command, and execute both the agent and the eval harness successfully.

---

## Success Criteria

| Criterion | Threshold |
|---|---|
| Agent generates a non-trivial investigation plan (3+ distinct questions) | Required |
| Agent completes at least one recovery cycle (re-plans after missing/conflicting evidence) | Required |
| Eval harness covers at least 4 scenarios including at least 2 failure/recovery cases | Required |
| Eval harness produces objective pass/fail scores per scenario | Required |
| Final report addresses the original goal with explicit reference to evidence | Required |
| Agent loop code is readable without inline explanation | Required |
| Reviewer can run the full system cold from README alone | Required |
| Eval results reveal at least one honest weakness of the agent | Required |

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Agent re-plans infinitely without converging | Medium | High | Hard cap on iteration count; agent must conclude at N steps |
| Context window grows unmanageable across long runs | Medium | High | Summarise intermediate findings into state; do not accumulate raw tool outputs |
| Eval rubric is too easy — all scenarios pass | Medium | High | Write rubric before building; include at least one scenario the agent is likely to fail |
| Self-planning loop is too vague — agent produces unfocused plans | Medium | Medium | Structured plan schema (not free prose); constrain output format |
| Test documents are too clean — no natural failure modes | Low | High | Deliberately plant missing documents and contradictory clauses before writing eval harness |
| Implementation overruns 5-hour budget | Medium | Medium | Cut FR-6 report formatting if necessary; eval harness is higher priority |

---

## Engineering Trade-offs

| Decision | Choice | Rejected Alternative | Reason |
|---|---|---|---|
| Agent planning | LLM generates its own plan | Pre-defined checklist | Checklist caps the 40% harness engineering score; self-planning is the point |
| Eval strategy | Pre-defined hidden rubric scored against agent output | LLM-as-judge | LLM-as-judge introduces non-determinism and circular reasoning; rubric is objective |
| Interaction model | CLI | Web UI | UI complexity would consume time better spent on the agent loop and eval |
| Document format | Plain text / markdown | PDF / DOCX | Binary formats add parsing complexity with no evaluation benefit |
| State representation | Structured dict / dataclass | Prose accumulated in prompt | Prose state is fragile and grows context; structured state is inspectable and controllable |
| Scope | Single domain, one scenario type | Multi-domain generalisation | Assignment explicitly penalises unnecessary complexity; narrow and polished scores higher |
