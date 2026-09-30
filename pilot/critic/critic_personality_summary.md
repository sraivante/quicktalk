# Critic summary: Personality & Individual Difference

Input: `.staging/critic/per_all` (87 records, 81 rows). Verdicts: `pilot/critic/critic_personality.jsonl`.
Reviewed against the 9 CRITIC checks and house rules (a)-(h). Cast-name repeats were not flagged.

## Counts

| Verdict | Count |
|---|---|
| pass | 66 |
| fix | 21 |
| reject | 0 |

## Recurring patterns (ranked)

1. **Perspective question centres the wrong person (7).**
   - Centres the protagonist: 4501 v2, 4508 v2 ("If you were Daniel"), 4542 v1.
   - R14 elder stories that centre the listener instead of someone in the story: 4486 v1 (Harsha), 4472 v2 (Aparna).
   - [Observer] rows that centre a third party instead of the person observed: 4441 v1 (Joost, not Elif), 4556 v1 (Mridul, not Ritesh).
2. **The application question asks for the elder's advice or moral, not a choice or turning point (3, all R14):** 4539 v1, 4516 v2, 4536 v2. They all use the same "What does <elder> advise <listener>…?" frame. The R14 turning points are already in the passages (calling the parents that evening, straining the dal, the teacher taking her to the counsellor), so each fix only rewrites the question.
3. **A relationship, role or fact is named in an answer or the grounding but not in the passage (4):**
   - 4486 v2: Mrs Iyer is called "a teacher".
   - 4438 v2: Maria is called "a partner".
   - 4431 v2: Ritu is called "her friend".
   - 4449 v1: the grounding says "medicine", but the passage names no field.
4. **In self-harm and suicide-risk scenes, the same-day response is not fully on the page (3). These are the safety items below.**
5. **The mental_state answer lists behaviour but names no feeling (2):** 4514 v1, 4524 v2.
6. **Small wording defects (2):**
   - 4344 v2: the literal answer keeps the first-person "our".
   - 4350 v1: the question says "first five hundred rupees", but the passage gives no amount for the second request.

Minor note: three records in this stage are set in Toronto (4550 v2, 4508 v2, 4341 v2). They are different rows, so this is not a variant clash, but it is worth watching.

## Rejects

None. No record is unsafe or fundamentally off-row.

## Safety items (all "fix", none unsafe)

- **4573 v1 (suicide risk, asking directly, R13):** Neelam says "It'd be easier for everyone if I just vanished" on Monday night. Baljeet does not ask until Tuesday, so the warning sits overnight. The fix is to keep Monday for quieter signs and move the remark to Tuesday, right before the direct question. The rest of the scene is strong: Baljeet stays, removes access with no method named, and calls the crisis line the same day.
- **4572 v2 (self-harm, reflective account):** Ojas offers to help, but the care arrives "that week". The fix is to show Ojas staying and helping make a call or tell a trusted person that same day.
- **4572 v1 (self-harm, dialogue):** Jahnavi stays tonight and plans the doctor for the morning, but telling Amma has no time attached. The fix is to make it "tonight".

Records that fully meet the safety rules:
- **4570 v1 (friend's disclosure):** the friend refuses the secrecy promise, stays, and brings in a parent who says it is not Kaito's fault; the mother and a helpline are called the same evening.
- **4569 v1 (warning signs):** the teacher phones the parents and the counsellor right away.
- **4562 v1 and v2 (grief and depression):** the helper asks directly; in v1 the crisis line is called the same night.
- **4542 v1 (depression, "better off without me"):** the friend stays and calls the helpline that night.
- **4544 v1 (supportive response):** the elder tells the friend's brother the same evening.
- **4585 v1 (stigma, child's worries):** the neighbour and the child tell Mummy together that evening.
- **Eating rows 4566 v1 and v2, 4568 v1:** no food or weight numbers.
- **Neurodivergence rows (autism, ADHD, tics, OCD, dyslexia, sensory):** no clinical label is applied as fact. Characters either name their own condition, the row's label is used, or a character reports a doctor's words.
- There are no emojis anywhere in the set.

## What is working well

- Pronoun discipline for first-person narrators and letter or diary writers is strong. Santosh, Kishore, Tanuja, Hrithik, Deepika, Chaitanya, Sudha, Ankita and Gurleen are never gendered in answers or grounding.
- The two variants of each double row differ in setting and central beat: 4324, 4485, 4486, 4562, 4566 and 4572.
- Disability and difference are shown respectfully and with variation, as ways of connecting rather than deficits. Examples are the bus stop at the sandcastle (4500), the moth trap (4506), the Holi text reply (4505) and the tics ignored during play (4529, 4532).
- Row fidelity is high. No leaked tags or copied description text were found.

## Systematic suggestions (for the user to approve; prompts were not edited)

1. **R14 elder stories:** add a line to the batch or recipe text: "application asks what someone in the story chose or what turned things; perspective centres someone inside the story, never the listener." This one line would have prevented 5 of the 21 fixes.
2. **[Observer] rows:** make it explicit that the perspective question centres the person observed. MASTER currently allows "or a third party", which conflicts with the house rule and led to 2 fixes.
3. **Self-harm and suicide-risk R13 (before, during, after) rows:** a note that a spoken warning sign and the helper's response belong in the same beat, so the day-split structure does not leave a warning unanswered overnight.
4. **mental_state:** remind generators that the answer should name the feeling in words, and not only list the cues.
