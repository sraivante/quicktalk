# Run 7 (bad-data attempt) vs run 6 vs run 5

Run 7 here = 97.6M parameters pretrained on only 73.5M tokens (an interrupted FineWeb download left a tiny pretraining
set; ~4% of the planned 1.92B). Run 6 = 69.5M on ~1.9B tokens in total (run 5 + 1.32B). Same 375 questions, same
decoding (greedy, repetition penalty 1.3), graded on run 6's scale by three independent graders.

| category | run 5 | run 6 | run 7 (bad data) |
|---|---|---|---|
| simple_oneliner | 13% | 11% | 8% |
| complex_oneliner | 12% | 19% | 4% |
| multiline_simple | 27% | 18% | 5% |
| multiline_complex | 16% | 30% | 12% |
| multi_question | 1% | 0% | 0% |
| multiturn | 38% | 34% | 8% |
| story | 22% | 32% | 2% |
| grammar | 21% | 30% | 19% |
| passage | 50% | 64% | 39% |
| writing | 17% | 33% | 13% |
| ALL | 22% | 28% | 13% |

Conclusion: a bigger model does not help without the text. With 73.5M pretraining tokens run 7 falls below even
run 5 (0.6B tokens): factual recall, stories and multiturn collapse; grammar "Why:" right in 0/40. The real run 7
(v8.3 notebook, full ~1.92B tokens) is still to be trained.
