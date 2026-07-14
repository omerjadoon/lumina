# Architecture: Legal Investigation Agent

---

## Overview

A single-process CLI agent that accepts a high-level legal investigation goal, plans its own
investigation across a local document corpus, executes using local tools, adapts when evidence
is missing or conflicting, and produces a structured report.

Four files. One loop. No framework.

---

## File Structure

```
agent/
  runner.py     ← entry point, agent loop, tool dispatch, inline logging
  planner.py    ← all LLM calls and prompts
  tools.py      ← list_files, read_file, search_in_file
  state.py      ← InvestigationState and Note dataclasses (~20 lines)

eval/
  harness.py    ← scenario runner and LLM judge scorer
  rubric.py     ← 10 adversarial judge criteria
  scenarios.py  ← 4 test scenarios (happy path + 3 failure/recovery)

data/documents/ ← plain text legal document corpus
results/        ← eval output JSON
logs/           ← per-run JSONL trace files
```

---

## Responsibilities

| File | Owns | Does NOT own |
|---|---|---|
| `runner.py` | Loop, convergence, tool dispatch, logging | LLM prompts, tool implementations |
| `planner.py` | All LLM calls, all prompt construction | State mutation, tool calls |
| `tools.py` | File operations and search | Anything LLM-related |
| `state.py` | Data contracts only | How state is used |

Each file has one reason to change. Swapping the LLM provider touches only `planner.py`.
Adding a tool touches only `tools.py` and the `match` in `runner.py`.

---

## State Model

```python
# state.py

@dataclass
class Note:
    kind: Literal["finding", "gap", "conflict"]
    category: str    # IP Ownership | Contractual Obligations | Litigation & Liabilities |
                     # Corporate Structure | Regulatory & Compliance
    description: str
    sources: list[str]

@dataclass
class InvestigationState:
    goal: str
    plan: list[str]           # ordered questions to answer
    current_step: int
    notes: list[Note]         # findings, gaps, and conflicts unified
    documents_read: list[str] # filenames already consumed
    iterations: int
    status: str               # "investigating" | "concluding" | "done"
```

**Why one `Note` dataclass, not three:** `Finding`, `Gap`, and `Conflict` are structurally
identical — each is a category, a description, and one or more source references. Separate
dataclasses signal a type system, not a judgment call. A `kind` field carries the same
information with less code.

**Why structured state, not message history:** Message history grows O(n) with loop steps.
The state summary passed to every LLM call is O(1) — it is always the current snapshot, never
the full transcript. After 10 tool calls, raw message history is thousands of tokens of
redundant content. Structured state is ~200 tokens regardless of how many steps have run.

**Why not a plain dict:** Both `runner.py` and `planner.py` import `InvestigationState`.
A typed dataclass is a shared contract — it makes field names explicit and `repr` readable
in logs. At this scale the overhead is zero.

---

## Execution Loop

```
run_investigation(goal, documents_dir)
│
├── 1. LIST available documents (tools.list_files)
│
├── 2. PLAN
│     planner.plan(goal, available_docs) → state.plan
│     _log("plan", ...)
│
└── 3. LOOP while state.status == "investigating"
      │
      ├── 3a. SELECT current question from state.plan[state.current_step]
      │
      ├── 3b. EXECUTE
      │     planner.select_tool(state, question)
      │     → {tool, args}
      │     tools.<tool>(**args) → raw_result
      │     _log("tool_call", ...)
      │
      ├── 3c. OBSERVE
      │     planner.observe(state, question, raw_result)
      │     → {note: Note, decision: "continue"|"replan"|"conclude"}
      │     state.notes.append(note)
      │     _log("observation", ...)
      │
      ├── 3d. DECIDE
      │     "continue"  → state.current_step += 1
      │     "replan"    → planner.replan(state) → revised remaining steps
      │                   _log("replan", ...)
      │     "conclude"  → state.status = "concluding"
      │
      ├── 3e. GUARD
      │     state.iterations += 1
      │     if iterations >= MAX_ITERATIONS → state.status = "concluding"
      │
      └── 3f. CONCLUDE
            planner.conclude(state) → report string
            _log("report", ...)
            return report
```

**Why a flat while-loop:** It maps directly to plan → act → observe → adapt. A reviewer
reads it in under a minute. No inheritance, no coroutines, no event bus.

**Why `planner.select_tool` as a separate LLM call from `planner.observe`:** These are
distinct decisions — "which tool to use" and "what does the result mean." Merging them into
one call produces a prompt that tries to do two things, which degrades output quality and
makes the prompt harder to read and tune.

**Why `MAX_ITERATIONS` guard:** Required by the PRD. An agent that loops without converging
is a broken agent. The guard is the simplest possible robustness mechanism — one integer
comparison, one state transition.

---

## Tools

```python
# tools.py

def list_files(directory: str) -> list[str]
def read_file(directory: str, filename: str) -> str      # truncated to MAX_CHARS
def search_in_file(directory: str, filename: str, query: str) -> str  # matching lines only
```

Three tools. The agent selects one per loop step via structured output from `planner.select_tool`.
Dispatch in `runner.py` is a `match` statement — no registry, no decorators, no dynamic dispatch.

**Why keyword search, not embeddings:** Keyword search fails loudly and clearly. If
`search_in_file` returns nothing, the agent knows the term is absent. Vector similarity
returns results regardless — a low-score match looks identical to a high-score match from
the agent's perspective, making gaps invisible. Transparency beats sophistication here.

**Why `read_file` truncation:** A document could be 20,000 characters. The agent answers
one specific question per step — it does not need the full text. Truncation is the forcing
function that makes the tool loop earn its existence. If the agent needs more, it calls
`search_in_file` with a targeted query.

**What was removed:** A fourth tool — `list_read_files` — appeared in the initial design.
It was state inspection dressed up as a tool. The agent checks `state.documents_read`
directly. Removed.

---

## Planner: LLM Calls

All LLM calls are in `planner.py`. All prompts are constructed inline in the function that
uses them — no separate context assembly module.

| Function | Input | Output |
|---|---|---|
| `plan(goal, docs)` | Goal string + filenames | `list[str]` — ordered questions |
| `select_tool(state, question)` | State summary + question | `{tool, args}` |
| `observe(state, question, result)` | State summary + result | `{note, decision}` |
| `replan(state)` | Full state summary | Revised remaining `list[str]` |
| `conclude(state)` | State summary (notes only) | Report string |

All calls use `response_format={"type": "json_object"}` where structured output is needed.
All calls use `temperature=0` for the planner. `observe` and `replan` use a slightly higher
temperature (0.3) to allow creative recovery when evidence is thin.

**Why prompts inline in each function:** A `context.py` module for prompt assembly is
abstraction without benefit. Prompt construction is f-strings. Extracting f-strings into
their own module means a reader must open two files to understand one LLM call. Inline
prompts mean the call and its instructions are always in the same place.

**Why `conclude` receives only notes, not raw tool outputs:** The report is a synthesis of
structured findings, not a memory of tool calls. Passing raw tool outputs to `conclude`
would invite the LLM to hallucinate details from earlier in the run. Notes are what the
agent explicitly decided to record — that is the ground truth for the report.

---

## Replanning

Triggered when `planner.observe` returns `decision: "replan"`. Conditions:

- A required document is missing (Gap created, raw result empty)
- A contradiction detected between two documents (Conflict created)
- Current question is unanswerable from available evidence

`planner.replan(state)` receives the full current state and returns a revised list of
**remaining** steps only. Already-answered steps are preserved. The replanner does not
restart — it appends or replaces only what is still open.

**What replanning looks like in practice:** In scenario S2 (missing litigation register),
the agent tries to read the file, gets nothing, creates a Gap note, and replans. The
replanner adds: "search all remaining documents for any mention of disputes or claims."
If that also yields nothing, the gap is confirmed and the agent moves to the next category.
This two-attempt pattern prevents a single missing document from producing a silently
clean report.

---

## Logging

A single `_log(event: str, payload: dict)` helper lives at the top of `runner.py`.
It writes to two sinks on every call:

**Stdout** — human-readable, prefixed with the event type:
```
[PLAN]      Step 1: Confirm IP ownership of LexScan v1
            Step 2: Check for change-of-control clauses in client contracts
            ...
[TOOL]      search_in_file · nexus_ip_assignment.txt · query="LexScan"
[RESULT]    3 lines matched (142 chars)
[OBSERVE]   finding · IP Ownership · IP assigned from Vasquez to Nexus
[DECIDE]    continue → step 2
[REPLAN]    gap: litigation register missing. Added fallback step.
[CONCLUDE]  Report written (1,240 chars)
```

**File** — one JSONL file per run at `logs/run_<timestamp>.jsonl`. Each line is a
self-contained JSON object with an `event` field and a `ts` timestamp:
```json
{"event": "tool_call", "tool": "search_in_file", "filename": "nexus_ip_assignment.txt", "query": "LexScan", "result_chars": 142, "ts": "..."}
{"event": "observation", "step": 2, "kind": "finding", "category": "IP Ownership", "decision": "continue", "ts": "..."}
{"event": "replan", "reason": "gap", "new_steps": ["search all docs for dispute mentions"], "ts": "..."}
```

**Why JSONL for file logs:** Machine-readable without parsing. The eval harness can replay
a run's trace to reconstruct exactly what the agent did and when. Trivially greppable.

**Why not Python's `logging` module:** Its handler/formatter/level hierarchy is configuration
complexity that provides no benefit at this scale. Two lines of direct `print` and `file.write`
are simpler, more readable, and easier to demo in a five-minute video.

**Why not a separate `tracer.py`:** Two functions do not justify a module. The helper lives
in `runner.py` where it is called. Moving it to its own file would mean a reader opening
`runner.py` sees logging calls but must open a second file to understand them.

---

## Persistence

None, intentionally. Each run is self-contained. The JSONL log is the durable record.
State lives only in memory for the duration of one `run_investigation` call.

**Why not SQLite or file-based state:** The PRD lists persistent memory as out of scope.
Persistence implies resumability, which implies process-level failure recovery, which is
substantially more code for zero evaluation benefit. If the process dies mid-run, re-run it.

---

## Evaluation Seam

```python
# runner.py
def run_investigation(goal: str, documents_dir: str) -> str:
    ...
    return report   # plain string
```

The harness calls `run_investigation`, receives a string, passes it to the LLM judge.
The agent knows nothing about the eval harness. The harness knows nothing about the
agent's internals. This is the only interface between them.

**Why a plain string:** The judge prompts are written to evaluate a prose report.
The structured findings live in `InvestigationState` and are rendered into prose by
`planner.conclude`. The report is what a real tool would produce for a real user.

---

## What Was Deliberately Removed

| Removed | Why it existed | Why it was cut |
|---|---|---|
| `context.py` | Prompt assembly responsibility | F-strings in a module are not abstraction; they are indirection |
| `tracer.py` | Logging responsibility | Two functions do not justify a file |
| `Finding`, `Gap`, `Conflict` as separate dataclasses | Type correctness | Structurally identical; `kind` field carries the same information |
| `list_read_files` tool | Completeness | State inspection is not a tool; it is a dict lookup |
| Vector search | Technical interest | Transparent failure matters more than recall quality here |
| `run_python` tool | Generality | Legal document analysis does not require code execution; removes an entire risk class |

---

## Investigation Categories

The agent's plan must cover all five. The eval rubric scores per category.

| Category | What must be established |
|---|---|
| IP Ownership | Who owns the core IP? Are there third-party claims or encumbrances? |
| Contractual Obligations | Change-of-control clauses, consent requirements, termination rights |
| Litigation & Liabilities | Active or threatened claims, unresolved liabilities |
| Corporate Structure | Valid incorporation, shareholder rights, transfer restrictions |
| Regulatory & Compliance | Required registrations, enforcement history, authorisation status |

---

## Summary

The architecture is four files, one loop, and a clean seam to the eval harness.
Every component exists because removing it would make the system harder to understand,
not because it demonstrates capability. The components that were removed existed because
they looked correct in a design document — they did not survive the question: *if you
deleted this and inlined its contents, would the code be harder to read?*
