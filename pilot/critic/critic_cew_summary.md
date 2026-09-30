# Critic summary: culture, execution, wellbeing (fin_cew, 67 records)

Reviewer: independent critic (not the generator). Input: `.staging/critic/fin_cew`. Per-record verdicts: `pilot/critic/critic_cew.jsonl`.

## Counts

| Stage | Records | Pass | Fix | Reject |
|---|---|---|---|---|
| culture | 22 | 17 | 5 | 0 |
| execution | 20 | 14 | 6 | 0 |
| wellbeing | 25 | 22 | 3 | 0 |
| **Total** | **67** | **53** | **14** | **0** |

Pass rate 79%. No rejects. No safety defects.

## Recurring patterns (ranked)

1. **mental_state / perspective role errors (5)**: the mental_state answer gives an intention or reason but names no feeling (execution 5025 v2, 5002 v1); the perspective question centres the protagonist again or reads as a second application question (5169 v2, 5194 v1); in an Observer row the observer drops out and the mental_state question centres the observed person (wellbeing 5358 v1).
2. **Small grounding overreach (3)**: an answer or grounding states something the passage only implies: "borrowed from a bank" (4843 v2), "arranged a meeting" plus an aunt never introduced (4983 v1), "to the families" when only the parents are named (4838 v1).
3. **Observer recipe on Actor or Receiver rows (2 fixes, several borderline passes)**: the R12 observer recipe hides the protagonist's inner state, which the tag needs (4954 v2 Receiver, 4843 v2 Actor). 4953 v2, 4881 v2 and 5438 v1 handled it acceptably.
4. **Awkward prose from avoiding pronouns (2)**: "facts about own life" (4978 v2). The same habit also produced "the heart thumped" (5355 v1) and a garbled self-introduction in an R14 story (5409 v1).
5. **Fidelity and logic slips (3)**: dowry demand and the "families say no" half of the row are missing (4843 v2); the sample and courier timeline contradicts itself (5003 v1); an R14 story has no age anchor for a 23-26 row (5348 v1).
6. **Emoji habit (1)**: 🙂 added to the end of the last answer (5117 v2). All other emoji use is within the caps and fits the scene.

## Rejects
None.

## Safety items reviewed (all pass)
- **5296 v1 (hopelessness and suicide risk)**: the supervisor asks directly, stays with Pradeep, calls the counselling line together with him, a family member arrives the same evening and a counsellor is booked. The warning sign and the response happen in the same beat. One gentle 🤍 in an answer is allowed.
- **4930 v1 and v2 (watching a bribe, forced)**: brief, not instructional. The teen's shame is on the page and the answers point to an honest talk or a trusted adult. In v2 the "Don't tell Papa" secret is handled.
- **4853 v2 (street harassment)**: a bystander intervenes, the fault is placed on the harasser ("It's not on you") and she plans to report it.
- **5111 v2 (UPI scam)**: urgency is named as the trick, nothing is approved and a parent is told.
- **5428 v2 (teen online secrecy)**: the parent states the safety rule (tell me about secrecy or meeting requests, no anger).
- **5089 v2 (unsafe machine)**: the unsafe instruction is refused and the guard is refitted.
- **5418 v2 (grief)**: no emoji and no platitudes.
- No brands, no diagnoses, and no medical, legal or financial advice. 5114 v2 and 5115 v2 describe money behaviour only.

## Suggestions for the prompt or validator (for the user to approve)
1. **Validator**: flag mental_state answers that contain no feeling word from a small lexicon, and warn when the perspective question's subject (the first capitalised name) matches the mental_state subject.
2. **Planner**: avoid giving R12 (observer's account) to [Receiver] and [Actor] rows, or add to the R12 recipe text: "let one line of the protagonist's own speech show their state".
3. **Prompt**: add "In [Observer] rows the observer stays present in every beat and the mental_state question is about the observer."
4. **Prompt**: add "When a first-person or ungendered name needs no pronoun, repeat the name or restructure the sentence; never drop the pronoun and leave broken grammar."
5. **Validator**: warn when an emoji is the last character of the final answer (non-sensitive rows).
6. **R14 recipe**: when the row's age is 18+, state the age of the remembered self in the story.
