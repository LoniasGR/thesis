import os
import random

import vowpalwabbit


def get_examples(filename):
    examples = []
    with open(filename, "r") as fin:
        example = []
        for line in fin:
            if line.startswith("shared |"):
                if len(example) > 0:
                    examples.append(example)
                example = []
                example.append(line.strip("\n"))
            else:
                if len(line.strip("\n")) > 0:
                    example.append(line.strip("\n"))
        examples.append(example)
    return examples


def dialogue_length(line):
    return len(line.split("|")[1].strip().split(" "))


def calculate_dialogue_lengths(examples):
    lengths = {}
    for e in examples:
        length = dialogue_length(e[0])
        if length in lengths:
            lengths[length] += 1
        else:
            lengths[length] = 1
    return lengths


def get_average(lengths: dict):
    sum = 0
    count = 0
    for k, v in lengths.items():
        sum += k * v
        count += v
    return sum / count, count


def sample_custom_pmf(pmf):
    total = sum(pmf)
    scale = 1 / total
    pmf = [x * scale for x in pmf]
    draw = random.random()
    sum_prob = 0.0
    for index, prob in enumerate(pmf):
        sum_prob += prob
        if sum_prob > draw:
            return index, prob


if __name__ == "__main__":
    random.seed()
    if os.path.isfile("candidate_model.vw"):
        os.remove("candidate_model.vw")
    cb_type = "dr"

    vw_train = vowpalwabbit.Workspace(
        cb_explore_adf=True,
        cb_type=cb_type,
        f="candidate_model.vw",
        softmax=True,
        d="data/train.dat",
        arg_list=["--lambda", "10"],
    )
    vw_train.finish()

    vw_test = vowpalwabbit.Workspace(
        cb_explore_adf=True,
        cb_type=cb_type,
        i="candidate_model.vw",
        t=True,
        d="data/test.dat",
        p="predictions.txt",
    )
    vw_test.finish()
