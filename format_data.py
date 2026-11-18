import json
import math
import statistics

from applications.mock_dialogues_service.app.common.helpers import (
    get_actions,
    get_unique_functionalities,
    remove_useless_intents,
)

most_popular_action_per_intent = {}


def create_vw_data(filename, lines, debug_file, all_data_file):
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
    with open(filename, "a") as out_file:
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
                    debug_file.write(f"Example nr: {examples}\n")
                    examples += 1
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
                    # User closed the chat.
                    if (
                        len(data["events"]) <= i + 4
                        or data["events"][i + 4]["event"] != "user"
                    ):

                        result = REJECTED
                        chat_closed += 1
                    # User accepts the suggestion
                    elif (
                        data["events"][i + 4]["parse_data"]["intent"]["name"]
                        == "affirmative"
                    ):
                        result = ACCEPTED
                        total_results += 1
                        accepted += 1

                        if intents[-1] not in most_popular_action_per_intent:
                            most_popular_action_per_intent[intents[-1]] = {}
                        if action not in most_popular_action_per_intent[intents[-1]]:
                            most_popular_action_per_intent[intents[-1]][action] = 0
                        most_popular_action_per_intent[intents[-1]][action] += 1

                    # User rejects the suggestion or answers something random
                    elif (
                        data["events"][i + 4]["parse_data"]["intent"]["name"]
                        == "negative"
                        or data["events"][i + 4]["parse_data"]["intent"]["name"]
                        == "out_of_scope"
                        or data["events"][i + 4]["parse_data"]["intent"]["name"]
                        == "nlu_fallback"
                    ) or (
                        data["events"][i + 2]["value"] != "no_action"
                        and data["events"][i + 2]["value"]
                        != data["events"][i + 4]["parse_data"]["intent"]["name"]
                    ):
                        result = REJECTED
                        clear_rejection += 1
                    # Bot asks no_action and user responds with a specific intent
                    else:
                        result = ACCEPTED
                        total_results += 1
                        fallback += 1

                    probability = 1.0 / (len(remaining_suggestions))

                    shared_state = (
                        f"shared | previous_states={','.join(map(str, context))}\n"
                    )
                    out_file.write(shared_state)
                    all_data_file.write(shared_state)

                    # Action can be 0, since index specifies the action
                    selected_action = f"0:{result}:{probability} | action={action}\n"
                    out_file.write(selected_action)
                    all_data_file.write(selected_action)

                    for sug in remaining_suggestions:
                        if sug != action:
                            action_line = f"| action={sug}\n"
                            out_file.write(action_line)
                            all_data_file.write(action_line)
                    out_file.write("\n")
                    all_data_file.write("\n")

                    if result == 1:
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
    )


def main():
    with open("data/conversations-all.json", "r") as f:
        lines = f.readlines()

    unique_actions = get_unique_functionalities()

    with open("data/actions.data", "w") as actions_f:
        actions_f.writelines(
            f"{i+1} - {action} \n" for i, action in enumerate(unique_actions)
        )

    with (
        open("data/actions.txt", "w") as debug_file,
        open("data/data.dat", "w") as all_data_file,
    ):
        debug_file.write(f"There are {len(unique_actions)} unique actions\n")

        (
            total_results,
            examples,
            useful_samples,
            loss1,
            chat_closed,
            clear_rejection,
            fallback,
            accepted,
            durations,
            suggestions,
        ) = create_vw_data(
            "data/train.dat",
            lines[: math.floor(0.7 * len(lines))],
            debug_file,
            all_data_file,
        )

        (
            temp_total_results,
            temp_examples,
            temp_useful_samples,
            loss2,
            temp_chat_closed,
            temp_clear_rejection,
            temp_fallback,
            temp_accepted,
            temp_durations,
            temp_suggestions,
        ) = create_vw_data(
            "data/test.dat",
            lines[math.floor(0.7 * len(lines)) :],
            debug_file,
            all_data_file,
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
        debug_file.write(f"Loss: {total_results/examples}\n")
        debug_file.write(f"Train loss: {loss1}\n")
        debug_file.write(f"Test loss: {loss2}")
        debug_file.write("\nMost popular action per intent:\n")
        debug_file.write(json.dumps(most_popular_action_per_intent, indent=4))


if __name__ == "__main__":
    main()
