# Chat-pattern set: full run (200 per type)

You generate ONE type. Read `train/spec/CHAT_PATTERNS.md` first and follow it exactly; this file only adds the
full-run mechanics.

1. Output: `train/chat/<type>.jsonl`, ids `<type>-f0001` .. `<type>-f0200`, group = id unless several examples share
   one source text.
2. Work in 4 chunks of 50. Build each chunk with your own script under `.staging/full_<type>/`, then write the
   cumulative file (chunk 1, then 1+2, ...) to `train/chat/<type>.jsonl` and run
   `python3 scripts/validate_chat.py train/chat/<type>.jsonl --type <type>`. Fix every FAIL before the next chunk.
   The orchestrator commits the file between chunks, so never leave a failing file in `train/chat/`.
3. Do not reuse any pilot example: read `train/pilot/<type>.jsonl` and avoid its questions, words, tasks and excerpts.
   Within your 200: no repeated question, word, task or excerpt.
4. Variety at this size: rotate topics evenly (no topic above 20% of the file), vary openings (avoid more than 3
   examples opening with the same 4 words), vary names (Indian and international, all genders), lengths and
   difficulty. Spread the ask wording for the same kind of task.
5. Book allocation (keeps excerpts from leaking between types):
   - comprehension: novels 01-05 (War and Peace, Moby Dick, Great Expectations, Jane Eyre, Dracula) + Mahabharata vol 1-2.
   - summary: novels 06-10 (Pride and Prejudice, Frankenstein, Wuthering Heights, Sherlock Holmes, Alice) + Mahabharata
     vol 3-4; up to 50 may use behaviour passages from `train/sources/corpus_behaviour.txt` (source
     `behaviour:<sno>-<variant>`, found by matching in `data/rows/*.jsonl`).
   - rewrite: your own sentences, behaviour passages, the Ramayana and the Panchatantra (clean balanced stretches only).
   - literature: questions may cover any book, but do not quote long excerpts; spread across all books and the raga book.
   - vocab: words from `train/spec/vocab_words.txt` not used in the pilot.
   - Note: Mahabharata paragraphs usually open a speech quote that closes only paragraphs later, so most fail the
     balanced-quote rule; use a Mahabharata excerpt only when its quotes balance (or it has none), otherwise take
     more from your novels. The Panchatantra rarely has a clean stretch.
6. Check your own work before writing each chunk: facts against the book files, arithmetic, instruct constraints
   (count them), grammar reasons.
7. Do not commit. Do not touch other files. Your final report: counts, validator result, judgement calls; never paste
   dataset content.
