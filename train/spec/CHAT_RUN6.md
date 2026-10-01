# Chat-pattern set: run 6 (1,000 per type)

You generate ONE type. Read `train/spec/CHAT_PATTERNS.md` first (format, rules, the type table and "Run 6 additions")
and follow it exactly; this file only adds the run-6 mechanics.

1. Output: `train/chat_r6/<type>.jsonl`, ids `<type>-r6-0001` onward, group = id unless several examples share one
   source text. You will be told how many to write (e.g. 200 for a trial batch, then later batches continue the ids).
   If the file already exists, keep it and append: continue from the last id.
2. Work in chunks of 50. Build each chunk with your own script under `.staging/r6_<type>/`, append it to the output
   file, then run `python3 scripts/validate_chat.py train/chat_r6/<type>.jsonl --type <type>` (add `--no-arithmetic`
   for reasoning). Fix every FAIL before the next chunk; never leave a failing file. The orchestrator commits between
   chunks.
3. No repeats. Read `train/chat/<type>.jsonl`, `train/pilot/<type>.jsonl` and everything already in
   `train/chat_r6/<type>.jsonl`, and do not reuse their questions, words, sentences, tasks or excerpts. Within your
   own output: no repeated question, word, error sentence, task or excerpt. Keep a list of what you have used in your
   staging folder so later chunks can check it.
4. Variety at this size: rotate topics evenly (no topic above 15% of the file), vary openings (no more than 3
   examples opening with the same 4 words), vary names (Indian and international, all genders), lengths and
   difficulty, and the wording of the ask.
5. Type notes:
   - grammar: 1-3 real learner errors per sentence, spread across error kinds (tense, agreement, articles,
     prepositions, word order, plurals/uncountables, comparatives, pronouns, spelling, punctuation, collocations such
     as make/do). The "Why:" line must name the rule correctly and match the fix; check every one.
   - multi_question: spread `metadata.n_questions` evenly over 2, 3, 4, 5. Mix the kinds of question listed in the
     spec in each message. Vocab words must come from `train/spec/vocab_words.txt` and must not be words already used
     in `train/chat/vocab.jsonl` or `train/pilot/vocab.jsonl`. No arithmetic.
   - dont_know, reasoning: follow "Run 6 additions" in the spec.
6. Check your own work before writing each chunk: facts, grammar reasons, constraints, numbering.
7. Do not commit. Do not touch other files. Final report: counts, validator result, judgement calls; never paste
   dataset content.
