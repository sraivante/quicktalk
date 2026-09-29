# Critic pilot summary (129 records)

## Verdicts
| | pass | fix | reject |
|---|---|---|---|
| Overall (129) | 82 | 47 | 0 |
| v1 (39: 33 rows + 6 graph) | 22 | 17 | 0 |
| v2 (90) | 60 | 30 | 0 |

v1 row records alone: 22 pass / 11 fix. All 6 graph clusters: fix.

## Most common issues
1. **Copied description text / labelling (12).** Worst in graph clusters: C0001 ends "four very different stances: trust, affection, suspicion from a teacher, and fear"; C0293 repeats "simple oversight… Rumours multiplied". Row records too: "respect means courtesy and care, not fear" (4786 v1); "She was not being naughty" (4119).
2. **QA types drifting (7).** mental_state and perspective questions turn into literal recall, mostly in v2 toddler planning rows. Examples: "How did Urmila try to open the box?" (5767 v1); "How does Kalyani feel…" used as the perspective question (5767 v3). One application question is also just recall (2946).
3. **Recipe or tag fit (8).** The R13 before/during/after recipe is squeezed into one day or one sitting (4772 v1, 5767 v1, 5478 v3). Some records lose the tag's point of view: in [Thinking] 6281 v1/v3, adults supply the reasoning; in [Receiver] 5459 v1, the teacher's note hides the child.
4. **Grounding and consistency (8).** 5493 v2 switches "Vasudha… his success" against "her". Some answers rely on facts the passage never gives: "her cousin Francis" (the passage only says "anna") and a speaker the answers call "he" though no gender is stated. 5450 v1 says "fractions test" where the class only did fractions. C0397's postmortem blames an untested rollback, but that rollback worked in four minutes.
5. **Length (5, all v1)** and **emoji habit.** 81% of records have exactly one answer emoji, but the rule is that about half should have none. Some emojis are decoration or don't match the feeling (🤔 on advice, 😠 on mild pouting).

## Safety
Nothing reached reject. Minor flags:
- The 5458 variants give numeric symptom rules ("two nights of bad cough, I call", "dizziness lasts more than a day"). A model could repeat these as general medical advice.
- One answer suggests a toddler "pull something to stand on" to reach a shelf (5763 v1).
- A camp leader smiles right after a child pushes another (4774 v1).

Sensitive rows are handled well: neglect, panic (no diagnosis, counsellor involved), silent treatment and prejudice.

Batch-level: family name mixes read as arbitrary (Deepika/Ammi, Jasleen/cousin Rafiq, Vinita/Khala at Eid). Favourite names repeat across rows (Kabir ×4, Arjun ×3, Payal, Himani, Ujjwal). Five monologues open with "you asked on this podcast".

## v2 vs v1
v2 is better on length (0 misses vs 5), question-frame variety ("What did X do well?" 10× in v1, 0× in v2), explicit hedging in observer records, and handling of safety in health rows. Its pass rate is about the same as v1 row records (67%). The new weak spots are QA-type drift, compressed R13 timelines and [Thinking] rows where adults do the thinking.

## Top 3 changes before scaling to ~16k
1. **Automated pre-validator checks:** word range by age; n-gram overlap with row_description (flag any 5+ word match); tag-word and subtype-label leaks; pronoun agreement for each named person; and a batch-level quota for answer emojis (≤50% of records).
2. **Tighten prompt definitions:** mental_state must ask what someone thinks, feels or intends, not what they did. Perspective must centre a person other than the protagonist. R13 beats must span at least two separate days. For [Thinking] rows the protagonist reaches the key insight themselves. Health scenes give no numeric thresholds.
3. **Cast and graph fixes:** generate cast names by coherent family or culture group, with a per-batch reuse cap. In graph mode, forbid closing summary lines, and have the critic check that the relational answer needs at least two rows and that details stay causally consistent.
