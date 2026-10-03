# External 11M model vs QuickTalk runs 7 / 7c / 8 (2026-10-03)

The model under test is a user-supplied "English discussion" model. It is GPT-2 shaped: 10.9M parameters,
11 layers × 256 width, 512-token context and an 8,192-token vocabulary. It was trained from scratch on 3.37B tokens of
Q&A/MCQ conversations, for 205,448 steps (~4.6 h on an A100). Its own metrics show training loss 1.01 against eval
loss 2.17 (perplexity 8.8). The weights are not in the repo.

Answers were generated with `scripts/test_hf_local_run.py`, using the model's own chat format
(`<|bos|><|user|>…<|eos|><|assistant|>`). That runner was checked token-for-token against the model's own
`inference.py`. Decoding was the same as for our runs: greedy, a repetition penalty of 1.3 on the answer's own tokens
(1.0 for maths), and the same answer budgets.

## Fair held-out test (210 new questions, blind)

The answers were graded blind by 3 graders. Each grader saw the 11M model, run 8 and run 7c as shuffled A/B/C answers
(`train/test_fair/round2_ext11m/`). Re-grading run 8 and run 7c in this round reproduced their earlier scores within a
few points, so the scale matches the earlier round: run 8 scored 49% (earlier 46%) and run 7c 29% (earlier 26%). Run 7's
column is from the earlier round.

| category | n | **11M** | run 7 | run 7c | run 8 |
|---|---|---|---|---|---|
| messy_question | 30 | **0%** | 2% | 12% | 28% |
| json_output | 30 | **0%** | 0% | 0% | 22% |
| context_qa | 30 | **0%** | 17% | 15% | 67% |
| greeting | 20 | **8%** | 25% | 28% | 75% |
| dont_know | 20 | **2%** | 80% | 75% | 90% |
| passage | 30 | **0%** | 37% | 50% | 50% |
| grammar | 15 | **3%** | 23% | 13% | 37% |
| multiturn | 15 | **0%** | 17% | 27% | 23% |
| story | 10 | **0%** | 20% | 25% | 20% |
| multi_question | 10 | **5%** | 20% | 30% | 30% |
| **ALL** | 210 | **1%** | 23% | 26% | 46% |

## Old 375-question test (in the style of our training material)

The answers were graded on run 7's scale: each grader read run 7's grades for the same ids first. The full table is in
`report.md`.

| model | accuracy |
|---|---|
| **11M** | **0%** (3 partly right, 372 wrong) |
| run 7 | 29% |
| run 8 | 28% |
| run 7c | 25% |
| SmolLM2-135M-Instruct | 9% |

## Maths (430 items, auto-graded)

| model | gsm8k_test | easy_fresh | laghumath_seen | easy_seen | ALL |
|---|---|---|---|---|---|
| **11M** | 0% (1/200) | 0% (0/100) | 0% (0/80) | 4% (2/50) | **1%** |
| run 8 | 1% | 2% | 12% | 6% | 4% |
| run 7 | 2% | 1% | 18% | 16% | 6% |

## HellaSwag

The user reported 26% for this model, run in Colab. It is not yet confirmed that this used the same scorer on all
10,042 items. For comparison: random guessing 25%, run 7 29.8%, run 8 33.6%, SmolLM2-135M 43.1%.

## What it shows

- The model almost never answers the question asked. It produces memorised templates from its own training data
  instead: emotional-support phrases, "Approach/Solution" maths blocks, research-abstract and citation boilerplate,
  grammar-correction frames that copy the wrong sentence back, and Gutenberg links.
- The cause is memorisation, not a decoding problem. Training loss 1.0 against eval loss 2.17 is a large gap, the data
  is template-heavy (its own dataset card warns of repetitive templates and MCQ dominance), and the model has only 11M
  parameters and a 512-token context.
- In fairness, the model was not trained on our data or formats. Even so, it fails formats that any general chat model
  should handle (a greeting, "I don't know"), and HellaSwag (~26%) puts its common sense close to random guessing.
- Ranking on every test: run 8 > run 7 / 7c > SmolLM2-135M-Instruct (on our formats) > this 11M model.
