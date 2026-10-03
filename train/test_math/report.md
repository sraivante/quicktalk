# Maths test: run 7 (97.6M) vs run 6 (69.5M)

430 questions, graded automatically (final number vs gold; scripts/test_math_grade.py). gsm8k_test and easy_fresh were never
seen in training; laghumath_seen and easy_seen were. Greedy decoding; "rep1.0" = no repetition penalty.

| answers | gsm8k_test | easy_fresh | laghumath_seen | easy_seen | ALL |
|---|---|---|---|---|---|
| run6_rep1.0 | 2% (4/200) | 0% (0/100) | 6% (5/80) | 6% (3/50) | 3% |
| run7_rep1.0 | 2% (3/200) | 1% (1/100) | 18% (14/80) | 16% (8/50) | 6% |
| run7_rep1.3 | 2% (4/200) | 1% (1/100) | 19% (15/80) | 16% (8/50) | 7% |

Findings
- The answer FORMAT is learned (run 7 writes "The answer is N.", "Answer: N ..." and "Rs N. Because a + b = c"), but the
  arithmetic is wrong: e.g. "14 + 18 = 14", "29 - 34 = 6" for an addition question, wrong operation chosen.
- Seen items: run 7 18-19% vs run 6 6% (memorised some training answers). Unseen: about 1-2%, no real ability.
- Number extraction was checked by hand on sample answers: the low scores are real, not a grading fault.
- Likely main cause: the tokenizer merges digits into arbitrary chunks (517 multi-digit tokens; "3528" -> "35","28",
  "1234" -> "12","34"), so the model cannot learn place value / column arithmetic. Small models need one token per
  digit for arithmetic. A fix needs a new tokenizer (split digits) and pretraining from scratch.

## Run 8 (digit tokenizer, 8.23B tokens), 2026-10-03

| answers | gsm8k_test | easy_fresh | laghumath_seen | easy_seen | ALL |
|---|---|---|---|---|---|
| train/test_math/answers_run7_rep1.0.jsonl | 2% (3/200) | 1% (1/100) | 18% (14/80) | 16% (8/50) | 6% |
| train/test_math/answers_run8_rep1.0.jsonl | 1% (2/200) | 2% (2/100) | 12% (10/80) | 6% (3/50) | 4% |

Run 8 did not improve maths (4% vs run 7 6% overall). The digit tokenizer works (numbers are now single digits), and
the model writes the trained format ("Because 29 + 34 = ..."), but the arithmetic itself is wrong (e.g. 29 + 34 = 15).
Splitting digits makes arithmetic learnable; it does not teach it. A ~100M model needs far more worked arithmetic in
training (thousands of generated sums with digit-by-digit / column working) for this to improve. The grader was checked
by hand on run 8 answers: it reads the numbers correctly.
