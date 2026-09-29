# Pilot quality report (v9 pack, pilot phase)

Date: 2026-09-29 · Branch: `claude/intelligent-ride-oxqjfy` · Status: **pilot complete, 15/15 batches validated, 426/426 records. Not scaled.**

## How the pilot was generated
- At the user's request, the **main session wrote every record itself** (no subagents). This differs from the pack default (Sonnet generator subagents), so every record comes from one author in one long context.
- Per batch: the records were written into a scratch Python file. A helper copied `age/topic/subtopic/subtype/recipe` from the batch JSON, wrote the JSONL, and then `validate_jsonl.py --mark` ran. Each failure got one repair round, as the pack allows. No batch was blocked.
- **No CRITIC pass has been run yet.** The pack requires the critic to be a different agent from the generator (see "Next steps").

## First-try pass rate per stage
| # | Stage | Rows passed first try | Failure reasons (all fixed in 1 repair) |
|---|---|---|---|
| 01 | core | 10/10 | — |
| 02 | expression | 10/10 | — |
| 03 | situational | 8/10 | literal-answer word overlap (a word in single quotes; plural vs singular) |
| 04 | dynamics | 10/10 | — |
| 05 | cognitive | 8/10 | literal overlap (plural); one chat passage at 72 words |
| 06 | foundational | 10/10 | — |
| 07 | personality | 10/10 | — |
| 08 | group | 9/10 | one passage at 74 words |
| 09 | deception | 10/10 | — |
| 10 | culture | 7/10 | three 13+ passages at 69–75 words |
| 11 | body | 8/10 | two 13+ passages at 69–73 words |
| 12 | execution | 10/10 | — |
| 13 | wellbeing | 9/10 | two 23–26 passages at 74–76 words |
| 14 | planning | 9/10 | literal overlap ("four times" vs "fourth time") |
| 15 | graph | 4/6 clusters | relational answers used abstract words not present in the passage (<40% overlap) |

**Total: 132/146 units (140 rows + 6 clusters) passed first try (90%).** Every failure was mechanical: length or word overlap. None was about safety or schema.

## What I noticed (honest read-through of my own output)
**Strengths**
- **Variant diversity is good.** The highest word-overlap between two variants of the same row is 0.13–0.30 per stage; the validator threshold is 0.55. Recipes (R1–R15) produce genuinely different forms and settings.
- **Tag POV was followed.** [Receiver], [Observer] and [Response] rows keep the right viewpoint. Expression rows always name one alternative reading in the mental_state answer.
- **Safety held in the sensitive rows.** These were neglect (S426), a heavy confidence involving drinking and domestic harm (S4625), fear-driven lies (S4594) and panic (C0573). All stay focused on recognition, a trusted adult and professional help, with no methods, dosing or diagnoses.
- **Emoji caps held.** Sensitive stages (personality, deception, body) use almost none: 1–3 answer emojis per batch. Other stages average about one emoji per record, almost always in an answer.

**Weaknesses (these matter for a small model)**
1. **Question templates are monotonous.** 126 of 420 application questions (30%) are some form of "What did X do well?". Perspective questions mostly start "How might the/his/her…". A small model will over-learn these frames. *Suggested fix (needs your approval, since it changes prompts):* add a rotating list of question forms to MASTER, or per-recipe question styles.
2. **Names repeat.** Across 420 records: Kabir 38, Arjun 29, Rohan 25, Riya 22, Meera 18. MASTER asks for varied names, but a single generator falls into habits. *Suggested fix:* a per-batch name pool in `make_batches.py` (seeded), or a validator warning for names that appear in more than 3% of records.
3. **Older-age passages run short.** 83 of 420 row records (20%) are below the nominal minimum. Almost all are 13+ passages at 77–89 words; they pass only because the validator allows 15% slack. Chat recipes (R6) and letters are the worst. *Suggested fix:* tell the generator to aim for 100–140 words at 13+, or tighten the validator slack to 5%.
4. **Emoji use is formulaic.** About one emoji per record, nearly always tacked onto the last clause of an answer. It is rarely in dialogue, where MASTER says real people use them. Consider requiring the emoji to live inside dialogue or chat lines.
5. **Opening lines repeat.** 60 passages start "In a…" and 29 start "At the…". This is minor, but openings could vary more.
6. **I caught two rule breaks in self-review.** Real cricketers named on trading cards (S2974) and a brand (a professional-network site, S6674) were both replaced before validation. The validator cannot catch these; a critic pass or a simple blocklist check would.

**Validator observations (for tuning `validate_jsonl.py`, with your approval)**
- The literal-answer check tokenises on `[a-z']+`. A word in single quotes (`'cringe`) and plural/singular differences fail even when the answer is correct. Light stemming (strip a trailing `s`, strip quotes) would remove about 5 false failures per 150 rows.
- For graph clusters, the relational-answer overlap check (≥40%) works against the stage instruction to "name the concept". Concept words are often not in the passage, so the generator has to plant them there.
- Length slack (±15%) lets many short 13+ passages through (see point 3).

## Usage and scale
- Pro-limit usage cannot be measured from inside this session. Generation used roughly 10–15k output tokens per 30-record batch.
- Writing the 15 pilot batches sequentially took most of one long session. **Phase1 is about 1,050 batches.** Generating that one batch at a time in the main session is impractical. For phase1 you will need parallel subagents (the pack's design), the API, or many sessions spread over days.

## Recommended next steps (your call)
1. **Run the CRITIC** on a sample (the README says all pilot batches) with a separate agent, as the pack's rules require. This is the one place a subagent is needed.
2. **Approve or reject prompt changes 1–4 above.** CLAUDE.md does not allow editing prompts or config without your approval. If approved, rerun `make_batches.py --phase pilot`, regenerate 2–3 batches, and compare.
3. **Validator tweaks** (stemming, slack), only with your approval.
4. Then decide on **phase1**, and whether validated rows should be committed per row with `commit_rows.py --repo . --branch claude/intelligent-ride-oxqjfy` (pilot rows only with `--include-pilot`).

---

## Update: fixes, v2 regeneration and critic pass (2026-09-29)

**Fixes applied** (user approved): name casts per record (`config/names.json`), a brand/public-figure blocklist (`config/blocklist.json`), new MASTER rules (question-frame and opening variety, mid-range length, emojis inside dialogue, no brands), a stricter `validate_jsonl.py`, and a `--trailer` option in `commit_rows.py`.

**v2 regeneration** of 06 foundational, 10 culture and 14 planning:

| Per batch | v1 | v2 |
|---|---|---|
| Passages under the nominal length | 5–8 | 0 |
| "What did X do well?" questions | 2–7 | 0 |
| Distinct names | 11–18 | 50–56 |
| Most-repeated name (records) | 3–5 | 2–3 |

**Critic pass**: run by a separate Opus agent on 129 records (all 90 v2 records, the 6 graph clusters and 33 v1 records). Files: `pilot/critic/critic_pilot.jsonl` and `critic_summary.md`.

| | pass | fix | reject |
|---|---|---|---|
| Overall | 82 | 47 | 0 |
| v1 (33 rows + 6 graph) | 22 | 17 | 0 |
| v2 (90) | 60 | 30 | 0 |

Critic findings:
- **Copied row wording and closing "labelling" lines.** This was worst in the graph clusters.
- **Question types drifting into recall**, mostly in toddler planning rows.
- **Before/during/after (R13) squeezed into one day.**
- **[Thinking] rows where an adult supplies the reasoning.**
- **Grounding slips:** a pronoun switch, and answers adding relations the passage never states.
- **Answer emojis in 81% of records.**
- **Repeated "you asked on this podcast" opener.**
- **Minor safety issues:** numeric symptom thresholds, an answer suggesting a toddler climb, and a leader smiling right after a push.
- **No rejects.** The sensitive rows were handled well.

**Acted on:**
- **Prompt:**
  - mental_state questions must ask about the inner state;
  - perspective questions must centre someone other than the protagonist;
  - R13 beats fall on different days (also written into `config/recipes.json`);
  - in [Thinking] rows the protagonist reaches the insight;
  - [Receiver] rows keep the affected person visible;
  - answers add no unstated relations, and names, pronouns and family terms stay consistent;
  - no numeric health thresholds;
  - graph passages have no closing summary line and stay causally consistent;
  - varied monologue openers.
- **Validator:**
  - fails any 5-word run copied from the row description (text the description quotes as speech is exempt);
  - fails a batch where more than 60% of records carry an answer emoji;
  - warns (does not fail) when a mental_state question looks like recall.
- **Repair round:** fixed all 36 flagged v2 and graph records, plus the new validator failures. All four batches (06, 10, 14, graph) now pass. Each batch has answer emojis in 15 of 30 records.

**Not acted on:**
- **Coherent-family name groups.** They would mean tagging names by religion or region, which risks stereotyping. The prompt instead asks for consistent, natural family terms within a household.
- **The 12 remaining v1 pilot batches.** They are kept for comparison only.

**Still limited:** the validator cannot check pronoun agreement or real recipe adherence. That depends on the generator's care and the critic sample, so run the critic on about 5% per stage during phase1.
