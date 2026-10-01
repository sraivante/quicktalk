# Run 6 vs run 5: same 375 questions, same grading scale

Both models answered `train/test_run5/testset.jsonl` (all questions from training material) with greedy decoding and
repetition penalty 1.3. Run 6 was graded by three independent reviewer agents using run 5's grades as calibration.
Full tables: `report.md` / `results.csv` in each folder.

| category | run 5 | run 6 |
|---|---|---|
| simple one-liner | 13% | 11% |
| complex one-liner | 12% | 19% |
| multi-line simple | 27% | 18% |
| multi-line complex | 16% | 30% |
| multi-question (2-5) | 1% | 0% |
| multi-turn | 38% | 34% |
| story | 22% | 32% |
| writing | 17% | 33% |
| grammar | 21% | 30% |
| passage | 50% | 64% |
| **overall** | **22%** | **28%** |

By training type: behaviour 50 -> 64, summary 18 -> 32, comprehension 15 -> 28, writing 21 -> 34, story 17 -> 29,
instruct 13 -> 33, hinglish_esl 7 -> 23, grammar 21 -> 30, vocab 13 -> 17; down: reasoning 15 -> 5 (the old test
items include arithmetic; run 6 was trained without arithmetic and with "I don't know" for exact maths), raga 23 -> 17,
literature 5 -> 0 (knowledge, not trained in run 6), rewrite 27 -> 18, multiturn 38 -> 34; flat: usage 5, mixed 1 -> 0.

Findings
- Clear gains in reading/passage work, summaries, writing, stories, instructions and Hinglish: the run 6 chat data and
  the extra dialogue/web pretraining helped where the model must use given text or produce a form.
- Multi-question is still 0%: answers are now numbered, but often fewer than asked, and drift into other trained
  formats ("Corrected: ... Why: ...", "I don't know; ...") and wrong definitions. The test's multi-question items are
  mostly knowledge (raga facts, idioms, sums), which this model does not hold.
- "I don't know" now appears in 19 answers (12 in multi-question, 4 complex one-liners), including two easy sums that
  run 5 attempted: the dont_know maths examples generalise to refusing simple arithmetic.
- Grammar: the corrected sentence is right in 17/40 (run 5: 15/40) but the "Why:" is still never right.
- Pretraining eval loss 3.19 (run 5 3.29) on the same text; the model now holds more general English.
