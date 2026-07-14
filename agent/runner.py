import json
import os
import sys
from datetime import datetime, timezone

import agent.planner as planner
import agent.tools as tools
from agent.state import InvestigationState

MAX_ITERATIONS = 20
MAX_RETRIES_PER_STEP = 2

_log_file = None


def _log(event: str, payload: dict) -> None:
    ts = datetime.now(timezone.utc).isoformat()

    if event == "plan":
        tasks = payload.get("tasks", [])
        for t in tasks:
            step = t.get("step", "?")
            cat = t.get("category", "")
            q = t.get("question", str(t))
            print(f"[PLAN]      Step {step} [{cat}]: {q}")

    elif event == "tool_call":
        tool = payload.get("tool", "")
        args = payload.get("args", {})
        arg_str = " | ".join(f'{k}="{v}"' for k, v in args.items() if k != "directory")
        decision = payload.get("decision", "")
        print(f"[TOOL]      {tool} | {arg_str}")
        if decision:
            print(f"[TOOL]        -> {decision}")

    elif event == "tool_result":
        chars = payload.get("chars", 0)
        label = payload.get("label", "")
        print(f"[RESULT]    {label} ({chars} chars)")

    elif event == "observation":
        kind = payload.get("kind", "")
        category = payload.get("category", "")
        description = payload.get("description", "")
        action = payload.get("action", "")
        print(f"[OBSERVE]   {kind} | {category} | {description[:80]}")
        print(f"[OBSERVE]     action={action} reason={payload.get('reason', '')[:60]}")

    elif event == "retry":
        step = payload.get("step", "")
        attempt = payload.get("attempt", "")
        print(f"[RETRY]     step={step} attempt={attempt}")

    elif event == "decide":
        action = payload.get("action", "")
        step = payload.get("step", "")
        print(f"[DECIDE]    {action} -> step {step}")

    elif event == "replan":
        action = payload.get("replan_action", "")
        detail = payload.get("detail", "")
        print(f"[REPLAN]    action={action} | {detail}")

    elif event == "guard":
        print(f"[GUARD]     iteration limit reached - forcing conclude")

    elif event == "conclude":
        chars = payload.get("chars", 0)
        print(f"[CONCLUDE]  Report written ({chars} chars)")

    else:
        print(f"[{event.upper()}]  {payload}")

    if _log_file is not None:
        record = {"event": event, "ts": ts, **payload}
        _log_file.write(json.dumps(record) + "\n")
        _log_file.flush()


def _apply_replan_action(state: InvestigationState, replan_data: dict) -> None:
    """Mutate state.plan according to the replanner's action."""
    action = replan_data.get("action", "continue")
    reason = replan_data.get("reason", "")

    if action == "continue":
        state.current_step += 1
        _log("replan", {"replan_action": "continue", "detail": reason})

    elif action == "retry":
        retries = state.step_retries.get(state.current_step, 0)
        state.step_retries[state.current_step] = retries + 1
        _log("retry", {"step": state.current_step, "attempt": retries + 1, "reason": reason})

    elif action == "insert_task":
        new_task = replan_data.get("new_task", {})
        insert_after = replan_data.get("insert_after_step")
        if insert_after is not None:
            idx = insert_after  # insert after step index (0-based: after step N means position N+1)
            state.plan.insert(idx, new_task)
        else:
            state.plan.append(new_task)
        state.current_step += 1
        _log("replan", {"replan_action": "insert_task", "detail": reason, "new_task": new_task})

    elif action == "modify_task":
        target = replan_data.get("target_step", state.current_step + 1) - 1
        updated_approach = replan_data.get("updated_approach", "")
        if 0 <= target < len(state.plan):
            state.plan[target]["approach"] = updated_approach
        state.current_step += 1
        _log("replan", {"replan_action": "modify_task", "target": target, "detail": reason})

    elif action == "remove_task":
        target = replan_data.get("target_step", state.current_step + 1) - 1
        if 0 <= target < len(state.plan):
            state.plan.pop(target)
        state.current_step += 1
        _log("replan", {"replan_action": "remove_task", "target": target, "detail": reason})

    elif action == "abort":
        state.concluded = True
        _log("replan", {"replan_action": "abort", "detail": reason})

    else:
        # Unknown action — treat as continue
        state.current_step += 1
        _log("replan", {"replan_action": f"unknown({action})->continue", "detail": reason})


def run_investigation(goal: str, documents_dir: str) -> str:
    global _log_file

    os.makedirs("logs", exist_ok=True)
    log_path = os.path.join(
        "logs",
        f"run_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.jsonl",
    )

    with open(log_path, "w", encoding="utf-8") as lf:
        _log_file = lf
        try:
            # 1. Discover documents
            available_docs = tools.list_files(documents_dir)

            # 1b. Pre-build embedding index (amortised cost, used by search_corpus)
            tools.build_index(documents_dir)

            # 2. Plan
            state = InvestigationState(goal=goal)
            state.plan = planner.plan(goal, available_docs)
            _log("plan", {"tasks": state.plan})

            # 3. Investigation loop
            while not state.concluded:

                # Guard — check before doing work
                if state.iterations >= MAX_ITERATIONS:
                    _log("guard", {"iterations": state.iterations})
                    break

                # Plan exhausted
                if state.current_step >= len(state.plan):
                    break

                task = state.plan[state.current_step]
                # Normalise bare-string tasks (defensive)
                if isinstance(task, str):
                    task = {"step": state.current_step + 1, "category": "IP Ownership",
                            "question": task, "approach": ""}
                    state.plan[state.current_step] = task

                # 3a — select and execute tool
                tool_call = planner.select_tool(state, task)
                tool_name = tool_call.get("tool", "")
                args = tool_call.get("args", {})
                args["directory"] = documents_dir

                _log("tool_call", {
                    "tool": tool_name,
                    "args": args,
                    "decision": tool_call.get("decision", ""),
                    "expected_outcome": tool_call.get("expected_outcome", ""),
                })

                match tool_name:
                    case "list_files":
                        raw_result = "\n".join(tools.list_files(args["directory"]))
                    case "read_file":
                        filename = args.get("filename", "")
                        raw_result = tools.read_file(args["directory"], filename)
                        if filename and filename not in state.documents_read:
                            state.documents_read.append(filename)
                    case "search_in_file":
                        filename = args.get("filename", "")
                        query = args.get("query", "")
                        raw_result = tools.search_in_file(args["directory"], filename, query)
                        if filename and filename not in state.documents_read:
                            state.documents_read.append(filename)
                    case "search_corpus":
                        query = args.get("query", "")
                        raw_result = tools.search_corpus(args["directory"], query)
                    case _:
                        raw_result = f"Unknown tool: {tool_name}"

                result_lines = len(raw_result.splitlines()) if raw_result else 0
                _log("tool_result", {
                    "tool": tool_name,
                    "chars": len(raw_result),
                    "label": (
                        f"{result_lines} lines matched"
                        if tool_name == "search_in_file"
                        else f"{len(raw_result)} chars read"
                    ),
                })

                # 3b — observe
                observation = planner.observe(state, task, raw_result)
                note = observation["note"]
                action = observation["action"]

                state.notes.append(note)
                _log("observation", {
                    "step": state.current_step,
                    "kind": note.kind,
                    "category": note.category,
                    "description": note.description,
                    "sources": note.sources,
                    "action": action,
                    "reason": observation.get("reason", ""),
                })

                # 3c — act on observe decision
                if action == "retry":
                    retries = state.step_retries.get(state.current_step, 0)
                    state.step_retries[state.current_step] = retries + 1
                    _log("retry", {
                        "step": state.current_step,
                        "attempt": retries + 1,
                        "reason": observation.get("reason", ""),
                    })
                    # Do not advance current_step — re-enter loop on same step

                elif action == "insert_task":
                    new_task = observation.get("new_task")
                    if new_task:
                        state.plan.insert(state.current_step + 1, new_task)
                    state.current_step += 1
                    _log("replan", {
                        "replan_action": "insert_task",
                        "detail": observation.get("reason", ""),
                        "new_task": new_task,
                    })

                elif action == "remove_task":
                    target = observation.get("target_step")
                    if target is not None:
                        idx = int(target) - 1  # target_step is 1-based into state.plan
                        if state.current_step < idx < len(state.plan):
                            state.plan.pop(idx)
                    state.current_step += 1
                    _log("replan", {
                        "replan_action": "remove_task",
                        "target": target,
                        "detail": observation.get("reason", ""),
                    })

                else:
                    # continue (or any unrecognised value)
                    state.current_step += 1
                    _log("decide", {"action": "continue", "step": state.current_step})

                state.iterations += 1

            # 4. Conclude
            report = planner.conclude(state)
            _log("conclude", {"chars": len(report)})

        finally:
            _log_file = None

    return report


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m agent.runner <goal> [documents_dir]")
        sys.exit(1)

    _goal = sys.argv[1]
    _docs_dir = sys.argv[2] if len(sys.argv) > 2 else "data/documents"

    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as _ef:
            for _line in _ef:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _v = _line.split("=", 1)
                    os.environ.setdefault(_k.strip(), _v.strip())

    print(run_investigation(_goal, _docs_dir))
