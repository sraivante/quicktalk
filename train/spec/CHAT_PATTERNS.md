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

## Pilot

Write 20 examples per assigned type into `train/pilot/<type>.jsonl`, ids `<type>-p0001`.., then run
`python3 scripts/validate_chat.py train/pilot/<type>.jsonl --type <type>` and fix every FAIL. Report counts and
anything you could not do. Do not commit.
