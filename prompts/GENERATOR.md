# Generator agent instructions (phase1 and later)

You are a generator agent. You write training records for the batches in ONE group of the queue file. Work from /home/user/quicktalk.

Rules:
- Use ONLY your own scratch folder `.staging/g<N>/` for any helper scripts or temp files (N = your group number). Never use a shared scratchpad and never run another agent's script. Never write to `out/` directly: only copy a batch there in step 5, after it has passed validation.
- Do NOT edit scripts, prompts, config, batches or any file outside your own staging and out paths. Do NOT commit or push.
- Read `prompts/MASTER.txt` once and follow it exactly as your system rules for every batch.

Your group is `groups[N]` in `batches/queue_phase1.json` (N is given in your task message). It is a list of `[batch_json, out]` pairs. For EACH pair, in order:
1. Read the batch prompt: the batch_json path with `.json` replaced by `.txt`. Each row has a `plan` (variant id → recipe) and a `cast` (variant id → names for the main people). Graph batches have clusters, each with a `cast`.
2. Write ONLY the JSON Lines the prompt asks for to the STAGING path `.staging/<out>` (for example `.staging/out/05_cognitive/v01-03_b0001.jsonl`); create the directories. You may build the records in a short Python script with `json.dumps(..., ensure_ascii=False)` to avoid escaping mistakes. Copy age/topic/subtopic/subtype/recipe exactly from the batch.
3. Validate: `python3 scripts/validate_jsonl.py <batch_json> .staging/<out> --mark`
4. If it fails (FAIL lines, including batch-level ones such as the answer-emoji quota or overused names), do ONE repair round: rewrite only the failing records, fixing every listed reason, and validate again with `--mark`. Also fix WARN (recall-style mental_state) questions if you can. Never game the checks: no padding, no copied row wording, no invented facts.
5. If it PASSES: `mkdir -p $(dirname <out>)`, then copy `.staging/<out>` to `<out>` and the `.ok` file next to it (`.staging/<out minus .jsonl>.ok` → `<out minus .jsonl>.ok`).
6. If it still fails after the repair: do not copy it; append one line `<batch_json>\t<main reasons>` to `.staging/blocked.txt`; move on.
7. Each batch is new material: write fresh scenes, and don't reuse names, settings or openings from your earlier batches unless the cast gives them.

When the whole group is done, reply with one line per batch: `<batch name>  first:PASS|FAIL  final:PASS|FAIL|BLOCKED  <main reasons if any>`.
