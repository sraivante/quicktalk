# Project memory

START HERE: read HANDOVER.md first (current state, next action, open decisions) and keep it updated after every meaningful step; commit and push it with the work.
Project: training-data generation for a from-scratch small language model on human behaviour (ages 1-26). Read README.md first.

Rules
- Work from the pack root. Use scripts/ only; do not hand-edit batches/ or out/.
- Never paste dataset content into chat; write files.
- A batch is done only when validate_jsonl.py --mark has written its .ok file.
- Do not edit the CSV, config or prompts without the user's approval; report findings instead.
- Generation subagents: model = sonnet unless the user says otherwise. Reviewer/critic must be a different agent from the generator.
- Never fabricate records or pad a batch to satisfy the validator. A row that cannot be written safely gets "passage": "SKIP" with a reason.
- Safety: no instructions to deceive, coerce, stalk, harm; no medical, legal or financial advice; no diagnoses.
- Colab/compute code must use all CPU cores (multiprocessing / batched tokenizer calls) for heavy CPU steps (text cleaning, conversion, tokenizing), and write big intermediate files to the local Colab disk first, then copy to Drive once (user rule, 2026-10-02).
- Commit nothing unless asked.
- Data repo: sraivante/quicktalk. Commit only through scripts/commit_rows.py (one file and one commit per S.No). Never commit unvalidated or synthetic records; never force-push.
