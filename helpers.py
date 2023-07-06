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

    remaining_suggestions = [
        f
        for f in list_of_functionalities
        if f not in previous_functionalities_from_intents
        and f not in previous_slot_values
    ] + ["no_action"]

    return (
        previous_intents,
        previous_slot_values,
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


def get_unique_functionalities():
    functionalities = intent_to_functionality_dict.values()
    return sorted(list(set(functionalities)))

