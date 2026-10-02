# HellaSwag comparison (2026-10-02)

HellaSwag validation: 10,042 everyday situations, 4 possible endings each; the model picks the ending it finds most
likely (no text is generated). Random guessing = 25%. acc_norm (log-probability divided by the ending's length in
characters) is the number usually published. Scorer: `train/colab/hellaswag_eval.py`; run in Colab with
`train/colab/hellaswag_earlier_runs.ipynb` (T4), identical scorer for every model. Raw numbers: `results.jsonl`.

| model | size | training text | acc | **acc_norm** |
|---|---|---|---|---|
| random guessing | - | - | 25.0% | 25.0% |
| run 7 (chat model) | 97.6M | ~2B tokens | 27.95% | **29.8%** |
| run 7c (chat model) | 97.6M | ~2B tokens (+ chat re-run) | 27.76% | **29.7%** |
| SmolLM2-135M (base) | 135M | ~2T tokens | 35.47% | **43.1%** |
| SmolLM2-135M-Instruct | 135M | ~2T tokens | 34.97% | **42.9%** |

Published references (acc_norm, approximate): GPT-2 small (124M, ~10B tokens) ~30%, Pythia-160M ~30%,
MobileLLM-125M ~39%, SmolLM2-135M ~42% (our scorer gives 43.1%, so it matches the published number).

## What it shows

- Runs 7 and 7c score ~30%: the level of GPT-2 small, about 5 points above random. Expected for a ~100M model
  trained on ~2B tokens. Run 7's base model was deleted, so these are chat models (base models usually score about the
  same or slightly higher on HellaSwag).
- Run 7c's chat re-run did not change general common sense (29.8% vs 29.7%): chat fine-tuning changes the reply format,
  not the underlying knowledge, as expected.
- SmolLM2-135M is ~13 points higher. It is a similar size, so the gap is almost all training data (~2 trillion
  tokens vs our ~2 billion, about 1,000x) plus its data curation.
- SmolLM2's instruct version scores the same as its base: again, chat tuning barely moves this test.
- HellaSwag measures general common sense only. It does not measure our six focus skills (messy questions, JSON,
  answers from a given text, greetings, polite "I don't know", passages); `train/test_fair/` does.

## Expectation for run 8

Run 8 (same 97.6M size, ~8-9B tokens, digit tokenizer, 1,024 context): roughly 31-34% acc_norm. Score it with
`train/colab/hellaswag_run8.ipynb` after training (base model and chat model, same scorer). Reaching SmolLM2-135M's
~43% would need far more training text (hundreds of billions of tokens) or a larger model.
