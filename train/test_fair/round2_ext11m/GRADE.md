# Grading task: fair held-out test (blind)
You grade answers of small chat models. Work in /home/user/quicktalk. Input: .staging/test_fair_ext11m/blind_items.jsonl. Each
line: id, category, type, history (earlier turns), question, reference (a good answer), notes (key facts, required form,
acceptable variants), answers {A, B, C} = three different models' answers in random order. You do NOT know which model
is which; do not try to guess and do NOT open blind_key.json or any answers_*.jsonl.
Grade EVERY answer A, B and C of every item in your categories on this scale:
1 = correct and acceptable (substance matches the reference/notes; wording may differ; required form followed)
0.5 = partly right (main idea right but something important wrong, missing, or the required form broken)
0 = wrong, off-topic, invented facts, unsafe, or nonsense.
Category rules (from the notes field when present):
- messy_question: understood the real question (restatement or answer shows it) AND answer correct/safe; a polite short
  "I don't know" with a safe next step is correct when the notes say the question is unknowable/specialist.
- json_output: ONLY valid JSON with the required keys and correct values = 1; valid JSON with a wrong/missing value or
  extra prose = 0.5; invalid JSON or wrong keys = 0.
- context_qa: in_context = answer from the text; general = must say the text doesn't say AND give the true fact;
  unknown = must say it doesn't know/can't know (inventing an answer = 0).
- greeting: returns the greeting appropriately, polite, short; follow-up request handled correctly.
- dont_know: says plainly it does not know / cannot check, short, no invented facts (any invented specific answer = 0).
- passage: literal = matches the passage; inference = supported by the passage.
- grammar: correct corrected sentence = needed for >=0.5; 1 needs a right reason too.
- multiturn: final reply judged in context of the history.
- story: fits the request and its constraint, coherent, right length; multi_question: fraction of sub-questions correct.
Be strict and consistent across A/B/C; do not reward fluency or length alone.
Output: one JSON line per item {"id", "A": grade, "B": grade, "C": grade, "note": "<= 15 words"} to the file you are
given. Do not edit any other file, do not commit. Report: counts and mean grade per label per category only; never
paste dataset content. Use your own private scratch folder for helpers.
