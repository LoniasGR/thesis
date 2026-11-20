"""Run conversation-grouped VW contextual-bandit cross-validation.

Usage:
    python cross_validate.py

Full example:
    python cross_validate.py \
        --input-file data/conversations-all.json \
        --folds 5 \
        --seed 42 \
        --no-action-probability 0.5 \
        --learning-rates 0.1 0.5 1.0 \
        --lambda-values 1 10 \
        --output cross_validation_results.json

Complete conversations are assigned to folds before conversion, so no
suggestions from one conversation are split between training and evaluation.
Configurations are ranked by mean fold SNIPS cost.
"""

import argparse
import contextlib
import io
import json
import random
import statistics
from itertools import product
from pathlib import Path
from tempfile import TemporaryDirectory

import vowpalwabbit

from data_generation.format_data import create_vw_data
from data_generation.train import calculate_test_metrics


def parse_args():
    parser = argparse.ArgumentParser(
        description="Conversation-grouped cross-validation for a VW contextual bandit."
    )
    parser.add_argument(
        "--input-file",
        type=Path,
        default=Path("data/conversations-all.json"),
    )
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-action-probability", type=float, default=0.5)
    parser.add_argument(
        "--learning-rates",
        type=float,
        nargs="+",
        default=[0.1, 0.5, 1.0],
    )
    parser.add_argument(
        "--lambda-values",
        type=float,
        nargs="+",
        default=[1.0, 10.0],
    )
    parser.add_argument("--cb-type", choices=("ips", "dr"), default="ips")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("cross_validation_results.json"),
    )
    args = parser.parse_args()
    if args.folds < 2:
        parser.error("--folds must be at least 2")
    if not 0.0 <= args.no_action_probability <= 1.0:
        parser.error("--no-action-probability must be between 0 and 1")
    return args


def create_folds(lines: list[str], fold_count: int, seed: int) -> list[list[str]]:
    shuffled = list(lines)
    random.Random(seed).shuffle(shuffled)
    folds = [[] for _ in range(fold_count)]
    for index, line in enumerate(shuffled):
        folds[index % fold_count].append(line)
    return folds


def write_fold_data(
    train_lines: list[str],
    test_lines: list[str],
    directory: Path,
    no_action_probability: float,
) -> tuple[Path, Path]:
    train_file = directory / "train.dat"
    test_file = directory / "test.dat"
    with (
        contextlib.closing(io.StringIO()) as debug_file,
        io.StringIO() as all_data_file,
    ):
        create_vw_data(
            train_file,
            train_lines,
            debug_file,
            all_data_file,
            no_action_probability,
        )
        create_vw_data(
            test_file,
            test_lines,
            debug_file,
            io.StringIO(),
            no_action_probability,
        )
    return train_file, test_file


def run_configuration(
    train_file: Path,
    test_file: Path,
    directory: Path,
    cb_type: str,
    learning_rate: float,
    lambda_value: float,
) -> dict:
    model_file = directory / "candidate_model.vw"
    predictions_file = directory / "predictions.txt"
    model_file.unlink(missing_ok=True)
    workspace_args = [
        "--lambda",
        str(lambda_value),
        "--learning_rate",
        str(learning_rate),
        "-q",
        "SA",
    ]

    train_workspace = vowpalwabbit.Workspace(
        cb_explore_adf=True,
        cb_type=cb_type,
        f=str(model_file),
        softmax=True,
        d=str(train_file),
        arg_list=workspace_args,
    )
    train_workspace.finish()

    test_workspace = vowpalwabbit.Workspace(
        cb_explore_adf=True,
        cb_type=cb_type,
        i=str(model_file),
        t=True,
        d=str(test_file),
        p=str(predictions_file),
    )
    test_workspace.finish()
    return calculate_test_metrics(test_file, predictions_file)


def summarize_configuration(configuration: dict, folds: list[dict]) -> dict:
    ips_values = [fold["ips_mean_cost"] for fold in folds]
    snips_values = [
        fold["snips_mean_cost"]
        for fold in folds
        if fold["snips_mean_cost"] is not None
    ]
    logger_values = [fold["logger_mean_cost"] for fold in folds]
    return {
        **configuration,
        "folds": folds,
        "ips_mean": statistics.mean(ips_values),
        "ips_standard_deviation": statistics.stdev(ips_values)
        if len(ips_values) > 1
        else 0.0,
        "snips_mean": statistics.mean(snips_values) if snips_values else None,
        "snips_standard_deviation": statistics.stdev(snips_values)
        if len(snips_values) > 1
        else 0.0,
        "logger_mean": statistics.mean(logger_values),
    }


def main():
    args = parse_args()
    lines = args.input_file.read_text().splitlines()
    folds = create_folds(lines, args.folds, args.seed)
    if min(map(len, folds)) == 0:
        raise ValueError("Fewer conversations than requested folds")

    configurations = []
    with TemporaryDirectory(prefix="vw-cross-validation-") as temporary_directory:
        root = Path(temporary_directory)
        fold_data = []
        for fold_index, test_lines in enumerate(folds):
            train_lines = [
                line
                for other_index, fold_lines in enumerate(folds)
                if other_index != fold_index
                for line in fold_lines
            ]
            directory = root / f"fold-{fold_index}"
            directory.mkdir()
            train_file, test_file = write_fold_data(
                train_lines,
                test_lines,
                directory,
                args.no_action_probability,
            )
            fold_data.append((train_file, test_file, directory))

        for learning_rate, lambda_value in product(
            args.learning_rates, args.lambda_values
        ):
            configuration = {
                "cb_type": args.cb_type,
                "learning_rate": learning_rate,
                "lambda": lambda_value,
            }
            fold_results = []
            for train_file, test_file, directory in fold_data:
                fold_results.append(
                    run_configuration(
                        train_file,
                        test_file,
                        directory,
                        args.cb_type,
                        learning_rate,
                        lambda_value,
                    )
                )
            configurations.append(
                summarize_configuration(configuration, fold_results)
            )

    configurations.sort(
        key=lambda result: (
            result["snips_mean"]
            if result["snips_mean"] is not None
            else float("inf")
        )
    )
    report = {
        "input_file": str(args.input_file),
        "folds": args.folds,
        "seed": args.seed,
        "no_action_probability": args.no_action_probability,
        "selection_metric": "snips_mean_cost",
        "configurations": configurations,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
