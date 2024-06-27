intent_to_functionality_dict: dict[str, str] = {
    "covid_stats": "covid_statistics_form",
    "EODY_faq": "no_action",
    "ask_chitchat": "no_action",
    "mask_faq": "no_action",
    "vaccines": "no_action",
    "time_declare": "no_action",
    "pharma_search": "pharmacy_form",
    "insult": "no_action",
    "affirmative": "no_action",
    "negative": "no_action",
    "greetings": "no_action",  # maybe tell we haven't greeted ourselves
    "stop_executing": "no_action",
    "region_declare": "no_action",
    "goodbye": "no_action",
    "thank_you": "no_action",
    "didnt_understand": "no_action",
    "am_i_ill": "ill_questionnaire_form",
    "why_avoid_pharma": "no_action",
    "what_to_do_if_positive": "what_to_do_if_positive",
    "symptoms": "symptoms",
    "whats_your_name": "no_action",
    "ways_of_protection": "ways_of_protection",
    "underlying_conditions": "underlying_conditions",
    "personal_ways_of_protection": "ways_of_protection",
    "collective_ways_of_protection": "ways_of_protection",
    "all_ways_of_protection": "ways_of_protection",
    "test_cost": "test_cost",
    "pcr_test_cost": "test_cost",
    "rapid_test_cost": "test_cost",
    "all_test_cost": "test_cost",
    "self_test": "no_action",
    "all_of_them": "no_action",
    "test_types": "test_types",
    "general_knowledge_tests": "no_action",
    "out_of_scope": "no_action",
    "vaccine_stats": "vaccine_stats_form",
    "find_new_icus": "icu_stats_form",
    "positive_feedback": "no_action",
    "affirmative+covid_stats": "covid_statistics_form",
    "affirmative+pharma_search": "pharmacy_form",
    "affirmative+find_new_icus": "icu_stats_form",
    "affirmative+vaccine_stats": "vaccine_stats_form",
    "negative+covid_stats": "covid_statistics_form",
    "negative+pharma_search": "pharmacy_form",
    "negative+find_new_icus": "icu_stats_form",
    "negative+vaccine_stats": "vaccine_stats_form",
    "negative+thank_you": "no_action",
    "greetings+covid_stats": "covid_statistics_form",
    "greetings+pharma_search": "pharmacy_form",
    "greetings+ask_chitchat": "no_action",
    "thank_you+covid_stats": "covid_statistics_form",
    "greetings+whats_your_name": "no_action",
    "what_is_ilsp+what_is_athena": "no_action",
    "why_theano": "no_action",
    "may_i_ask": "no_action",
    "sorry": "no_action",
    "what_is_athena": "no_action",
    "what_is_ilsp": "no_action",
    "no_action": "no_action",
}


list_of_functionalities: list[str] = [
    "icu_stats_form",
    "vaccine_stats_form",
    "covid_statistics_form",
    "pharmacy_form",
    "ill_questionnaire_form",
    "ways_of_protection",
    "symptoms",
    "test_types",
    "test_cost",
    "what_to_do_if_positive",
    "underlying_conditions",
    "no_action",
]


def remove_intents_without_context(intents: list[str]) -> list[str]:
    """Remove all the intents that have no_action as a corresponding action"""
    return list(set([x for x in intents if x not in create_no_action_intents_list()]))


def create_no_action_intents_list() -> list[str]:
    intents_without_context = []
    for k, v in intent_to_functionality_dict.items():
        if v == "no_action":
            intents_without_context.append(k)
    return intents_without_context


def get_unique_functionalities() -> list[str]:
    functionalities = intent_to_functionality_dict.values()
    return sorted(list(set(functionalities)))
