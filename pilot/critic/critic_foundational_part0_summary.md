# Critic summary: Foundational Concepts, part 0

Input: `.staging/critic/fnd_part0` (55 records). Per-record verdicts: `pilot/critic/critic_foundational_part0.jsonl`.
Checks used: the 9 CRITIC checks plus house rules (a) to (j). Check 8 (relations) does not apply to this stage.

## Counts

| Verdict | Count |
|---|---|
| pass | 46 |
| fix | 9 |
| reject | 0 |

## Recurring patterns (ranked)

1. **Variant diversity: 2 records (plus 1 logic slip in a multi-variant row).**
   - 5747 v1 closely mirrors 5747 v4. In both, a friend says "It's one line" or "It's one test". In both, the protagonist says "I'm being realistic" in a calm voice that makes it sound true, and both give up debate.
   - 5493 v2 and 5493 v3 explain the downplaying with the same precedent: last year a classmate got into the state team and was mocked for months.
   - The other multi-variant rows differ well. 5548 is a village cricket screening in one variant and a school film-club note in the other. 5489 is a dam-scare letter in one and a bird-flu hostel scene in the other. 5668 is a tuition-centre talk in one and a biology file during power cuts in the other.
2. **Question-type drift (house rule e): 2 records.**
   - 5748 v3: the perspective question asks why the observer cannot be sure. That is about the recipe's form, not about how Ramesh sees or is affected.
   - 5668 v1: the mental_state question is answered by recalling Shreya's stated thought.
   - Application questions are strong across the batch. Almost all of them ask about a turning point or a choice, and none of them ask for a moral.
3. **Gender and role (house rules a and b): 2 records.**
   - 5694 v4: the application question uses "he" for Shankar, a diary narrator whose gender the passage never states.
   - 5608 v3: the row says "good friend and son", but the protagonist is a daughter.
   - Otherwise the generators consistently write around names whose gender the passage does not state: Harsha, Jaya, Shalini, Naveen, Deepika, Mohit, Hemant, Sangeeta, Parul, Vasudha and Simran.
4. **Safety-adjacent (house rules f and j): 2 records.**
   - 5489 v3: on a misinformation row, the specific false health claim ("eating chicken this week makes you seriously ill") is never marked as unverified on the page. The scene ends with the spreader certain and winning the likes.
   - 5723 v4: 😔 appears in an answer on a stereotype row, where only none or one gentle emoji is allowed.
5. **Grounding and length: 1 record** (5550 v4). The literal answer slips into the letter's own voice ("Our office"), and the passage is 166 words, above the 160 cap.
6. **Minor notes (passed, no fix needed):**
   - 5497 v1 has 81 words and 5585 v5 has 161, both within tolerance.
   - 5497 v1 is an R2 record with more narration than dialogue, which is reasonable for a toddler.
   - 5731 v4 has ❤️ inside a performative post. It fits the row, which is about allyship done for applause.
   - 5548 v2's "old film about a girl who runs away to join a football team" gently hints at a real film.
   - 5607 v4's grounding says "five-year-old", but the passage never states the age.
   - 5599 v1 uses a mother as the R14 "elder", which is acceptable.

## Rejects and safety items

- **Rejects:** none.
- **Safety items:**
  - 5489 v3: the misinformation claim is not marked false on the page (fix).
  - 5723 v4: an emoji on a discrimination row (fix).
- **Disclosure (rule c):** no child disclosures in this part.
  - 5559 v3 (teen distress): the mother responds on the page with gentle support.
  - 5695 v3 (an adult shamed at work): the letter shows its own action, going to HR. Rule c is not triggered.
- **Misinformation (rule j):** 5489 v4 debunks its claim clearly ("It wasn't true"), so it is fine.
- **Health scenes:** 5456 v3 (nocebo) handles health safely. It gives no numbers and says "tell the doctor ... if it keeps happening".
- **Foundational concepts (rule i):**
  - No record names a concept the protagonist could not know. 5694 v4 is a psychology student reading "that old obedience study", which is plausible.
  - Milgram, Asch, Kohlberg and Schwartz never appear in any passage.

## Systematic suggestions

1. **Cast pool reuses names in pairs across different rows.** The same pairs of names appear together in unrelated rows of this one part:
   - Thomas + Noor (5756, 5476)
   - Yamini + Ramesh (5752, 5748)
   - Akash + Jahnavi (5641, 5760)
   - Zeenat + Dilnaz (5608, 5751)
   - Rajni + Vishal (5542, 5489)
   - Kashish + Sachin (5632, 5475)
   - Vasudha + Parul (5663, 5493)
   - Ayesha + Keerthana (5650, 5585)
   - Minakshi + Bhavna (3 rows)

   Minakshi appears 4 times in 55 records. This is a cast-assignment issue, not a generator fault, so no record was flagged for it. Consider re-seeding or shuffling the cast per row. This needs user approval, because it touches config and scripts.
2. **Multi-variant rows need a distinct "beat".** When two variants of one row are generated, the batch prompt could ask the generator to change the cause, the turning point and the ending, not just the names and form (see 5747 and 5493).
3. **Misinformation rows:** the prompt could say that a scare-forward passage must mark the claim as unverified or false within the passage itself, even when the scene ends before it is corrected.
4. **Observer-recipe perspective questions:** discourage "why is the observer unsure" questions. That uncertainty is already required by the recipe, and it is not a perspective on the events.
