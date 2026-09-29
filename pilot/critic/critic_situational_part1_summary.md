# Critic review: situational sample, part 1 (89 records)

Input: `.staging/critic/sit_part01`. Per-record verdicts: `pilot/critic/critic_situational_part1.jsonl`.

**Overall: 53 pass, 36 fix, 0 reject.**

There are no rejects. No record is unsafe or fails its row at root. Every fix is a small edit, mostly to answers or questions. Only 7 fixes need a passage change: 1701, 851, 1684, 1208, 873, 1210 and 326. Four of these add one sentence.

## Recurring patterns (ranked)

1. **Pronouns for people the passage never genders (20 records; the main cause of fixes).** First-person narrators are the usual case (diary, letter, monologue, observer and elder recipes). The passage gives only a name, and the answers or grounding then say she/he.
   - Records: 981 Payal, 1395 Himani, 1432 Naveen, 1302 Reena, 1022 Pooja, 1336 Lavanya, 1050 Arohi, 1348 Anjali, 1496 Alka, 489 Sudha, 1208 Dilnaz.
   - The same slip affects third parties never gendered in the text: 856 Ganga, 1053 Sharmila, 1165 Madhav, 1278 Simran, 450 Jasleen, 1472 Sarita, 2041 Hafsa. It also appears in the grounding line only: 1396 Parul, 1903 Elizabeth.
   - Many other records avoid this but read awkwardly as a result ("Jeevan felt... as Jeevan sat", "Yamini wanted... what Yamini wanted"). The cleaner fix is to gender the narrator once in the passage.
2. **Perspective question not centred on another person or the counterpart (6).**
   - 1210 and 1992 centre the protagonist.
   - 1714 and 1705 ask the observer "how can you tell". That is evidence recall; it misses the counterpart the situational addendum asks for (mother, spouse).
   - 980 asks the mother about a shrug she never saw.
   - 981 turns the friend's view into the protagonist's feelings.
3. **Recipe R2 ("dialogue-heavy family or home scene") set away from home (5):** 856 shop, 851 school, 1527 office counter, 1006 cycle shed, 326 no setting. The recipe's wording "any setting" is probably being read as "any place" and not "any country/culture".
4. **Cast names reused across rows, often as the same pair (about 20 records touched).**
   - Pairs repeated in this part: Parveen+Ujjwal ×3; Sumit+Urmila ×2; Harsha+Gargi; Himani+Pallavi; Mahima+Sharmila; Jahnavi+Rafiq; Anjali+Joseph; Vijay+Sarita; Mohit+Sudha; Salma+Elizabeth; Sharmila+Minakshi; Maria+Simran; Payal+Vandana.
   - Individual names used 3 to 4 times: Sharmila ×4; Sudha, Ujjwal, Parveen, Urmila, Sumit, Mahima, Elizabeth, Reena, Jahnavi and Anjali ×3.
   - The cast map seems to hand out pairs from a small pool. This is flagged in the per-record notes, and it drove a fix verdict only in 1701 (together with a real fidelity gap).
5. **Wording slips (4):**
   - 1007 and 1022: the elder opens with "I was Ayesha/Pooja then", which reads as if the name has changed.
   - 2041: "then said feeling lighter".
   - 1139: "made her good parts believable".
6. **Fidelity or row mismatch (3):**
   - 1701: the row's "a little indebted" is not shown.
   - 851: the row's classmate is male ("he... welcome him") but the passage writes a girl.
   - 1684: the row says married; the passage never states it, yet the answers talk about "the marriage".

Minor notes (pass verdicts): 468 is 84 words for the 1–3 band, which the validator's +15% allows. 1065 ends its last beat outside the 13–17 bracket, as the row's "years later" invites. 1675 and 471 import a phrase from the row description into an answer.

## Rejects

None.

## Safety items (all "fix", none unsafe)

- **1208 (online stranger, meeting in person):** the contact has already said "don't tell your parents, they wouldn't get it". The row names that as the signal to step back. Here the meeting still goes ahead, the answers present it as the safe plan, and the mother's agreement is only implied. Fix: the secrecy push is the reason Zeenat pauses, and a parent decides any meeting.
- **873 (stranger asking a friend for photos):** the child tells her mother, but the passage stops there. To meet the disclosure rule, add one line: the mother listens, says the child did nothing wrong, and contacts Ritika's parents that same day.
- **1210 (gifts plus secrecy from an adult gamer):** as with 873, the teen tells his mother, but her same-day response is not shown.
- **1224 (unsafe party with drinks):** 👍 on a sensitive-topic answer. Use none or 🤍.
- **326 (age 4–6):** 😊 ends a child's spoken line in the passage. For this band only a caregiver's or teacher's note may carry emojis.
- **2033:** 🙂 on an answer about being "embarrassed or defensive". The emoji does not match the feeling.

Handled well:
- The suicidal-ideation monologue (1752) asks directly, stays with the friend, involves a counsellor and states the safety exception.
- Coming out and family rejection (1237) points to a helpline and a youth worker and checks whether home is safe.
- Consent pressure (1348) and bribery (1527) keep manipulators' lines brief and generic.
- The quota and faith rows (1496, 845, 1551) are even-handed.
- There are no brands, no real figures, and no medical, legal or financial advice.

Answer emojis are used sparingly: 16 of 89 records have one, and there is no last-answer habit.

## Systematic suggestions (for the user to approve; no files changed)

1. **Validator pronoun check.** For each capitalised name in the qa and grounding fields, flag she/her/he/his/him in the same sentence when the passage never uses a pronoun near that name. Or, more simply, warn when a first-person passage (R3/R5/R10/R11/R12/R14) has answers that use she/he for the narrator. In prompt rule 2, add: "A first-person narrator's gender is unknown unless the passage states it. Either state it once in the passage or never use he/she for them."
2. **Clarify R2.** Change "any setting" to "any country or culture; the scene takes place at home or among family". Alternatively, let the planner avoid giving R2 to workplace and school rows.
3. **Perspective rule for the situational stage.** Make it explicit that the perspective question names the counterpart from the subtype (the "X" in "X × Stance") where the passage shows them. It must never be an observer's "how can you tell" question or a question about the protagonist.
4. **Disclosure rule, extend to reported telling.** When the child or teen tells an adult off-page ("I told my mother"), include one sentence of that adult's same-day response (listen, not your fault, pass it on).
5. **Cast diversity.** The planner should not reuse a name, and above all a name pair, within a stage part. A validator warning could fire when a cast name appears in more than 2 records of one output file.
6. **Elder recipe (R14) opening.** Give a pattern such as "I'm <name>. When I was <age>...". This prevents "I was <name> then".
