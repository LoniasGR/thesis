# Remaining application-pipeline review

## Implemented

### 1. Remove the external `no_action` draw in smart-service mode

[`actions.py`](applications/covid-va-chatbot/actions.py) now applies the
`NO_ACTION_PROBABILITY` draw only in legacy random mode. When
`ACTIONS_USE_SMART_SUGGEST_SERVICE=yes`, every recommendation comes from VW.
This makes the stored VW PMF probability the full action-selection
probability instead of a probability conditional on bypassing an earlier
random draw.

### 2. Normalize user intents before assigning online cost

[`vw_utils.py`](applications/smart-suggest-microservice/app/vw/vw_utils.py)
maps incoming intents through `intent_to_functionality_dict` before comparing
them with the recommendation. Direct responses such as `covid_stats`,
`pharma_search`, `am_i_ill`, `vaccine_stats`, and `find_new_icus` can now
accept their corresponding recommendation.

## Remaining findings

### A1. Resolved - model estimator must match the training command

The microservice and `train.py` now both default to `cb_type="ips"`. The
primary 50% model was trained with IPS and verified to load with the service
configuration. A prior DR-trained model cannot be loaded through the
IPS-initialized service:

```text
Disagreeing option values for 'cb_type': 'ips' vs 'dr'
```

The selected production candidate is now trained from the `q=0.2` dataset
with learning rate `0.1` and lambda `1`. The service-bound model has been
replaced with that candidate. Its saved configuration includes IPS and the
`SA` interaction, so loading the model restores both without duplicate command
line options.

The service serializer, intent-to-action cost mapping, online learn path, and
atomic replacement flow were exercised against a temporary copy of the
production candidate. The learned model remained valid and no temporary save
file was left behind.

### A2. Resolved - the global VW workspace is unsynchronized

Prediction, learning, and model saving now run under one process-local lock.
If multiple service workers are introduced later, the deployment will still
require a single-writer update architecture because a Python lock does not
coordinate separate processes.

### A3. Accepted risk - pending recommendation state can be overwritten

The deployment assumes feedback is processed before another suggestion is
generated, so overlapping pending decisions are not addressed.

### A4. Resolved - parsed online examples are not finalized

`vw_learn` now finishes every parsed example in `finally`, so workspace-owned
example state is released even if learning fails.

### A5. Resolved - model saves are not atomic

Online updates save to a temporary file in the model directory and replace the
configured path atomically with `os.replace`.

### A6. Not applicable - streaming messages

The streaming input path is not used by the deployment.

### A7. Resolved - remove unused online-learning configuration

The unused `ONLINE_LEARNING` setting was removed. Online learning is always
enabled.

### A8. Documented reward assumption - inactivity is rejection

The cleanup job calls `vw_learn(user_data, "")`, and an empty intent becomes
cost `1`. This intentionally interprets an unanswered recommendation as loss
of interest.

### A9. Resolved - context/action features did not interact

Training and serving filtering now remove duplicates deterministically while
preserving first-seen order. Context features use `|S`, actions use `|A`, and
training, evaluation, and serving enable `-q SA`. Human-feedback argmax
predictions now cover all 12 actions rather than only two.

### A10. Not in scope - structured service audit trail

Structured per-decision production logging is deferred; the current task
accepts the existing feedback records and operational logging.

## Recommended review order

There are no remaining implementation blockers for the current single-process,
non-streaming deployment under the accepted reward and decision-flow
assumptions.
