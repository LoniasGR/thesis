"""Evaluate a trained VW contextual-bandit model on human feedback.

Usage:
    python evaluate_human_feedback.py

Full example:
    python evaluate_human_feedback.py \
        --model candidate_model.vw \
        --data applications/mock_dialogues_service/new_data.dat \
        --output human_feedback_evaluation.json

The human-feedback data is held out from production-model training. Results
compare candidate, random, and always-no_action policies using IPS and SNIPS.
"""

import argparse
import json
from pathlib import Path

import vowpalwabbit

from data_generation.train import parse_labeled_examples


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate a VW model on synthetic human-feedback examples."
    )
    parser.add_argument("--model", type=Path, default=Path("candidate_model.vw"))
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("applications/mock_dialogues_service/new_data.dat"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("human_feedback_evaluation.json"),
    )
    parser.add_argument(
        "--predictions",
        type=Path,
        default=Path("human_feedback_predictions.txt"),
    )
    return parser.parse_args()


def parse_prediction(line: str) -> dict[int, float]:
    return {
        int(index): float(probability)
        for index, probability in (
            item.split(":", 1) for item in line.strip().split(",")
        )
    }


def evaluate(examples: list[list[str]], prediction_lines: list[str]) -> dict:
    if len(examples) != len(prediction_lines):
        raise ValueError(
            f"Expected {len(examples)} predictions, got {len(prediction_lines)}"
        )

    candidate_weights = []
    random_weights = []
    no_action_weights = []
    costs = []
    selected_action_counts = {}

    for example, prediction_line in zip(examples, prediction_lines):
        action_lines = example[1:]
        labeled_index = next(
            index
            for index, line in enumerate(action_lines)
            if ":" in line.split("|", 1)[0]
        )
        label, _ = action_lines[labeled_index].split("|", 1)
        action_index, cost, logging_probability = map(float, label.split(":"))
        if action_index != 0:
            raise ValueError("The logged action must be at ADF index 0")

        predictions = parse_prediction(prediction_line)
        candidate_probability = predictions.get(0, 0.0)
        candidate_weights.append(candidate_probability / logging_probability)
        random_weights.append(1.0)
        costs.append(cost)

        no_action_index = next(
            index
            for index, line in enumerate(action_lines)
            if line.split("action=", 1)[-1].strip() == "no_action"
        )
        no_action_weights.append(
            (1.0 if no_action_index == 0 else 0.0) / logging_probability
        )
        best_action = max(predictions, key=predictions.get)
        action = action_lines[best_action].split("action=", 1)[-1].strip()
        selected_action_counts[action] = selected_action_counts.get(action, 0) + 1

    def estimate(weights: list[float]) -> dict:
        weighted_costs = [
            weight * cost for weight, cost in zip(weights, costs)
        ]
        weight_sum = sum(weights)
        ips = sum(weighted_costs) / len(weighted_costs)
        variance = sum((value - ips) ** 2 for value in weighted_costs) / len(
            weighted_costs
        )
        return {
            "ips_mean_cost": ips,
            "snips_mean_cost": (
                sum(weighted_costs) / weight_sum if weight_sum > 0.0 else None
            ),
            "standard_error": (variance / len(weighted_costs)) ** 0.5,
            "effective_sample_size": (
                weight_sum**2 / sum(weight**2 for weight in weights)
                if any(weights)
                else 0.0
            ),
        }

    random_cost = sum(costs) / len(costs)
    return {
        "examples": len(examples),
        "observed_random_cost": random_cost,
        "observed_relevance_rate": 1.0 - random_cost,
        "candidate": estimate(candidate_weights),
        "random": estimate(random_weights),
        "always_no_action": estimate(no_action_weights),
        "candidate_argmax_actions": selected_action_counts,
    }


def main():
    args = parse_args()
    examples = parse_labeled_examples(args.data)
    workspace = vowpalwabbit.Workspace(
        cb_explore_adf=True,
        cb_type="ips",
        i=str(args.model),
        t=True,
        d=str(args.data),
        p=str(args.predictions),
    )
    workspace.finish()

    prediction_lines = [
        line.strip()
        for line in args.predictions.read_text().splitlines()
        if line.strip()
    ]
    report = {
        "model": str(args.model),
        "data": str(args.data),
        **evaluate(examples, prediction_lines),
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
