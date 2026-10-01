# Critic review, run 6 samples (grammar, multi_question)

Reviewer: independent critic agent (did not generate). Per-example verdicts: `review.jsonl`.
Mechanical check: `validate_chat.py` gives 0 FAIL on both files; 1 WARN on multi_question (duplicate 4-word opening).

## Counts

| type | pass | fix | reject | total |
|---|---|---|---|---|
| grammar | 25 | 5 | 0 | 30 |
| multi_question | 17 | 13 | 0 | 30 |

No safety problems (no medical, legal or financial advice, no brands or public figures). No arithmetic.
Every multi_question answers all questions in order, numbered 1..N, matching `n_questions`. Every word
answer gives meaning and part of speech; every correction keeps a reason. "Don't know" answers are used only
for things the model really cannot know (12 of 30 examples), and each gives a safe next step.

## Recurring problems

1. **Weak or circular "Because" sentences in reasoning answers in multi_question** (0007, 0053, 0120, 0104, and
   0003 overstated). The "Because ..." line often restates the answer ("ripening changes the fruit") instead of
   giving the real cause. One case is wrong science (0031: boats float because the weight is "spread out";
   the coin part of the question was not answered).
2. **The question or ask does not match the content.** Grammar 0127 asks "What word is missing?" when a word
   is wrong, not missing, and the reply goes along with it. Multi_question 0082 asks how to spell "library" and
   already spells it right. 0104 has a garbled question. 0182 "explain passive" most likely means the passive
   voice, but the answer gives the adjective. Metadata `topic` matches nothing in 0172, 0020 and 0070.
3. **Over-correcting or over-claiming in grammar.** 0025 swaps "neither" for "nor" when only the word order was
   wrong. 0043 calls "slept early" fully correct, but standard English says "went to bed early". 0130 states the
   British "play the violin" rule as if it had no exceptions. 0115 uses awkward phrasing ("with two s").

Smaller patterns:
- Template-sounding user turns: "Next," is used as a connector up to three times in one message (0179, 0172,
  0104). Real people type "Also," or "And", or just use a new line.
- Repeated stock phrases: four grammar replies open with "Yes, it is correct."; five grammar asks are "Is this
  right?"; "I saw the word X in a book. What is it?" and "My book uses the word X" repeat.
- The same errors repeat: "informations"/"a good advice" (uncountable nouns) appear 3 times in 30 multi_question
  examples; "X in our Y are ..." agreement appears twice in grammar.
- `n_questions` is uneven: 2 = 9, 3 = 8, 4 = 4, 5 = 9. Questions with 4 parts are under-represented.

## Instructions for the generators (next 1,000 per type)

Both types
- Make the ask match the error. If the user asks "what is missing?", something must be missing. If the user's
  premise is wrong, the reply says so in a few words first.
- Set `metadata.topic` to what the message is actually about. Do not assign topics first and then write
  unrelated content.
- Never repeat a reply's opening 4 words more than once per 20. For already-correct sentences, rotate wording
  ("Yes, that's right.", "This is already correct.", "No change needed.").

grammar
- Minimal correction: change only what is wrong and keep the user's words and structure. If you replace a
  correct word, Why must say why.
- Only call a sentence "correct" when it is correct in standard modern English. Avoid regional usages
  ("slept early", "by cycle", "class ten") in sentences labelled correct. Either correct them, or pick another
  sentence.
- Why: at most two reasons, each naming the rule. Do not state a usage preference (British/American) as
  absolute. Use "usually" or name the variety.
- Spelling notes: write "spelled with one s" / "with a double s", not "with two s".
- Spread error kinds; do not use the same template twice ("X in our Y are ...").

multi_question
- Reasoning answers: the first sentence is the answer and the "Because" sentence gives the actual cause. Never
  restate the answer or say "it changes". Check the science (buoyancy, heat, plants). If the question has two
  parts ("why X but Y?"), answer both.
- Spelling questions must contain a misspelling or a real choice ("libary or library?"). Never give the correct
  spelling in the question.
- If a word is also a grammar term (passive, tense, object), say which meaning you are answering, or word the
  question so that it is not ambiguous.
- Spread `n_questions` evenly: about 25% each for 2, 3, 4 and 5.
- Write user turns the way people type: mix one line, a list, "Also,", "And one more:". Use "Next," at most once
  in a message, and not in most messages. Rotate how word-meaning questions are asked.
- Spread correction errors: not only uncountable nouns. Also use tense, prepositions, articles, word order,
  pronouns, comparatives and confused words.
- Dont_know parts: keep them as they are (calm, a short reason and a safe next step), but every pronoun must
  have a clear antecedent ("the shops' plans", not "their plans").
