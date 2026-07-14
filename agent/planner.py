import json
import os
import time

from openai import RateLimitError, InternalServerError, APIStatusError

import agent.rate_limiter as _rl
from agent.client import get_client
from agent.state import InvestigationState, Note
import prompts.planner as _plan_prompts
import prompts.executor as _exec_prompts
import prompts.observer as _obs_prompts
import prompts.replanner as _replan_prompts
import prompts.summarizer as _sum_prompts

MODEL = "gpt-5.6-sol"
MAX_OBSERVE_CHARS = 6000


def _chat(messages: list[dict], temperature: float, json_mode: bool) -> str:
    system_msg = next((m["content"] for m in messages if m["role"] == "system"), None)
    user_parts = [m["content"] for m in messages if m["role"] == "user"]
    user_msg = "\n\n".join(user_parts)

    kwargs: dict = dict(model=MODEL, input=user_msg)
    if system_msg:
        kwargs["instructions"] = system_msg
    if json_mode:
        kwargs["text"] = {"format": {"type": "json_object"}}

    for attempt in range(6):
        try:
            _rl.wait_if_needed()
            response = get_client().responses.create(**kwargs)
            _rl.record(response.usage.total_tokens)
            return response.output_text
        except (RateLimitError, InternalServerError):
            if attempt == 5:
                raise
            time.sleep(30 * (attempt + 1))


def _state_summary(state: InvestigationState) -> str:
    notes_text = "\n".join(
        f"  [{n.kind.upper()}] {n.category}: {n.description} (sources: {', '.join(n.sources) or 'none'})"
        for n in state.notes
    ) or "  (none yet)"

    remaining = state.plan[state.current_step:]
    remaining_text = "\n".join(
        f"  Step {state.current_step + i + 1}: [{t.get('category', '')}] {t.get('question', str(t))}"
        for i, t in enumerate(remaining)
    ) or "  (none)"

    return (
        f"GOAL: {state.goal}\n\n"
        f"NOTES SO FAR:\n{notes_text}\n\n"
        f"REMAINING PLAN STEPS:\n{remaining_text}\n\n"
        f"DOCUMENTS ALREADY READ: {', '.join(state.documents_read) or 'none'}\n"
        f"ITERATION: {state.iterations}"
    )


def _recent_notes_text(state: InvestigationState, n: int = 3) -> str:
    recent = state.notes[-n:] if state.notes else []
    if not recent:
        return "  (none yet)"
    return "\n".join(
        f"  [{note.kind.upper()}] {note.category}: {note.description}"
        for note in recent
    )


# ---------------------------------------------------------------------------
# plan
# ---------------------------------------------------------------------------

def plan(goal: str, docs: list[str]) -> list[dict]:
    """Return an ordered list of structured task dicts (step, category, question, approach)."""
    docs_list = "\n".join(f"  - {d}" for d in docs)
    user_content = _plan_prompts.USER.format(
        goal=goal,
        available_documents=docs_list,
    )
    raw = _chat(
        messages=[
            {"role": "system", "content": _plan_prompts.SYSTEM},
            {"role": "user", "content": user_content},
        ],
        temperature=0,
        json_mode=True,
    )
    data = json.loads(raw)
    tasks = data.get("tasks") or data.get("steps") or []
    if not isinstance(tasks, list):
        raise ValueError(f"plan() expected a list, got: {type(tasks)}")
    # Normalise: if bare strings returned, wrap into task dicts
    result = []
    for i, t in enumerate(tasks):
        if isinstance(t, str):
            result.append({"step": i + 1, "category": "IP Ownership", "question": t, "approach": ""})
        else:
            result.append(t)
    return result


# ---------------------------------------------------------------------------
# select_tool
# ---------------------------------------------------------------------------

def select_tool(state: InvestigationState, task: dict) -> dict:
    """Return {"tool": str, "args": dict, "decision": str, "expected_outcome": str}."""
    summary = _state_summary(state)
    completed = state.plan[:state.current_step]
    completed_text = "\n".join(
        f"  Step {t.get('step', i + 1)}: [{t.get('category', '')}] {t.get('question', '')}"
        for i, t in enumerate(completed)
    ) or "  (none)"

    recent_obs = _recent_notes_text(state)

    user_content = _exec_prompts.USER.format(
        goal=state.goal,
        step=task.get("step", state.current_step + 1),
        total_steps=len(state.plan),
        category=task.get("category", ""),
        question=task.get("question", str(task)),
        completed_tasks=completed_text,
        recent_observations=recent_obs,
        project_summary=summary,
    )
    raw = _chat(
        messages=[
            {"role": "system", "content": _exec_prompts.SYSTEM},
            {"role": "user", "content": user_content},
        ],
        temperature=0,
        json_mode=True,
    )
    data = json.loads(raw)
    if "tool" not in data or "args" not in data:
        raise ValueError(f"select_tool() missing keys in: {data}")
    return data


# ---------------------------------------------------------------------------
# observe
# ---------------------------------------------------------------------------

def observe(state: InvestigationState, task: dict, result: str) -> dict:
    """Return {"note": Note, "action": str, "reason": str, "new_task"?: dict}."""
    summary = _state_summary(state)
    result_preview = result[:MAX_OBSERVE_CHARS] if result else "(empty — no content returned)"
    retry_count = state.step_retries.get(state.current_step, 0)
    recent_notes = _recent_notes_text(state, n=3)

    user_content = _obs_prompts.USER.format(
        goal=state.goal,
        question=task.get("question", str(task)),
        result_preview=result_preview,
        recent_notes=recent_notes,
        state_summary=summary,
        retry_count=retry_count,
    )
    raw = _chat(
        messages=[
            {"role": "system", "content": _obs_prompts.SYSTEM},
            {"role": "user", "content": user_content},
        ],
        temperature=0.3,
        json_mode=True,
    )
    data = json.loads(raw)

    kind = data.get("kind", "gap")
    if kind not in ("finding", "gap", "conflict"):
        kind = "gap"

    action = data.get("action", "continue")
    if action not in ("continue", "retry", "insert_task"):
        action = "continue"

    # Enforce retry cap
    if action == "retry" and retry_count >= 2:
        action = "continue"
        kind = "gap"

    note = Note(
        kind=kind,
        category=data.get("category", task.get("category", "IP Ownership")),
        description=data.get("description", ""),
        sources=data.get("sources") or [],
    )
    return {
        "note": note,
        "action": action,
        "reason": data.get("reason", ""),
        "new_task": data.get("new_task"),
    }


# ---------------------------------------------------------------------------
# replan
# ---------------------------------------------------------------------------

def replan(state: InvestigationState) -> list[dict]:
    """Return a revised list of remaining task dicts using the 6-action replanner schema."""
    summary = _state_summary(state)
    remaining = state.plan[state.current_step:]
    remaining_text = "\n".join(
        f"  Step {t.get('step', state.current_step + i + 1)}: [{t.get('category', '')}] {t.get('question', '')}"
        for i, t in enumerate(remaining)
    ) or "  (none)"

    notes = state.notes
    finding_count = sum(1 for n in notes if n.kind == "finding")
    gap_count = sum(1 for n in notes if n.kind == "gap")
    conflict_count = sum(1 for n in notes if n.kind == "conflict")
    last_note = notes[-1] if notes else None

    user_content = _replan_prompts.USER.format(
        goal=state.goal,
        remaining_tasks=remaining_text,
        observation_kind=last_note.kind if last_note else "none",
        observation_category=last_note.category if last_note else "none",
        observation_description=last_note.description if last_note else "none",
        observation_sources=", ".join(last_note.sources) if last_note else "none",
        steps_completed=state.current_step,
        steps_remaining=len(remaining),
        finding_count=finding_count,
        gap_count=gap_count,
        conflict_count=conflict_count,
        iterations_used=state.iterations,
        max_iterations=20,
    )
    raw = _chat(
        messages=[
            {"role": "system", "content": _replan_prompts.SYSTEM},
            {"role": "user", "content": user_content},
        ],
        temperature=0.3,
        json_mode=True,
    )
    data = json.loads(raw)
    # Return the action + data for runner to interpret
    return data


# ---------------------------------------------------------------------------
# conclude
# ---------------------------------------------------------------------------

def conclude(state: InvestigationState) -> str:
    """Return the final prose report synthesised from state.notes only."""
    notes_text = "\n".join(
        f"[{n.kind.upper()}] {n.category}\n  {n.description}\n  Sources: {', '.join(n.sources) or 'none'}"
        for n in state.notes
    ) or "(no notes recorded)"

    user_content = _sum_prompts.USER.format(
        goal=state.goal,
        notes=notes_text,
    )
    return _chat(
        messages=[
            {"role": "system", "content": _sum_prompts.SYSTEM},
            {"role": "user", "content": user_content},
        ],
        temperature=0,
        json_mode=False,
    )
