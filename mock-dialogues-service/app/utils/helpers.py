from .mappings import (
    intent_to_functionality_dict,
    list_of_functionalities,
    limited_intent_to_functionality_dict,
)


def get_all_intents():
    return list(limited_intent_to_functionality_dict.keys())


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

    remaining_suggestions = generate_remaining_suggestions(
        previous_functionalities_from_intents, previous_slot_values
    )

    return (
        previous_intents,
        previous_slot_values,
        remaining_suggestions,
    )


def generate_remaining_suggestions(functionalities, slot_values=[]):
    return [
        f
        for f in list_of_functionalities
        if f not in functionalities and f not in slot_values
    ] + ["no_action"]


def remove_useless_intents(intents: list[str]):
    clean_intents = list()
    for i in intents:
        if "+" in i:
            clean_intents += i.split("+")
        else:
            clean_intents.append(i)
    return list(
        set(
            [
                x
                for x in clean_intents
                if x
                not in [
                    "time_declare",
                    "insult",
                    "affirmative",
                    "negative",
                    "greetings",  # maybe tell we haven't greeted ourselves
                    "stop_executing",
                    "region_declare",
                    "goodbye",
                    "thank_you",
                    "didnt_understand",
                    "all_of_them",
                    "out_of_scope",
                    "positive_feedback",
                    "may_i_ask",
                    "sorry",
                    "no_action",
                ]
            ]
        )
    )


def get_unique_functionalities():
    functionalities = intent_to_functionality_dict.values()
    return sorted(list(set(functionalities)))
