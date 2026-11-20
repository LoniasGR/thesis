# Thesis data exploration and offline training

## How to use

1. vowpal wabbit needs to be installed.
2. Run `python format_data.py` to convert all conversations from
   `conversations-all.json`. The conversion assumes that the historical logging
   policy selected `no_action` with probability `0.5` and otherwise selected
   uniformly among the remaining actions. This assumption is recorded in the
   generated `actions.txt`. Complete conversations are shuffled with seed `42`
   before the 70/30 split. Use `--seed` to select another reproducible shuffle.

   To run sensitivity analyses without overwriting the main generated data:

   ```bash
   python format_data.py --no-action-probability 0.2 --output-dir data/q020
   python format_data.py --no-action-probability 0.5 --output-dir data/q050
   python format_data.py --no-action-probability 0.8 --output-dir data/q080
   ```

   `actions.txt` reports examples skipped because their selected action was
   outside the reconstructed logging-policy support. To train a variant, set
   `VW_DATA_FILE` to its generated `data.dat` before running the notebook.

   To evaluate with the standalone trainer:

   ```bash
   python train.py \
     --cb-type ips \
     --learning-rate 0.1 \
     --lambda-value 1 \
     --train-data data/q020/train.dat \
     --test-data data/q020/test.dat \
     --model models/candidate-q050.vw \
     --predictions predictions-q050.txt \
     --summary summary-q050.json
   ```

   To evaluate multiple VW learning rates and lambda values without allowing
   examples from the same conversation into different folds:

   ```bash
   python cross_validate.py \
     --folds 5 \
     --seed 42 \
     --learning-rates 0.1 0.5 1.0 \
     --lambda-values 1 10 \
     --output cross_validation_results.json
   ```

   Configurations are ranked by the mean fold SNIPS cost; lower is better.
   Training uses `|S` context features, `|A` action features, and `-q SA` so
   recommendations can depend on context-action interactions.

   To regenerate and independently evaluate the human-feedback dataset:

   ```bash
   python format_human_feedback.py
   python evaluate_human_feedback.py
   ```

   These examples are held out from production-data training and are not mixed
   into the grouped cross-validation folds.
3. `offline_training.ipynb` is a Jupyter notebook that creates the candidate model using offline policy evaluation.
