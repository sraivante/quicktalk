# Repair agent instructions

You repair already-generated batches that fail the CURRENT validator (or that the critic marked "fix"). Work from /home/user/quicktalk.
Rules: do NOT edit scripts, prompts, config or batch files; do NOT commit or push; use only your own scratch folder `.staging/r<N>/`.

Read `prompts/MASTER.txt` (current rules) first. Your group is entry N (0-based) of the list in the queue file named in your task message; its `"batches"` field lists `[batch_json, out]` pairs. For EACH pair:
1. The source is `<out>`, or `.staging/needs_repair/<out>` if `<out>` does not exist. Copy the source to `.staging/r<N>/<basename>` and run `python3 scripts/validate_jsonl.py <batch_json> <that copy>` to see the FAIL lines.
2. The group has a `"critic"` list of notes `{batch, sno, variant, issue}` (sno/variant may be null = whole batch). Handle every note for your batches:
   - critic issues: fix as described; "REJECT" means rewrite that record from scratch to the row and current MASTER rules;
   - "SAFETY REVIEW": read the scene; if a child/young person discloses or shows possible signs of harm, the adult must not dismiss it or wait: they stay with the child, say it is not their fault and pass it to the right person the same day (MASTER disclosure rule). Fix any record that falls short;
   - "ROW CHECK": for every record in that batch, compare the genders and roles with the row description; if a record changed them to fit a cast name, keep the row's version and rename the person instead.
   In ALL your batches also check every answer and grounding line: no he/she/his/her for a person whose gender the passage does not state (use the name, role or "they").
3. Fix ONLY the failing / noted records, minimally, keeping everything else identical:
   - "name(s) [...] used in questions/answers but not in the passage": the passage never names that person (usually a first-person narrator). Either work the name into the passage naturally (a signature on a letter or diary, a self-introduction, someone addressing them) while keeping the passage within its word range, or change the questions/answers to "the narrator" / the role word. Never give a person a gender (he/she) the passage does not state; use the name, the role or "they".
   - "emoji on the last answer" (batch-level): move or remove emojis so at most a quarter of records have one on the last answer; keep at most about half of records with any answer emoji.
   - anything else: follow the FAIL reason.
   Do not rewrite passages beyond what the fix needs; no padding, no copied row wording, no invented facts.
4. Validate the fixed copy with `--mark`. If it passes, copy the fixed `.jsonl` AND its `.ok` over `<out>` and `<out minus .jsonl>.ok`. If it fails, do one more repair; if it still fails, leave `<out>` untouched and add a line to `.staging/blocked.txt`.
Reply with one line per batch: `<batch name>  records fixed: <n>  final: PASS|BLOCKED  <notes>`.
