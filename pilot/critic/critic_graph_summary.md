# Critic summary: graph stage (fin_graph, cluster mode)

Input: `.staging/critic/fin_graph` (50 cluster records, 50 batches g_b0007 to g_b0155; no items flagged `forced`).
Output: `pilot/critic/critic_graph.jsonl` (one line per cluster, keyed by `cluster_id` + `batch`).

## Counts

| Verdict | Count |
|---|---|
| pass | 41 (4 of them carry a note about non-cast names only) |
| fix | 8 |
| reject | 1 |

By cluster type: approach_comparison 15 (14 pass, 1 fix), contrast 14 (13 pass, 1 fix), progression 9 (5 pass, 4 fix), concept_link 6 (5 pass, 1 reject), view_pair 5 (4 pass, 1 fix), sequence 1 (fix).

## Weight rule (c): relation shown and every row on the page

- 49 of 50 passages show every row in `rows_used` and a real relation. Contrast, view_pair and approach_comparison records are strong: most show one household, office or event, and the relational answer really needs two rows.
- **C0830: reject (the known suspect is confirmed).** Row 3896 (Cognitive Machinery / *Splitting*: a friend who is all good, then all bad) is paired with row 5828 (Planning / *Tidying a room*: bargaining to divide chores). The only link is the word "split". The passage puts two unrelated scenes side by side, and the relational answer and grounding openly treat it as a pun ("two different kinds of splitting"). It teaches a false relation. The same record also flips a cast name's gender (Chaitanya, usually male, is the older sister).
- **C0628: fix, thin link.** Bossy commands at ten and a risky peer recommendation at fifteen share only the subtopic label "Guidance and direction". The passage works, but the relational answer strains to connect them.
- **C0761: fix.** The age-nine marker goes to Payal, who only holds the ladder. The child who shows the optimism bias is her unnamed little brother, whose age is not given.
- These concept_link pairs were checked and are genuine: C0926 and C0853 (avoidance → avoidance of a crush or essay), C0893 and C0883 (procrastination), C0886 (imposter feelings).

## Rules (a) and (b): pronouns and cast-name gender

- Cast gender flips: **C0235** (Kamal used as a mother; in C0820 Kamal is a Nana) and **C0830** (Chaitanya as a sister).
- Pronoun and relationship problems in answers or grounding: **C0297** (answer calls Varun a "friend", which the passage never says), **C0761** (unnamed cousin given "she", and the referent is ambiguous), **C0226** (Binita's parent role is never stated, but the rows are Parent rows).
- Generators handled ungendered protagonists well. Gurpreet (C0893), Jatin (C0628), Vikas (C0637) and Amandeep (C0438) keep no pronouns throughout. The only cost is one ungrammatical literal question in C0637 ("do with the hands").

## Recurring patterns (ranked)

1. **Cast gender vs row gender conflict (6 records: C0488, C0561, C0853, C0519, C0543, C0235).** Rows often fix a gender ("he", "her"), but the cast sampler hands out names without regard to it. Generators either invent non-cast names (Rohan, Dev, Arjun, Darshan, Anaya; acceptable, noted as pass) or use a cast name against its usual gender (C0235 fix, C0830 reject).
2. **Progression and concept_link clusters built on shared labels rather than shared meaning (C0830, C0628, C0761).** Progression has the highest fix rate (4 of 9), and the only reject is a concept_link. The contrast, view_pair and approach clusters are almost clean.
3. **Facts or labels in answers and grounding that the passage doesn't state (C0297, C0726, C0226).** C0726's grounding calls Wasim "autistic" although the passage never says so, which reads as a narrator diagnosis under rule (h).
4. **Small prose defects from rewriting (C0519, C0637):** garbled sentences, or a story beat left unresolved.

## Rejects and safety items

- **Reject: C0830 (g_b0139).** Word-coincidence cluster plus a cast gender flip. Drop it from graph mining, or SKIP it.
- **Safety (d): C0628 (g_b0105).** A secret balcony-jump challenge is reported to a teacher, but the teacher's only same-day response on the page is thanks. Escalation comes "that same week" and no protective step is shown. It needs a same-day protective response (tell the counsellor and parents, warn the school).
- **Safety (h): C0726 (g_b0121).** The grounding applies a diagnostic label ("autistic") that the passage never states.
- No emoji problems: the sensitive records (C0056 assault aftermath, C0231 grief, C0637 vigil) have none, and the gentle 🤍 in C0543 and C0560 answers is within the rules. No brands or public figures appear. The money records (C0426, C0543, C0222) describe behaviour and recognition, not advice, and C0426 points to a qualified adviser. The online-stranger and night-job records (C0222, C0462) show an adult stepping in.

## Systematic suggestions (for user approval; nothing was edited)

1. **Cluster mining:** for `concept_link` and `progression`, require a shared concept, not a shared token or subtopic label. Add a denylist or a check for polysemous links (e.g. "splitting", "bargaining"), or require an explicit mined relation beyond the subtopic name. Re-audit other concept_link clusters whose two rows come from different topics and share only a keyword.
2. **Cast sampler:** when a row's description fixes a gender ("he"/"his", "she"/"her"), draw the cast name for that slot from matching-gender names. That would remove most of pattern 1.
3. **Validator (cheap check):** flag a record when a cast name from a known-gender list appears alongside an opposite kin or pronoun term ("her mother Kamal", "Chaitanya ... she"), and flag diagnostic words (autistic, ADHD, depressed) that appear in grounding or answers but not in the passage.
4. **Prompt, ADDENDUM graph:** add "if a child reports a dangerous dare or challenge, the adult's protective step happens the same day, on the page" (the MASTER rule exists, but C0628 missed it). For progression, add "each age marker belongs to the person showing that row's behaviour".
