# Critic summary: planning stage (fin_planning)

Input: `.staging/critic/fin_planning` (60 records, all variant 1, 60 distinct S.Nos; no items marked `forced`).
Tags: Action 19, Pitfall 17, Thinking 15, Revision 9.
Output: `pilot/critic/critic_planning.jsonl`.

## Counts

| Stage | Pass | Fix | Reject |
|---|---|---|---|
| planning | 47 | 13 | 0 |

Fix: 6720, 6786, 6758, 7309, 7300, 6392, 5960, 7634, 6012, 5993, 6393, 5840, 6301.

## Recurring patterns (ranked)

1. **Internal consistency slips (4)**: 5993 (Rs 130 in two weeks, then "three more weeks" for Rs 70), 6301 (books "at their opening pages" while at Chapter 8), 7634 (book in plastic cover but only chapters 3-6 unopened), 6758 (listener and partner both "Anjali").
2. **mental_state and perspective centre the same person, or perspective misses someone affected (3)**: 6012, 5993 (both centre the protagonist twice); 6720 (perspective centres the observer, not someone affected by the plan).
3. **Pronouns for people whose gender is never stated (2)**: 7309 ("he" for Hrithik), 5840 ("she" for Rehana). Both are name-only cues.
4. **Disclosure / reporting chain incomplete (2)**: 6392, 6393 (see safety list).
5. **Answers that add facts or give a reason in place of a feeling (2)**: 7300 (Damini "calmly", "guilt"), 6786 (mental_state gives a reason, not the feeling at that moment).
6. **Cast name against usual gender (1)**: 5960 (Simran as a boy).
7. **Revision driven by someone else (1)**: 5993 (the older sister supplies the smaller-goal idea; the row says the boy notices and changes it).

## Rejects

None.

## Safety items

- **6392** (bullying, silent endurance, chat): Ritu tells a peer about months of bullying and wanting to stay away from school. The passage ends on "mum tonight. I'll try" with no adult response on the page. It needs a same-day adult beat. No emoji in the passage, which is correct.
- **6393** (bystander reports bullying): the class teacher only praises Sumit. It needs the teacher's actual response on the page.
- **7309** (SIP during a market crash): the application answer gives a personal-finance instruction (lower the instalment for a month or two). Reframe it as checking with someone qualified. **6865** (clear the card debt first) passes because it has no numbers and stays tied to the row, but finance rows are borderline for rule (h) by design.
- Checked and OK: 6506 scam (named as a trick, counsellor contacts parents the same day, no emoji), 6978 online threats (lecturer, portal and principal all act the same day), 7047 high-control group (self-protective limits), 7300 remedies (the doctor reviews them, the passage gives no medical advice), 7215 burnout (sees a doctor, no diagnosis).

## Other observations

- No passage uses an emoji (0/60). Answer emoji appear in 9/60 records and all fit. That is within the caps, but chat and dialogue recipes on non-sensitive rows (6601, 6693, 5993) could carry an occasional in-passage emoji as the house rule prefers.
- Stems repeat often. About 20 application questions start "What alternative approach could X...". The addendum asks for "alternative approach", but rule 14 asks for varied frames.
- Some perspective questions centre a hypothetical person who is not in the passage ("a classmate who hoped for costly plans", "a parent or teacher", "a Class 7 student"). This is acceptable, but a named character is stronger.
- Some grounding lines repeat the row description word for word (6395, 6393). This is allowed but adds nothing.
- 6267 and 7634 (different rows) both show decorative planning with no studying. Each fits its own row, so this is not a variant clash.

## Systematic suggestions (for user approval, not applied)

1. **Validator**: for pronouns in answers and grounding, check he/she/his/her against the passage. Flag a pronoun when the passage has no gendered pronoun or kin term within a sentence of that name.
2. **Validator/prompt**: check that the mental_state and perspective questions name different people (compare the first capitalised name in each question).
3. **Prompt (planning addendum)**: allow the application stem to vary ("What else could...", "Which approach would suit... better?") so "alternative approach" does not become a fixed template.
4. **Prompt (rule 8)**: when a young person discloses to a *peer*, the passage still ends with a trusted adult's same-day response, not a plan to tell.
5. **Prompt**: for finance rows (SIP, debt, loans), the application answer names a choice or points to a qualified adult. It never gives a money rule.
6. **Generator self-check**: add "re-check any numbers, days and counts in the passage against each other" to rule 15.
