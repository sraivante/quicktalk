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
- Each generator agent gets ONE group, with the prompt: "Read /home/user/quicktalk/prompts/GENERATOR.md and follow it exactly. Your group is N = <i> in /home/user/quicktalk/batches/queue_phase1.json." Use the group's `model`.
- Agents stage their work in `.staging/` (git-ignored) and copy only passing batches, with their `.ok`, into `out/`. Unrepairable batches go into `.staging/blocked.txt`.
- After each agent finishes, run `python3 scripts/sync_out.py --trailer "Co-Authored-By: ...\nClaude-Session: ..."`. It re-validates, commits and pushes; a batch that fails the re-check gets its marker removed and goes back to pending.
- Run 5 agents at a time.

**Queue progress:** groups 0–8 and 10–12 are done (all pass, 0 blocked; core is complete except group 9). Groups 9, 13, 14, 15 and 16 have been launched (running or unsynced). Launch the next groups in order from **17**. Observed: Sonnet expression batches almost always fail the answer-emoji quota on the first try, and one repair fixes it.
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
