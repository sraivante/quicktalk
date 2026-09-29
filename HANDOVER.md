# HANDOVER — read this first, update it before you stop

This file keeps consecutive Claude Code sessions in sync. Every session:
1. Reads this file, then README.md and CLAUDE.md.
2. Runs `python3 scripts/status.py` and checks it agrees with **Current state** below (the `.ok` markers are the source of truth; if they disagree, trust the markers and fix this file).
3. Updates **Current state**, **Next action** and appends to **Session log** after every meaningful step (each validated group of batches, each decision, each blocker) — not only at the end. Commit + push this file with the work it describes, so a container reset loses nothing.

---

## Current state  (last updated: 2026-09-29, session 1 — pilot COMPLETE)

- **Phase:** pilot — DONE. `status.py`: pilot 15/15 batches validated, 426/426 records. **Not scaled to phase1** (the pack's rule: stop after the pilot and report).
- **Pilot report:** `PILOT_REPORT.md` has first-try pass rates per stage, strengths and weaknesses, validator notes, and recommended next steps. Read it before doing anything else.
- **How generation was done (user instruction 2026-09-29):** the main session wrote all records itself — **no subagents unless unavoidable**. Per batch: a scratch Python file lists (sno, variant, passage, 4×(q,a), grounding); a helper copies age/topic/subtopic/subtype/recipe from the batch JSON, writes the JSONL to the manifest out path and warns when a passage is outside the nominal word range; then `validate_jsonl.py --mark`. The scratch files are not committed; the validated `.jsonl` + `.ok` files are the record.
- **Branch:** `claude/intelligent-ride-oxqjfy`. Validated pilot outputs (`pilot/out/**`) are committed here as working state. Nothing has gone through `commit_rows.py`.
- **Blocked batches:** none.
- **CRITIC pass:** NOT run yet (it needs a different agent from the generator).

## Open decisions / questions for the user

1. **Commit target for generated rows.** `scripts/commit_rows.py` defaults to `--branch main` and pushes there. The session rule is to push only to `claude/intelligent-ride-oxqjfy`, so run it as
   `python3 scripts/commit_rows.py --repo . --branch claude/intelligent-ride-oxqjfy` unless the user approves `main`. Pilot rows are not committed unless the user asks (`--include-pilot`).
2. **Stale commit trailer in `commit_rows.py`.** Its `TRAILER` constant names an older session URL and a fixed model. Per CLAUDE.md, scripts/config/prompts are not edited without approval — ask before changing it.
3. **Pack tooling lives in the data repo.** The pack's own docs assume a separate clone of `quicktalk`; here the pack was committed into `quicktalk` itself (so any future session can resume). `commit_rows.py --repo .` then writes `data/rows/*.jsonl` next to `data/human_development_framework_v9.csv` — no clash, but confirm the user is happy with this layout before large commits.

## Environment notes

- Python 3.11. `validate_jsonl.py`, `status.py`, `make_batches.py`, `export_dataset.py`, `commit_rows.py` use only the stdlib — they work as-is.
- `build_kg.py` needs `networkx` + `scikit-learn` (not installed). Only needed if the CSV changes; `kg/` ships pre-built.
- Cloud container is ephemeral: anything not committed and pushed is lost. Commit `pilot/out/`/`out/` outputs + `.ok` markers + this file after each validated group so resume state survives.
- Model guidance (README): Sonnet for bulk/tier C/repairs; Opus for tier A, sensitive stages (deception, personality, body, dynamics) and the critic. Generator and critic must be different agents.

## Pack map (quick reference)

| Path | Role |
|---|---|
| `README.md` | Plan: 15 stages, tiers A/B/C/G, phases pilot → phase1 (~16.2k records) → full (~46.7k) |
| `RUN_IN_CLAUDE_CODE.md` | Orchestrator loop for subagent generation |
| `CLAUDE.md` | Project rules (safety, no hand-edits of batches/out, sonnet generators, never fabricate/pad) |
| `data/human_development_framework_v9.csv` | 7,689 rows, ages 1–3 … 23–26, 57 topics |
| `kg/` | Pre-built knowledge graph (10,032 nodes, 54,893 edges, 940 clusters) |
| `config/variants.json`, `config/recipes.json` | Variant counts per tier/phase; recipes R1–R15, twists T1–T6 |
| `prompts/training_data_prompt.md` → `prompts/MASTER.txt` | MASTER system prompt, BATCH template, stage addenda, CRITIC, REPAIR |
| `scripts/` | make_batches, validate_jsonl, status, export_dataset, commit_rows, build_kg |
| `pilot/batches/` | 15 ready pilot batches (14 stages × 10 rows × 3 variants + 6 graph clusters) |
| `spec/`, `source/` | How the rows were authored; reference only |

## Session log (append newest at the bottom)

- **2026-09-29 — session 1:** Repo was empty. Unpacked `human_dev_pack.zip` (89 entries) into the repo root, read README, RUN_IN_CLAUDE_CODE, CLAUDE.md, config, prompt structure, specs and scripts. Verified `status.py` runs (pilot 0/15). Found the three open points above. Created this HANDOVER.md, added a pointer to it in CLAUDE.md, committed and pushed to `claude/intelligent-ride-oxqjfy`. No generation done yet.
- **2026-09-29 — session 1 (cont.):** User said start the pilot, avoid subagents. Generated and validated pilot batches 01–05 in-session (150 records). Helper: `emit(batch_json, out, items)` builds each record as {sno, variant, recipe=plan[variant], age, topic, subtopic, subtype from batch row, passage (whitespace-normalised per line, newlines kept for chat/letters), qa typed literal/mental_state/application/perspective, grounding}. Committed pilot outputs + .ok markers + this file.
- **2026-09-29 — session 1 (cont.):** Pilot batches 06–10 generated and validated (300/426 records total). Added nominal word-count warning to the helper.
- **2026-09-29 — session 1 (cont.):** Pilot batches 11–15 generated and validated; the pilot is complete (426 records). Wrote PILOT_REPORT.md. Stopped before phase1 as the pack instructs.
