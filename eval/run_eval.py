"""Compare Decision Engine predictions with the Phase 0 labeled set.

Usage:
    python eval/run_eval.py --predictions path/to/predictions.json

Predictions may be a list of workflow objects, a list of StepScore objects, or
an object containing a ``workflows`` list. Each step must contain ``workflow_id``,
``step_id``, a nested ``scores`` object matching StepScores, and ``verdict``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


DIMENSIONS = (
    "repetitiveness",
    "judgment_need",
    "compliance_sensitivity",
    "ai_suitability",
)


def load_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read valid JSON from {path}: {exc}") from exc


def workflows_from(payload: Any, path: Path) -> list[dict[str, Any]]:
    workflows = payload.get("workflows") if isinstance(payload, dict) else payload
    if not isinstance(workflows, list):
        raise ValueError(f"{path} must contain a workflows list or be a workflow list")
    return workflows


def step_index(workflows: list[dict[str, Any]], label_name: str) -> dict[tuple[str, str], dict[str, Any]]:
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for workflow in workflows:
        workflow_id = workflow.get("workflow_id")
        steps = workflow.get("steps", [workflow])
        for step in steps:
            step_id = step.get("step_id")
            if not workflow_id or not step_id:
                raise ValueError(f"Every workflow and step in {label_name} needs an id")
            key = (workflow_id, step_id)
            if key in index:
                raise ValueError(f"Duplicate step id: {workflow_id}/{step_id}")
            index[key] = step
    return index


def step_scores(step: dict[str, Any]) -> dict[str, Any]:
    """Read the nested StepScores shape used by the Pydantic models."""

    nested_scores = step.get("scores")
    if not isinstance(nested_scores, dict):
        return {}
    return {dimension: nested_scores.get(dimension) for dimension in DIMENSIONS}


def step_verdict(step: dict[str, Any]) -> Any:
    return step.get("verdict")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--predictions",
        required=True,
        type=Path,
        help="JSON file containing Decision Engine predictions",
    )
    parser.add_argument(
        "--labeled-set",
        default=Path(__file__).with_name("labeled_set.json"),
        type=Path,
        help="Ground-truth JSON file (default: eval/labeled_set.json)",
    )
    args = parser.parse_args()

    try:
        labeled_workflows = workflows_from(load_json(args.labeled_set), args.labeled_set)
        predicted_workflows = workflows_from(load_json(args.predictions), args.predictions)
        labels = step_index(labeled_workflows, "labeled set")
        predictions = step_index(predicted_workflows, "predictions")
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    missing = sorted(set(labels) - set(predictions))
    unexpected = sorted(set(predictions) - set(labels))
    comparable = sorted(set(labels) & set(predictions))
    labeled_workflow_ids = {workflow["workflow_id"] for workflow in labeled_workflows}
    predicted_workflow_ids = {workflow["workflow_id"] for workflow in predicted_workflows}
    comparable_workflows = labeled_workflow_ids & predicted_workflow_ids
    counts = {dimension: {"exact": 0, "within_1": 0} for dimension in DIMENSIONS}
    absolute_errors = {dimension: 0 for dimension in DIMENSIONS}
    score_counts = {dimension: 0 for dimension in DIMENSIONS}
    verdict_exact = 0
    verdict_count = 0
    invalid_scores: list[str] = []
    invalid_verdicts: list[str] = []

    for key in comparable:
        label = labels[key]
        prediction = predictions[key]
        label_scores = step_scores(label)
        predicted = step_scores(prediction)
        label_name = f"{key[0]}/{key[1]}"
        for dimension in DIMENSIONS:
            actual = label_scores.get(dimension)
            guess = predicted.get(dimension)
            if not isinstance(actual, int) or not isinstance(guess, int) or not 1 <= guess <= 5:
                invalid_scores.append(label_name + ":" + dimension)
                continue
            error = abs(guess - actual)
            score_counts[dimension] += 1
            absolute_errors[dimension] += error
            counts[dimension]["exact"] += error == 0
            counts[dimension]["within_1"] += error <= 1

        actual_verdict = step_verdict(label)
        predicted_verdict = step_verdict(prediction)
        if predicted_verdict is not None:
            verdict_count += 1
            if predicted_verdict == actual_verdict:
                verdict_exact += 1
            elif predicted_verdict not in {"leave_as_is", "automate", "redesign"}:
                invalid_verdicts.append(label_name)

    report: dict[str, Any] = {
        "labeled_workflows": len(labeled_workflows),
        "predicted_workflows": len(predicted_workflows),
        "comparable_workflows": len(comparable_workflows),
        "labeled_steps": len(labels),
        "predicted_steps": len(predictions),
        "comparable_steps": len(comparable),
        "missing_predictions": [f"{workflow}/{step}" for workflow, step in missing],
        "unexpected_predictions": [f"{workflow}/{step}" for workflow, step in unexpected],
        "dimensions": {},
        "verdict": {
            "predicted_count": verdict_count,
            "exact": verdict_exact,
            "exact_rate": verdict_exact / verdict_count if verdict_count else None,
        },
        "invalid_scores": invalid_scores,
        "invalid_verdicts": invalid_verdicts,
    }
    for dimension in DIMENSIONS:
        count = score_counts[dimension]
        report["dimensions"][dimension] = {
            "count": count,
            "exact": counts[dimension]["exact"],
            "exact_rate": counts[dimension]["exact"] / count if count else None,
            "within_1": counts[dimension]["within_1"],
            "within_1_rate": counts[dimension]["within_1"] / count if count else None,
            "mean_absolute_error": absolute_errors[dimension] / count if count else None,
        }

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
