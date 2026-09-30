# Critic review: Group Behaviour stage

Input: `.staging/critic/grp_all` (82 records, 76 rows; 6 rows have two variants: 3355, 3386, 3432, 3468, 3504, 3510).
Verdicts: `pilot/critic/critic_group.jsonl`.
Checks: the 9 CRITIC checks plus house rules (a) to (i).

## Counts

| verdict | count |
|---|---|
| pass | 55 (67%) |
| fix | 27 (33%) |
| reject | 0 |

Automatic checks were clean on all 82: word counts in range, qa order correct, no framework tag words, no brands, no 5-word description leaks, no emoji in grounding, emoji caps respected.

## Recurring patterns (ranked by frequency)

1. **Wrong focus in the perspective or mental_state question (6):** 3393 v2, 3536 v1, 3386 v2, 3479 v1, 3498 v2, 3531 v1.
   - In [Response] and [Receiver] rows written with an observer recipe (R12 or R4), the perspective question centres the protagonist. Usually both mental_state and perspective ask about the same person.
   - Twice the mental_state question asks about an unnamed person (the man in the queue, the conductor).
   - Cause: when the recipe's narrator is an onlooker, the generator seems to treat the observed protagonist as "the other person".
2. **Answer or grounding not supported by the passage (7):** 3524 v2, 3454 v2, 3516 v2, 3378 v2, 3421 v1, 3410 v2, 3518 v2.
   - Some answers state facts the passage does not: "60 people saw" is read as the group's size, "who owns what" is put in Aparna's mouth, "knocked on Farhan's door", "without hesitation".
   - Some grounding lines name roles the passage never gives: "the junior", "a hiring lead", "older colleague".
   - In 3410 v2 the count does not add up: the passage says "four hires in a row" but lists only three.
3. **The mental_state answer gives a reason or opinion, not a feeling (4):** 3501 v2, 3421 v1, 3544 v1, 3482 v2. The answers explain why or what the person thought ("felt that it was slow", "believed the referee was fine") but never name the emotion.
4. **Authority's response not shown on the page, rule (d) (3):** 3555 v1 (counsellor to head of department), 3559 v1 (Yash to the compliance officer), 3522 v1 (Papa to the class teacher).
   - Every disclosure by a child or teen is handled well: the adult's same-day response is on the page in 3386 v1/v2, 3365 v2, 3355 v2, 3515 v1, 3388 v2 and 3522 v1.
   - What is missing is the reply of the next authority up the chain.
5. **Variants of one row share the same central beat, rule (i) (3 flags):**
   - 3504: both variants use the same dead student (Neha), a whole-school assembly, and a student who jokes and then sits alone.
   - 3468: both are office outbursts set off by a desk object (stapler, pen).
   - 3386: both show a crowd of 20 to 30 in a canteen or corridor, then one peer takes the target to an adult who acts the same day.
   - The other pairs (3355, 3432, 3510) differ well enough.
6. **Small wording or clarity defects (4):**
   - 3500 v2 and 3355 v1: the literal question is misframed.
   - 3412 v1: the elder's self-introduction is garbled ("I was Gurpreet then").
   - 3491 v1: the application answer uses "She" for a generic student and gives a self-contradictory tip.
7. **Emoji does not match the feeling (1):** 3489 v1. A 🙂 ends an answer that describes Payal as torn between friendship and the rank list.
8. **Fidelity drift (2):**
   - 3518 v2: the recipe (an institution setting) turned a *family* ritual into a workplace prayer.
   - 3531 v1: "waits patiently in line" is never shown.

## Safety items

- **No rejects.** No incitement, no manipulation scripts, no medical, legal or financial advice, no brands or real public figures. Mockery scenes carry no caste, faith or real regional cues: the accent joke in 3359 and the "colony behind the market" in 3405 are both generic.
- **3556 v1 (fix, priority):** a cover-up about a live electrical hazard (bare wires over wet sacks). The scene ends with only a private notebook entry. No protective step is shown for the workers at risk, and none is named in the answers. A small safe action is needed on the page.
- Scapegoating, mob and cover-up rows otherwise protect targets properly: 3412, 3415, 3421, 3422, 3543, 3555, 3558 and 3559 all end in recognition and safe action. 3559 still needs the compliance officer's reply added (pattern 4).
- Grief and sensitive scenes (3504, 3507, 3386, 3388, 3522) have no emojis in the passage. At most they carry one gentle 🤍 in an answer, as allowed.
- Pronoun and gender rules (a) and (b) were followed well:
  - Ungendered names (Ganga, Kiran, Chen, Kashish, Pema, Sarita, Gurleen, Nikita in 3515, Hrithik, Santosh, and others) never get he or she in answers.
  - Genders and roles match the row descriptions.
  - The only pronoun slip is the generic "She" in 3491 v1.

## Systematic suggestions

1. **Tag and recipe rule for observer recipes:** in R12 and R4 records whose tag is not [Observer], the perspective question should centre neither the protagonist nor the narrator. Add one line to the generator's self-check: "mental_state and perspective must centre different people". This is a suggestion only; the prompt was not edited.
2. **Chain of reporting:** extend the DISCLOSURE check. Whenever an adult passes a report upward (to a head of department, compliance officer or teacher), one line of that authority's response should appear. This is cheap to add and would clear 3 of the 27 fixes.
3. **Variant planning:** when a row has two variants, the plan could give the second a different "central beat" hint as well as a different recipe. Grief, harassment and conflict rows collapse onto the same beat when only the form changes.
4. **mental_state answers:** ask the generator to open with a feeling word ("anxious", "proud", "torn") before giving the evidence. This would fix pattern 3.
5. **Safety-critical cover-ups (institutional pressure):** when the hidden problem is a physical danger, the scene should include at least one protective step now, not only a record for later.
