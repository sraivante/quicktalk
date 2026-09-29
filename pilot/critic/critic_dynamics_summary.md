# Critic review: Interaction Dynamics sample (90 records)

**Overall:** 78 pass, 12 fix, 0 reject.

Input: `.staging/critic/dyn_sample` (90 records, 88 rows; two rows have both variants: 2987 v1/v2 and 2914 v1/v2).
Per-record verdicts: `pilot/critic/critic_dynamics.jsonl`.
Checked against the 9 CRITIC checks, MASTER rules and house rules (a)-(h). Automatic checks (length, emoji caps, tag words, brands, 5-word runs copied from the description, qa order) were run first. Every record was then read in full.

This stage is in good shape. There are no safety failures. All sensitive arcs (scams, addiction, radicalisation, bullying, grief, self-worth) teach recognition and support. Scammer and extremist lines stay brief and generic. Emoji use is disciplined, and pronoun hygiene for unnamed-gender characters is much better than in earlier stages.

## Recurring patterns (ranked)

1. **Weak perspective, application or mental_state questions (5 fixes: 21, 22, 35, 52, and 51 as a minor issue).**
   - The perspective question asks for something the passage states outright: 2948/1 ("How did Saurabh's wife react?"), 2946/2 ("What did Bidisha think Nazia should do?").
   - The perspective question centres the same person as the mental_state question: 3312/2.
   - The application question pulls out a moral instead of asking about a turning point or intervention: 3081/1 ("What can Norbu learn...?"). This happens most often in R14 elder stories, where the listener is a ready-made target for "what can you learn".
   - A softer version, not flagged separately: several application questions only recall what the helper did ("What did X do that helped?"). Examples are 3252/2, 3114/2, 3347/2 and 3045/2. These are acceptable but do not ask about the turning point that is open now.
2. **Gendered pronouns for a character whose gender the passage never states (2 fixes: 3340/2 "herself" for Elizabeth; 3305/1 "his friend" for Dhruv).** Both slips are in perspective answers, and both involve the counterpart rather than the protagonist. Most records now avoid this carefully, for example by repeating the name.
3. **Passage over the length cap (2 fixes: 3195/1 at 161 words, 3185/1 at 164 words).** Both are 23-26 rows with an R13 or R15 structure (three beats, or an added complication). The validator should already catch these, so check whether these records passed `--mark`.
4. **Answer imports facts from the row description (1 fix: 3136/1).** The perspective answer says the wife was "tired from her own day" and saw "one more sign she didn't matter". Both come from the description; neither is in the passage.
5. **Earlier arc stage not recognisable (1 fix: 2995/1).** The confrontation scene never shows that the two people are friends or what the betrayal was.
6. **Variants of one row share a plot beat (1 fix: 2914/2 against 2914/1).** In both variants the teased boy hits back by accusing the teaser of copying, and the teasers' names are near-duplicates (Jyoti/Rehana against Nirmala/Rehan).
7. **DISCLOSURE wording (1 fix: 3176/2).** The child reveals being laughed at in school. The parent responds calmly and plans a teacher call the same calendar day, but never says "it's not your fault".

## Rejects

None.

## Safety items (all pass unless listed as a fix)

- **3176/2 (fix):** the "not your fault" line is missing from a disclosure of possible bullying (see pattern 7).
- **Scams** (3266/1, 3265/1, 3269/1, 3272/1, 3273/2): all show pausing, checking through an official number or app, and telling a trusted person. No scam scripts.
- **Radicalisation** (3259/1): slurs stay off the page ("a word for the other lot"). The friend's response keeps the door open. 3252/2 shows the parent staying calm with no ridicule.
- **Addiction** (3177/1 betting, 3185/1 smoking, 3180/2 drinking, 3176/2 gaming): no methods or amounts, and each points to a counsellor, clinic or trusted person. There are no emojis in the passages.
- **Bullying and rumour** (3049/1, 3048/2, 3054/1, 3043/1, 3045/2, 3042/1, 3046/2): each application answer points to a trusted adult or counsellor. In 3054/1 the sister stays with her brother.
- **Revenge fantasies** (3328/1): mild, never carried out, and not usable as instructions. Acceptable.
- **Low mood** (3281/1): the friend offers to go to the counsellor together. This is appropriate.
- **Borderline emoji use (passed):** 3045/2 has 😊 in an answer on a rumour or fake-account recovery row. The stage is healing and the feeling matches, but see suggestion 4.

## Systematic suggestions

1. **The cast generator reuses names, and name pairs, across rows (prompt or cast config; needs user approval).** In this 90-record sample, Devika appears in 4 records. Wasim appears in 3, always paired with Devika (3321/2, 2924/1, 2909/2). Other pairs that recur across different rows: Jatin+Ramesh (3130/1, 3140/1), Uday+Harsha (3022/2, 3046/2), Jyoti+Rehana (3281/1, 2914/2), Himani+Pallavi (3136/1, 3020/2), Farida+Nandini (3191/1, 3221/2), Nitin+Hafsa (3177/1, 3195/1) and Minakshi+Bhavna (3021/2, 3210/1). About 45 names occur in 2 or more records. The cast pool looks small, or it is sampled in fixed co-occurring pairs. This follows the prompt, so no record is marked down for it. It will still teach the model spurious name associations. Suggestion: enlarge the pool and sample names independently per record. Also consider community-consistent casts within one family: in 3195/1, siblings Nitin and Hafsa are plausible but come from the cast pairing, not from a choice.
2. **Formulaic "I'm <Name>" openings.** 8 of 90 passages open with "I'm ...". This is how first-person, observer and diary recipes satisfy the narrator-naming rule. Suggest the prompt offer alternatives: a signature, being addressed by name in dialogue, or a named greeting.
3. **Question templates (prompt).** For dynamics, add to the addendum: "The perspective question must not be answerable by quoting one line of the passage, and it must be about a different person from the mental_state question. In elder-story (R14) records, the application question asks what someone in the story, or the listener in their own situation, could do; not 'what can X learn'."
4. **Emoji on sensitive-adjacent recovery rows (prompt clarification).** State whether rumour, bullying or harassment rows count as "sensitive" for the gentle-emoji-only rule even at a recovery stage. The current wording lists abuse, trauma and discrimination but not bullying.
5. **Validator.** (a) Confirm that the length check runs on every record: two over-length records are in the sample. (b) Add a cheap heuristic that flags any pronoun in an answer when the passage uses no pronoun for any character named in that answer. This would have caught both slips in pattern 2. (c) Add a check for mental_state or perspective answers that repeat a quoted passage sentence of 6 or more words, to flag questions that are only recall.
