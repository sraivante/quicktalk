# Critic review: expression sample (85 records)

**Overall:** 43 pass, 41 fix, 1 reject.
- Flagged 11: 2 pass, 8 fix, 1 reject.
- Other 74: 41 pass, 33 fix, 0 reject.
- 15 of the 41 fixes are only a pronoun or a clumsy name insertion.

## Most common issues
1. **Gender that the passage never states (26 records, 31%).** Named first-person narrators get "he" or "she" (2446/2, 2450/1, Wasim, Nazia, Santosh), and so do unnamed roles (the teacher in 2138/1, the nurse in 2229/2).
2. **Clumsy late name insertion (8).** Examples: "Madhav here has a story" (2445/2) and "I am Simran" inside a diary. 2446/2 and 2450/1 read naturally.
3. **Name reuse with conflicting roles.** Gopika/Arnab appear as daughter/father, sister/brother and student/teacher.
4. Other issues: a garbled perspective Q (2495/2), a perspective Q that centres the protagonist (2576/2), emojis in narration (2446/1 grief 🤍, 2848/2).

## Grounding line
7 of 85 grounding lines (8%) add something the passage does not state. Three add a gender (2446/2, 2450/1, 2866/1). Four add a relation or fact, such as "the mother" (2082/1) or "A deaf toddler" (2152/2).

## Safety concerns
- **REJECT 2240/1:** a five-year-old trails off about "the bruise on his arm... he said..." and pulls his sleeve down. The teacher decides "he may simply have lost the word" and only keeps an eye on him. This teaches an under-response to a possible disclosure.
- 2220/2: the adult leaves a disclosing child alone to fetch the head teacher.
- 2235/1: a disclosure with no adult response, although Ayo is in the room.
- 2220/1: no check-in for a child who goes still and asks about secrets.
- 2514/2: an unwanted touch by a coach, with no adult shown responding.
- 2152/2: invented sign meanings are stated as fact, and "never said a spoken word... did not worry" could mislead.

Consent is handled well elsewhere, and no passage claims a cue proves lying.

## Top 3 changes for remaining stages
1. **Pronoun check.** The validator should flag he/she in qa and grounding for any person the passage never genders. The narrator's name goes in the opening line or a signature.
2. **Disclosure template.** An adult stays with the child, says "not your fault" and passes the report on the same day.
3. **Cast checks.** Block reuse of a name pair across rows, and check the perspective target and emoji placement in narration.
