import os
from random import random

import vowpalwabbit
from data_models.classes import UserData
from logger.logger import CustomLogger
from utils.utils import envOrDefault
from .mappings import remove_intents_without_context, get_unique_functionalities

logger: CustomLogger = CustomLogger(__name__)


def init_model() -> None:
    global vw_model
    vw_model = vowpalwabbit.Workspace(
        enable_logging=True,
        cb_explore_adf=True,
        i=envOrDefault("VOWPALWABBIT_MODEL", "./models/candidate_model.vw"),
        cb_type="ips",
    )


def to_vw_format(
    context: list[str],
    actions: list[str],
    cb_label: None | tuple[str, float, float],
) -> str:
    """Format data to a configuration that vw understands"""
    context_formatted_for_vw: str = f"shared | {' '.join(map(str, context))}\n"
    actions_for_vw = ""
    for sug in actions:
        action = ""
        if cb_label is not None:
            chosen_action, cost, prob = cb_label
            if sug == chosen_action:
                action += f"0:{cost}:{prob} "
        action += f"| {sug}\n"
        actions_for_vw += action
    return context_formatted_for_vw + actions_for_vw


def sample_custom_pmf(pmf: list[float]) -> tuple[int, float] | None:
    """When we call VW we get a pmf, probability mass function, as the output. Since we are incorporating exploration into our strategy,
    VW will give us a list of probabilities over the set of actions.

    We sample the pmf to create an exploration strategy"""
    total = sum(pmf)
    scale = 1 / total
    pmf = [x * scale for x in pmf]
    draw = random()
    sum_prob = 0.0
    for index, prob in enumerate(pmf):
        sum_prob += prob
        if sum_prob > draw:
            return index, prob


def vw_learn(user: UserData, intent: str) -> None:
    if user.recommendation == '':
        return

    unique_actions = get_unique_functionalities()
    cost = calculate_cost(intent, user.recommendation)
    user.set_cost(cost)

    context = remove_intents_without_context(
        user.previous_intents + user.previous_suggestions
    )

    vw_data = to_vw_format(
        context,
        user.remaining_suggestions,
        (
            unique_actions[unique_actions.index(user.recommendation)],
            cost,
            user.recommendation_probability,
        ),
    )
    logger.debug(
        f"\nContext: {context}\nRemaining Suggestions:{user.remaining_suggestions}"
    )
    logger.debug(unique_actions[unique_actions.index(user.recommendation)])
    logger.debug(f"Learning VW data: {vw_data}")
    vw_format = vw_model.parse(
        vw_data,
        vowpalwabbit.LabelType.CONTEXTUAL_BANDIT,
    )
    vw_model.learn(vw_format)

    vw_model.save(envOrDefault("VOWPALWABBIT_MODEL", "./models/candidate_model.vw"))


def calculate_cost(intent: str, recommendation: str) -> float:
    unique_actions = get_unique_functionalities()
    # TODO: This needs to be expanded
    # Empty intent means the user left
    if intent == "":
        return 0.0
    if intent == "affirmative":
        return -1.0
    if intent in unique_actions:
        if intent != recommendation:
            return 0.0
        else:
            return -1.0
    if intent == "negative":
        return 0.0
    return 0.0


def create_suggestion(user: UserData) -> int | None:
    previous_data: list[str] = user.previous_intents + user.previous_suggestions
    context: list[str] = remove_intents_without_context(previous_data)
    input_to_vw: str = to_vw_format(context, user.remaining_suggestions, None)
    logger.debug(f"\n{input_to_vw}")
    recommendations_pmf = vw_model.predict(input_to_vw)
    recommendation, recommendation_prob = sample_custom_pmf(recommendations_pmf)

    user.set_recommendation_data(
        user.remaining_suggestions[recommendation], recommendation_prob
    )
    logger.debug(f"Suggestion name: {user.remaining_suggestions[recommendation]}")

    return recommendation
