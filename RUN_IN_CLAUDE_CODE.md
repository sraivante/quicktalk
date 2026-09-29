# Orchestrator prompt for a fresh Claude Code session (copy everything below the line)

Open Claude Code in the pack root (the folder containing README.md), then paste:

---
Read README.md and CLAUDE.md. We are generating training data batch by batch.

Current target: PHASE=pilot   (change to phase1 or full later)   BATCHES_PER_RUN=5

Loop:
1. Run `python scripts/status.py next 5 --phase <PHASE>` to get the next pending batches (prompt, batch_json, out paths).
2. For each batch, start ONE subagent (general-purpose, model sonnet), all of them in parallel in a single message, with this instruction:
   "Read prompts/MASTER.txt and follow it exactly as your system rules. Read <prompt path>. Write ONLY the JSON Lines it asks for (no commentary) to <out path> using the Write tool. Reply with just the path and the record count."
3. When they finish, run `python scripts/validate_jsonl.py <batch_json> <out path> --mark` for each.
4. If a batch fails: build a repair message from the REPAIR section in prompts/training_data_prompt.md using only the failing rows (from the batch json) and the printed failures; run one subagent to write the repaired records (replace those records in the out file, keep the rest); validate again. Only one repair round. If it still fails, list the batch as blocked in `pilot/blocked.txt` (or `blocked.txt`) and move on.
5. If the repo `quicktalk` is attached and cloned (git clone https://github.com/sraivante/quicktalk), run `python scripts/commit_rows.py --repo <path to quicktalk clone>` to commit each validated row as its own file (data/rows/<S.No>.jsonl) with its own commit and push. Skip this for the pilot unless I say so (add --include-pilot only if I ask).
6. Print `python scripts/status.py`. Stop after BATCHES_PER_RUN batches, or earlier if a subagent hits a usage limit, and tell me what finished, what failed and what usage this consumed. Do not continue past the limit on your own.

For the pilot: after all 15 batches, do not scale. Give me a short quality report (per stage: pass rate on first try, failure reasons, anything you noticed about tone, age fit, recipe adherence, emoji use) and stop.
---
