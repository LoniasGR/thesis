import json
import math
from helpers import get_actions, remove_useless_intents, get_unique_functionalities


def create_train_test_data():
    with open("data.dat", "r") as f_in:
        lines = f_in.readlines()
    with open("train.dat", "w") as fo1:
        fo1.writelines(lines[: math.floor(0.7 * len(lines))])
    with open("test.dat", "w") as fo2:
        fo2.writelines(lines[math.floor(0.7 * len(lines)) :])


def main():
    with open("conversations-all.json", "r") as f:
        lines = f.readlines()

    unique_actions = get_unique_functionalities()
    with open("actions.data", "w") as actions_f:
        for i, action in enumerate(unique_actions):
            actions_f.write(f"{i+1} - {action} \n")

    probability = 1.0 / len(unique_actions)
    total_results = 0
    examples = 0
    with open("./actions.txt", "w") as debug_file:
        debug_file.write(f"There are {len(unique_actions)} unique actions")
        with open("./data.dat", "w") as out_file:

            for j, line in enumerate(lines):
                debug_file.write*"------------------------------------------------------"
                data = json.loads(line)
                for i, e in enumerate(data["events"]):
                    if e["event"] == "action" and e["name"] == "action_smart_suggestion":
                        examples += 1
                        intents, previous_suggestions, _ = get_actions(data["events"][:i])
                        debug_file.write(f"User intents: {intents}\n")
                        debug_file.write(f"Bot previous suggestions: {previous_suggestions}\n")
                        context = remove_useless_intents(intents)
                        debug_file.write(f"Context: {context}\n")
                        action = data["events"][i + 2]["value"]
                        debug_file.write(f"Action: {action}\n")
                        action_id = unique_actions.index(action)
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
                        out_file.write(
                            f"{action_id+1}:{result}:{probability} | {' '.join(map(str, context))}\n"
                        )
            print(f"Loss: {total_results/examples}")


if __name__ == "__main__":
    main()
    create_train_test_data()
