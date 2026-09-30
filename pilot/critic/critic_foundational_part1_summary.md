# Critic summary: Foundational Concepts, part 1

Input: `.staging/critic/fnd_part1` (56 records). Per-record verdicts: `pilot/critic/critic_foundational_part1.jsonl`.
Checks used: the 9 CRITIC checks plus house rules (a) to (j). Check 8 (relations) does not apply to this stage. Repeated cast names were not flagged, as instructed.

## Counts

| Verdict | Count |
|---|---|
| pass | 44 |
| fix | 12 |
| reject | 0 |

## Recurring patterns (ranked)

1. **Answers or grounding add relationships the passage does not state (5 records).** The grounding line is the usual culprit. It turns an unstated tie into "brother", "cousin", "father" or "friend": 5647 v2 (Lalit written up as "his father"), 5667 v3 ("her brother", and the row says friend), 5619 v5 ("cousin" from "di"), 5692 v1 ("older cousin", and Rumi as "a friend"), 5444 v3 (Ojas as "a friend"). The generator seems to fill in the relationship from the row description or the cast rather than the passage.
2. **Perspective questions that do not centre another person's view (3 records).** 5749 v5 asks about the observing protagonist herself. 5529 v1 and 5660 v1 (both R14 elder stories) ask what the listener might *do*, which repeats the application question. R14 seems to invite this, because the listener is the obvious "other" but has no stake in the story.
3. **Mental_state answers that describe behaviour or quote a line rather than name the state (1 fix, several borderline).** 5521 v5 lists actions and never names delight. Borderline, left as pass: 5643 v5 ("What did Kashish realise"), 5633 v4 ("What does Gurpreet hope to say") and 5543 v1 ("What did Ankita realise"). These are inner states, but the answers mostly restate the passage.
4. **Small internal inconsistency (1):** 5615 v4 says Lokesh started learning "this year" but also split stems "last year".
5. **Community cues in a mockery scene (1):** 5529 v1 names the smirking colleagues Sharma and Bhatia. The surnames carry caste or community signals that the schadenfreude row does not need.

## Rejects

None.

## Safety and sensitive items

- **5553 v1 (disclosure, rule c): fix.** A teen, worn out by a grieving friend, breaks down to the librarian. The librarian listens and takes her to the counsellor the same day, and that response is shown on the page. The missing piece is "it is not your fault", even though the passage shows the teen "hating herself". The fix is one line.
- **5693 v3 (Milgram chat, humiliation of a teammate): fix.** The passage ends on a senior's "👍", but sensitive chats must carry no emojis. The senior's lines are otherwise brief and generic, and the harm is shown from the target's side in the perspective answer.
- Checked and passing:
  - Misinformation rows keep the false claim from standing. 5489 v1: the cousin notes that the child-lifter photo "has been going round for years". 5491 v1: the fever forward is traced to an old foreign report. 5444 v3 and 5442 v3: the palm reading and horoscope are undercut by a question or by comparing the other signs.
  - 5539 v1 and 5556 v1 bring in a counsellor, and neither gives any clinical advice.
  - 5458 v2 (placebo) reports the symptom to the physio, with no numbers.
  - 5484 v2 (thin ice) and 5508 v2 (fire evacuation): the application answers name the safe choice.
  - Faith and region rows (5657 v1, 5660 v1, 5675 v1, 5653 v2) use identity cues only where the row needs them. None spells out a slur or joke.
- No brands, no real public figures, and no diagnoses were found. Rule (i) holds: no passage names a concept by its label. All of them show it in action.

## Emoji

The emoji use is generally good: sparse, fitting (😰 for dread, 😅 for blanking, 🤍 as a gentle answer emoji) and absent from grief, burnout and bereavement scenes. The only violation is 5693 v3. A minor habit that was not flagged: an emoji tacked onto the end of the last (perspective) answer (5484 v2, 5496 v3, 5692 v1, 5539 v1). Each fits the feeling, but MASTER rule 10 warns against doing this by habit.

## Systematic suggestions

1. In the foundational addendum (or MASTER rule 2), add one explicit line: "grounding must not name a relationship (brother, cousin, father, friend) that the passage does not state." This is the most frequent defect in this sample and it is cheap to prevent.
2. For R14 (elder tells a younger listener), steer the perspective question toward someone *inside* the story (the helper, the mockers, the newcomer's colleague) rather than what the listener should do.
3. For Observer-tagged rows, remind the generator that the perspective question must centre someone other than the observer, because the observer is the protagonist.
4. Otherwise the stage's addendum is working. Concepts are shown in action rather than named, experiments are kept at human scale, and every recipe was followed: R13 beats fall on different days, R2 is dialogue-led, and R6 is in short lines.
