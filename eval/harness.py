"""
Evaluation harness for the Legal Investigation Agent.

Usage:
    python eval/harness.py --scenario S1
    python eval/harness.py --all
    python eval/harness.py --all --output results/eval_results.json

Scoring is done by an adversarial LLM judge at temperature=0.
The judge receives the ground-truth source documents and the agent's
report, and is prompted to find what the agent missed — not to confirm
what it got right.
"""

import argparse
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path
from datetime import datetime

from openai import RateLimitError, InternalServerError

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from eval.rubric import RUBRIC, MAX_SCORE, REQUIRED_CRITERIA, Criterion
from eval.scenarios import ALL_SCENARIOS, Scenario
import agent.utils.rate_limiter as _rl
from agent.utils.client import get_client

DOCUMENTS_DIR = PROJECT_ROOT / "data" / "documents"
MODEL = "gpt-5.6-sol"


# ---------------------------------------------------------------------------
# Corpus isolation
# ---------------------------------------------------------------------------

def build_scenario_corpus(scenario: Scenario, tmp_dir: Path) -> Path:
    corpus_dir = tmp_dir / "corpus"
    corpus_dir.mkdir()
    for filename in scenario.available_documents:
        src = DOCUMENTS_DIR / filename
        if not src.exists():
            print(f"  [WARN] Document not found in master corpus: {filename}")
            continue
        shutil.copy(src, corpus_dir / filename)
    return corpus_dir


def _load_source_documents(filenames: list[str]) -> str:
    """Load ground-truth documents from master corpus for the judge."""
    parts = []
    for filename in filenames:
        path = DOCUMENTS_DIR / filename
        if path.exists():
            parts.append(f"=== {filename} ===\n{path.read_text(encoding='utf-8')}")
        else:
            parts.append(f"=== {filename} ===\n[DOCUMENT NOT FOUND IN MASTER CORPUS]")
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Agent invocation
# ---------------------------------------------------------------------------

def run_agent(goal: str, corpus_dir: Path) -> str:
    try:
        from agent.runner import run_investigation
        return run_investigation(goal=goal, documents_dir=str(corpus_dir))
    except ImportError:
        print("  [INFO] Agent module not found. Running harness in stub mode.")
        return "[STUB REPORT — agent not yet implemented]"


# ---------------------------------------------------------------------------
# LLM judge
# ---------------------------------------------------------------------------

def judge_criterion(criterion: Criterion, report: str) -> dict:
    """
    Call the LLM judge for a single criterion at temperature=0.
    Returns {"score": float, "verdict": str, "reasoning": str}.
    """
    source_documents = _load_source_documents(criterion.relevant_documents)
    prompt = (
        criterion.judge_prompt
        .replace("{source_documents}", source_documents)
        .replace("{report}", report)
    )

    try:
        for attempt in range(6):
            try:
                _rl.wait_if_needed()
                response = get_client().responses.create(
                    model=MODEL,
                    text={"format": {"type": "json_object"}},
                    instructions=(
                        "You are an adversarial legal reviewer. You score AI-generated due "
                        "diligence reports strictly and skeptically. Always respond with valid "
                        "JSON containing exactly: score (float), verdict (string), reasoning (string)."
                    ),
                    input=prompt,
                )
                _rl.record(response.usage.total_tokens)
                break
            except (RateLimitError, InternalServerError):
                if attempt == 5:
                    raise
                time.sleep(30 * (attempt + 1))
        raw = response.output_text
        result = json.loads(raw)
        score = float(result.get("score", 0.0))
        # Clamp to valid values
        if score >= 0.9:
            score = 1.0
        elif score >= 0.4:
            score = 0.5
        else:
            score = 0.0
        return {
            "score": score,
            "verdict": result.get("verdict", _grade(score)),
            "reasoning": result.get("reasoning", ""),
        }
    except Exception as e:
        print(f"  [ERROR] Judge call failed for {criterion.id}: {e}")
        return {"score": 0.0, "verdict": "FAIL", "reasoning": f"Judge error: {e}"}


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_report(report: str, scenario: Scenario) -> dict:
    results = []
    total_score = 0.0

    for criterion in RUBRIC:
        print(f"    Judging {criterion.id}...", end=" ", flush=True)
        judgment = judge_criterion(criterion, report)
        score = judgment["score"]
        total_score += score

        print(judgment["verdict"])

        results.append({
            "id": criterion.id,
            "category": criterion.category,
            "description": criterion.description,
            "required": criterion.required,
            "score": score,
            "verdict": judgment["verdict"],
            "reasoning": judgment["reasoning"],
            "expected_gap": criterion.id in scenario.expected_gaps,
            "expected_conflict": criterion.id in scenario.expected_conflicts,
            "gap_correctly_flagged": (
                criterion.id in scenario.expected_gaps and score >= 0.5
            ),
        })

    required_passes = sum(
        1 for r in results if r["required"] and r["score"] >= 1.0
    )
    scenario_pass = required_passes >= scenario.minimum_required_pass

    return {
        "total_score": round(total_score, 2),
        "max_score": MAX_SCORE,
        "percentage": round((total_score / MAX_SCORE) * 100, 1),
        "required_passes": required_passes,
        "required_total": len(REQUIRED_CRITERIA),
        "scenario_pass": scenario_pass,
        "criteria": results,
    }


def _grade(score: float) -> str:
    if score >= 1.0:
        return "PASS"
    if score >= 0.5:
        return "PARTIAL"
    return "FAIL"


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_scenario_result(scenario: Scenario, scoring: dict) -> None:
    width = 76
    print("\n" + "=" * width)
    print(f"  SCENARIO {scenario.id}: {scenario.name}")
    print("=" * width)
    print(f"  Goal: {scenario.goal}")
    print()

    print(f"  {'ID':<14} {'Category':<28} {'Verdict':<9} {'Score'}  {'Judge Reasoning'}")
    print(f"  {'-'*14} {'-'*28} {'-'*9} {'-'*5}  {'-'*30}")
    for c in scoring["criteria"]:
        req = " *" if c["required"] else "  "
        gap_flag = ""
        if c["expected_gap"]:
            gap_flag = " [gap flagged]" if c["gap_correctly_flagged"] else " [gap MISSED]"
        reasoning = c["reasoning"][:40] + "…" if len(c["reasoning"]) > 40 else c["reasoning"]
        print(
            f"  {c['id']:<14} {c['category']:<28} {c['verdict']:<9} {c['score']:.1f}{req}"
            f"  {reasoning}{gap_flag}"
        )

    print()
    print(f"  Total score:      {scoring['total_score']} / {scoring['max_score']} ({scoring['percentage']}%)")
    print(f"  Required passes:  {scoring['required_passes']} / {scoring['required_total']} "
          f"(need {scenario.minimum_required_pass})")
    print(f"  Scenario result:  {'PASS' if scoring['scenario_pass'] else 'FAIL'}")
    print("=" * width)


def print_summary(all_results: list[dict]) -> None:
    print("\n" + "=" * 76)
    print("  EVALUATION SUMMARY")
    print("=" * 76)
    for r in all_results:
        status = "PASS" if r["scoring"]["scenario_pass"] else "FAIL"
        print(
            f"  {r['scenario_id']:<6} {r['scenario_name']:<44} "
            f"{r['scoring']['percentage']:>5.1f}%   {status}"
        )
    passed = sum(1 for r in all_results if r["scoring"]["scenario_pass"])
    print(f"\n  {passed}/{len(all_results)} scenarios passed")
    print("=" * 76 + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_scenario(scenario: Scenario) -> dict:
    print(f"\nRunning scenario {scenario.id}: {scenario.name}")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        corpus_dir = build_scenario_corpus(scenario, tmp_dir)
        print(f"  Corpus: {len(list(corpus_dir.iterdir()))} documents loaded")
        print("  Invoking agent...")
        report = run_agent(goal=scenario.goal, corpus_dir=corpus_dir)

    print("  Scoring with LLM judge (temperature=0)...")
    scoring = score_report(report, scenario)
    print_scenario_result(scenario, scoring)

    return {
        "scenario_id": scenario.id,
        "scenario_name": scenario.name,
        "goal": scenario.goal,
        "available_documents": scenario.available_documents,
        "scoring": scoring,
        "report_excerpt": report[:600] + "…" if len(report) > 600 else report,
        "timestamp": datetime.utcnow().isoformat(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Legal Investigation Agent — Evaluation Harness")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--scenario", choices=[s.id for s in ALL_SCENARIOS])
    group.add_argument("--all", action="store_true")
    parser.add_argument("--output", type=str)
    args = parser.parse_args()

    scenarios_to_run = ALL_SCENARIOS if args.all else [
        s for s in ALL_SCENARIOS if s.id == args.scenario
    ]

    all_results = []
    for scenario in scenarios_to_run:
        result = run_scenario(scenario)
        all_results.append(result)

    if args.all:
        print_summary(all_results)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2)
        print(f"Results written to {out_path}")


if __name__ == "__main__":
    # Load .env from project root so OPENAI_KEY is available
    _env_path = PROJECT_ROOT / ".env"
    if _env_path.exists():
        with open(_env_path) as _ef:
            for _line in _ef:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _v = _line.split("=", 1)
                    os.environ.setdefault(_k.strip(), _v.strip())
    main()
