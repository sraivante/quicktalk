# Repair agent instructions

You repair already-generated batches that fail the CURRENT validator (or that the critic marked "fix"). Work from /home/user/quicktalk.
Rules: do NOT edit scripts, prompts, config or batch files; do NOT commit or push; use only your own scratch folder `.staging/r<N>/`.

Read `prompts/MASTER.txt` (current rules) first. Your group is entry N (0-based) of the list in the queue file named in your task message; its `"batches"` field lists `[batch_json, out]` pairs. For EACH pair:
1. Copy `<out>` to `.staging/r<N>/<basename>` and run `python3 scripts/validate_jsonl.py <batch_json> <that copy>` to see the FAIL lines.
2. The group has `"critic"` notes (a list of {sno, variant, issues}); fix those records too, in whichever of your batches contains them.
3. Fix ONLY the failing / noted records, minimally, keeping everything else identical:
   - "name(s) [...] used in questions/answers but not in the passage": the passage never names that person (usually a first-person narrator). Either work the name into the passage naturally (a signature on a letter or diary, a self-introduction, someone addressing them) while keeping the passage within its word range, or change the questions/answers to "the narrator" / the role word. Never give a person a gender (he/she) the passage does not state; use the name, the role or "they".
   - "emoji on the last answer" (batch-level): move or remove emojis so at most a quarter of records have one on the last answer; keep at most about half of records with any answer emoji.
   - anything else: follow the FAIL reason.
   Do not rewrite passages beyond what the fix needs; no padding, no copied row wording, no invented facts.
4. Validate the fixed copy with `--mark`. If it passes, copy the fixed `.jsonl` AND its `.ok` over `<out>` and `<out minus .jsonl>.ok`. If it fails, do one more repair; if it still fails, leave `<out>` untouched and add a line to `.staging/blocked.txt`.
Reply with one line per batch: `<batch name>  records fixed: <n>  final: PASS|BLOCKED  <notes>`.
