from enum import unique
import json
import math
from helpers import get_actions, remove_useless_intents, get_unique_functionalities


def create_vw_data(filename, lines, debug_file):
    unique_actions = get_unique_functionalities()

    total_results = 0
    examples = 0
    useful_samples = 0

    with open(filename, "w") as out_file:
        for j, line in enumerate(lines):
            debug_file.write(
                "------------------------------------------------------\n"
            )
            debug_file.write(f"| DIALOGUE {j}\n")
            debug_file.write(
                f"------------------------------------------------------\n"
            )
            data = json.loads(line)

            counted = False
            for i, e in enumerate(data["events"]):
                if (
                    e["event"] == "action"
                    and e["name"] == "action_smart_suggestion"
                ):
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
                    if len(data["events"]) <= i + 4:
                        result = 0
                    # There was a bug and the user didn't answer to the question.
                    elif data["events"][i + 4]["event"] != "user":
                        result = 0
                    # User accepts the suggestion
                    elif (
                        data["events"][i + 4]["parse_data"]["intent"]["name"]
                        == "affirmative"
                    ):
                        result = 1
                        total_results += 1
                    # User rejects the suggestion or answers something random
                    elif (
                        data["events"][i + 4]["parse_data"]["intent"]["name"]
                        == "negative"
                        or data["events"][i + 4]["parse_data"]["intent"]["name"]
                        == "out_of_scope"
                        or data["events"][i + 4]["parse_data"]["intent"]["name"]
                        == "nlu_fallback"
                    ):
                        result = 0
                    # The bot suggests something and the user asks something else.
                    elif (
                        data["events"][i + 2]["value"] != "no_action"
                        and data["events"][i + 2]["value"]
                        != data["events"][i + 4]["parse_data"]["intent"]["name"]
                    ):
                        result = 0
                    # Fallback
                    else:
                        result = 1
                        total_results += 1

                    probability = 1.0 / (len(remaining_suggestions) + 1)

                    out_file.write(f"shared |{' '.join(map(str, context))}\n")

                    if result == 1:
                        written_result = -1
                    else:
                        written_result = 0
                    out_file.write(
                        f"{unique_actions.index(action)}:{float(written_result)}:{probability} |{action}\n"
                    )
                    for sug in remaining_suggestions:
                        if sug != action:
                            out_file.write(
                                f"|{sug}\n"
                            )
                    out_file.write("\n")

                    if result == 1:
                        debug_file.write("Outcome: ACCEPTED\n")
                    else:
                        debug_file.write("Outcome: REJECTED\n")
                    debug_file.write("====\n")

    return total_results, examples, useful_samples, total_results/examples



def main():
    with open("conversations-all.json", "r") as f:
        lines = f.readlines()

    unique_actions = get_unique_functionalities()

    with open("actions.data", "w") as actions_f:
        for i, action in enumerate(unique_actions):
            actions_f.write(f"{i+1} - {action} \n")

    with open("./actions.txt", "w") as debug_file:
        debug_file.write(f"There are {len(unique_actions)} unique actions\n")

        total_results, examples, useful_samples, loss1 = create_vw_data("./train.dat", lines[: math.floor(0.7 * len(lines))], debug_file)

        temp_total_results, temp_examples, temp_useful_samples, loss2 = create_vw_data("./test.dat", lines[math.floor(0.7 * len(lines)) :], debug_file)

        total_results += temp_total_results
        examples += temp_examples
        useful_samples += temp_useful_samples

        debug_file.write(f"Total number of conversations: {len(lines)}\n")
        debug_file.write(f"Total number of useful conversations: {useful_samples}\n")
        debug_file.write(f"Total number of examples: {examples}\n")
        debug_file.write(f"Loss: {total_results/examples}\n")
        debug_file.write(f"Train loss: {loss1}\n")
        debug_file.write(f"Test loss: {loss2}")



if __name__ == "__main__":
    main()
