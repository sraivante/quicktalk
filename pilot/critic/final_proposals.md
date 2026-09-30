# Phase1 wrap-up: open decisions and proposed rule changes (need user approval)

## Status
- Generation: 1,044/1,050 batches, 16,080/16,200 records, 8,569/8,629 rows. Missing: culture group 106 (v01-02_b0001-b0006).
- Final critic (Opus, 290 records over deception, body, culture/execution/wellbeing, planning, graph): 231 pass / 58 fix / 1 reject.
- Repair 9 (Opus, 38 groups, 248 batches): all 58 critic fixes applied; all 276 narrator-pronoun WARNs hand-checked (most were false alarms; ~120 real pronoun/relationship slips fixed, many found by the agents' own sweeps); 24 emoji-in-sensitive checked (several removed); 10 cleanup items incl. 4 safety fixes.
- Re-validation after repair: 1,044/1,044 pass; 245 remaining WARNs are hand-checked false positives.
- Export (scripts/export_dataset.py): 16,080 records, 64,320 QA pairs, 7,629 rows covered, 0 exact duplicates, 0 near-duplicate variant pairs (Jaccard > 0.5). Report: export/report.txt. The export .jsonl files (~105 MB) are not committed.

## Decisions for the user
1. C0830 (graph, g_b0139): rejected; two rows linked only by the word "splitting". Recommend dropping it from the export (and fixing cluster mining, item P7). It is currently in the export.
2. Culture group 106: relaunch on Opus? (6 batches, 120 records.)
3. commit_rows.py (final per-S.No commits) and the `full` phase: not run; waiting for approval.

## Proposed changes (not applied)
Validator
- P1. WARN when a mental_state answer has no feeling word (small emotion lexicon). The most common defect in every critic sample; still present outside the samples (e.g. 5621 v2).
- P2. WARN when the mental_state and perspective questions name the same person.
- P3. WARN when a stated age falls outside the row's bracket; WARN when an R11/R14 spoken passage ends with a letter sign-off.
- P4. WARN on diagnostic labels (autistic, ADHD, depressed...) in answers/grounding that the passage does not state.
- P5. Narrow the first-person narrator WARN: skip pronouns that sit next to a kin term or gender word (it produced ~90% false alarms).
Prompt (MASTER / addenda)
- P6. Mental_state answer must contain a feeling word ("realised/thought/wanted" alone do not count). [Observer] rows: mental_state centres the observer, perspective the observed person; the observer stays present in every beat.
- P7. Self-harm: if the talk ends at night, show a same-night step (helpline, warden, check-in). Disclosure to a peer still ends with a trusted adult's same-day response. Dangerous dares get a same-day protective step (graph addendum).
- P8. Finance rows: never a personal money rule; name a choice or point to a qualified adult.
- P9. Re-check numbers/days/counts inside the passage; vary the planning application stem (avoid a fixed "What alternative approach...").
Planner / KG
- P10. Cast sampler: when the row fixes a gender, draw that slot from matching-gender names (graph agents repeatedly had to rename or flip names).
- P11. Cluster mining: concept_link/progression clusters need a shared concept, not a shared word or subtopic label.
- P12. Don't assign R12 (observer's account) to [Receiver]/[Actor] rows; for two-variant rows, suggest different central beats.

## Next-cycle items (not fixed)
- 5709 v5 (06_foundational v04-05_b0027): narrator "Urmila Dadi" calls her brother "Nana" (kin mismatch; needs a passage rewrite).
- Mental_state answers without a feeling word across the unsampled data: fix by a scripted scan once P1 is approved.
