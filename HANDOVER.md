# HANDOVER — read this first, update it before you stop

This file keeps consecutive Claude Code sessions in sync. Every session:
1. Reads this file, then README.md and CLAUDE.md.
2. Runs `python3 scripts/status.py` and checks it agrees with **Current state** below (the `.ok` markers are the source of truth, but see the v1/v2 note below).
3. Updates **Current state**, **Next action** and appends to **Session log** after every meaningful step (each validated group of batches, each decision, each blocker), not only at the end. Commit and push this file with the work it describes, so a container reset loses nothing.

---

## Current state  (last updated: 2026-09-29, session 1: fixes applied, v2 check done, critic running)

- **User decision (2026-09-29):** "do as your recommended plan", meaning (1) apply fixes, (2) regenerate 2–3 pilot batches to check them, (3) run the critic, (4) then phase1, (5) judge phase1 before full. The user has granted permission to edit prompts, config and scripts for these fixes.
- **Step 1 done: fixes applied** (commit 9ad8586):
  - `config/names.json` plus a per-record `cast` in the batch JSON (make_batches.py);
  - `config/blocklist.json` (brands and public figures);
  - MASTER rule changes: cast names, no brands or apps, aim for mid-range length, emoji placement inside dialogue, question-frame and opening variety (new rule 14);
  - `validate_jsonl.py`: quote- and plural-tolerant overlap, 5% lower length slack, blocklist, a name may appear in at most 3 records per batch, at most one "do well" question per batch, emoji in at most 2 answers, graph relational answers may use row labels;
  - `commit_rows.py`: the commit trailer now comes from `--trailer` (no hard-coded session).
- **Step 2 done: v2 regenerated** for pilot 06 foundational, 10 culture and 14 planning (commit aa80da1). All pass the new validator. Versus v1: 0 short passages (was 5–8 per batch), 0 "do well" questions (was 2–7), 50–56 distinct names (was 11–18). **Still weak:** in 10 and 14 nearly every record has an answer emoji; the "about half with none" guidance is not enforced by the validator.
- **The other 12 pilot batches are still v1.** Their `.ok` markers came from the OLD validator; under the new validator most fail (short passages, "do well", 6 brand mentions, overused names). They are kept for comparison only and are not exported unless `--include-pilot` is passed. Do not treat them as good data.
- **Step 3 done: critic.**
  - A separate Opus agent reviewed 129 records: 82 pass, 47 fix, 0 reject. Details are in `pilot/critic/` and in `PILOT_REPORT.md` → Update.
  - Its findings led to more prompt rules, a copied-wording check and an answer-emoji quota in the validator, and R13 beats on different days.
  - All 36 flagged v2 and graph records were repaired. Pilot 06, 10, 14 and graph now pass the current validator.
- **Current pilot status:** `status.py` shows 15/15, but only 06, 10, 14 and 15_graph pass the CURRENT validator. The other 11 are v1, marked under old rules, and are for comparison only.
- **How generation is done:** the main session writes records itself (the user prefers no subagents except where needed, e.g. the critic, which must be a separate agent). A scratch helper copies metadata and recipe from the batch JSON, writes the JSONL and warns on the nominal word range; then `validate_jsonl.py --mark`. Scratch files are not committed.
- **Branch:** `claude/intelligent-ride-oxqjfy`. Nothing has been pushed through `commit_rows.py` yet.

## Next action

**Phase1 is running** with the user's choice (option 1, 2026-09-29): Opus for core, foundational, cognitive, dynamics, personality, deception and body; Sonnet for the rest. Calibration (5 batches) is done and committed.

How it runs:
- `batches/queue_phase1.json` holds 183 groups of up to 6 pending batches, each with its stage and model.
- Each generator agent gets ONE group, with the prompt: "Read /home/user/quicktalk/prompts/GENERATOR.md and follow it exactly. Your group is N = <i> (0-based index) in /home/user/quicktalk/batches/queue_phase1.json. Check before starting: your batches are <first> through <last>. If what you read does not match, stop and report." Use the group's `model`. (Always name the first and last batch: one agent once misread the index and redid the previous group.)
- Agents stage their work in `.staging/` (git-ignored) and copy only passing batches, with their `.ok`, into `out/`. Unrepairable batches go into `.staging/blocked.txt`.
- After each agent finishes, run `python3 scripts/sync_out.py --trailer "Co-Authored-By: ...\nClaude-Session: ..."`. It re-validates, commits and pushes; a batch that fails the re-check gets its marker removed and goes back to pending.
- Run 5 agents at a time.

**Queue progress:** core (64/64) and expression (85/85) are complete. Generation groups 0–40 are done. Group 43 is being rerun, and group 183 (the leftovers of groups 41, 42, 44 and 45 after the usage-limit stop) is running. Launch the next generation groups from **46**. **Concurrency: max ~6 agents at once.** 12 parallel agents hit the account usage limit on 2026-09-29, around 15:25 UTC; it reset at 15:40.
**Core critic (80 records):** 58 pass, 22 fix, 0 reject (`pilot/critic/critic_core*`). The main issue was answers using names and genders the passage never gives. This led to a new validator check (a pool name in Q/A must appear in the passage), a last-answer emoji cap, and MASTER rules (a narrator is named in the passage or called "the narrator"; role words or "they" for unnamed roles; family-term glossary; the sensitive emoji rule overrides chat recipes).
**Expression critic (85 records):** 43 pass, 41 fix, 1 reject (2240 v1: a teacher under-responds to a possible abuse disclosure). This led to a MASTER disclosure rule and a validator check for he/she when the passage states no gender.
**Repair pass 2: DONE (all 22 groups).** Was: `batches/queue_repair2.json` holds 22 groups covering 162 batches: 77 fail the current validator, 36 have critic notes, 69 contain possible harm or disclosure scenes (96 records) for safety review, and 48 early situational batches need the row-vs-gender check. All groups run on Opus with REPAIR_AGENT.md. Launch the groups in order; the launched set is noted in the session log.
**For repair pass 2 (known issues, not caught by the validator):** SYSTEMATIC: situational batches generated before the "row description wins over cast" rule (groups 26–33) may change the gender or role that a row states; have a checker compare each record with its row description. Specific: situational v01-01_b0045–b0050 snos 776, 781, 811, 817 (the agent reported a gender or role different from the description); situational v01-01_b0038 sno 693 (check the gender against the row's "her") and v01-01_b0037 sno 681 (a typically male name used for an elder sister: rename); situational v01-01_b0032 sno 631: the friend was made male to fit the cast name, but the row description says "her"; fix by renaming. Also the grounding lines may state genders the passage doesn't (check in the critic).
**Repair pass 1: DONE.** All 8 groups finished; about 290 records fixed, mostly by naming narrators in the passage, neutral pronouns and last-answer emojis. All 22 core critic notes are fixed. Full re-check: all 111 finished batches pass the current validator. New failures found by sync_out go to `.staging/needs_repair/`; collect them into a `queue_repair2.json` when there are enough.
**Flag for the critic sample** (sensitive rows the agents reported): expression 2216, 2219, 2220, 2235 v1, 2240 v1 (unwanted or unsafe touch, disclosures, bruise); core 225 (blackmail/grooming), 232 (controlling relationship), 233 (grief), 235 (friend in distress), 141, 144, 150 (mortality/grief/child labour/device defect), 174, 191, 205, 209 (unsafe touch, online pressure, puberty, abuse reporting), 231, 252 (sexual health), 258 (addiction).
**Fixes made during the run:**
- per-agent scratch folders, and no direct writes to `out/` (GENERATOR.md);
- cast names capped at 2 per batch; the phase1 batch files were rebuilt with the same rows and plans (make_batches.py).
**To resume in a new session:** `python3 scripts/status.py` shows what is done. Before relaunching a group, check which of its batches already have `.ok` and skip them; the agent's step 1 simply redoes any batch without `.ok`.

After phase1: critic on about 5% per stage (a separate agent), then `export_dataset.py`, then ask the user before `full`.

Reference commands:
```
python3 scripts/status.py                  # progress
python3 scripts/status.py next 5 --phase phase1
python3 scripts/validate_jsonl.py <batch_json> <out.jsonl> --mark
python3 scripts/commit_rows.py --repo . --branch claude/intelligent-ride-oxqjfy --trailer "Co-Authored-By: ...\nClaude-Session: ..."
python3 scripts/export_dataset.py
```

## Open decisions / questions for the user

1. **Commit target for generated rows.** Run `commit_rows.py` with `--branch claude/intelligent-ride-oxqjfy` unless the user approves `main`. Pilot rows are not committed unless the user asks (`--include-pilot`).
2. **Pack tooling lives in the data repo.** `commit_rows.py --repo .` writes `data/rows/*.jsonl` next to the framework CSV. There is no clash, but confirm the user is happy with this layout before large commits.
3. **How to generate phase1 at scale** (subagents in parallel vs. many in-session runs): the user's preference was "no subagents unless it's a must". At ~1,050 batches it is effectively a must; confirm with the user.

## Environment notes

- Python 3.11. `validate_jsonl.py`, `status.py`, `make_batches.py`, `export_dataset.py` and `commit_rows.py` use only the stdlib.
- `build_kg.py` needs `networkx` + `scikit-learn` (not installed). It is only needed if the CSV changes; `kg/` ships pre-built.
- The cloud container is ephemeral: commit outputs, `.ok` markers and this file after each validated group.
- Model guidance (README): Sonnet for bulk, tier C and repairs; Opus for tier A, the sensitive stages and the critic. The generator and the critic must be different agents.

## Pack map (quick reference)

| Path | Role |
|---|---|
| `README.md` | Plan: 15 stages, tiers A/B/C/G, phases pilot → phase1 (~16.2k records) → full (~46.7k) |
| `RUN_IN_CLAUDE_CODE.md` | Orchestrator loop for subagent generation |
| `CLAUDE.md` | Project rules (safety, no hand-edits of batches/out, never fabricate/pad) |
| `PILOT_REPORT.md` | Pilot findings and recommendations |
| `data/human_development_framework_v9.csv` | 7,689 rows, ages 1–3 … 23–26, 57 topics |
| `kg/` | Pre-built knowledge graph (10,032 nodes, 54,893 edges, 940 clusters) |
| `config/variants.json`, `config/recipes.json` | Variant counts per tier/phase; recipes R1–R15, twists T1–T6 |
| `config/names.json`, `config/blocklist.json` | Name pool for casts; banned brands and public figures |
| `prompts/training_data_prompt.md` → `prompts/MASTER.txt` | MASTER system prompt, BATCH template, stage addenda, CRITIC, REPAIR |
| `scripts/` | make_batches, validate_jsonl, status, export_dataset, commit_rows, build_kg |
| `pilot/batches/`, `pilot/out/` | Pilot inputs and outputs (06, 10, 14 are v2; the rest are v1) |
| `pilot/critic/` | Critic sample, verdicts and summary |

## Session log (append newest at the bottom)

- **2026-09-29, session 1:** The repo was empty. Unpacked `human_dev_pack.zip` into the repo root, read the docs and scripts, created this HANDOVER.md and pointed CLAUDE.md at it.
- **Session 1 (cont.):** The user said to start the pilot without subagents. Generated and validated all 15 pilot batches in-session (426 records). First try: 132/146 units passed; all failures were mechanical and fixed in one repair.
- **Session 1 (cont.):** Wrote PILOT_REPORT.md: repetitive question templates, repeated names, short 13+ passages, formulaic emojis, and brand or real-person slips the validator cannot see.
- **Session 1 (cont.):** The user approved the full plan. Applied the fixes, rebuilt the pilot batches with casts, regenerated 06, 10 and 14 as v2 (all pass, clear gains), and launched the critic on a 129-record sample.
- **Session 1 (cont.):** The critic finished (82/47/0). Applied its prompt and validator fixes and repaired the flagged v2 and graph records; the four batches pass. Waiting on the user about subagents for phase1.
- **Session 1 (cont.):** The user approved subagents for phase1. Built the phase1 batches (1,050 / 16,200) and launched a 5-batch calibration round (3 core on Opus, 2 situational on Sonnet).
- **Session 1 (cont.):** The user chose option 1 (Opus + Sonnet). Wrote GENERATOR.md, queue_phase1.json and sync_out.py; launched round 1 (groups 0–4, core).
- **Session 1 (cont.):** Expression critic found 1 reject and 4 weak disclosure responses. Added the MASTER disclosure rule and a validator gender check. Built repair pass 2 (22 groups, 162 batches); launched repair2 groups 0, 4, 6 and 7. Hold repair2 groups 19–21 until generation groups 39–42 (situational b0081–b0104) have finished, to avoid overwriting their files.
- **Session 1 (cont.):** All 12 agents stopped at the account usage limit. After the reset: synced (258/1050 batches), queued leftover group 183, reran group 43, and reran repair2 groups 7, 1, 2 and 3. Repair2 groups 0 and 6 are done. Still to run: repair2 groups 4, 5, 8, 9, 10–18, then 19–21 (after group 183 and group 43 finish), then generation from group 46.
- **Session 1 (cont.):** Repair2 groups 0–8 are done (group 8 fixed about 48 pronoun issues in b0032–b0045 plus the b0039 critic notes; 2419v1 disclosure now reaches an adult the same day). Running: repair2 groups 9, 10, 11 and 12, generation group 43 (rerun) and group 183. Next: repair2 groups 13–18, then 19–21, then generation from group 46. Minor items for the critic: 2409v1 (b0035) has 🙂 on a "worried" answer, and 2422v2 (b0037) has 🙂 on a teacher's note about stammer teasing.
- **Session 1 (cont.):** Generation group 43 (rerun, situational b0105–b0110) is done and committed. Launched repair2 group 13. Row to review: S1405 (b0109, "Parents × Protectiveness [Actor]", ages 18–22) describes a parent worried about their child; the generator wrote a 22-year-old father, so check the row's age or subtype. Note: commit d2e1d40 has a placeholder trailer "x" (pushed; not rewritten).
- **Session 1 (cont.):** Leftover group 183 is done and committed (situational b0098, b0104, b0115, b0116, b0120, b0121, b0122). All situational batches up to b0122 now exist, so repair2 groups 19–21 are no longer blocked. Launched repair2 group 14. Running: repair2 groups 9–14. Next: repair2 groups 15–21, then generation from group 46.
- **Session 1 (cont.):** Repair2 group 9 is done (expression b0046–b0053; about 76 records fixed, mostly pronouns). Safety: 2514v2 now reaches the club's safeguarding officer the same day; 2553v1 and v2 now reach an adult the same day. Minor items for the critic: in 2549v1 the narrator "Thomas" is named only in the signature; 2588v1 is missing a closing quotation mark. Launched repair2 group 15. Running: 10–15.
- **Session 1 (cont.):** Repair2 groups 10, 11, 12 and 13 are done and committed. Expression repair2 is complete (groups 0–12). Safety: 2800v1 now meets the disclosure rule. Group 13: 402 now reads "her husband Thomas" to match the row. Running: repair2 groups 14–19. Next: repair2 groups 20 and 21, then generation from group 46, then a critic on ~5% of situational.
- **Session 1 (cont.):** Repair2 group 14 is done (situational b0010–b0017; ROW CHECK fixed many Parent/Sibling roles and 3 child genders: 439 Rituraj, 465 Hrishita, 473 Jyoti). For the critic: 426 (b0011) is a neglected-toddler scene where no one outside the family is told. Launched repair2 group 20. Running: 15–20. Next: repair2 group 21 (b0094), then generation from group 46.
- **Session 1 (cont.):** Repair2 group 15 is done (situational b0018–b0025; 24 records fixed, mostly by stating Parent/Sibling roles and removing unstated pronouns). All 22 repair2 groups are now launched; the last, group 21 (b0094), is running. Running: repair2 groups 16–21. Next: generation from queue_phase1 group 46 as slots free, then a critic on ~5% of situational.
- **Session 1 (cont.):** Repair2 group 21 is done (b0094). Generation resumed: phase1 group 46 (situational b0123–b0128, Sonnet) launched. Running: repair2 groups 16–20 and gen group 46. **Next gen group: 47.**
- **Session 1 (cont.):** Repair2 group 16 is done (b0026–b0033). Safety: 582, 586, 590, 591 and 641 now meet the disclosure rule. Row fixes: 631 (friends renamed Sumita and Aarti), 633, 616 and 629. Launched gen group 47. Running: repair2 groups 17–20 and gen groups 46–47. **Next gen group: 48.** Validator note (not changed): a float rounding issue makes the upper word limit for ages 4–6 effectively 114, not 115 (100*1.15 comes out just under 115). It could be fixed with round() if the user approves.
- **Session 1 (cont.):** Repair2 groups 17 and 18 are done (b0034–b0049). Known row issues 631, 681, 693, 776 and 781 are fixed, plus more renames to match rows (665 Ishan, 692 Kalyan, 792 Imrana, 797 Bhairavi, 766 grandfather). Safety: 702, 706 and 742 now meet the disclosure rule. Rows 811 and 817 are actually in b0050 (group 19); the group 19 agent was told to handle them. Launched gen groups 48 and 49. Running: repair2 groups 19 and 20, gen groups 46–49. **Next gen group: 50.**
- **Session 1 (cont.):** Repair2 group 19 is done (b0050–b0069, 8 batches). 811 matched its row already; 817, 827, 944 and 821 were renamed or cued to match their rows. Safety: 812 (a teacher hitting in a story → standing outside the class), 870 and 967 now meet the disclosure rule. Launched gen group 50. Running: repair2 group 20, gen groups 46–50. **Next gen group: 51.**
- **Session 1 (cont.):** **Repair pass 2 is complete** (all 22 groups, 162 batches). Group 20 fixed 1082 and 1123 (disclosure now reaches an adult the same day) and many narrator pronouns. 272 phase1 batches are validated and committed. Launched gen group 51. Running: gen groups 46–51 (situational b0123–b0158). **Next gen group: 52.** When situational is finished (b0175), run a critic on ~5% of situational, with a separate Opus agent, including grounding-gender checks.
- **Session 1 (cont.):** Gen groups 46 and 48 are done (b0123–b0128, b0135–b0140). Launched 52 and 53. Running: gen 47, 49, 50, 51, 52, 53. **Next gen group: 54** (situational b0171–b0175, the last situational batches), then 55 onward (04_dynamics, Opus).
- **Session 1 (cont.):** Gen group 51 is done (b0153–b0158). Launched group 54 (b0171–b0175, the last situational batches). Running: gen 47, 49, 50, 52, 53, 54. **Next gen group: 55** (04_dynamics, Opus).
- **Session 1 (cont.):** Gen groups 47 and 49 are done (b0129–b0134, b0141–b0146; 1607 renamed Tanmay to match the row). Dynamics started: launched 55 and 56 (04_dynamics b0001–b0012, Opus). Running: gen 50, 52, 53, 54, 55, 56. **Next gen group: 57.** Once 50, 52, 53 and 54 finish, situational is complete; then run the situational critic (~5%).
- **Session 1 (cont.):** Gen group 50 is done (b0147–b0152). Launched 57 (dynamics b0013–b0018). Running: gen 52, 53, 54, 55, 56, 57. **Next gen group: 58.**
- **Session 1 (cont.):** Gen group 54 is done (b0171–b0175). Launched 58 (dynamics b0019–b0024). Running: gen 52, 53, 55, 56, 57, 58. **Next gen group: 59.**
- **Session 1 (cont.):** **Situational is complete** (175/175 batches, 1,744 records). The situational critic has started: `pilot/critic/sample_situational.jsonl` (180 records, a third from sensitive-looking rows, seed 303, built by `.staging/critic/sample.py`) is split into two Opus critic agents. Outputs go to `pilot/critic/critic_situational_part{0,1}.jsonl` and `_summary.md`. When they finish, build `batches/queue_repair3.json` from the fix and reject notes. Running: gen 55–58 (dynamics) and critics part 0 and 1. **Next gen group: 59** (dynamics b0025–b0030). Critic note: 1951 (b0164), where an adult's letter about unwelcome touching goes to the police the next morning; check.
- **Session 1 (cont.):** **Situational critic done:** 123 pass, 57 fix, 0 reject (part0 70/21/0, part1 53/36/0). Top patterns:
  1. he/she for named first-person narrators and third parties the passage never genders (32 records);
  2. perspective questions centring the protagonist (7);
  3. R2 recipe clash for non-family counterparts, and R7 without a rural setting;
  4. same-day adult response missing on the page after a child tells a parent (873, 1210);
  5. 1208: an online contact asked for secrecy, yet the meeting still goes ahead;
  6. emoji mismatches (326, 398, 841, 936, 1224, 2033);
  7. cast names repeat as fixed pairs.
  **Root cause of the pairs:** `cast_for` in make_batches.py steps by 7919, so each first name always gets the same partner.
  **Applied (prompt/config, under the user's earlier approval):**
  - rule 2: a first-person narrator is ungendered unless the passage states it;
  - rule 8: show the adult's same-day response on the page; secrecy from an online contact means end the contact and tell an adult;
  - R2 reworded.
  NOT yet regenerated into MASTER.txt.
  **Blocked (a permission check denied the edit, needs the user's OK):**
  - a validator WARN for he/she in first-person records;
  - a per-index hash in `cast_for` to break the fixed pairs;
  - then rerunning `make_batches.py --phase phase1` to rebuild MASTER.txt and the casts.
  Until then, the launch prompts carry the narrator, perspective, R2 and disclosure guidance.
  **Next:** `batches/queue_repair3.json` is built (6 groups, 46 batches, 57 notes, Opus). Launched repair3 group 0. Remaining: repair3 groups 1–5, and gen from 60.
- **Session 1 (cont.):** Gen group 57 is done (dynamics b0013–b0018). Launched repair3 groups 0 and 1. Running: gen 55, 56, 58, 59 and repair3 0 and 1. **Next:** repair3 groups 2–5, and gen group 60 (dynamics b0031–b0036).
- **Session 1 (cont.):** Repair3 group 0 is done (8 batches; 326, 398, 449, 480, 496, 640, 641, 776 and 841 per the critic, plus pronoun fixes). Launched repair3 group 2. Running: gen 55, 56, 58, 59 and repair3 1 and 2. Waiting on the user's OK for the blocked script edits (see above).
- **Session 1 (cont.):** Gen group 55 is done (dynamics b0001–b0006; many cast renames to match the rows). Launched gen 60. Running: gen 56, 58, 59, 60 and repair3 1 and 2. **Next:** repair3 groups 3–5, gen 61.
- **Session 1 (cont.):** Repair3 group 2 is done (b0078–b0099; 30 records). Safety: 1208 now ends the contact and blocks/reports with the mother, no meeting; 1210 shows the mother's same-day response. The narrator in 1210 was renamed Sumit → Nakul (the critic flagged Sumit as overused); the user may want to revert. Even after repair2, many narrator pronoun slips remained in these batches, so the hand checks miss some; a validator WARN would help (awaiting approval). Launched repair3 group 3.
- **Session 1 (cont.):** Repair3 group 1 is done (b0054–b0074; 35 records).
  - 851: classmate made male per the row.
  - 873: mother's same-day response added.
  - 874: small-town detail added.
  - 987 and 1050 (R10 letters): the agent added a short same-day adult reply; review whether a second voice fits R10.
  - CSV issue for the user: sno 874's subtopic ("Chatting with an online stranger") does not match its description (a classmate's group-chat post).
  Launched repair3 group 4. Running: gen 56, 58, 59, 60 and repair3 3 and 4. **Next:** repair3 group 5, gen 61.
- **Session 1 (cont.):** Repair3 groups 3 and 4 are done (b0101–b0148). 1636's closing now reads the policy and books the lawyer call first. 1684 has a wedding-ring cue. 1701 has an indebtedness cue. The critic's cast-pair notes (1348, 1472, 1701, 1714) were not applied (they keep the row cast); they depend on the cast-picker fix awaiting approval. Added repair3 **group 6** (1682, 1683: "marriage" without a cue; 1522, 1791: hanging signatures) and launched it with group 5. Running: gen 56, 58, 59, 60 and repair3 5 and 6. **Next:** gen 61.
- **Session 1 (cont.):** Gen group 56 is done (dynamics b0007–b0012). S3025 has a teen disclosure handled per the rule. Launched gen 61. Running: gen 58, 59, 60, 61 and repair3 5 and 6. **Next gen group: 62.**
- **Session 1 (cont.):** Repair3 group 6 is done (1522, 1682, 1683, 1791). Launched gen 62. Running: gen 58, 59, 60, 61, 62 and repair3 5 (the last repair3 group). **Next gen group: 63.**
- **Session 1 (cont.):** **Repair pass 3 is complete** (all 7 groups; every situational critic note is addressed). 2020 now says "not your fault" per its row, and 2040 had a truncated question fixed. For a later critic: 2036 (perspective centres the mentee while the mentor narrates). 349 phase1 batches are validated and committed (core 64, expression 85, situational 175, dynamics ~25). Launched gen 63. Running: gen 58–63 (dynamics). **Next gen group: 64.** Still awaiting the user's OK for the validator WARN, the cast-picker fix and the make_batches rerun.
- **Session 1 (cont.):** Correction: dynamics is 45 batches (queue entries 55–62; entry 62 = b0043–b0045). Entry 63 onward is **05_cognitive** (Opus). The gen 63 agent is now running cognitive b0001–b0006. **Next gen group: 64** (cognitive b0007–b0012). After dynamics finishes (58–62), run the dynamics critic (~90 records).
- **Session 1 (cont.):** Gen group 58 is done (dynamics b0019–b0024). 3099 v1: an online secrecy request is handled per the rule. Launched gen 64 (cognitive b0007–b0012). Running: gen 59–64. **Next gen group: 65.**
- **Session 1 (cont.):** Gen group 62 is done (dynamics b0043–b0045, the end of dynamics). Launched gen 65 (cognitive b0013–b0018). Running: gen 59, 60, 61 (dynamics) and 63, 64, 65 (cognitive). **Next gen group: 66.** Run the dynamics critic when 59–61 finish.
- **Session 1 (cont.):** Gen group 59 is done (dynamics b0025–b0030). Launched gen 66 (cognitive b0019–b0024). Running: gen 60, 61 (the last dynamics) and 63–66 (cognitive). **Next gen group: 67.**
- **Session 1 (cont.):** Gen group 60 is done (dynamics b0031–b0036; high-control, radicalisation and scam rows have no emojis and generic villains; secrecy requests in 3245 and 3265 are handled). Launched gen 67 (cognitive b0025–b0030). Running: gen 61 (the last dynamics) and 63–67. **Next gen group: 68.** Dynamics critic after 61.
- **Session 1 (cont.):** **Dynamics is complete** (45/45 batches, 882 records). Dynamics critic launched on `pilot/critic/sample_dynamics.jsonl` (90 records, seed 404); output goes to `pilot/critic/critic_dynamics.jsonl` and `_summary.md`. Then build `queue_repair4.json`. Running: gen 63–67 (cognitive) and the dynamics critic. **Next gen group: 68.**
- **Session 1 (cont.):** **Dynamics critic: 78 pass, 12 fix, 0 reject.** Patterns: weak perspective/application question types (5), unstated pronouns (2), 2 passages slightly over the length (within validator slack), 3176/2 missing "not your fault". Cast name pairs repeat across rows again (awaiting the cast-picker fix approval). `batches/queue_repair4.json` (1 group, 12 batches, 12 notes) was launched. Running: gen 63–67 and repair4. **Next gen group: 68.**
- **Session 1 (cont.):** **Repair4 is done** (12 dynamics batches; all 12 critic notes fixed, and 3176/2 now says "not your fault" with a same-day response). The sweep still found 17 more unstated-pronoun slips in 240 records, so generator hand checks miss about 7%; this strengthens the case for the validator WARN (awaiting approval). Launched gen 68 (cognitive b0031–b0036), whose prompt now asks for a final scripted pronoun scan. Running: gen 63–68. **Next gen group: 69.**
