# Human Development SLM: data generation pack (v9)

Goal: turn a 7,689-row framework of human behaviour, mindset and execution (ages 1-26, 57 topics) into training passages plus Q&A for a small language model built from scratch. This pack lets a fresh session pick up generation with no earlier context.

## What is in here
| Path | What |
|---|---|
| `data/human_development_framework_v9.csv` (+ .xlsx) | The framework. Columns: S.No, Age, Topic, Subtopic, Subtype, Human Learning & Development. Ages: 1–3, 4–6, 7–12, 13–17, 18–22, 23–26 (en dash). |
| `kg/` | Knowledge graph made by `build_kg.py`: nodes/edges, normalised columns, `row_context.jsonl` (short relations per row), `clusters.jsonl` (~940 related-row clusters), `stats.txt`. Pre-built; rerun only if the CSV changes. |
| `config/variants.json` | Variant counts per tier and phase (edit here to change the plan). |
| `config/recipes.json` | 15 form/setting recipes R1-R15 and 6 twists T1-T6 that make the variants of a row differ. |
| `prompts/training_data_prompt.md` | MASTER system prompt, BATCH template, per-stage addenda, CRITIC and REPAIR prompts. `prompts/MASTER.txt` is generated from it. |
| `scripts/` | `make_batches.py`, `validate_jsonl.py`, `status.py`, `export_dataset.py`, `build_kg.py`. |
| `spec/`, `source/` | How the rows were written, the original 153-row table, the 70-item expression taxonomy, the handover guide. Reference only. |
| `pilot/`, `batches/`, `out/`, `export/` | Created and filled by you (batches, generated outputs, final training files). |

## The plan (decided)
- 15 stages: core (S.No 1-317), expression, situational, dynamics, cognitive, foundational, personality, group, deception, culture, body, execution, wellbeing, planning, graph.
- Variants (passages per row): **A** core+foundational+cognitive 1,185 rows -> 15; **B** nine mid-tier topics 2,831 rows -> 6; **C** situational+planning 3,673 rows -> 3; **graph** clusters -> 1 record each.
- Phases: pilot (10 stratified rows per stage x 3 variants + 6 clusters, 15 batches, 426 records) -> phase1 (A5 / B2 / C1, about 16,200 records) -> full (adds A ids 6-15, B ids 3-6, C ids 2-3, about 30,500 more; about 46,700 in total).
- Why tiers: 15 variants of a thin row mostly repeat; 15 is only worth it where the row is a mechanism that everything else builds on. Stop at phase1 if the pilot shows near-duplicates or you run out of budget. Data quality beats count.
- Each record = one passage (40-160 words by age) + 4 Q&A (literal, mental_state, application, perspective) + one-line grounding. Graph records = one passage over a cluster + 4 Q&A (literal, relational, mental_state, application). Emojis allowed with hard caps (see MASTER rule 10).
- Each variant id of a row has a fixed recipe from `config/recipes.json` (e.g. R3 first-person reflection, R6 chat, R14 elder tells it). Records echo their recipe; the validator checks it.

## Steps
```
python scripts/make_batches.py --phase pilot     # 15 batches under pilot/batches/, outputs go to pilot/out/
python scripts/status.py next 5                  # prompt path, batch json, out path for the next batches
# generate (see below), save the reply as the out path, then:
python scripts/validate_jsonl.py <batch_json> <out.jsonl> --mark
python scripts/status.py                         # progress
python scripts/make_batches.py --phase phase1    # after the pilot is judged good
python scripts/make_batches.py --phase full      # adds ids after phase1 (use --after none to build from scratch)
python scripts/export_dataset.py                 # export/records.jsonl, pretrain.jsonl, qa.jsonl, report.txt
python scripts/commit_rows.py --repo /path/to/quicktalk   # one file + one commit per row (see below)
```

## Per-row commits to the data repo
Target repo: `sraivante/quicktalk` (public, was empty). `scripts/commit_rows.py` writes `data/rows/<S.No, 5 digits>.jsonl` (all validated variants of that row, one record per line, sorted by variant id) and makes one commit per row file; graph-stage records go to `data/clusters/<cluster_id>.jsonl`, one commit each. It only takes batches with a `.ok` marker, merges by variant id (so later phases add variants to the same file with a new commit), skips unchanged rows, and pushes every 25 commits (`--push-every`). Generation itself still runs 10 rows per batch for quality and cost; the per-row split happens at commit time. Run it after each validated group of batches, e.g. after every 5 batches. The repo is public, so everything committed is public.
Generating a batch: use `prompts/MASTER.txt` as the system prompt and the batch's `.txt` as the message; the reply must be JSON Lines only. Either paste manually in fresh chats or let Claude Code subagents do it: see `RUN_IN_CLAUDE_CODE.md`.

## Pilot review checklist (do this before scaling)
1. Read every pilot batch fully, not a sample. Judge: fidelity to the row, answers supported by the passage, age fit, recipe followed, emoji feeling matches, no preachiness, no tag words.
2. Run the CRITIC prompt on the pilot outputs in a different chat.
3. Tighten the stage addendum in `prompts/training_data_prompt.md`, rerun `make_batches.py`, regenerate the weak batch.
4. Note how much of your Pro usage limit one batch (30 records) consumed, then estimate: phase1 is about 1,050 batches, full adds about 370 more. Multi-day pacing is expected on Pro; the API is billed separately.
5. Check whether the model hesitates on any stage (Fable has extra safeguards around some topics). If so use Opus or Sonnet for that stage.

## Model guidance
Accuracy-first: Opus 5.5 or Fable 5.1 if your Pro limits allow (check `/model`). Sonnet 5.5 is the practical bulk model; use it for tier C and for repairs, Opus for tier A, the sensitive stages (deception, personality, body, dynamics) and the critic. Never generate and review in the same chat.

## Honest known issues
- Framework: core topics are thin (44 topics in 317 rows); ages skew toward 13-26; about 23% of rows (85% of situational) mix "I/you" voice in descriptions; 384 raw stance labels are only partly normalised in the KG.
- Knowledge graph: edges are rule-derived plus TF-IDF heuristics (threshold 0.22); `heuristic` items in graph_context can be wrong, the prompt tells the model to ignore them if they do not fit.
- Validator checks structure, length, emoji caps, leaks, copying, answer-in-passage overlap, variant similarity, recipe echo. It cannot check truth or that a recipe's style was really followed; that is what the pilot read-through and the critic are for.
- The scripts were tested on synthetic outputs only, never on real model output. Expect the first real run to expose validator thresholds that are too strict or too lax; adjust `validate_jsonl.py` after the pilot.
- Variants from different passes (e.g. ids 1-3 and 4-6) are not compared with each other by the validator; `export_dataset.py` reports near-duplicates across all variants of a row.
- Pilot outputs are not used unless you pass `--include-pilot` to the export; duplicates by (sno, variant) are removed.
- Training-side plan (not in this pack): shuffle all records together; use passages for pretraining text and Q&A as instruction data; hold out a validation split by S.No (not by record) so variants of the same row never sit on both sides.
