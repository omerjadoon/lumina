# Improvement Plan

Derived from the post-implementation review. Tasks are ordered by impact on the hiring
evaluation score. Each task references the specific rubric criterion or review finding
it addresses.

## Status legend

- `[ ]` not started
- `[~]` in progress
- `[x]` complete

---

## P1 — Corpus integrity fix (invalidates gap tests)

**Review finding:** `CORPUS_INDEX.txt` lists the planted gaps explicitly. An agent that
reads this file knows what to flag without detecting it from missing evidence. Scenarios
S2, S3, and criteria CONTRACT-02, CORP-02 are unreliable while this file is in the corpus.

- [x] **I1.1** Move `data/documents/CORPUS_INDEX.txt` to `docs/CORPUS_INDEX.txt`
- [x] **I1.2** Update `docs/CORPUS_INDEX.txt` header to clarify it is a human-readable
  design reference, not an agent-accessible document
- [x] **I1.3** Verify `agent/tools.list_files("data/documents")` no longer returns it

**Affected scores:** S2 LIT-01/LIT-02 gap detection, S3 IP-01 gap detection, CONTRACT-02, CORP-02

---

## P2 — Wire `agent/planner.py` to import from `prompts/`

**Review finding:** `prompts/` contains a richer, designed prompt set that is never
imported. `agent/planner.py` uses different inline f-strings. A reviewer cannot tell which
is authoritative. `prompts/` is the correct single source of truth — keeping prompts
in dedicated files makes them easier to update and review independently of execution logic.

The designed prompts in `prompts/` are strictly better:
- `prompts/planner.py` — structured tasks with `category`, `question`, `approach` fields
- `prompts/replanner.py` — 6-action control (continue/retry/insert_task/modify_task/remove_task/abort)
- `prompts/executor.py` — includes `decision` + `expected_outcome` fields alongside tool/args
- `prompts/summarizer.py` — report writer system prompt (max 800 words, 5 headings + CONCLUSION)

Plan: update `agent/planner.py` to import SYSTEM/USER strings from `prompts/*.py` and
adopt the richer schemas. The `prompts/` directory stays — it is the single source of
truth for all prompt templates.

- [x] **I2.1** Upgrade `plan()` to return structured task dicts (`step`, `category`, `question`, `approach`) instead of bare strings. Update `InvestigationState.plan` type accordingly. Import system/user prompt strings from `prompts/planner.py`.
- [x] **I2.2** Update `runner.py` to read `question` from the task dict; log `category` in `[DECIDE]` events
- [x] **I2.3** Upgrade `observe()` → `replan()` pipeline to use the 6-action control schema from `prompts/replanner.py`. Implement `retry` (max 2 attempts per step before declaring gap) and `insert_task` (add a specific new task rather than rewriting all remaining steps). Import prompt strings from `prompts/replanner.py`.
- [x] **I2.4** Update `select_tool()` to log `decision` and `expected_outcome` from the executor prompt. Import prompt strings from `prompts/executor.py`.
- [x] **I2.5** Update `conclude()` to use the system prompt from `prompts/summarizer.py` instead of the inline f-string.
- [x] **I2.6** Remove inline f-string prompt templates from `agent/planner.py` once all five functions import from `prompts/`. The `prompts/` directory is kept as the authoritative source.

**Affected scores:** Prompt Engineering (design/implementation coherence), Code Quality

---

## P3 — Add system prompts to all five planner functions

**Review finding:** All five LLM calls in `planner.py` use a single user message only.
The system/user distinction improves instruction following. Costs five lines per function.

- [x] **I3.1** Add system prompt to `plan()` — role: investigation planner, instruction: return JSON only
- [x] **I3.2** Add system prompt to `select_tool()` — role: executor, instruction: single tool selection
- [x] **I3.3** Add system prompt to `observe()` — role: observer, instruction: classify strictly; conflict when result contradicts any prior note
- [x] **I3.4** Add system prompt to `replan()` — role: replanner, instruction: adapt remaining steps minimally
- [x] **I3.5** Add system prompt to `conclude()` — role: report writer, instruction: synthesise from notes only

**Affected scores:** Prompt Engineering, LLM call quality, IP-02 / LIT-02 pass rate

---

## P4 — Fix observe() truncation inconsistency

**Review finding:** `read_file` returns up to 8000 chars. `observe()` previews only
`result[:2000]`. Content in characters 2001–8000 is invisible to the model. IP conflicts
and litigation details that appear mid-document are silently dropped.

- [x] **I4.1** Increase `observe()` preview to `result[:6000]` (leaves 2000 chars headroom for the prompt and state summary within a 128k context window)
- [x] **I4.2** Document the truncation limit in a comment at the `result_preview` line
- [x] **I4.3** Add a `MAX_OBSERVE_CHARS` constant alongside `MAX_CHARS` in `tools.py` for single-source-of-truth

**Affected scores:** IP-01, IP-02, LIT-01, LIT-02 (conflict and finding detection in longer documents)

---

## P5 — Fix `_log_file` resource safety

**Review finding:** If `planner.conclude()` raises an exception, `_log_file = None` is
never reached. The global stays pointing at a closed or exhausted file handle.
Subsequent runs may silently fail to write logs.

- [x] **I5.1** Wrap the body of `run_investigation` in a `try/finally`:
  ```python
  try:
      ...
      report = planner.conclude(state)
      _log("conclude", {"chars": len(report)})
  finally:
      _log_file = None
  ```
- [ ] **I5.2** Consider replacing the global with a closure or passing the file handle
  into `_log` as a parameter (makes `run_investigation` re-entrant for future test isolation)

**Affected scores:** Code Quality, robustness

---

## P6 — Add `requirements.txt` with pinned dependency

**Review finding:** PRD NFR-5 requires reproducibility. `pip install openai` without a
version is not reproducible. The openai SDK has breaking changes between major versions.

- [x] **I6.1** Create `requirements.txt`:
  ```
  openai>=1.30,<2.0
  ```
- [x] **I6.2** Update README setup section to reference `pip install -r requirements.txt`

**Affected scores:** Eval Engineering (harness reproducibility), NFR-5 compliance

---

## P7 — Implement retry logic in the observe/replan pipeline

**Review finding:** The current pipeline declares a gap after a single empty result.
The designed replanner in `prompts/replanner.py` includes a `retry` action for trying
a different search term or document before declaring a gap. Without retry, a bad initial
query produces a gap note even when the information is present under different phrasing.

This blocks LIT-01, CONTRACT-01 partial scores on keyword-miss failures.

- [x] **I7.1** Add `step_retries: dict[int, int]` to `InvestigationState` to track retry count per step
- [x] **I7.2** In `observe()` prompt: distinguish `continue` (answered or confirmed absent after retry) from `retry` (try different approach, first attempt)
- [x] **I7.3** In `runner.py`: when action is `retry`, call `select_tool()` again with updated state (attempt count visible) without incrementing `current_step`
- [x] **I7.4** Cap retries at 2 per step — on third attempt force `continue` and record gap if still empty
- [x] **I7.5** Log retry attempts as `[RETRY]` events with the new tool/query

**Affected scores:** LIT-01 (DataVault), CONTRACT-01 (change-of-control), LIT-02 (anonymous threat)

---

## P8 — Strengthen conflict detection in `observe()` prompt

**Review finding:** The agent found both IP assignment and Imperial licence documents but
did not always classify the note as `conflict`. The observe prompt instructs conflict
classification but does not give the model enough specificity about what "contradicts a
prior note" means in practice.

- [x] **I8.1** Add explicit conflict-detection instruction to the `observe()` system prompt:
  "If the result contains a term, claim, or restriction that directly contradicts any
  FINDING or prior note — record kind=conflict."
- [x] **I8.2** Pass the last 3 finding/conflict notes inline in the observe prompt's state
  summary as a "RECENT FINDINGS AND CONFLICTS (watch for contradictions)" section
- [x] **I8.3** Add a specific named-pattern trigger for the two required conflicts:
  - non-transferable licence + IP assignment = conflict trigger
  - anonymous IP claim + sole-inventor representation = conflict trigger

**Affected scores:** IP-02 (1.0 vs 0.5), LIT-02 (1.0 vs 0.5) — these are both required criteria

---

## P9 — `InvestigationState.status` simplification

**Review finding:** `status` has three values (`investigating`, `concluding`, `done`) but
`concluding` is set and immediately overwritten with `done` in the same function body.
The loop checks `status == "investigating"` only. `concluding` is vestigial.

- [x] **I9.1** Remove `status` field; replace with `concluded: bool = False`
- [x] **I9.2** Update runner loop condition: `while not state.concluded`
- [x] **I9.3** Replace all `state.status = "concluding"` and `state.status = "done"` with `state.concluded = True`

**Affected scores:** Code Quality (minor but signals attention to design hygiene)

---

## P10 — Majority-vote judge for required criteria

**Review finding:** A single LLM judge call at temperature=0 is more reproducible than
higher temperatures but not deterministic on borderline cases (0.5/1.0 boundary). IP-02
and LIT-02 are the hardest criteria and most likely to be borderline.

- [ ] **I10.1** In `eval/harness.py`, add `judge_criterion_with_majority(criterion, report, n=3)` that calls `judge_criterion` three times and returns the median score
- [ ] **I10.2** Apply majority voting only to required criteria (`criterion.required == True`) to control cost
- [ ] **I10.3** Log all three scores and the median in the JSON output

**Affected scores:** Eval reliability on IP-02, LIT-02, CONTRACT-01 (the three most variable)

---

## P11 — End-to-end validation run

**Review finding:** Zero eval scores exist. No scenario has been run. The agent has never
executed against its own rubric. This is the most significant submission gap.

- [ ] **I11.1** Resolve OpenAI quota (add billing or switch key)
- [ ] **I11.2** Run agent on S1 (full corpus). Capture stdout and JSONL trace.
- [ ] **I11.3** Run `python eval/harness.py --all --output results/eval_results.json`
- [ ] **I11.4** Review scores. For any required criterion scoring 0.0: trace to the specific plan step and observe output that should have covered it; fix prompt.
- [ ] **I11.5** Re-run after prompt fixes. Record final scores.
- [ ] **I11.6** Update README with actual eval scores (even if imperfect — honest results beat no results)

**Affected scores:** Everything — no score is a gating failure for the submission

---

## Implementation order

Strict ordering for maximum score impact before the submission deadline:

```
I1  (corpus fix)       — 10 min  — fixes evaluation validity before anything else
I5  (finally block)    — 5 min   — correctness bug, fast fix
I6  (requirements.txt) — 5 min   — NFR-5 compliance, fast fix
I4  (observe truncation)— 15 min — directly improves IP-02, LIT-02 hit rate
I3  (system prompts)   — 30 min  — improves all LLM calls
I8  (conflict detection)— 45 min — targets the two hardest required criteria
I7  (retry logic)      — 60 min  — closes keyword-miss gap failures
I11 (validation run)   — ?? min  — gating; do this as soon as quota is available
I2  (prompts/ wiring)  — 90 min  — coherence + adopts richer schemas (prompts/ kept as source of truth)
I9  (status cleanup)   — 15 min  — hygiene; last because lowest impact
I10 (majority vote)    — 45 min  — reliability improvement; last because highest cost
```

Total estimated time for P1–P8 (highest impact): ~3 hours
P9–P11 add ~2 hours depending on quota turnaround.
