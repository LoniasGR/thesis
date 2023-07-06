import json
from mappings import intent_to_functionality_dict, list_of_functionalities


def get_actions(data):
    previous_slot_values = list(
        set(
            [
                x["value"]
                for x in data
                if x["event"] == "slot" and x["name"] == "bot_suggestion"
            ]
        )
    )

    user_events = [x for x in data if x["event"] == "user"]

    previous_intents = [
        event["parse_data"]["intent"]["name"]
        for event in user_events
        if event["parse_data"]["intent"]["name"] not in [None, "nlu_fallback"]
    ]

    # Map previous intents to functionalities
    previous_functionalities_from_intents = [
        intent_to_functionality_dict[x] for x in previous_intents
    ]

    useful_functionalities_to_intents = [
        x for x in previous_functionalities_from_intents if x != "no_action"
    ]

    remaining_suggestions = [
        f
        for f in list_of_functionalities
        if f not in previous_functionalities_from_intents
        and f not in previous_slot_values
    ]
    return (
        previous_intents,
        useful_functionalities_to_intents,
        remaining_suggestions,
    )


def remove_useless_intents(intents):
    return list(
        set(
            [
                x
                for x in intents
                if x
                not in [
                    "time_declare",
                    "stop_executing",
                    "region_declare",
                    "no_action",
                    "affirmative",
                    "negative",
                    "greetings",
                    "ask_chitchat",
                    "out_of_scope",
                    "insult",
                    "goodbye",
                    "thank_you",
                    "didnt_understand",
                    "whats_your_name",
                    "positive_feedback",
                    "sorry",
                    "what_is_athena",
                    "what_is_ilsp",
                    "greetings+whats_your_name",
                    "what_is_ilsp+what_is_athena",
                    "why_theano",
                    "may_i_ask",
                ]
            ]
        )
    )


def increment_hash_table_value(dict, key):
    if key not in dict:
        dict[key] = 1
    else:
        dict[key] += 1
    return dict


def main():
    with open("conversations-all.json", "r") as f:
        lines = f.readlines()
    usable_conversations = 0
    bandit_problems = 0
    context_hash_table = dict()
    for j, line in enumerate(lines):
        print(
            "-----------------------------------------------------------------------------"
        )
        print(f"| DIALOGUE #{j}")
        print(
            "-----------------------------------------------------------------------------"
        )
        data = json.loads(line)
        interaction_usable = True
        for i, e in enumerate(data["events"]):
            if e["event"] == "action" and e["name"] == "action_smart_suggestion":
                bandit_problems += 1
                if interaction_usable:
                    usable_conversations += 1
                    interaction_usable = False
                intents, actions_so_far, suggestions = get_actions(data["events"][:i])
                useful_intents = remove_useless_intents(intents)
                useful_intents_tmp = useful_intents.copy()
                useful_intents_tmp.sort()
                intent_string = "-".join(useful_intents_tmp)
                increment_hash_table_value(context_hash_table, intent_string)
                print(f"All previous intents: {intents}")
                print(f"Context: {useful_intents}")
                print(f"Times seen context: {context_hash_table[intent_string]}")
                # print(f"Remaining suggestions: {suggestions}")
                # print(f"Bot suggestion: {data['events'][i + 2]['value']}")
                print(f"Action: {data['events'][i + 2]['value']}")
                # User closed the chat.
                if len(data["events"]) <= i + 4:
                    print("Outcome: REJECTED")
                # There was a bug and the user didn't answer to the question.
                elif data["events"][i + 4]["event"] != "user":
                    print("Outcome: REJECTED")
                # User accepts the suggestion
                elif (
                    data["events"][i + 4]["parse_data"]["intent"]["name"]
                    == "affirmative"
                ):
                    # print(
                    #     f"USER: {data['events'][i + 4]['parse_data']['intent']['name']}"
                    # )
                    print("Outcome: ACCEPTED")
                # User rejects the suggestion or answers something random
                elif (
                    data["events"][i + 4]["parse_data"]["intent"]["name"] == "negative"
                    or data["events"][i + 4]["parse_data"]["intent"]["name"]
                    == "out_of_scope"
                    or data["events"][i + 4]["parse_data"]["intent"]["name"]
                    == "nlu_fallback"
                ):
                    # print(
                    #     f"USER: {data['events'][i + 4]['parse_data']['intent']['name']}"
                    # )
                    print("Outcome: REJECTED")
                # The bot suggests something and the user asks something else.
                elif (
                    data["events"][i + 2]["value"] != "no_action"
                    and data["events"][i + 2]["value"]
                    != data["events"][i + 4]["parse_data"]["intent"]["name"]
                ):
                    # print(
                    #     f"USER: {data['events'][i + 4]['parse_data']['intent']['name']}"
                    # )
                    print("Outcome: REJECTED")
                # Fallback
                else:
                    # print(
                    #     f"USER: {data['events'][i + 4]['parse_data']['intent']['name']}"
                    # )
                    print("Outcome: ACCEPTED")

                print("=====")
    print(f"USABLE CONVERSATIONS: {usable_conversations}")
    print(f"BANDIT PROBLEMS: {bandit_problems}")
    print(context_hash_table)


if __name__ == "__main__":
    main()
