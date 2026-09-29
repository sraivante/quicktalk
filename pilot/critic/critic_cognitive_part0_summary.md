# Critic summary: Cognitive Machinery, part 0

Input: `.staging/critic/cog_part0` (61 records). Per-record verdicts: `pilot/critic/critic_cognitive_part0.jsonl`.
Checks used: the 9 CRITIC checks plus house rules (a) to (h).

## Counts

| Verdict | Count |
|---|---|
| pass | 55 |
| fix | 6 |
| reject | 0 |

## Recurring patterns (ranked)

1. **Gendered pronoun for a person whose gender is never stated (house rule a).** 4 records. In three, a perspective answer uses "he" for a secondary child or friend who is only named in the passage: 3642 v3 (Deepu), 3715 v4 (Jatin) and 3668 v5 (Rohit). In the fourth, 4113 v1, an answer uses "her" for the diary writer Hansa. The fix in each case is to use the name. Generators mostly handle protagonists and signed narrators correctly. The slip happens with minor characters in perspective answers.
2. **Name pairs reused across different rows (systematic, cast-level; not marked per record).** The same pairs of names turn up in different rows: Vaibhav + Indu (3581, 3668), Mahima + Sharmila (3924, 3897), Sharmila + Minakshi (3819, 3619), Nitin + Hafsa (3856, 4093), Bhupen + Sabina (3781, 3826) and Madhav + Shankar (3837, 3956). Ayesha appears 3 times (3594, 3879, 3885), Hafsa 3 times and Kavitha 3 times. For the rows I checked in `batches/05_cognitive`, the pairs come from the row `cast` itself (for example, 3581 v5 and 3668 v5 are both cast Vaibhav + Indu). This makes it a problem with the cast generator, not a generator error.
3. **Question-type drift (house rule e).** 1 record (3795 v5). The perspective question mostly recalls a line ("How did the mother react"), and the mental_state question asks why Rukmini "feels sure" at a point where the passage shows her doubting. Everywhere else the mental_state, perspective and application frames were good and varied. "What did X do well?" appears exactly once in the batch (3837), which is within the limit.
4. **Two variants of one row hinge on the same key detail.** 1 record. Both variants of 4085 turn on "missed follow-up calls". People, setting and form differ, but the fact that carries the row is the same.
5. **Minor notes, no fix needed (passed).**
   - 3951 v4 has 166 words, a little over the 160-word target but within the validator's tolerance.
   - 3581 v5 says "as a boy of nine", which slightly suggests a narrator looking back from further than "a little".
   - 3805 v1 is tagged [Observer], but both friends are the ones remembering. That follows the row description, so it is acceptable.
   - Recurring motifs across records: "pressure cooker whistling" (3856, 3952) and "stacking chairs" (4071, 3641).

## Rejects

None.

## Safety items

- **4113 v1 (Resilience, reaching for a trusted person; fix).** This is a low-mood disclosure (weeks of waking early, withdrawing, crying).
  - The passage has 😅 at the moment Hansa cries. Emoji are not allowed in a sensitive passage, and here it makes light of the moment.
  - The disclosure is to a cousin (a peer). Telling Mummy is put off to "tomorrow", so no adult's same-day response appears on the page.
  - Suggested fix: remove the emoji, and have both cousins tell Mummy that night. Show Mummy staying, listening, saying it is not Hansa's fault, and suggesting they talk to a doctor or counsellor together.
- Checked and acceptable:
  - 3956 v2: a child blames himself for his parents' fights. The counsellor listens, says it is about grown-up things and calls the mother the same day.
  - 3885 v5 and 4117 v3: grief scenes with no emoji.
  - 3781 v4: a near miss while driving and on a call. It ends in a "calls only when parked" rule.
  - 3683 v1: a teenager and a raffle. He ends up not gambling.
  - 3699 v2: a coffee headline. There is no health advice, and it covers reverse causation.
- No brands, no real public figures, no diagnoses, no numeric health thresholds, and no copying of the row description (5-gram check: 0 hits).
- The R2 records (4033, 3842, 3945, 4117, 3911, 4093) are all dialogue-heavy with family counterparts in home or family settings.

## Emoji

12 of 61 records carry any emoji. All fit the feeling (🙏 gratitude, 😠 a child's anger, 😤 hanging up in a huff, 🎉 a congratulations post, 😔 envy and sadness). The only misfit is the 😅 in 4113 v1, noted above. No record exceeds the limits, and no grounding field has an emoji.

## Systematic suggestions

1. **Generator prompt / self-check:** add "check every he/she/his/her in perspective answers against a stated cue for that exact person; otherwise use the name". Minor characters are where this fails.
2. **Cast builder (needs user approval, since it touches config/scripts):** stop reusing the same two-name combinations across rows within a stage. Keep a per-stage usage count and prefer names used 0 or 1 times.
3. **Distress disclosures to peers:** say explicitly in the MASTER/personality addenda that telling a peer is not the end point. When a struggling teen confides, the scene should reach an adult the same day and show that adult's response, or at least the handover happening that day.
4. **Variant differentiation:** when a row has several variants in one batch, ask the generator to vary the central concrete clue (the fact the lesson turns on), not only names and setting.
