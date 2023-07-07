# Thesis data exploration and offline training

## How to use

1. vowpal wabbit needs to be installed.
2. By running  `python format_data.py` all conversations from `conversations_all.json` are converted into a human readable version in `actions.txt` (which includes statistics on its final lines) and a VW input version split in two parts `test.dat` and `train.dat`.
3. `offline_training.ipynb` is a Jupyter notebook that creates the candidate model using offline policy evaluation.
