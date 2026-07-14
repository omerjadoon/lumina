# Implementation Tasks

## Status legend
- `[ ]` not started
- `[x]` complete

---

## Milestone 1 — Core data model (`agent/state.py`)

Single file, no LLM dependency. Do this first so every later file has a shared import.

- [x] **M1.1** Create `agent/__init__.py` (empty)
- [x] **M1.2** Create `agent/state.py` with `Note` and `InvestigationState` dataclasses exactly as specified in `docs/architecture.md`

**Done when:** `from agent.state import Note, InvestigationState` succeeds and `repr()` on both dataclasses is readable.

---

## Milestone 2 — Tools (`agent/tools.py`)

Pure file I/O. No LLM, no state imports.

- [x] **M2.1** Implement `list_files(directory: str) -> list[str]` — returns sorted list of filenames in the directory
- [x] **M2.2** Implement `read_file(directory: str, filename: str) -> str` — reads the file, truncates to `MAX_CHARS = 8000`
- [x] **M2.3** Implement `search_in_file(directory: str, filename: str, query: str) -> str` — returns all lines containing the query (case-insensitive), joined with newlines; returns empty string if none match or file not found

**Done when:** All three functions return correct output for the documents in `data/documents/` and return graceful empty/error strings on bad inputs (no exceptions).

---

## Milestone 3 — Planner (`agent/planner.py`)

All LLM calls live here. Requires `OPEN_AI_KEY` in environment.

- [x] **M3.1** Implement `plan(goal: str, docs: list[str]) -> list[str]` — returns an ordered list of investigation questions (3–8 items). Prompt instructs the model to cover all five categories: IP Ownership, Contractual Obligations, Litigation & Liabilities, Corporate Structure, Regulatory & Compliance.
- [x] **M3.2** Implement `select_tool(state: InvestigationState, question: str) -> dict` — returns `{"tool": str, "args": dict}` via JSON structured output. Tool must be one of `list_files`, `read_file`, `search_in_file`.
- [x] **M3.3** Implement `observe(state: InvestigationState, question: str, result: str) -> dict` — returns `{"note": Note, "decision": "continue"|"replan"|"conclude"}` via JSON structured output. Use `temperature=0.3`.
- [x] **M3.4** Implement `replan(state: InvestigationState) -> list[str]` — returns revised remaining plan steps (does not include already-completed steps). Use `temperature=0.3`.
- [x] **M3.5** Implement `conclude(state: InvestigationState) -> str` — generates the final prose report from `state.notes` only (not raw tool outputs). Report must address: findings, gaps, conflicts, and a conclusion on the original goal.

**Prompt requirements for all functions:**
- Inline prompts (f-strings), no separate prompt file
- State summaries passed to LLM are always the current snapshot, never accumulated message history
- `plan`, `select_tool`, `observe`, `replan` use `response_format={"type": "json_object"}`
- `plan` and `select_tool` use `temperature=0`; `observe` and `replan` use `temperature=0.3`

**Done when:** Each function can be called in isolation and returns the expected type without raising.

---

## Milestone 4 — Runner (`agent/runner.py`)

The loop. Imports from all three other agent files.

- [x] **M4.1** Implement `_log(event: str, payload: dict)` — writes human-readable stdout line and appends a JSONL line to `logs/run_<timestamp>.jsonl`. Create `logs/` if absent.
- [x] **M4.2** Implement `run_investigation(goal: str, documents_dir: str) -> str` — the main entry point as specified in `docs/architecture.md`. Sequence:
  1. `list_files` to discover documents
  2. `planner.plan` to build `state.plan`
  3. While loop until `state.status != "investigating"` or `iterations >= MAX_ITERATIONS` (default: 20)
  4. Each iteration: `select_tool` → tool dispatch via `match` → `observe` → decide `continue/replan/conclude`
  5. On conclude or guard: `planner.conclude` → return report string
- [x] **M4.3** Add CLI entry point: `if __name__ == "__main__"` block that reads `goal` from `sys.argv[1]` and `documents_dir` from `sys.argv[2]` (default: `data/documents`), then prints the returned report.
- [x] **M4.4** Verify tool dispatch uses a `match` statement (not `getattr` or a dict of callables)

**Done when:** `python agent/runner.py "Can Orion Capital safely acquire Nexus Legal Technologies?" data/documents` runs end-to-end, prints structured logs to stdout, writes a JSONL trace to `logs/`, and returns a non-trivial report.

---

## Milestone 5 — End-to-end smoke test

Manual verification before running the eval harness.

- [ ] **M5.1** Run the agent on S1's goal with the full `data/documents` corpus. Confirm:
  - Log shows `[PLAN]`, `[TOOL]`, `[OBSERVE]`, and `[CONCLUDE]` events
  - At least one `[REPLAN]` or `[OBSERVE] decision=replan` triggered (the Imperial licence conflict should cause this)
  - Final report mentions: IP assignment, Imperial College licence, Alpha & Partners, DataVault, Meridian Ventures, ICO
- [ ] **M5.2** Run the agent with `data/documents` minus `nexus_litigation_register.txt`. Confirm:
  - Agent flags litigation status as a gap
  - Report does not fabricate litigation details

---

## Milestone 6 — Eval harness run

The harness is already implemented (`eval/harness.py`). This milestone wires it to the agent.

- [ ] **M6.1** Run `python eval/harness.py --scenario S1` and record the score
- [ ] **M6.2** Run `python eval/harness.py --all --output results/eval_results.json`
- [ ] **M6.3** Review scores. If any required criterion fails:
  - Read the criterion's judge prompt in `eval/rubric.py`
  - Trace which plan step and which `observe` output covers that criterion
  - Fix the planner prompt (not the rubric) to improve coverage
- [ ] **M6.4** Re-run `--all` after any prompt fixes. Target: all 5 required criteria pass on S1; S2–S4 meet their `minimum_required_pass` thresholds.

---

## Milestone 7 — README

- [x] **M7.1** Write `README.md` covering:
  - Setup (one command: `pip install openai`, set `OPEN_AI_KEY`)
  - How to run the agent
  - How to run the eval harness
  - Architecture summary (4 files, 1 loop) with a pointer to `docs/architecture.md`
  - Honest evaluation of at least one known weakness surfaced by the eval results

---

## Implementation order

```
M1 (state) → M2 (tools) → M3 (planner) → M4 (runner) → M5 (smoke) → M6 (eval) → M7 (README)
```

M1 and M2 have no LLM dependency and can be verified offline. M3 requires the API key but each
function is independently testable. M4 is last because it depends on all three.

---

## File checklist

```
agent/__init__.py          ← empty, M1.1
agent/state.py             ← M1.2
agent/tools.py             ← M2
agent/planner.py           ← M3
agent/runner.py            ← M4
logs/                      ← created at runtime by M4.1
results/                   ← created at runtime by M6.2
README.md                  ← M7
```

Already complete:
```
eval/harness.py            ✓
eval/rubric.py             ✓
eval/scenarios.py          ✓
eval/__init__.py           ✓
data/documents/            ✓ (7 documents)
docs/PRD.md                ✓
docs/architecture.md       ✓
```
