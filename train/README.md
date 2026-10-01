# train/ — data for the chat experiment

A small from-scratch model: human behaviour gives it its flavour, the books give it reading, and a small chat-pattern
set teaches it how to answer different kinds of requests.

## Use these (train/build/)
| File | What |
|---|---|
| `pretrain_01.txt`, `pretrain_02.txt` | plain text for pretraining: books (English only) + behaviour passages, shuffled by block, eval text removed (~10.3M words) |
| `sft_train_01.jsonl`, `sft_train_02.jsonl` | all chat data mixed and shuffled, `{"messages": [...], "metadata": {...}}` |
| `eval/sft_eval_<type>.jsonl` | held-out examples per type; `eval/sft_eval_all.jsonl` = all of them |
| `eval/pretrain_eval.txt` | held-out text for perplexity |
| `manifest.json` | seed, counts and share per type, which groups went to eval |

Every dataset (sources, paths, sizes, licences, downloads, Drive artefacts, test sets): `train/dataset_info.txt`.

Splits are by group (all variants of a behaviour row, or one source text, stay on one side). Nothing in eval appears in
training or in the pretraining text (checked).

## Rebuild
```
python3 scripts/build_behaviour_chat.py   # data/rows -> sources/behaviour_chat_*.jsonl, corpus_behaviour.txt
python3 scripts/build_book_corpus.py      # compressdata/*.zip -> sources/books/*.txt (+ REPORT.txt), raga_qa.jsonl
python3 scripts/build_train.py [--seed 1234] [--chat-repeat N]   # -> build/
```
`--chat-repeat N` repeats the 12 chat-pattern types N times in training (default 1: they are ~5% of the chat data,
behaviour is ~94%).

## Sources
- `sources/behaviour_chat_*.jsonl`: 46,719 behaviour records as multi-turn chats (passage + 4 questions).
- `sources/corpus_behaviour.txt`: the behaviour passages as plain text.
- `sources/books/`: 10 novels, Ramayana (Griffith), Mahabharata (Ganguli), Panchatantra (Ryder), raga teaching book;
  Gutenberg text and all non-English sentences removed; see `books/REPORT.txt`.
- `sources/raga_qa.jsonl`: 338 raga Q&As.
- `chat/<type>.jsonl`: 200 per type for 12 types (grammar, multiturn, vocab, rewrite, comprehension, writing, usage,
  hinglish_esl, summary, literature, instruct, reasoning); `pilot/`: 20 per type from the pilot, plus `pilot/critic/`.
- `spec/`: CHAT_PATTERNS.md (format and rules), CHAT_FULL.md (full-run mechanics), vocab_words.txt.
