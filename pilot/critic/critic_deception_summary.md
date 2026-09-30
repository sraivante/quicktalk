# Critic summary: deception stage (final review)

Input: `.staging/critic/fin_deception` (61 records, 21 marked forced). Output: `pilot/critic/critic_deception.jsonl`.
I weighted rule (g) heavily: deception, influence and manipulation content has to be there for recognition and self-protection.

## Counts

| Verdict | All | Forced (21) | Not forced (40) |
|---|---|---|---|
| pass | 43 | 9 | 34 |
| fix | 18 | 12 | 6 |
| reject | 0 | 0 | 0 |

Every passage length is inside its age band. Emoji use is within the caps. There are only two emoji, both in non-sensitive chats: 🤍 and 😠 in passages, 🙂 in one answer. The sensitive chats (self-harm, scams, deepfakes) have no emoji.

## Rule (g) safety pass: nothing unsafe found

I checked every record that shows a tactic from the inside:

- 4675 v1/v2: coercive control, from the controller's point of view.
- 4645 v1: a joining-fee pyramid pitch.
- 4643 v1/v2: flattery lines.
- 4734 v1: dehumanising words.
- 4672 v2: a threat to spread a false rumour.
- 4769 v2: a request to backdate a form.
- 4722 v1: a rumour cascade.
- 4692, 4765, 4689, 4688: romance and catfish scams.
- 4697, 4712, 4642, 4641: pressure sales and impersonation.

In each one the villain's lines are short and generic. Nothing in them could be reused as a script. Each tactic is also named or resisted on the page, and none is shown as a win:

- the scammer's smile vanishes;
- the counterfeit photos are traced;
- the controller hears "something colder" under the word love;
- Ira says "losing her" in counselling;
- the flattered student says "let me think";
- the backdating request is refused and a legitimate route is offered.

The children's rows (4616, 4637, 4682, 4683) teach honesty and safety, not cunning.

The application answers name a protective step each time: pause, verify through a separate channel, tell a trusted adult, or report. No record gives medical, legal or financial advice, names a brand, or makes a diagnosis. General cautions such as "real investments can lose money" come from the row itself, so they count as recognition, not advice.

## Safety and disclosure items (all marked fix, none rejected)

1. **4625 v1 (forced).** The friend says "I'm so tired of everything", which is a possible self-harm warning sign. The helper asks "are you safe?" in the same beat, but the counsellor visit is set for "Tomorrow, 11" and the entry ends overnight. The fix is a same-night step: call Yusuf, the warden or a helpline if the feeling gets worse, plus a check-in before sleep. The same row's v2 (Afreen) handles this well: the warden and counsellor are brought in within minutes.
2. **4637 v2 (forced).** The head teacher saw the humiliating bench punishment "the week before" and acted only after the child lied. The fix is to have the adult act the same day they see it.

The disclosure scenes all show an adult responding the same day:

- 4624 v1/v2
- 4627 v1/v2
- 4683 v1
- 4726 v2
- 4637 v1
- 4625 v2

The online-secrecy case (4624 v2) ends the contact (block and report) and involves a trusted adult. No meeting happens.

## Recurring patterns (ranked)

1. **mental_state answers that name no feeling (13 of the 18 fixes)**: 4666 v2, 4762 v1, 4658 v2, 4743 v1, 4718 v1, 4627 v1, 4640 v1, 4641 v1, 4642 v1, 4643 v1/v2, 4644 v1, 4645 v1. The question is often framed as "What did X realise / think / want?", and the answer gives a belief or goal only. The passage usually has a body cue (face went hot, looked embarrassed, heart thumping) that the answer could have named.
2. **Question centring in [Observer] rows (2)**: 4692 v1 (mental_state and perspective both centre the observed person) and 4640 v2 (the observer never gets a question, and the perspective centres a third party).
3. **Tag point of view for [Observer] (1)**: 4640 v1 is told from the person who holds the bias and catches it himself. That reads as Actor/Thinking, not Observer.
4. **Variant sameness (1)**: in 4645, v1 and v2 share the same central beat (lavish praise, then a fee request, then a pause to check). Only the setting differs.
5. **Delayed adult response (2)**: 4625 v1 and 4637 v2, described above.
6. **Minor, left as pass with a note**:
   - Some perspective questions just recount what another person did ("How did the officer / compliance head / Mummy respond?"): 4765 v2, 4751 v1, 4726 v2.
   - 4716 v1 uses an invented product name, "Chandan Glow". It is fine if fictional, but "a sandalwood face powder" is safer.

The house rules on gender cues and grounding (rule (a)) held throughout. First-person narrators with no gender cue are always called by name, and kin terms are used correctly. I found no gendered-pronoun defects.

## Systematic suggestions (for approval; I did not edit the prompt or validator)

- **Prompt, MASTER qa definition.** Add: "The mental_state answer must contain an emotion word (e.g. anxious, ashamed, relieved). 'Realised', 'thought', 'wanted' alone do not count." Also discourage "What did X realise/think/want?" as the mental_state question frame.
- **Validator (optional heuristic).** Warn when the mental_state answer contains no word from a small emotion lexicon. Nearly all of this stage's fixes would have been caught.
- **Prompt, self-harm clause.** Add a concrete example: "If the person says they are safe but the talk ends at night, show a same-night step (helpline, warden, a check-in); do not leave professional help until the next day without one."
- **Prompt, [Observer] clause.** Spell it out: "mental_state centres the observer and perspective centres the observed person."
- **Planner.** For rows with two variants, suggest different central beats, or require that what the manipulator wants differs between variants (money in one, a favour or loyalty in the other).
