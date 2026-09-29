# Critic review: phase1 core sample (80 records)

**Overall:** 58 pass, 22 fix, 0 reject.
- First 25 (flagged sensitive): 12 pass, 13 fix, 0 reject.
- Remaining 55: 46 pass, 9 fix, 0 reject.

Note: a few of the "sensitive" 25 are not sensitive topics (sno 150, 144, 141, 174/1).

## Most common issues
1. **Unnamed narrator named in answers (6).** Monologue, diary and elder recipes leave the speaker unnamed, but the answers use the cast name and a gender: 252/5 "Omkar", 317/4 "Vikas", 130/3 "Jyoti", 57/3 "Tushar" plus "each brother", 74/3 "Anjali", 146/1 "Damini".
2. **Added gender or kinship (6).** An unnamed teacher becomes "She" (209/2, 235/2). Yuki becomes "He" (195/3). 233/4 calls Ammamma Appa's "mother", but Ammamma is the maternal grandmother. 225/5 turns "Mami" into "a parent". 69/2's answer adds "rupees".
3. **Perspective question centres the protagonist (3):** 231/1, 174/3, 74/2.
Other issues:
- Mental_state answers that restate behaviour instead of naming a feeling (234/3).
- Muddled speaker attribution (150/1).
- Partial fidelity (203/1: Zeenat returns the shopkeeper's error but never admits her own delay).
- An emoji habit: 14 of the 18 records with an answer emoji put it on the last answer.
- Names reused across rows: Ramesh, Vikas and Damini each appear 3 times.

## Safety concerns (no rejects)
Safety handling is strong overall. Every abuse, grooming, addiction and distress scene shows recognition, no blame and a trusted adult or professional. None contains explicit content, numeric health thresholds or advice. Points to watch:
- **258/5:** an addiction chat has 🤍 and 🙏 in the passage. The sensitive-emoji rule allows one gentle emoji, in an answer only, so this rule conflicts with the chat recipe.
- **252/3:** muddled timing of when the drunk girlfriend declined. The narrator also inventories the flatmate's condoms, which reads as snooping. Needs a rewrite.
- **252/5:** 🙂 on a consent answer, which is outside the allowed gentle set.
- **231/5:** the peer line "Girls say no to play hard to get" is a stereotype. It is acceptable because it is rebutted on the page. Keep watching lines like this.

## Top 3 recommended changes
1. **Names must appear in the passage.** Any name used in the answers must appear in the passage. In first-person recipes (R3/R5/R10/R11/R14), the speaker gives their name through a signature or self-introduction; otherwise answers say "the narrator". Add a validator check that every capitalised name in qa or grounding occurs in the passage.
2. **QA-type and pronoun checks.** Perspective must name a non-protagonist or be an explicit "what would change if" question. Mental_state answers must name a state. For unnamed roles (teacher, referee), answers use the role word or "they". The validator could flag she/he for people the passage never genders.
3. **Emoji and kinship rules.** Make the sensitive-topic emoji rule override chat recipes. Have the validator reject a last-answer emoji in more than about 25% of a batch. Add a short kin-term glossary to MASTER (Ammamma, Nani, Mami, Masi, Bua, didi), and stop reusing the same cast names across rows.
