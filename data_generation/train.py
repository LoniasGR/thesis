import argparse
import json
import os
import random
from pathlib import Path

import vowpalwabbit


def get_examples(filename):
    examples = []
    with open(filename, "r") as fin:
        example = []
        for line in fin:
            if line.startswith("shared |"):
                if len(example) > 0:
                    examples.append(example)
                example = []
                example.append(line.strip("\n"))
            else:
                if len(line.strip("\n")) > 0:
                    example.append(line.strip("\n"))
        examples.append(example)
    return examples


def dialogue_length(line):
    return len(line.split("|")[1].strip().split(" "))


def calculate_dialogue_lengths(examples):
    lengths = {}
    for e in examples:
        length = dialogue_length(e[0])
        if length in lengths:
            lengths[length] += 1
        else:
            lengths[length] = 1
    return lengths


def get_average(lengths: dict):
    sum = 0
    count = 0
    for k, v in lengths.items():
        sum += k * v
        count += v
    return sum / count, count


def sample_custom_pmf(pmf):
    total = sum(pmf)
    scale = 1 / total
    pmf = [x * scale for x in pmf]
    draw = random.random()
    sum_prob = 0.0
    for index, prob in enumerate(pmf):
        sum_prob += prob
        if sum_prob > draw:
            return index, prob


def parse_args():
    parser = argparse.ArgumentParser(description="Train and evaluate a VW contextual bandit.")
    parser.add_argument("--train-data", type=Path, default=Path("data/train.dat"))
    parser.add_argument("--test-data", type=Path, default=Path("data/test.dat"))
    parser.add_argument("--model", type=Path, default=Path("candidate_model.vw"))
    parser.add_argument("--predictions", type=Path, default=Path("predictions.txt"))
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--cb-type", choices=("ips", "dr"), default="ips")
    parser.add_argument("--lambda-value", type=float, default=1.0)
    parser.add_argument("--learning-rate", type=float, default=0.1)
    return parser.parse_args()


def parse_labeled_examples(filename: Path):
    examples = []
    with filename.open() as source:
        current = []
        for raw_line in source:
            line = raw_line.strip()
            if line.startswith("shared |"):
                if current:
                    examples.append(current)
                current = [line]
            elif line:
                current.append(line)
        if current:
            examples.append(current)
    return examples


def calculate_test_metrics(test_data: Path, predictions: Path):
    examples = parse_labeled_examples(test_data)
    prediction_lines = [
        line.strip() for line in predictions.read_text().splitlines() if line.strip()
    ]
    if len(examples) != len(prediction_lines):
        raise ValueError(
            f"Expected {len(examples)} prediction lines, got {len(prediction_lines)}"
        )

    weighted_costs = []
    logger_costs = []
    importance_weights = []
    for example, prediction_line in zip(examples, prediction_lines):
        labeled_line = next(line for line in example[1:] if ":" in line.split("|")[0])
        label, _ = labeled_line.split("|", 1)
        action_index, cost, propensity = map(float, label.split(":"))
        if action_index != 0:
            raise ValueError(f"Expected the logged action at index 0, got {action_index}")

        probabilities = [
            (int(index), float(probability))
            for index, probability in (
                item.split(":", 1) for item in prediction_line.split(",")
            )
        ]
        candidate_probability = dict(probabilities).get(0, 0.0)
        importance_weight = candidate_probability / propensity
        weighted_costs.append(cost * importance_weight)
        importance_weights.append(importance_weight)
        logger_costs.append(cost)

    count = len(weighted_costs)
    if count == 0:
        raise ValueError("Cannot evaluate an empty test dataset")
    mean_ips_cost = sum(weighted_costs) / count
    mean_logger_cost = sum(logger_costs) / count
    variance = sum((cost - mean_ips_cost) ** 2 for cost in weighted_costs) / count
    total_weight = sum(importance_weights)
    return {
        "test_examples": count,
        "logger_mean_cost": mean_logger_cost,
        "ips_mean_cost": mean_ips_cost,
        "ips_standard_error": (variance / count) ** 0.5,
        "effective_sample_size": (
            sum(importance_weights) ** 2 / sum(weight**2 for weight in importance_weights)
            if any(importance_weights)
            else 0.0
        ),
        "snips_mean_cost": (
            sum(weighted_costs) / total_weight if total_weight > 0.0 else None
        ),
    }


def main():
    args = parse_args()
    args.model.unlink(missing_ok=True)
    args.model.parent.mkdir(parents=True, exist_ok=True)
    args.predictions.parent.mkdir(parents=True, exist_ok=True)

    vw_train = vowpalwabbit.Workspace(
        cb_explore_adf=True,
        cb_type=args.cb_type,
        f=str(args.model),
        softmax=True,
        d=str(args.train_data),
        arg_list=[
            "--lambda",
            str(args.lambda_value),
            "--learning_rate",
            str(args.learning_rate),
            "-q",
            "SA",
        ],
    )
    vw_train.finish()

    vw_test = vowpalwabbit.Workspace(
        cb_explore_adf=True,
        cb_type=args.cb_type,
        i=str(args.model),
        t=True,
        d=str(args.test_data),
        p=str(args.predictions),
    )
    vw_test.finish()

    metrics = {
        "train_data": str(args.train_data),
        "test_data": str(args.test_data),
        "model": str(args.model),
        "predictions": str(args.predictions),
        "cb_type": args.cb_type,
        "lambda": args.lambda_value,
        "learning_rate": args.learning_rate,
        **calculate_test_metrics(args.test_data, args.predictions),
    }
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(json.dumps(metrics, indent=2) + "\n")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
