# Critic review: situational stage, part 0

Input: `.staging/critic/sit_part00` (91 records, all variant 1, ages 1–3 to 23–26).
Per-record verdicts: `pilot/critic/critic_situational_part0.jsonl`.
The reviewer is a separate agent from the generator. Nothing in out/, batches/, scripts/, prompts/ or config/ was edited.

## Counts

| Verdict | Count |
|---|---|
| pass | 70 |
| fix | 21 |
| reject | 0 |

Several passes carry minor or "note" issues that are recorded but not counted as defects.

## Recurring patterns (ranked)

1. **Gendered pronouns for a narrator or name whose gender the passage never states** (12 fixes: sno 1093, 884, 1367, 841, 640, 1321, 641, 2011, 1110, 1447, 936, 496).
   The most common failure. It almost always involves a first-person narrator (letter, diary, monologue, observer, elder) who is named only by a signature or "I'm X" and then called she/he in the answers. It also hits a minor named character (Thomas in 936, Hafsa in 496, Lalit in 641, where the question text itself says "his").
   Many other first-person records get this right by repeating the name (e.g. 1144, 1996, 1790, 1954, 1636), so the model can do it but does not do it reliably.
2. **Recipe setting not delivered** (2 fixes: 449 and 874 on R7 rural/small-town). The R2 conflict is a separate, non-defect note: R2 is "Dialogue-heavy family or home scene", and 4 records (779, 2047, 1592, 1452) use it for non-family counterparts (clique, old friend, professor, groupmate). There the dialogue form is kept but the scene is not at home. Per MASTER the tag wins, so these are passes, but the recipe text causes a systematic clash.
3. **Emoji fit and placement** (2 fixes plus notes): 😊 at the end of narration in 936 (decoration, not a typed or spoken line). A cheerful 😊 on a "still felt heavy" failure scene in 398. A mid-sentence 😊 in 841. Notes: emoji inside spoken (not typed) lines in 704 and 1452. Emoji caps and the sensitive-topic rules were otherwise respected throughout (grief, grooming, abuse and consent records use none or one 🤍).
4. **Row message element missing or answer not grounded** (2 fixes: 2020 omits "not your fault / no deadline" and leaves "should have moved on" unanswered; 480's answer claims a "gentle nudge" that the passage never shows). Softer gaps are noted on passes (696 "respect and boundaries", 649 "not my fault" only implied, 1217 made rather than joined).
5. **Small consistency and form slips** (fixes: 1386 has Thursday vs Saturday; 1790 has a dangling signature in a reflective account; 776 has a perspective question that centres the protagonist). Note only: 540 is 103 words at age 4–6, inside the validator's 15% tolerance.
6. **Cast names repeat as fixed pairs across rows** (systemic, not scored per record). Omkar+Tushar appears 3 times (father/son, spouses, friends). Lokesh+Baljeet, Darshan+Madhav, Minakshi+Bhavna, Uday+Harsha, Rukmini+Aparna, Pranav+Vidya, Anjali+Joseph, Vandana+Madhuri and Karthik+Sabina each appear twice. Sabina, Bhupen and Avni appear 4 times each in 91 records. The root cause is in the cast picker, described below.

## Rejects

None. No record is unsafe or fundamentally fails its row.

## Safety items

- **sno 1636 (fix, legal-adjacent):** a whistleblowing diary ends with "Tomorrow I'll copy the files at home, not at the office", which acts on company documents before the lawyer consultation just advised. Suggested ending: read the whistleblower policy and set up the lawyer call first.
- **Disclosure and harm scenes checked and compliant:** 1093, 640, 649, 874, 808, 493, 1209, 1206, 449, 641. The adult listens, says it is not the child's fault where the row needs it, and involves the right person the same day or next morning. 449 (toddler shut in) shows the grandmother responding warmly and redirecting the father.
- Financial and legal rows (1930 loan app, 1543 investing, 1928 scam, 1624 discrimination, 1209 scam) stay generic: keep records, talk to the bank or legal aid, tell parents. No specific legal or financial advice is given.
- Health rows (1996, 759, 1233) give no numbers and no diagnoses. No brands or public figures were found.
- Scam and grooming lines (1928, 1206, 1460) are brief and generic, and cannot be used as scripts.

## Suggestions for the prompt, validator or config (for the owner to approve; nothing changed)

1. **Cast picker bug (`scripts/make_batches.py`, `cast_for`).** Names are drawn as `pool[(h + i*7919) % len(pool)]`. Because 7919 mod 179 = 43 (India pool) and 7919 mod 81 = 62 (global pool), the second name is always the first name shifted by a fixed offset. So every time name X is chosen first, its partner is always the same name. The `used` cap is also per batch only, so the same pairs recur across batches. Suggested fix: draw the second index from an independent hash (e.g. sha1 of key+i), and make `max_records_per_name` (already 3 in names.json) a cap across the whole stage.
2. **Validator pronoun heuristic.** Flag answers or grounding that use he/she/his/her/him when the passage contains no gendered pronoun or kin word for any named person. It could warn on first-person records (a signature line or "I'm X" / "My name is X" / "X here") whose answers contain gendered pronouns. That alone would have caught 9 of the 12 pronoun fixes.
3. **MASTER rule 2 wording.** Add one explicit sentence: "A first-person narrator's gender is unknown unless the passage states it; in answers, repeat the narrator's name instead of using he or she." The current rule covers only unnamed roles.
4. **R2 recipe text.** Change it to "Dialogue-heavy scene (mostly spoken lines, little narration); at home or with family where the counterpart allows, otherwise wherever the counterpart naturally is." This removes a recurring recipe/tag clash that critics would otherwise have to judge case by case.
5. **Emoji placement.** The validator could flag an emoji that appears in narration (outside quotation marks or a chat/text line) in a passage, and a 😊/🙂 in an answer when the passage contains words like "heavy", "cried" or "ashamed". Low priority.
6. **Length tolerance.** `validate_jsonl.py` accepts 95–115% of each age band's range, so a 4–6 passage can reach 115 words while the prompt says 50–100. This is fine if intended; otherwise tighten the upper bound for the youngest bands.
7. **CSV data note.** Subtopic and description disagree at sno 874 (subtopic "Chatting with an online stranger", description about a classmate's mean group-chat post). Report this to the owner; do not edit.
