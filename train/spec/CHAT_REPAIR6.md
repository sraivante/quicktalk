# Chat-pattern set: run 6 repair pass

You review and repair ONE id range of ONE type in `train/chat_r6/<type>.jsonl`. You did not write these examples.
Read first: `train/spec/CHAT_PATTERNS.md` (rules, type table, "Run 6 additions") and
`train/chat_r6/critic/summary.md` (the critic's checklist, "Instructions for the generators").

1. Do NOT edit `train/chat_r6/<type>.jsonl` (generators may be appending to it). Read your id range from it.
2. Check every example in your range against the spec and the critic checklist:
   - facts and science true; grammar fixes right, minimal, and the "Why:" names the rule that matches the change;
   - every "Because" gives the real cause (not a restatement); vocab gives the right meaning and part of speech;
   - the user's ask matches its content (a "missing word" is really missing, a spelling question really misspells);
   - instruct output meets every constraint exactly (count words/items); summaries and comprehension answers are
     supported by the excerpt; rewrites keep the meaning and follow the instruction;
   - dont_know: says plainly it does not know/cannot check, short reason, safe next step; never invents a fact;
   - multi_question: every question answered in order, numbered 1..n_questions, no arithmetic;
   - safety (no medical/legal/financial advice, no real brands/public figures), clear modern English, no filler
     openings, metadata.topic fits the content.
3. For each example that needs a change, write the FULL corrected JSON line (same id, group, type) to
   `.staging/r6_repair/<type>_<first>-<last>.jsonl`. Keep changes minimal; do not rewrite good examples. If an
   example cannot be fixed well, rewrite it completely as a new example of the same type (same id).
4. Also write `.staging/r6_repair/<type>_<first>-<last>_log.jsonl`: one line per changed id {"id", "problem", "change"}.
4b. Run `python3 scripts/check_r6_dupes.py <type>` and rewrite every id in your range that it lists as a new example.
5. Validate your fixes file: `python3 scripts/validate_chat.py .staging/r6_repair/<type>_<first>-<last>.jsonl --type
   <type>` (add `--no-arithmetic` for reasoning). Ignore WARNs about repeated openings across a small file; fix FAILs.
6. Do not commit. Do not touch other files. Final report: how many checked, how many changed, top problems; never
   paste dataset content.
