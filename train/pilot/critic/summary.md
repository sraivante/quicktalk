# Pilot critic review

Independent Opus critic (not a generator) reviewed all 240 pilot examples in train/pilot/*.jsonl.
Per-example verdicts: review.jsonl. Result: 219 pass, 21 fix, 0 reject. All files pass validate_chat.py; all 30 book
excerpts are verbatim; every instruct constraint counted and met; reasoning arithmetic correct; no safety, brand or
advice problems.

| type | pass | fix |
|---|---|---|
| grammar | 16 | 4 |
| multiturn | 17 | 3 |
| vocab | 20 | 0 |
| rewrite | 17 | 3 |
| comprehension | 18 | 2 |
| writing | 15 | 5 |
| usage | 20 | 0 |
| hinglish_esl | 19 | 1 |
| summary | 19 | 1 |
| literature | 19 | 1 |
| instruct | 19 | 1 |
| reasoning | 20 | 0 |
| total | 219 | 21 |

## Requested checks
- rewrite-p0012 "the pocket" -> "her pocket": pass (meaning unchanged; user asked to fix odd wording).
- Onam (writing-p0007), Shimla (multiturn-p0006): correct.
- hinglish_esl-p0012 sample name greeting: fix (use a placeholder such as [your name]).
- Panchatantra: comprehension-p0011/-p0012 end inside an open quote; summary-p0011 starts mid-quote. The source file
  is OCR text with verse mixed into prose; exact-copy checks cannot catch that noise.

## Recurring problems
1. Invented facts about the user (9: writing x5, multiturn x3, hinglish x1): made-up signatures, siblings, an age, a
   bill amount, pet details, genders for people the user never described.
2. Grammar items (4) treat acceptable English as wrong (singular "their", collective "team are", "late by two hours")
   or make changes the "Why" does not explain.
3. Excerpt boundaries cut quotations open (3).
4. Reasoning: spec makes every answer a standalone "Because ..." fragment (spec issue).
5. Rewrite drift (3): "wrote" -> "sent", a tense backshift error, loose reported speech of "let's".
6. literature-p0020: book gives Ga as Yaman's main note, answer says tivra Ma.
7. Same story used in 2-3 types under different groups (Aruni, Drona's test, the bow, Bharat's sandals): train/eval leak.
8. Minor: 7/20 multiturn replies open "That's ..."; arbitrary topic labels on book items; small name pool.

## Recommended spec changes
- Never invent facts about the user; use placeholders or neutral wording.
- Grammar: fix only clear errors; avoid disputed or regional usage; explain every change.
- Reasoning: full sentence ("This is because ...") instead of a standalone "Because".
- Excerpts start and end at sentence boundaries with balanced quotes; avoid noisy Panchatantra paragraphs.
- One group key per story across all types.
- Allow a `books` topic for book-based items.
- Vary multiturn openers.

## Recommended validator changes
- Check the whole excerpt verbatim (not just the first 80 characters).
- Enforce excerpt word ranges (comprehension 40-150, summary 120-350) and balanced quotes.
- OCR-noise check for book excerpts.
- `metadata.constraints` so instruct constraints are checked automatically.
- Require "Why:" in grammar and "Example:" in vocab/usage; warn on a bare "Because" line in reasoning.
- Warn when a signature/greeting uses a name the user never gave.
- Warn when the same opener is used more than 3 times in a file.
