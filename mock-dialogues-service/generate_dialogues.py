import os
import random
import signal

from mappings import (
    intent_to_functionality_dict,
    limited_intent_to_functionality_dict,
    list_of_functionalities,
    limited_intent_to_dialogue_dict,
    functionality_proposal,
    limited_intent_to_response_dict,
)
from helpers import remove_useless_intents, get_unique_functionalities


def screen_clear():
    # for mac and linux(here, os.name is 'posix')
    if os.name == "posix":
        _ = os.system("clear")
    else:
        # for windows platfrom
        _ = os.system("cls")


def generate_dialogue():
    user = list()
    for i in range(random.randint(1, 10)):
        user_utt = random.choice(list(limited_intent_to_functionality_dict.keys()))
        while user_utt in user:
            user_utt = random.choice(list(limited_intent_to_functionality_dict.keys()))
        user.append(user_utt)
    return user


def present_dialogue(dialogue, verbose=False):
    for utt in dialogue:
        if not verbose:
            print(f"User: {limited_intent_to_dialogue_dict[utt]}")
        else:
            print(
                f"User: {limited_intent_to_dialogue_dict[utt]}. [intent: {utt}, functionality:{limited_intent_to_functionality_dict[utt]}]"
            )


def create_user_utterances(dialogue):
    utterances = list()
    for utt in dialogue:
        utterances.append(f"{limited_intent_to_dialogue_dict[utt]}")
    return utterances


def create_bot_responses(dialogue):
    responses = list()
    for utt in dialogue:
        responses.append(f"{limited_intent_to_response_dict[utt]}")
    return responses


def get_remaining_suggestions(previous_intents, previous_slot_values=[]):
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
    return remaining_suggestions


def generate_suggestion(previous_intents, previous_slot_values=[]):
    remaining_suggestions = get_remaining_suggestions(
        previous_intents, previous_slot_values
    )
    return random.choice(remaining_suggestions)


def present_suggestion(suggestion):
    return f"{functionality_proposal[suggestion]}"


def get_user_input():
    while True:
        resp = input("Is the suggestion relevant?[y/n] ")
        if resp == "":
            resp = "y"
        if resp.lower()[0] == "y" or resp.lower()[0] == "n":
            return int(resp[0] == "y")
        print("Unclear input. Please enter 'y' or 'n'")


def record_feedback(
    dialogue, suggestion, resp, previous_slot_values=[], filename="rl_hf.dat"
):
    unique_actions = get_unique_functionalities()
    remaining_suggestions = get_remaining_suggestions(dialogue, previous_slot_values)

    probability = 1.0 / (len(remaining_suggestions) + 1)
    context = remove_useless_intents(dialogue + previous_slot_values)

    buffer = f"shared |{' '.join(map(str, context))}\n"
    buffer += f"{unique_actions.index(suggestion)}:{float(resp)}:{probability} |{suggestion}\n"
    for sug in remaining_suggestions:
        if sug != suggestion:
            buffer += f"|{sug}\n"
    buffer += "\n"

    with open(filename, "a") as out_file:
        out_file.write(buffer)


def gracefully_exit(signum, frame):
    print("\nGracefully exiting")
    exit(0)


def main():
    random.seed()
    signal.signal(signal.SIGINT, gracefully_exit)

    while True:
        screen_clear()
        # generate dialogue
        dialogue = generate_dialogue()
        # present dialogue
        present_dialogue(dialogue)
        # create suggestion
        suggestion = generate_suggestion(dialogue)
        print(f"THEANO suggests: {present_suggestion(suggestion)}")
        # ask for user feedback
        resp = get_user_input()
        # record user feedback as example
        record_feedback(dialogue, suggestion, resp)


if __name__ == "__main__":
    main()
