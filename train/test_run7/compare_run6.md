# Run 7 (full, 97.6M) vs run 6 (69.5M) vs run 5

Run 7 = new 97.6M model from scratch on 1.92B pretraining tokens (19.7 per parameter) + run 7 chat data (short Why,
no maths in dont_know, more multi_question/rewrite, easy sums, laghumath + GSM8K). Same 375 questions, same decoding
(greedy, repetition penalty 1.3), graded on run 6's scale by three independent graders. The bad-data attempt (73.5M
tokens) is in train/test_run7_baddata/.

| category | run 5 | run 6 | run 7 bad data | **run 7** |
|---|---|---|---|---|
| complex_oneliner | 12% | 19% | 4% | **12%** |
| multiline_simple | 27% | 18% | 5% | **22%** |
| simple_oneliner | 13% | 11% | 8% | **25%** |
| multiline_complex | 16% | 30% | 12% | **36%** |
| multi_question | 1% | 0% | 0% | **5%** |
| multiturn | 38% | 34% | 8% | **24%** |
| story | 22% | 32% | 2% | **14%** |
| writing | 17% | 33% | 13% | **33%** |
| grammar | 21% | 30% | 19% | **39%** |
| passage | 50% | 64% | 39% | **62%** |
| ALL | 22% | 28% | 13% | **29%** |

Findings
- Overall 29% (run 6: 28%): a small gain; the 100M model on Chinchilla data is at least as good, not a big jump.
- Better: grammar corrections (23/40 corrected vs 12 in the bad-data run; 39% vs 30%), multiline_complex (36% vs 30%),
  simple one-liners (25% vs 11%), multi_question first non-zero (5%), passages and writing level.
- Worse: stories (14% vs 32%: shorter, less coherent), multiturn (24% vs 34%), complex one-liners (12% vs 19%).
- Grammar "Why:" right in 0/40: the short style was learned, but the reason given is usually wrong (checked by hand).
