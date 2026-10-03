# Fair held-out test: run 7 vs run 7c vs run 8 (2026-10-03)

210 questions written fresh for this test (never in any training data; near-duplicate checked against all chat data),
reviewed by an independent agent. Each answer graded 1 / 0.5 / 0 by three independent graders who saw the three
models' answers shuffled as A/B/C and could not tell which model wrote which (key: `blind_key.json`, guide: `GRADE.md`).
Greedy decoding, repetition penalty 1.3 (scripts/test_model_run.py). Grades: `grades.jsonl`.

| category | n | run 7 | run 7c | **run 8** |
|---|---|---|---|---|
| messy_question | 30 | 2% | 12% | **28%** |
| json_output | 30 | 0% | 0% | **22%** (valid JSON in 27/30 = 90%; run 7/7c 0%) |
| context_qa | 30 | 17% | 15% | **67%** |
| greeting | 20 | 25% | 28% | **75%** |
| dont_know | 20 | 80% | 75% | **90%** |
| passage | 30 | 37% | 50% | **50%** |
| grammar | 15 | 23% | 13% | **37%** |
| multiturn | 15 | 17% | 27% | 23% |
| story | 10 | 20% | 25% | 20% |
| multi_question | 10 | 20% | 30% | 30% |
| **six focus skills** (first six rows) | 160 | 23% | 27% | **52%** |
| **ALL** | 210 | 23% | 26% | **46%** |

## What it shows

- Run 8 doubles run 7 on held-out questions (46% vs 23%) and more than doubles it on the six focus skills (52% vs
  23%). The gains come where run 8 got new targeted chat data: answering from a given text (17% -> 67%), greetings
  (25% -> 75%), JSON format (0% -> 90% valid), messy questions (2% -> 28%), polite "I don't know" (80% -> 90%).
- JSON: the format is learned; the strict grade is low because answers often add extra keys with invented values or get
  a value wrong (e.g. sport "swimmer"). Next data step: more rows where extra keys are wrong, and value-copy checks.
- context_qa: the "general" case (text lacks it, give the real fact) and inference questions on passages are the weak
  spots; "unknown" handling improved a lot.
- Unchanged: stories, multi-turn and two-question prompts stay at 20-30% for all three models (these need more model
  capacity / knowledge, not only format data).

## Other tests for run 8 (same day)

- Old 375-question test (questions from the training material, graded on run 7's scale): run 8 28.2%, run 7 29.0%,
  run 7c 25.2% (`train/test_run8/report.md`). No gain there: that test measures recall of the run 1-7 training
  material, which run 8's mix covers relatively less.
- Maths (auto-graded): run 8 4%, run 7 6% (`train/test_math/report.md`). The digit tokenizer did not by itself teach
  arithmetic; worked digit-by-digit arithmetic data is needed.
- HellaSwag (common sense, train/test_hellaswag/results.md): run 8 33.6% (chat) / 33.4% (base) vs run 7 29.8%,
  SmolLM2-135M 43.1%.
