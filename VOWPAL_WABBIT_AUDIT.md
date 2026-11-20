# Vowpal Wabbit training and evaluation audit

## Scope

This is a read-only review of the Vowpal Wabbit data, training, evaluation, and
model-serving paths. The main training path is
[`format_data.py`](format_data.py) followed by
[`offline_training.ipynb`](offline_training.ipynb), as requested. Related
microservice and human-feedback code was checked where it defines the logging
policy or supplies data to the same model.

The original audit was read-only. The implementation status below records the
later follow-up changes.

## Follow-up implementation status

The first historical-data mitigation has since been implemented:

- `format_data.py` now assumes a configurable fixed `no_action` logging
  probability, defaulting to `0.5`.
- The selected action receives probability `q` when it is `no_action`, or
  `(1 - q) / number_of_specific_actions` otherwise.
- Eight examples outside reconstructed logging support are reported and
  skipped.
- The generated train/test files are overwritten rather than appended.
- 20%, 50%, and 80% sensitivity datasets can be generated separately with
  `--output-dir`.
- The notebook can select one of those datasets through `VW_DATA_FILE`.
- Generated acceptance-rate statistics are no longer mislabeled as loss.

This is a conditional-data fix, not recovery of the exact historical policy.
All IPS conclusions must still state the fixed-`q` assumption and report
sensitivity to alternative values.

## Executive summary

The current pipeline should not be used to make reliable offline-policy
comparisons. The largest problem is that the recorded logging probabilities do
not describe the policy that generated the data, which invalidates ordinary IPS
training/evaluation. The formatter also assigns the wrong label to a
significant number of examples and destroys the grouping needed for a clean
evaluation split. The notebook then evaluates through an incorrect
workspace/example lifecycle, and its reported comparison mixes an acceptance
rate with a cost/loss estimate.

The human-feedback dataset has separate ADF-format errors and is not currently
included in training, while the saved notebook output uses inconsistent input
syntax and contains an execution error.

## Findings

### VW-1: Critical - recorded propensities are not the logging-policy propensities

**Status:** mitigated for historical training, conditional on the documented
fixed-`no_action` probability. The remaining limitation is uncertainty about
the period-specific historical values.

[`format_data.py:109`](format_data.py#L109) assigns
`probability = 1 / len(remaining_suggestions)` to every chosen action.

The corresponding production policy is not uniform. In
[`actions.py:1537-1547`](applications/covid-va-chatbot/actions.py#L1537), it first
chooses `no_action` with probability `NO_ACTION_PROB` (default `0.2` at
[`actions.py:54-57`](applications/covid-va-chatbot/actions.py#L54)); only the
remaining `(1 - NO_ACTION_PROB)` mass is sampled uniformly from the candidate
list.

For a normal candidate set of size `n`, the logging probabilities are
therefore approximately:

- `no_action`: `q + (1 - q) / n`
- each other action: `(1 - q) / n`

where `q` is `NO_ACTION_PROB`. Recording `1 / n` for both cases understates the
probability of `no_action` and overstates the probability of every other
action. IPS/DR estimates depend on these exact propensities, so the training
losses and model updates are biased rather than merely noisy.

The source data supports that the special `no_action` policy was active:
`no_action` accounts for 594 of 1,043 logged suggestions (about 57%), rather
than the roughly uniform 1/11 share.

This also means that the assertion that the behavior policy was uniformly
random is not sufficient. The actual probability selected by the historical
policy must be logged at decision time; it cannot safely be reconstructed from
only the final action and current candidate count.

### VW-2: High - 72 rewards are assigned from a fixed event offset, and 63 are clear false closures

**Status:** fixed. `format_data.py` now scans forward for the next user event
and ignores intermediate Rasa events. Direct intents are also mapped to their
action functionality. A missing later user response remains a rejection.
Unsupported examples are still excluded separately. The 1,035 supported
examples contain 533 accepted and 502 rejected outcomes.

The formatter reads the outcome at the fixed position `events[i + 4]`
([`format_data.py:65-100`](format_data.py#L65)). If that event is absent **or is
not a user event**, the example is classified as a user closing the
conversation and receives cost `1`.

Rasa histories do not guarantee that exact shape. In the current source:

- 72 suggestions have a non-user event at `i + 4`;
- 63 of those histories contain a later user response;
- these are distributed across slot, action, active-loop, and bot events.

These examples are labeled as rejection before the actual user's next
response is inspected. The formatter should locate the next relevant user
event, with an explicit timeout/session boundary rule, rather than treating
any intervening Rasa event as closure.

### VW-3: High - the random 80/20 split leaks dialogue history

**Status:** superseded for `train.py`. `format_data.py` now shuffles complete
conversation records with a fixed seed (`42` by default) before the 70/30
split. Every suggestion from a conversation therefore remains on one side.
The older notebook's row-level shuffle remains unrelated to the current
`train.py` pipeline.

The notebook flattens the file into individual CB examples and then shuffles
and splits the examples
([`offline_training.ipynb`, cell 4](offline_training.ipynb)). It does not
retain a conversation identifier.

The 1,043 source examples come from only 468 conversations. A total of 194
conversations contain multiple suggestions. A row-level random split can
therefore put early and late suggestions from the same conversation on
opposite sides of the split. Their contexts and rewards are temporally and
behaviorally correlated, so this is not an independent evaluation.

The split is also nondeterministic: `random.seed()` is called without a fixed
seed and the data is shuffled before every split. The exact train and
validation sets cannot be reproduced from the notebook alone.

For evaluation, split by conversation (or by user/time), and keep every
suggestion from one conversation in one fold. If progressive validation is the
claimed method, report a true chronological pre-update prediction stream and
do not present an unrelated random holdout as progressive validation.

### VW-4: High - the test workspace receives examples parsed by another, already-finished workspace

**Status:** fixed in `offline_training.ipynb`; validation examples are now
parsed by `vw_test`. `train.py` did not contain this defect because it provides
the test dataset to a separate test-only workspace through the `d` argument.

The notebook creates `vw_test` and then does:

```python
vw_format = vw_test.parse(data_validate[i])
vw_test.learn(vw_format)
vw_test.finish_example(vw_format)
```

See the evaluation loop in [`offline_training.ipynb`, cell 10](offline_training.ipynb).
`vw_train` was already closed by `vw_train.finish()` in the preceding cell.
Parsed examples belong to the workspace that created them and should be parsed,
used, and finished against the same test workspace.

The validation loop should parse and finish examples through `vw_test`. More
importantly, mixing workspace lifecycles makes the stored validation result
difficult to interpret and risks behavior that depends on pyvw version and
state-management internals.

### VW-5: High - the main reported baseline comparison uses incompatible metrics

**Status:** the generated `actions.txt` now reports acceptance rates instead of
calling them loss. The thesis table and VW candidate-policy loss comparison
still require correction.

[`format_data.py:226-228`](format_data.py#L226) labels
`total_results / examples` and the two split ratios as `Loss`, even though
`total_results` counts accepted examples. These values are acceptance rates,
not costs.

The current `data/data.dat` contains:

- 479 examples with cost `0` (accepted);
- 564 examples with cost `1` (rejected).

Thus:

- observed acceptance is `479 / 1043 = 0.45925`;
- observed rejection/cost is `564 / 1043 = 0.54075`.

The thesis table labels the `0.459` value as the random-policy
**loss/cost**, then compares it to VW's estimated candidate-policy cost
([`our_work.tex:606-619`](thesis-report/body_matter/our_work/our_work.tex#L606)).
The two quantities are not the same measure and must not be used to claim that
`0.284 < 0.459` demonstrates a better candidate policy.

Because the logger propensities are also wrong (VW-1), an adjusted IPS
value/variance must be recomputed before drawing a model-quality conclusion.

### VW-6: High, dormant - the human-feedback ADF examples use global action numbers instead of ADF row indices

**Status:** fixed. Human-feedback generators now write ADF index `0`,
`action=...` features, and a propensity based on the actual sampled candidate
set. The existing 582-example file was converted to this format.

[`generate_dialogues_from_db.py:37-44`](applications/mock_dialogues_service/app/utils/generate_dialogues_from_db.py#L37)
and
[`generate_dialogues.py:98-108`](applications/mock_dialogues_service/app/utils/generate_dialogues.py#L98)
place the chosen action on the first action row after `shared`, but label that
row with `unique_actions.index(suggestion)`.

In ADF format, the selected action index refers to the position within that
example's action list. Since the selected row has been moved to the first
position, its index must be `0` (as it is in `format_data.py`).

The current `new_data.dat` demonstrates the problem: its 582 examples use
label indices `0` through `11`; only 31 examples use `0`. These labels refer to
different rows than the first, labeled row that is actually written, and many
indices are outside a reduced candidate set.

The additional-data files also use a different representation from the main
format:

- old data: `shared | previous_states=...` and `| action=...`;
- human-feedback data: `shared | ...` and `| ...` (without `action=`).

That creates different VW feature identities and prevents the two datasets
from matching even when they describe the same context/action.

This bug is currently dormant in the notebook: `examples_new` is read for
plots, but `data = examples_old` is trained and the use of `examples_new` as
validation is commented out.

### VW-7: Medium, dormant - human-feedback reward and propensity calculations are inconsistent

**Status:** fixed. Accepted feedback is written as cost `0`, rejected as cost
`1`, and propensity uses `1 / len(remaining_suggestions)`.

[`generate_dialogues.py:85-108`](applications/mock_dialogues_service/app/utils/generate_dialogues.py#L85)
turns "yes" into `1` and writes it directly as the VW cost. The main pipeline
defines accepted as cost `0` and rejected as cost `1`. Therefore this generator
reverses the direction of the reward.

The database generator corrects that direction with
`-(int(response) - 1)`, but both human-feedback generators divide by
`len(remaining_suggestions) + 1`, despite `remaining_suggestions` already
being the list sampled to select the action. The extra denominator yields the
wrong logging probability in general.

These points must be fixed and covered with format-level tests before merging
the 582 human-feedback examples into training.

### VW-8: Medium - `train.dat` and `test.dat` are appended to and are currently stale/duplicated

**Status:** fixed. The formatter overwrites generated files on every run.

`all_data_file` is opened in write mode, but both split files are opened in
append mode in [`format_data.py:28`](format_data.py#L28). Re-running the
documented conversion command accumulates old training runs.

In the current repository:

- `data/data.dat`: 1,043 CB examples;
- `data/train.dat`: 3,400 blocks;
- `data/test.dat`: 772 blocks.

The split files contain large numbers of duplicate blocks and their totals do
not match the 70/30 split described in the README. The notebook currently
avoids this by ignoring them and re-splitting `data/data.dat`, but
`train.py` and any reader following the README will train/evaluate on stale
data.

### VW-9: Medium - context construction is nondeterministic and overly collapsed

**Status:** fixed. Context filtering preserves first-seen order and removes
duplicates deterministically. Context and action features now use `|S` and
`|A`, and training/serving use `-q SA`. The model selects all 12 actions
across human-feedback contexts rather than collapsing to two.

[`remove_useless_intents`](applications/mock_dialogues_service/app/common/helpers.py#L62)
returns a `list(set(...))`, discarding order and duplicates. The formatter then
joins that list into one `previous_states=a,b,...` categorical value.

Consequences:

- Python hash randomization can change serialized feature values between
  runs/processes;
- a set of past states is represented as one compound feature, not as
  individual composable context features;
- exact-order differences disappear or reappear inconsistently.

The current data contains three logical context bags that were observed in
multiple serialized orders. The same conversation semantics can therefore hit
different VW features, reducing reuse and making offline and serving
representations dependent on process/runtime ordering.

The context serializer should be deterministic. If the intended semantics are
an unordered bag, emit sorted, individual categorical features. If history
order is important, preserve it explicitly and encode it consistently in both
training and serving.

### VW-10: Medium - eight chosen historical actions are not in the reconstructed candidate set

The formatter rebuilds the action set from previous intents and slots, but for
eight examples the logged selected action is absent from that reconstructed
list. The formatter still emits the selected row first, but the propensity
`1 / len(remaining_suggestions)` was computed for a candidate set that did not
contain the action that actually occurred.

For an IPS-capable record, support must be established:
`p_logging(chosen action | context) > 0`. A zero-support record is invalid.
Action-set reconstruction must use the exact candidate list recorded at
decision time rather than inferring it later from a lossy event history.

### VW-11: Medium - the prediction/online-learning implementation does not manage shared workspace state safely

The microservice keeps a global VW workspace and exposes it through FastAPI
sync endpoints. It parses and learns examples in
[`vw_utils.py:87-93`](applications/smart-suggest-microservice/app/vw/vw_utils.py#L87)
but never calls `finish_example`, and it performs `predict`, `learn`, and
`save` without synchronization.

Concurrent requests can therefore:

- operate on the same mutable workspace at the same time;
- interleave model updates and predictions;
- race while saving the model file;
- retain parsed-example state that the offline notebook correctly releases.

The serving process should serialize workspace access (or otherwise provide a
documented thread-safe update design), finish examples consistently, and
save via a temporary file plus atomic replacement.

### VW-12: Low - the notebook's final prediction check is invalid and the saved run is not clean

The prediction cell uses a manually written format different from the training
format: bare shared/action features instead of `previous_states=...` and
`action=...`, and it calls the previously finished `vw_train` workspace
([`offline_training.ipynb`, cell 11](offline_training.ipynb)). The recorded
output is consequently uniform and the cell ends with
`NameError: sample_custom_pmf is not defined`.

The table and results later in the notebook are hand-written snapshots from
previous runs, not assertions produced from the current cells. The notebook
therefore cannot currently serve as a reproducible training/evaluation
artifact.

## Evaluation redesign requirements

Before trusting a policy-quality claim, the following should be true:

1. Log the exact action set and sampled-action propensity **at decision time**.
2. Enforce one reward definition and encode it as VW cost consistently.
3. Associate every example with a conversation/user identifier.
4. Split by conversation (preferably by time/user), or use genuine progressive
   validation with pre-update predictions.
5. Keep the training and serving feature/action serializers identical and
   validate them automatically.
6. Recompute IPS with coverage checks, report effective sample size and
   uncertainty, and add a doubly-robust estimator with an independently trained
   reward model.
7. Compare against the logging policy using the same cost metric.
8. Make a clean, restartable notebook/script run that regenerates all files and
   the model from a fixed seed and exits without errors.

## Verification notes

The audit was performed against the current working-tree contents. Data counts
and event-shape checks were calculated from the repository JSON and VW data
files. Runtime VW execution was not available in the existing project virtual
environments (`vowpalwabbit` was not installed), so the workspace-lifecycle
finding is based on the pyvw object ownership/lifecycle visible in the
notebook rather than on a local package-version test.
