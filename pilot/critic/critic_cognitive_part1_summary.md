# Critic summary: Cognitive Machinery, part 1

Input: `.staging/critic/cog_part1` (61 records). Per-record verdicts: `pilot/critic/critic_cognitive_part1.jsonl`.
Checks used: the 9 CRITIC checks plus house rules (a) to (h). Check 8 (relations) does not apply to this stage.

## Counts

| Verdict | Count |
|---|---|
| pass | 46 |
| fix | 15 |
| reject | 0 |

## Recurring patterns (ranked)

1. **Question-type drift (house rule e): 3 records.**
   - 3664 v2 and 4039 v1: the perspective question only recalls lines or a list from the passage.
   - 3853 v5: in an [Observer] row, the perspective question centres the observer, who is the protagonist.
   - Mental_state questions are strong across the batch. Most explain why the mechanism feels reasonable from the inside, as the cognitive addendum asks.
2. **Grounding or clarity slips about who is who: 4 records.**
   - 3778 v4: "Madhav" is never linked to Dadu.
   - 3997 v2: "Her husband" grammatically points to the child.
   - 3983 v4: the answer adds a cause ("because of it") that the letter does not state.
   - 3610 v4: "sold at cost" contradicts "take the profit".
3. **Sensitive-topic handling: 4 records.**
   - 4113 v2: emoji in a low-mood chat, and no adult responds on the page.
   - 3903 v1: a bullying disclosure with no adult response.
   - 4025 v3: a "pandit-ji" tease from a Muslim-named peer adds a faith and caste overtone.
   - 3987 v4: a dehumanised group tied to a real regional origin ("from Bihar").
   - 3989 v4 (🙂 in an answer on a contempt row) is a smaller emoji slip of the same kind.
4. **Unstated-gender pronoun (house rule a): 1 record** (3751 v3, "his book" for Sachin). This is much better than part 0. Generators now consistently write around names like Zubin, Urmila, Aadhya, Hansa, Noor and Karthik.
5. **Variant diversity: 1 record.**
   - 3984 v2 and v4 both turn on the same beat: a mocking clip, one calm message, "agreed" replies, then the post is removed.
   - The other multi-variant rows differ well. 3997 v1 and v2 are an office colleague and a child at home. 3902 v1 and v2 are a cricket diary and a village sprinter.
6. **Formatting: 1 record** (3830 v4, a closing quote mark is missing at the end of the passage).
7. **Minor notes (passed, no fix needed):**
   - 3976 v4 has 162 words, within the validator's tolerance.
   - 3902 v2 uses a sprinter where the row says cricketer. The lesson is intact.
   - 3932 v1 says "ticks turning blue", which hints at one particular chat app.
   - 3928 v5 repeats "Afreen" even though "Apa" is a gender cue.
   - Recurring motifs: an animal sound dubbed over a mocking clip (3980 dog, 3984 v4 goat), "140 people" in a group (3984 v2, 3980) and samosas as comfort (3976, 3945).

## Rejects

None.

## Safety items

- **4113 v2 (Resilience, reaching for a trusted person; fix).**
  - The passage has 😔 and 🙏 in a low-mood disclosure chat. Sensitive chats must have no emoji in the passage.
  - Hafsa has been hiding this from Ammi. The counsellor visit is only planned for the next day, so no adult's response appears on the page.
  - Row 4113 v1 in part 0 had the same problem.
  - Suggested fix: remove both emoji, and add a narrator line in which Ammi is told that night and responds (stays, listens, says it is not Hafsa's fault, agrees they will see the counsellor together).
- **3903 v1 (Identification, a bullied teen becoming a bully; fix).** The monologue reveals past bullying, distress and ongoing harm to Omkar, but it ends with no response from Didi or any adult. Add a closing line: Didi listens, says what was done to him was not his fault, and they go to the teacher or counsellor together, including about Omkar.
- **4025 v3 (Belonging, dropping a hobby; fix).** The "pandit-ji" nickname, a caste and religious title, is aimed by Wasim at a boy on his way to bhajan practice. It brings in an inter-faith and caste overtone that the row does not have. Use a neutral tease.
- **3987 v4 (Dehumanising, mocking a group; fix).** The workers mocked as "donkeys" are given a real regional origin ("from Bihar"). Drop the origin so the group is defined by work alone. Apart from this, the record is a good model: it shows recognition, a named human face (Dinesh), and a follow-up plan.
- **3664 v2 (Authority bias; fix).** A numeric sleep claim ("more than five hours") is questioned in the passage, but it is never clearly set aside, and Saurabh half-keeps it in pencil. Drop the number, or anchor the answer to the teacher's view.
- **3989 v4 (Restoring the face; fix).** The 🙂 in an answer on a contempt row should go, or become 🤍.
- **Checked and acceptable:**
  - 3979 v1: a harassment note in which the teacher speaks with the target the same day, informs the counsellor and calls both families that evening. This is a model disclosure response.
  - 3956 v4: Mummy tells Sachin the same night that the arguments are not about him.
  - 3980 v4: a ragging chat with no emoji. The friend names it as humiliation and offers to go to the anti-ragging cell.
  - 3984 v2: the warden calls Reena straight away.
  - 3675 v5: the mother says "It wasn't your fault" the same evening.
  - 3986 v4 and 3988 v4: the dehumanised groups are hut-dwelling children and international students. Neither is a real ethnic, religious or caste group, and both give a human face.
  - 3584 v1: home-safety hazards with no numbers or product advice.
  - 3993 v5: one gentle 🤍 in a burglary chat, which fits.
- **Across the batch:** no brands, no real public figures, no diagnoses, no medical, legal or financial advice beyond everyday choices, and no copying of the row description (5-gram check: 0 hits). No framework tags appear in any passage.
- **R2 records:** 3778 v4 (Dadu, family outing), 3733 v2 (family, home), 3997 v2 (family, home) and 3853 v5 (roommate, flat). All are dialogue-heavy and fit rule (g).

## Emoji

18 of 61 records carry emoji. All are within the caps, and none is in a grounding field. Most fit the feeling: 🎉 for a job offer, 😬 for realising the deposit money is needed, 😰 for a lost lucky pen, 😞 for a low mark, and 😅 for a friend's cheerful apology. The misfits are only the sensitive-context ones noted above (4113 v2 and 3989 v4).

## Systematic suggestions

1. **Cast builder (needs user approval; touches config or scripts).** The row `cast` still repeats the same name pairs across rows. This was confirmed in `batches/05_cognitive`: for example, 3664 v2 and 3615 v5 are both cast Sonali + Saurabh, and 3903 v1 and 3763 v3 are both cast Hemant + Omkar. Other repeated pairs:
   - Samir + Francis (3694, 3818)
   - Sharmila + Minakshi (3902 v1, 3997 v2; also in part 0)
   - Aparna + Rukmini (3669, 4021)
   - Mahima + Sharmila (4039; also in part 0)

   Mohit, Joseph, Noor, Darshan and Omkar each appear three times. This repeats the part 0 recommendation: keep a per-stage usage count and avoid reusing pairs.
2. **Disclosure to peers.** For the second time, this row (4113) ends on a peer plus a counsellor visit "tomorrow". Add to the generator guidance that a peer disclosure scene reaches an adult the same day, and shows that adult's response on the page. This covers monologue and letter recipes too: add a one-line reply or a narrator tag.
3. **Perspective in [Observer] rows.** Add to the self-check: "in Observer rows the observer is the protagonist; the perspective question must centre the observed person or a third party."
4. **Faith and region cues in mockery scenes.** Add a note to the addenda: when a character mocks or dehumanises, do not attach a caste or religious title, or a real regional origin, to the target or the mocker unless the row requires it.
5. **Variant differentiation.** This repeats part 0: for multi-variant rows, vary the central concrete clue (here, the mocking clip followed by "agreed" replies), not only names and setting.
