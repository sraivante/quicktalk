# HellaSwag results (validation, 10,042 items, 4 endings, random = 25%)

Scorer: train/colab/hellaswag_eval.py (sum of log-probabilities of each ending; acc_norm = divided by ending length in
characters, the commonly published number). Run in Colab with train/colab/hellaswag_earlier_runs.ipynb.

| model | what was scored | acc | acc_norm |
|---|---|---|---|
| run 7 (97.6M, ~2B tokens) | chat model (sft_final.pt; base model deleted) | 27.95% | 29.8% |
| run 7c | chat model | (running) | (running) |
| SmolLM2-135M base | same scorer | (pending) | (pending) |
| SmolLM2-135M-Instruct | same scorer | (pending) | (pending) |

Published reference (acc_norm, approximate): GPT-2 small 124M ~30%, Pythia-160M ~30%, MobileLLM-125M ~39%,
SmolLM2-135M ~42%.
