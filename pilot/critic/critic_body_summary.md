# Critic summary: body stage (final sample)

Input: `.staging/critic/fin_body` (52 records, 12 marked `forced`). Verdicts are in `pilot/critic/critic_body.jsonl`.
Reviewed against the CRITIC checks (1)-(9) plus house rules (a)-(i). Rules (h) (medical advice and diagnoses) and (d) (disclosure and same-beat response to hopelessness) got extra weight.

## Counts

| Stage | Pass | Fix | Reject |
|---|---|---|---|
| body | 47 | 5 | 0 |

Forced items (12): 11 pass, 1 fix (4174 v2, the pronoun wording). All 12 are safe.

Automated checks on all 52 records found nothing: every length is in range, there are no emoji, no brands, no framework tag words, no 5-word copying from the description, and the QA order is correct.

## Safety review: (h) medical and (d) disclosure

No record breaks a safety rule.

- **Hopelessness and dark mood, response in the same beat**
  - 4165 v1: essay line "grey and pointless". The counsellor sees the student that afternoon and the parent is called that evening.
  - 4165 v2: "nothing felt worth trying". The same day, the teacher talks to the mother and walks the student to the counsellor.
  - 4174 v2: "the low felt so heavy it frightened her". The sibling sits with her at once and they phone the clinic together that night.
  - 4133 v2: weeks of grey mood. They decide to see the doctor, and the partner offers to go with her.

  None of these is left overnight without help. None mentions self-harm methods.
- **No diagnoses by a narrator or in an answer**
  - "I'm autistic" (4292 v1) and "panic"/"attack" (4198 v2) are the characters describing themselves, which is allowed.
  - Professional findings are reported in general terms only ("a doctor explained...", "the audiologist said a hearing aid would help", "there was a physical reason, and a plan"). 4146 v1 avoids naming the likely condition, which is correct.
  - "Since the flu hit" (4159 v2) is an everyday illness label and I did not flag it.
- **No dosing, drugs, diet numbers or thresholds.** Health scenes send people to a doctor, nurse, counsellor or psychologist: 4294, 4293, 4190, 4197, 4146, 4133, 4174 (both), 4202, 4196, 4240, 4239, 4311. Food rows use general words only (dal, curd, banana, egg). The substance rows (weed 4238, nicotine 4239, alcohol 4240, energy drinks 4235) show recognition and support, not use as a win.
- **Puberty and sexuality (4161, 4166 x2, 4168 x2)** are factual and calm, with nothing explicit. Where a peer suggests secrecy ("don't tell Amma", "sneak out"), a trusted person steers the teen away from it.

## Fixes

1. **4168 v1, age fit.** The row is 13-17 but the passage says "Nandini, twelve". Change it to thirteen.
2. **4174 v2, rule (a) wording.** The literal question "asking Bhupen if he has done something wrong" can be read as making the ungendered narrator male. Rephrase it around the fiancé.
3. **4292 v2, recipe form.** An R14 spoken story ends with a letter sign-off ("Your colleague, Vaibhav"). Name the speaker inside the speech instead.
4. **4196 v1, QA quality.** The mental_state answer says "frustrated" with no cue in the passage. The application question only asks for recall.
5. **4293 v1, dialogue.** Two nurse lines come one after the other with no reply between them, so the second reads as if Uday said it.

## Recurring patterns, most common first

1. **Weak QA types (1 record: 4196 v1), plus 1 dialogue-attribution slip (4293 v1).** An application question sometimes becomes "What did X do...?", which is recall, and a mental_state answer sometimes names a feeling the passage never shows.
2. **Form drift at the end of a piece (1 record).** A signature line gets added to an elder's spoken story. Signatures are right for letters, notes and diaries; in a spoken monologue the speaker should introduce themselves.
3. **Hard numbers in the passage versus the age bracket (1 record).** A stated age sits just outside the row bracket (12 in a 13-17 row).
4. **Pronoun wording around an ungendered narrator (1 record).** A question reuses a "he" from the passage, and the "he" could attach to the wrong person.
5. **Watch item, no verdict: variant closeness.** Both variants of 4165 follow the same arc: teasing, then eating alone, then a hopeless line, then counsellor and parent the same day. They differ in form (a present-day R13 account versus an elder's memory) and in details. This is acceptable because the row requires that arc, but the central beat is close.

## Suggestions for the prompt and validator

- **Validator:** read the age stated in a passage ("X, twelve", "age eight", "N-year-old") and warn when it falls outside the row bracket. Handle 7-12 and 13-17 carefully, since 12 and 13 sit on the boundary.
- **Validator:** for R14 and R11 (spoken forms), warn when the last line of the passage is a bare name or "Your ..., Name" sign-off.
- **Prompt (rule 14):** add one line: "application must not be answerable by copying a sentence of the passage; ask why, which is wiser, or what next."
- **Prompt (rule 2):** in questions about a first-person narrator, avoid he/she even when it refers to someone else; name that person instead.
- **Prompt (body addendum):** the current wording is working well. Doctor referrals are present, there are no numbers, and responses to hopelessness come the same day. Keep it unchanged.
