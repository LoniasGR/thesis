# Vowpal Wabbit and recommendation-pipeline work summary

## Data and preprocessing

- Converted 1,043 historical recommendations into VW contextual-bandit data.
- Reconstructed the historical action choice as an assumed fixed
  `no_action` probability, with sensitivity runs at 20%, 50%, and 80%.
- Excluded 8 examples where the chosen action was outside the reconstructed
  action set, leaving 1,035 examples.
- Replaced fixed-offset reward extraction with the next actual user event.
- Mapped direct user intents to their corresponding recommendation actions.
- Preserved context order deterministically and removed set/hash-order
  instability.
- Replaced stale appended train/test files with reproducible regeneration.
- Split complete conversations after deterministic shuffling.
- Current supported historical data contain 533 accepted and 502 rejected
  recommendations.

## VW representation and training

- Shared context uses namespace `S`: `shared |S covid_stats symptoms`.
- Actions use namespace `A`: `|A action=test_types`.
- Training and serving enable the `-q SA` interaction.
- This fixed a real modeling problem: without context-action interactions,
  predictions were nearly identical across contexts and collapsed mainly to
  two actions.
- The trained policy now produces context-dependent rankings and uses all 12
  available actions as argmax choices in human-feedback evaluation.
- Training and production use IPS consistently.
- The production candidate uses the 20% historical `no_action` assumption,
  learning rate 0.1, and lambda 1.

## Historical evaluation

For the fair three-way sensitivity comparison, all models used learning rate
0.1 and lambda 1.

| q | IPS cost | Standard error | SNIPS cost | Effective sample |
|---:|---:|---:|---:|---:|
| 0.2 | 0.3861 | 0.0252 | 0.5408 | 277.8 |
| 0.5 | 0.4988 | 0.0377 | 0.5698 | 220.9 |
| 0.8 | 1.0121 | 0.0887 | 0.6045 | 167.8 |

The observed test logger cost is 0.4946. q=20% has the strongest stability in
this comparison, including the highest effective sample size. IPS and SNIPS
still differ materially, so these results remain conditional on the unknown
historical logging policy.

Grouped five-fold CV keeps all examples from a conversation in one fold. The
q=20% configuration selected by mean SNIPS uses learning rate 0.1 and lambda
1:

- IPS: 0.3921
- SNIPS: 0.5678
- logger cost: 0.4865

The CV estimator does not establish a production improvement, but lambda 1
avoids the extreme weights and lower effective sample sizes of lambda 10.

## Human-feedback synthetic data

The 585 answered human-feedback examples are used only as an independent
evaluation set, never for model training or hyperparameter fitting.

Each example contains a randomly generated dialogue context, a randomly
selected recommendation, and a human relevance judgment. The candidate policy
is evaluated with IPS/SNIPS using the known uniform logging propensity
`1 / number_of_actions`.

| Policy | IPS cost | SNIPS cost | ESS |
|---|---:|---:|---:|
| Random logger | 0.4615 | 0.4615 | 585.0 |
| q=20% candidate | 0.4682 | 0.4576 | 562.8 |
| q=50% candidate | 0.5590 | 0.4767 | 207.6 |

The q=20% candidate is only marginally better than random by SNIPS, but it is
substantially more stable than q=50%. This is evidence against the earlier
two-action collapse, not proof of production superiority.

## Application and service changes

- The Rasa external `no_action` draw is bypassed when the smart-suggest
  microservice is enabled.
- Intent responses are mapped to their functionality before reward assignment.
- Unused `ONLINE_LEARNING` configuration was removed.
- The service and training serializer now match.
- VW prediction, learning, and saving are protected by one process lock.
- Parsed online examples are finalized.
- Model saves use temporary files plus atomic replacement.
- The q=20% model is installed in the smart-suggest service.
- Timeout is intentionally interpreted as rejection/loss of user interest.

Accepted limitations are the current sequential decision flow, single Uvicorn
worker, and non-streaming evaluation path.

## Side-by-side simulated evaluation

Two 300-round databases were generated independently:

- `without_llm.db`
- `with_llm.db`

Concrete-topic results after excluding `no_action`:

| Policy | Without LLM option | With LLM option |
|---|---:|---:|
| Random | 27.8% | 8.9% |
| Smart/VW | 51.9% | 10.0% |
| Popularity | 25.9% | 3.3% |
| LLM | not present | 85.6% |

Including `no_action` changes the result strongly:

| Policy | Without LLM option | With LLM option |
|---|---:|---:|
| Random | 26.3% | 11.4% |
| Smart/VW | 23.7% | 9.8% |
| Popularity | 60.2% | 31.8% |
| LLM | not present | 58.3% |

Shared-credit scoring means percentages may sum above 100% when strategies
propose the same action. For the 90 actionable with-LLM cases, Smart received
exclusive/shared automated credit in 9/90 cases, while the LLM won 70/90.

## Conclusion and next steps

The best available candidate is the q=20% IPS model with `-q SA`, learning
rate 0.1, and lambda 1. It should proceed to live validation.

Priority next steps:

1. Run a blinded human pilot focused on Smart/VW versus the alternatives.
2. Reuse the 90 actionable with-LLM cases first; duplicate a subset for
   inter-rater reliability.
3. Compare human choices with the LLM judge and report exact agreement plus
   chance-adjusted agreement.
4. In production, log available actions, selected action, propensity,
   model version, and outcome.
5. Use live data to replace the historical q assumption and re-estimate model
   performance.
6. Only collect substantially more synthetic Smart/VW comparisons if human
   validation confirms that the automated LLM judge reflects human preference.
