# HellaSwag reference: LMLM_97M_1 (QuickTalk) vs other small models

This file stands on its own. Use it as the reference table, and add new models to it with the same method (see
"How to add a model").

Model: **LMLM_97M_1** (QuickTalk run 8), https://huggingface.co/sraivante/LMLM_97M_1. It has 97.6M parameters and
was trained from scratch on 8.23B tokens. Date of measurement: 2026-10-03.

## Main table (all 10,042 HellaSwag validation items, same scorer for every row)

| Model | Parameters | Training tokens | acc | **acc_norm** |
|---|---|---|---|---|
| Random guessing | - | - | 25.00% | 25.00% |
| QuickTalk run 7, chat model (earlier version) | 97.6M | ~1.9B | 27.95% | **29.80%** |
| QuickTalk run 7c, chat model (earlier version) | 97.6M | ~1.9B | 27.76% | **29.67%** |
| **LMLM_97M_1 base** (run 8, after pretraining) | 97.6M | 8.23B | 30.12% | **33.43%** |
| **LMLM_97M_1 chat** (run 8, after chat fine-tuning) | 97.6M | 8.23B + 18.3M chat | 30.47% | **33.63%** |
| HuggingFaceTB/SmolLM2-135M (base) | 135M | ~2T | 35.47% | **43.07%** |
| HuggingFaceTB/SmolLM2-135M-Instruct | 135M | ~2T | 34.97% | **42.89%** |

## Published reference numbers (not run with our scorer, approximate)

These are taken from public papers and leaderboards. Our scorer gives SmolLM2-135M 43.1%, close to its published
~42%, so these rows are comparable within about 1 point.

| Model | Parameters | Training tokens | acc_norm (published) |
|---|---|---|---|
| GPT-2 small | 124M | ~10B | ~30-31% |
| Pythia-160M | 160M | 300B | ~30% |
| OPT-125M | 125M | 300B | ~31% |
| GPT-Neo-125M | 125M | 300B | ~30% |
| MobileLLM-125M | 125M | 1T | ~39% |
| SmolLM-135M (v1) | 135M | 600B | ~41% |
| SmolLM2-135M | 135M | 2T | ~42% |

## Method (to reproduce, or to add a model fairly)

- **Data:** HellaSwag validation split, all 10,042 items (`Rowan/hellaswag` on Hugging Face, split `validation`).
  Each item has a context and 4 possible endings; one is correct.
- **Zero-shot, no generation:** for each ending, the model scores the log-probability of the ending tokens given the
  context. The model picks the highest-scoring ending.
- **Text preparation** (same as EleutherAI lm-evaluation-harness):
  - The context is `activity_label + ": " + ctx_a + " " + ctx_b.capitalize()`.
  - In the context and in each ending, ` [title]` becomes `. `, other `[...]` tags are removed, and double spaces are reduced.
  - The scored text is `context + " " + ending`.
- **acc:** pick the ending with the highest *sum* of token log-probabilities.
- **acc_norm:** pick the ending with the highest log-probability *divided by the ending's length in characters*.
  This is the number usually published, and the one to compare.
- **Truncation:** if `context + ending` is longer than the model's context window, the oldest tokens are dropped.
- **Precision:** bfloat16 autocast on GPU (float16 on GPUs without bf16); scores are summed in float32.
- **Scorer:** `train/colab/hellaswag_eval.py` in https://github.com/sraivante/quicktalk (branch
  `claude/intelligent-ride-oxqjfy`). It batches 64 endings per forward pass with right padding. It was checked to give
  identical results to scoring one ending at a time.

## How to add a model

Any Hugging Face causal language model:
```bash
pip install torch transformers datasets tokenizers
python hellaswag_eval.py --hf-model <org/model-name> --out result.json
# prints e.g. {"model": "...", "items": 10042, "acc": 0.xxxx, "acc_norm": 0.xxxx}
```
A QuickTalk checkpoint:
```bash
python hellaswag_eval.py --workdir <folder with tokenizer.json> --ckpt <checkpoint.pt> --out result.json
```
On an A100 this takes about 15 s for a ~100M model; a T4 is slower. Add the new row to the main table. Mark it
"published" if the number was not produced with this scorer.

For a quick check, `--limit 1000` scores only the first 1,000 items. Only full 10,042-item runs belong in the main
table.

## Raw results (JSON lines, as written by the scorer)

```json
{"model": "quicktalk_run7 (sft_final.pt, chat)", "items": 10042, "acc": 0.2795, "acc_norm": 0.298}
{"model": "quicktalk_run7c (sft_final.pt, chat)", "items": 10042, "acc": 0.2776, "acc_norm": 0.2967}
{"model": "quicktalk_run8 (pretrain_final.pt, base)", "items": 10042, "acc": 0.3012, "acc_norm": 0.3343}
{"model": "quicktalk_run8 (sft_final.pt, chat)", "items": 10042, "acc": 0.3047, "acc_norm": 0.3363}
{"model": "HuggingFaceTB/SmolLM2-135M", "items": 10042, "acc": 0.3547, "acc_norm": 0.4307}
{"model": "HuggingFaceTB/SmolLM2-135M-Instruct", "items": 10042, "acc": 0.3497, "acc_norm": 0.4289}
```

## How to read the results

- LMLM_97M_1 (33.6%) beats GPT-2 small (~30%) with fewer parameters and about the same amount of training text.
- SmolLM2-135M is about 10 points higher. Its size is similar, so the gap is mostly training data: about 2 trillion
  tokens, roughly 250x more, plus careful data curation.
- Chat fine-tuning barely moves HellaSwag: run 8 base 33.4% vs chat 33.6%, and SmolLM2 43.1% vs 42.9%.
  HellaSwag measures general common sense, not chat skills.
- Going from run 7 to run 8 (+3.8 points) came from 4x more training text, a 1,024-token context and a cleaner tokenizer.

## About LMLM_97M_1

| | |
|---|---|
| Architecture | Decoder-only GPT: 12 layers, width 768, 12 heads, RMSNorm, RoPE, tied embeddings |
| Context / vocabulary | 1,024 tokens / 16,384 BPE tokens (numbers split into single digits) |
| Pretraining data | FineWeb-Edu sample-10BT, TinyStories, SODA, Simple English Wikipedia, WordNet, public-domain books |
| Chat data | 101,691 conversations, mostly project-written |
| Training | 125,600 steps × 64 × 1,024 tokens on one A100 (~9 h 50 min); chat fine-tuning 558 steps |
