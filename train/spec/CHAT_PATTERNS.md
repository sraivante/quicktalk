# Chat-pattern set: spec for generators

Purpose: a SMALL set (a few hundred per type) that teaches a small from-scratch model the shape of each conversation
pattern. The model's "human" flavour comes from the behaviour data; its reading comes from the book corpus. These
examples only show HOW to answer each kind of request. Quality and variety matter more than volume.

## Format (every type)

One JSON object per line:

```json
{"messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}],
 "metadata": {"type": "grammar", "id": "grammar-p0001", "group": "grammar-p0001", "source": "generated", "topic": "school"}}
```

- Roles alternate `user`, `assistant`, starting with `user` and ending with `assistant`. No system messages.
- `metadata.type` is one of the type names below (12 original + 2 added for run 6); `id` is unique; `group` is the id unless several examples share
  one source text (then they share a group, e.g. `book:Jane_Eyre:p1234`), so train/eval splits keep them together.
- `metadata.source`: `generated`, or `book:<file name without .txt>` when the example uses a book excerpt, or
  `behaviour:<sno>-<variant>` when it uses a behaviour passage.
- `metadata.topic`: a short everyday topic word (school, family, friends, food, travel, work, health, money, festival,
  sport, nature, books, feelings, ...). Spread topics; no topic more than 4 times in 20.

## Rules for every example

1. **Assistant text is clear, modern, correct English.** Short sentences, plain words, standard grammar. Indian
   settings, names and everyday words (tiffin, auto, chai) are welcome; no slang a learner should not copy.
2. **English only** in assistant text. Only `hinglish_esl` user turns may contain Hinglish (Roman-script Hindi mixed
   with English). No other scripts or languages anywhere.
3. **Book text is input, not a model.** Old or verse English from the books may appear in a user turn as the text
   to work on; the assistant never imitates it.
4. **Copy book excerpts exactly** (from `train/sources/books/*.txt`, a paragraph or 2-6 consecutive sentences). Do
   not invent quotations or put words in a real author's mouth. An excerpt starts and ends on whole sentences and
   never cuts a quotation open: its double quote marks must balance. Put the excerpt in its own paragraph (blank line
   before and after). The Panchatantra file is OCR text with verse mixed in: use it only where a clean, balanced
   stretch exists; otherwise pick another book.
5. **Facts must be true.** Literature answers must be checkable in the book file. If unsure, choose another question.
6. **Safety (project rule):** no instructions to deceive, coerce, stalk or harm; no medical, legal or financial
   advice; no diagnoses. Sad or hard topics are fine when handled kindly. No real brands, apps or public figures
   (config/blocklist.json); authors and characters of the source books are allowed.
7. **Variety:** vary openings, question wording, names (Indian and international, mixed genders), lengths and
   topics. Never start two examples in a batch with the same 4 words. No emoji.
8. **Assistant voice:** friendly and direct. No "Great question!", no "As an AI", no sign-offs. Do not end every
   reply with a question.
9. Never paste dataset content into chat with the orchestrator; write files.

## The types

| type | turns (user+assistant pairs) | user | assistant | length (assistant words) |
|---|---|---|---|---|
| grammar | 1 | a sentence or two with 1-3 real learner errors, asking to fix it (vary the ask) | the corrected text, then "Why:" one or two short reasons naming the rule | 15-60 |
| multiturn | 2-5 | everyday chat: plans, a problem, sharing news, asking opinion, small talk; follow-ups that depend on earlier turns | natural replies that remember earlier turns; may ask one question back | 10-80 per turn |
| vocab | 1 | asks the meaning of one word (take words from train/spec/vocab_words.txt) | meaning in simple words, part of speech, one modern example sentence; mention an old sense only if the book use differs | 20-60 |
| rewrite | 1 | an instruction (simpler / more polite / formal / informal / shorter / modern English / change tense / active voice) + a text (own sentence, behaviour passage bit, or book excerpt) | only the rewritten text, no preamble | 10-120 |
| comprehension | 1 | a short book excerpt (40-150 words) + one question | a short answer that the excerpt supports, in own words | 5-50 |
| writing | 1 | a writing task: short note, message, invitation, apology, description, diary entry, tiny story, paragraph on a topic; states length or audience | the text itself, fitting the length asked | 30-150 |
| usage | 1 | a question about an idiom, a phrasal verb, a pair of confused words (affect/effect, lend/borrow, since/for...) or a spelling | the answer, then one or two example sentences | 20-70 |
| hinglish_esl | 1-3 | Hinglish ("Kal mujhe interview hai, how to introduce myself?") or learner English with mistakes; asks for English help, translation or meaning | clear simple English only; when translating, give the English version; when correcting, show the fix | 10-90 per turn |
| summary | 1 | a text (book excerpt 120-350 words, or a behaviour passage) + a request to summarize (vary: one line / three sentences / for a child) | the summary at the asked length, own words | 10-70 |
| literature | 1 | a question about a source book: plot, character, who/what/why, moral of a Panchatantra story, Ramayana/Mahabharata episode, a raga basic | a short true answer, 1-3 sentences | 8-60 |
| instruct | 1 | a task with an explicit constraint (exactly N items, under N words, start each line with X, one sentence, use the word Y, no word Z, numbered steps, question form) | output that meets every constraint exactly | 5-100 |
| reasoning | 1 | an everyday common-sense, cause-effect, simple number or logic question (from run 6: NO numbers or arithmetic, see below) | the answer first, then "Because ..." with the short reasoning | 15-70 |
| multi_question | 1 | 2-5 independent questions in ONE message, on one line or several; kinds: word meaning, idiom/usage, spelling, a sentence to correct, everyday reasoning, simple advice, a request it cannot know (see dont_know). Never arithmetic. | one numbered answer per question, in the order asked, each on its own line starting "1.", "2.", ...; each answer short (1-2 sentences, same rules as the matching type, e.g. a correction keeps its reason) and never merged with another | 15-200 total |
| dont_know | 1 | a question the model cannot answer: today's/recent news, scores, weather, prices, timetables, the user's own details ("what is my friend's name?"), private facts about people, very specific facts (exact dates, numbers, rare names), exact maths it cannot do reliably | says plainly it does not know or cannot check ("I don't know." / "I'm not sure." / "I can't see the news."), gives the short reason, then one useful next step (who or where to ask, what to check). Never guesses a fact, never makes one up | 8-60 |

## Run 6 additions (agreed with the user 2026-10-01)

- **reasoning:** new examples are everyday reasoning only: cause and effect, common sense, social sense, simple logic,
  planning. No numbers, sums, prices, times or measurements (`validate_chat.py --no-arithmetic` fails any digit). The
  existing 200 (90 with numbers) stay as they are.
- **multi_question:** set `metadata.n_questions` (2-5) and spread it evenly. Write the questions the way people type
  them (sometimes one line, sometimes a list, sometimes with "Also," or "And one more:"). Answer every question; when
  one cannot be known, that numbered answer says so (dont_know style) and the others are still answered.
- **dont_know:** spread the kinds evenly (recent events, personal/user details, private people, live data such as
  prices/weather/timetables, very specific facts, maths). Keep the reply calm and helpful, not apologetic; do not say
  "As an AI". The next step must be safe and general (ask a teacher, check the official website, use a calculator),
  never medical, legal or financial advice.
- **literature:** no new examples (knowledge is not the goal of this run).

## Run 7 changes (agreed with the user 2026-10-01, after the run 6 test)

- **grammar "Why:" (all grammar data, and corrections inside multi_question and hinglish_esl):** one fixed short style.
  After the corrected text, one line: `Why: <rule>.` with one short clause per fix, separated by "; ", at most 15
  words in total, plain words, naming the trigger and the fix, e.g. `Why: "yesterday" needs the past tense (went).`
  or `Why: "she" takes "doesn't"; "advice" has no plural.` No long explanations, no "because" chains.
- **dont_know:** no maths. "I don't know" is only for things the model cannot know (recent events, the user's own
  details, private people, live data, very specific facts). The run-6 maths rows are replaced by these kinds.
- **easy maths is allowed again (reasoning, new rows only):** small whole-number sums a child can do in their head
  (add, subtract, times tables, simple money/time). The reply gives the answer first, then one short working line
  (e.g. "60. Because 15 x 4 = 60."). No hard arithmetic (no percentages of large numbers, no long division).
- **multi_question (+500):** familiar everyday topics only (school, home, friends, food, weather, simple word meanings,
  easy grammar fixes, easy sums); 2-3 questions in most messages (2: 40%, 3: 40%, 4: 15%, 5: 5%); every question
  answered in order with a short answer; never switch into a different format inside an answer.
- **rewrite (+300):** instructions whose change is obvious and checkable (tense, person, formal/casual, polite,
  shorter, simpler); the output must clearly differ from the input in the asked way.
- **math (converted, not generated; user request 2026-10-01):** `scripts/build_math_chat.py` turns the user's own
  maths curriculum (github.com/sraivante/laghumath, stages 0-8 = school level) and GSM8K train (MIT licence) into
  `train/math/*_chat.jsonl` (type `math`). The full curriculum text (all stages) also goes into pretraining
  (`train/sources/math/`). Math is NOT upsampled in chat training (1x). GSM8K test is kept for testing only.
- New examples go to `train/chat_r7/<type>.jsonl` (ids `<type>-r7-NNNN`; easy maths `reasoning-r7m-NNNN`).

## Run 8 data (agreed with the user 2026-10-01, after the run 7 test: stories 14%, multiturn 24%, multi_question 5%)

New examples go to `train/chat_r8/<type>.jsonl` (ids `<type>-r8-NNNN`; stories `writing-r8s-NNNN`). Validate with
`python3 scripts/validate_chat.py <file> --type <type> --short-why --run8`.

- **multiturn (+1,000):** 3-5 user/assistant pairs (3: 35%, 4: 40%, 5: 25%). The LAST user turn must depend on an
  earlier turn (refers back with "that", "the second one", "what I told you", a name or detail given before, a change
  of plan); the last assistant reply must use that earlier detail correctly and by name. Mix kinds: planning, a
  problem, sharing news, asking advice on everyday things, small talk, a story the user tells in parts, recall checks
  ("what was the name of my cousin I mentioned?"). Assistant turns 15-70 words, warm and specific, no lists.
  Set `metadata.n_pairs`.
- **stories (+800, type `writing`, `metadata.kind = "story"`):** the user asks for a story in one sentence (vary:
  "Tell me a story about...", "Write a short story where...", "Make up a bedtime story for my little brother about...",
  sometimes with a constraint: a title, a happy ending, for a 6-year-old, set in a village, with a talking animal).
  The assistant writes ONLY the story, 80-150 words, past tense, named characters, a clear beginning, a problem and
  an ending that resolves it; it fits every constraint asked. No moral lecture at the end, no "Once upon a time" in
  more than 1 story in 10, no title unless asked.
- **multi_question (+600):** exactly 2 questions (`n_questions = 2`), familiar topics (word meaning, easy grammar fix,
  everyday reasoning, simple advice, spelling, one dont_know kind); the user writes them naturally (one line, two
  lines, "Also, ..."). Answers "1." and "2.", each 1-2 short sentences. A correction answer keeps the rule-name Why.
- **grammar "Why:" rule names (all 1,220 grammar rows; repair, not new rows):** the Why line names the rule from a
  fixed list, then the trigger and fix in brackets: `Why: <rule> (<trigger> -> <fix>); <rule> (...).` e.g.
  `Why: past tense ("yesterday" -> "went"); article ("an" -> "a" before "university").` At most 20 words; one clause
  per fix; rules: subject-verb agreement, past tense, present tense, future tense, perfect tense, continuous tense,
  verb form, article, plural, uncountable noun, preposition, pronoun, possessive, word order, comparative,
  superlative, question form, negative, spelling, capital letter, punctuation, apostrophe, missing word, extra word,
  word choice, conjunction. The corrected text itself is not changed unless it is wrong. When the sentence is already
  correct, the line is `Why: no error (<rule>: "<phrase>" is correct).`

## Run 8 capabilities (agreed with the user 2026-10-02: keep every earlier type and rule, add these as the focus)

The user's six goals: (1) understand messy or misspelled questions and answer them (or say politely it does not
know), (2) answer in a JSON structure when asked, (3) answer from a given context, or from its own knowledge when the
context lacks it, (4) greet and stay polite, (5) say "I don't know" politely and briefly, never a meaningless
paragraph, (6) answer questions about given passages. New rows go to `train/chat_r8/<type>.jsonl`
(ids `<type>-r8-NNNN`); validate with `python3 scripts/validate_chat.py <file> --type <type> --short-why --run8`.

| type | turns | user | assistant | length (assistant words) |
|---|---|---|---|---|
| messy_question (new, 1,500) | 1 | an everyday question written badly: 2+ real misspellings, missing words, ESL word order or text-speak ("I wat fli a plain what should i do", "hw to make tea wit milk"); vary how messy (light / heavy) | first ONE short sentence that states the understood question plainly ("You want to learn to fly a plane." / "You're asking how to make milk tea."), then the answer in 1-4 plain sentences. If it is something the model cannot know or a specialist matter (medical, legal, money), the answer part is a polite short don't-know with one safe next step. Never comment on the spelling, never "correct" the user unless asked | 15-90 |
| json_output (new, 1,500) | 1 | asks for the answer as JSON: names the keys ("as JSON with keys name, age, city"), gives an example shape, or just says "in JSON"; kinds: extract facts from a short given text, answer a question as fields, list items, classify (sentiment, topic, yes/no), convert a sentence into fields | ONLY the JSON (no code fences, no words before or after), valid, double quotes, keys exactly as asked (snake_case when not given), values correct and supported by the text; arrays for lists; numbers as numbers; null when the text lacks a value. Set `metadata.keys` to the top-level keys | 3-120 |
| context_qa (new, 2,000) | 1 | a short context (40-180 words: a notice, message, note, short article, story bit; generated, never copied from books) + one question. `metadata.kind`: `in_context` (50%), `general` (30%: the text lacks it but it is common knowledge), `unknown` (20%: neither) | in_context: the answer from the text in own words (1-2 sentences). general: starts "The text doesn't say, but" + the common-knowledge answer. unknown: starts "The text doesn't say," + "and I don't know" (or "and I can't know that") + one short next step. Never invent details | 3-60 |
| greeting (new, 800) | 1-3 | greetings, how-are-you, thanks, goodbyes, introductions, apologies, compliments, "good morning/night", festival wishes; sometimes followed by a small request in the same chat | warm, polite, short; returns the greeting, may ask ONE friendly question back; when a request follows, greet briefly then help | 2-45 |
| dont_know (+500, run 8 rule for new rows) | 1 | as before, plus topics outside its knowledge (specialist, very recent, private, exact niche facts) | polite and SHORT: says it does not know or cannot check, one-sentence reason, one safe next step. At most 40 words, no padding, no lecture | 8-40 |
| comprehension (+1,500, generated passages) | 1 | a generated passage (80-220 words, everyday Indian/international settings; `source: generated`) + one question; 50% literal (who/what/where/when), 50% inference (why, how did X feel, what will probably happen, what does this show) | the answer, 1-2 sentences, supported by the passage; inference answers give the clue from the text ("because she ...") | 5-50 |

Safety rule 6 applies to all of them (no medical, legal or financial advice; messy questions about health/money get
a polite pointer to a doctor / trusted adult / official source).

## Pilot

Write 20 examples per assigned type into `train/pilot/<type>.jsonl`, ids `<type>-p0001`.., then run
`python3 scripts/validate_chat.py train/pilot/<type>.jsonl --type <type>` and fix every FAIL. Report counts and
anything you could not do. Do not commit.
