import argparse
import json
import math
import random
import statistics
from pathlib import Path

from applications.mock_dialogues_service.app.common.helpers import (
    get_actions,
    get_unique_functionalities,
    remove_useless_intents,
)
from applications.mock_dialogues_service.app.common.mappings import (
    intent_to_functionality_dict,
)

most_popular_action_per_intent = {}


def get_next_user_event(events: list[dict], suggestion_index: int) -> dict | None:
    return next(
        (
            event
            for event in events[suggestion_index + 1 :]
            if event.get("event") == "user"
        ),
        None,
    )


def classify_suggestion_outcome(action: str, user_event: dict | None) -> int:
    if user_event is None:
        return 1

    intent = user_event["parse_data"]["intent"]["name"]
    if intent == "affirmative":
        return 0
    if intent in {"negative", "out_of_scope", "nlu_fallback"}:
        return 1
    if action == "no_action":
        return 0
    return (
        0
        if intent_to_functionality_dict.get(intent, intent) == action
        else 1
    )


def calculate_logging_probability(
    action: str, remaining_suggestions: list[str], no_action_probability: float
) -> float:
    specific_suggestions = [
        suggestion for suggestion in remaining_suggestions if suggestion != "no_action"
    ]

    if action == "no_action":
        return no_action_probability if specific_suggestions else 1.0

    if action not in specific_suggestions or no_action_probability == 1.0:
        return 0.0

    return (1.0 - no_action_probability) / len(specific_suggestions)


def create_vw_data(
    filename,
    lines,
    debug_file,
    all_data_file,
    no_action_probability: float,
):
    # VW tries to minimize loss/cost, therefore we will pass cost as -reward
    ACCEPTED = 0
    REJECTED = 1

    total_results = 0
    examples = 0
    useful_samples = 0
    chat_closed = 0
    clear_rejection = 0
    fallback = 0
    accepted = 0
    durations = []
    suggestions = []
    invalid_logging_support = 0
    with open(filename, "w") as out_file:
        for j, line in enumerate(lines):
            durations.append(0)
            suggestions.append(0)
            debug_file.write("------------------------------------------------------\n")
            debug_file.write(f"| DIALOGUE {j}\n")
            debug_file.write("------------------------------------------------------\n")
            data = json.loads(line)
            counted = False
            for i, e in enumerate(data["events"]):
                if e["event"] == "user":
                    durations[j] += 1
                #     print(e["text"])
                # else:
                #     print(e)
                # if input("next?") == "y":
                #     continue
                if e["event"] == "action" and e["name"] == "action_smart_suggestion":
                    suggestions[j] += 1
                    if counted == False:
                        useful_samples += 1
                        counted = True
                    (
                        intents,
                        previous_suggestions,
                        remaining_suggestions,
                    ) = get_actions(data["events"][:i])
                    debug_file.write(f"User intents: {intents}\n")
                    debug_file.write(
                        f"Bot previous suggestions: {previous_suggestions}\n"
                    )
                    context = remove_useless_intents(intents + previous_suggestions)
                    debug_file.write(f"Context: {context}\n")
                    action = data["events"][i + 2]["value"]
                    debug_file.write(f"Action: {action}\n")
                    probability = calculate_logging_probability(
                        action,
                        remaining_suggestions,
                        no_action_probability,
                    )
                    if probability <= 0.0:
                        invalid_logging_support += 1
                        debug_file.write(
                            f"Skipped: action '{action}' has no support in the "
                            "assumed historical logging policy\n"
                        )
                        debug_file.write("====\n")
                        continue

                    debug_file.write(f"Example nr: {examples}\n")
                    examples += 1
                    next_user_event = get_next_user_event(data["events"], i)
                    result = classify_suggestion_outcome(action, next_user_event)
                    if next_user_event is None:
                        result = REJECTED
                        chat_closed += 1
                    elif result == ACCEPTED and next_user_event["parse_data"]["intent"][
                        "name"
                    ] == "affirmative":
                        total_results += 1
                        accepted += 1

                        if intents[-1] not in most_popular_action_per_intent:
                            most_popular_action_per_intent[intents[-1]] = {}
                        if action not in most_popular_action_per_intent[intents[-1]]:
                            most_popular_action_per_intent[intents[-1]][action] = 0
                        most_popular_action_per_intent[intents[-1]][action] += 1

                    elif result == REJECTED:
                        clear_rejection += 1
                    else:
                        result = ACCEPTED
                        total_results += 1
                        fallback += 1

                    shared_state = f"shared |S {' '.join(map(str, context))}\n"
                    out_file.write(shared_state)
                    all_data_file.write(shared_state)

                    # Action can be 0, since index specifies the action
                    selected_action = f"0:{result}:{probability} |A action={action}\n"
                    out_file.write(selected_action)
                    all_data_file.write(selected_action)

                    for sug in remaining_suggestions:
                        if sug != action:
                            action_line = f"|A action={sug}\n"
                            out_file.write(action_line)
                            all_data_file.write(action_line)
                    out_file.write("\n")
                    all_data_file.write("\n")

                    if result == ACCEPTED:
                        debug_file.write("Outcome: ACCEPTED\n")
                    else:
                        debug_file.write("Outcome: REJECTED\n")
                    debug_file.write("====\n")
    return (
        total_results,
        examples,
        useful_samples,
        total_results / examples,
        chat_closed,
        clear_rejection,
        fallback,
        accepted,
        durations,
        suggestions,
        invalid_logging_support,
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Convert historical conversations to VW data using an assumed "
            "fixed probability for selecting no_action."
        )
    )
    parser.add_argument(
        "--no-action-probability",
        type=float,
        default=0.5,
        help="Assumed historical probability of selecting no_action (default: 0.5).",
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data"),
        help="Directory containing conversations-all.json (default: data).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data"),
        help="Directory for generated VW data (default: data).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Seed used to shuffle complete conversations before splitting.",
    )
    args = parser.parse_args()
    if not 0.0 <= args.no_action_probability <= 1.0:
        parser.error("--no-action-probability must be between 0 and 1")
    return args


def main():
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    with open(args.input_dir / "conversations-all.json", "r") as f:
        lines = f.readlines()
    random.Random(args.seed).shuffle(lines)

    unique_actions = get_unique_functionalities()

    with open(args.output_dir / "actions.data", "w") as actions_f:
        actions_f.writelines(
            f"{i+1} - {action} \n" for i, action in enumerate(unique_actions)
        )

    with (
        open(args.output_dir / "actions.txt", "w") as debug_file,
        open(args.output_dir / "data.dat", "w") as all_data_file,
    ):
        debug_file.write(f"There are {len(unique_actions)} unique actions\n")
        debug_file.write(f"Conversation shuffle seed: {args.seed}\n")

        (
            total_results,
            examples,
            useful_samples,
            train_acceptance_rate,
            chat_closed,
            clear_rejection,
            fallback,
            accepted,
            durations,
            suggestions,
            invalid_logging_support,
        ) = create_vw_data(
            args.output_dir / "train.dat",
            lines[: math.floor(0.7 * len(lines))],
            debug_file,
            all_data_file,
            args.no_action_probability,
        )

        (
            temp_total_results,
            temp_examples,
            temp_useful_samples,
            test_acceptance_rate,
            temp_chat_closed,
            temp_clear_rejection,
            temp_fallback,
            temp_accepted,
            temp_durations,
            temp_suggestions,
            temp_invalid_logging_support,
        ) = create_vw_data(
            args.output_dir / "test.dat",
            lines[math.floor(0.7 * len(lines)) :],
            debug_file,
            all_data_file,
            args.no_action_probability,
        )

        total_results += temp_total_results
        examples += temp_examples
        useful_samples += temp_useful_samples
        chat_closed += temp_chat_closed
        clear_rejection += temp_clear_rejection
        fallback += temp_fallback
        accepted += temp_accepted
        durations += temp_durations
        suggestions += temp_suggestions
        invalid_logging_support += temp_invalid_logging_support

        debug_file.write(f"Total number of conversations: {len(lines)}\n")
        debug_file.write(f"Total number of useful conversations: {useful_samples}\n")
        debug_file.write(f"Total number of examples: {examples}\n")
        debug_file.write(f"Total number of chat closed conversations: {chat_closed}\n")
        debug_file.write(f"Total number of clear rejections: {clear_rejection}\n")
        debug_file.write(f"Total number of fallbacks: {fallback}\n")
        debug_file.write(f"Total number of accepted conversations: {accepted}\n")
        debug_file.write(f"Total positive conversations: {total_results}\n")
        debug_file.write(f"Total number of durations: {sum(durations)}\n")
        debug_file.write(f"Total number of suggestions: {sum(suggestions)}\n")
        debug_file.write(f"Average duration: {statistics.mean(durations)}\n")
        debug_file.write(f"STDEV durations: {statistics.stdev(durations)}\n")
        debug_file.write(f"Average suggestions: {statistics.mean(suggestions)}\n")
        debug_file.write(f"STDEV suggestions: {statistics.stdev(suggestions)}\n")
        debug_file.write(
            "Assumed no_action logging probability: " f"{args.no_action_probability}\n"
        )
        debug_file.write(
            "Skipped examples outside reconstructed logging support: "
            f"{invalid_logging_support}\n"
        )
        debug_file.write(f"Observed acceptance rate: {total_results/examples}\n")
        debug_file.write(f"Train acceptance rate: {train_acceptance_rate}\n")
        debug_file.write(f"Test acceptance rate: {test_acceptance_rate}")
        debug_file.write("\nMost popular action per intent:\n")
        debug_file.write(json.dumps(most_popular_action_per_intent, indent=4))


if __name__ == "__main__":
    main()
