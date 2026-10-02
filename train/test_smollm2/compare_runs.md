# Accuracy comparison: QuickTalk runs vs SmolLM2-135M-Instruct (reference)

Same 375 questions (train/test_run6/testset.jsonl), same decoding (greedy, repetition penalty 1.3, same answer budgets),
graded by three independent graders on the same scale (1 / 0.5 / 0). Caveat: the questions come from QuickTalk's own
training material (Indian-English behaviour passages, ragas, our grammar/rewrite formats), which SmolLM2 never saw, so
this measures "how well does it do OUR tasks", not general ability. Run 7b's 40% is mostly memorisation (see test_run7b).

| category | n | run 5 (69.5M) | run 6 (69.5M) | run 7 (97.6M) | run 7b | run 7c | **SmolLM2-135M** |
|---|---|---|---|---|---|---|---|
| simple_oneliner | 50 | 13% | 11% | 25% | 37% | 22% | **20%** |
| complex_oneliner | 50 | 12% | 19% | 12% | 41% | 9% | **7%** |
| multiline_simple | 30 | 27% | 18% | 22% | 42% | 13% | **0%** |
| multiline_complex | 40 | 16% | 30% | 36% | 49% | 32% | **2%** |
| multi_question | 40 | 1% | 0% | 5% | 3% | 3% | **3%** |
| multiturn | 25 | 38% | 34% | 24% | 40% | 16% | **10%** |
| story | 25 | 22% | 32% | 14% | 20% | 20% | **8%** |
| passage | 60 | 50% | 64% | 62% | 51% | 57% | **18%** |
| grammar | 40 | 21% | 30% | 39% | 69% | 32% | **0%** |
| writing | 15 | 17% | 33% | 33% | 37% | 33% | **17%** |
| ALL | 375 | 22% | 28% | 29% | 40% | 25% | **9%** |

What SmolLM2-135M does well: fluent, grammatical English; common vocabulary and idioms; a friendly chat tone.
What it does badly on our tasks: never corrects a grammar sentence (0/40), never performs a rewrite (0/30), invents
passage details instead of reading them, ignores asked length/form, knows nothing about ragas or our literature set,
answers only the first part of multi-questions, gets every arithmetic question wrong.
Run 7 (97.6M, 1.92B pretraining tokens) beats it on every category of this test (29% vs 9%), because it was trained
on these task formats; SmolLM2 (~2T tokens) is the stronger general-English model.
