# HANDOVER — read this first, update it before you stop

This file keeps consecutive Claude Code sessions in sync. Every session:
1. Reads this file, then README.md and CLAUDE.md.
2. Runs `python3 scripts/status.py` and checks it agrees with **Current state** below (the `.ok` markers are the source of truth; if they disagree, trust the markers and fix this file).
3. Updates **Current state**, **Next action** and appends to **Session log** after every meaningful step (each validated group of batches, each decision, each blocker) — not only at the end. Commit + push this file with the work it describes, so a container reset loses nothing.

---

## Current state  (last updated: 2026-09-29, session 1)

- **Phase:** pilot — NOT STARTED. `status.py`: pilot 0/15 batches validated, 0/426 records.
- **Pack location:** the whole `human_dev_pack` is unpacked at the repo root (README.md, scripts/, data/, kg/, prompts/, pilot/ …).
- **Branch:** `claude/intelligent-ride-oxqjfy` (this is the working branch for all sessions unless the user says otherwise).
- **Pilot batches:** already built in `pilot/batches/` (manifest `pilot/batches/manifest_pilot.csv`); no need to rerun `make_batches.py --phase pilot`.
- **Outputs so far:** none (`pilot/out/`, `out/`, `batches/` empty).
- **Blocked batches:** none.
- **Open decisions waiting on the user:** see below.

## Next action

Start the pilot per `RUN_IN_CLAUDE_CODE.md` (PHASE=pilot, 5 batches per run), **only when the user asks to generate**:
```
python3 scripts/status.py next 5 --phase pilot
# one sonnet subagent per batch: system rules = prompts/MASTER.txt, message = batch .txt, write JSONL to out path
python3 scripts/validate_jsonl.py <batch_json> <out.jsonl> --mark
python3 scripts/status.py
```
After all 15 pilot batches: write the pilot quality report (per stage: first-try pass rate, failure reasons, tone, age fit, recipe adherence, emoji use) into `PILOT_REPORT.md` and STOP — do not scale to phase1 without the user's go-ahead.

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
