# Final scripted scan of out/ (phase1, 1,044/1,050 batches; culture group 106 not yet generated)

Scripts: scratchpad scan/*.py (copies of results in pilot/critic/scan/).

| check | result |
|---|---|
| Re-validate every batch with the current validator | 1,044/1,044 pass (rc=0), 0 FAIL |
| SKIP records | 0 |
| Near-identical passages (first 300 normalised chars) | 0 groups |
| Names from the name pool in answers but not in the passage | 0 |
| Validator WARNs | 279: 276 "first-person passage + he/she in Q/A/grounding", 3 recall-style mental_state |
| Emoji in passages of sensitive-looking rows | 24 records (emoji_sensitive.json) |

## Narrator gender (the 276 WARNs)
The WARNs sit only in stages generated before the narrator rule (core 51, expression 20, situational 23, dynamics 28, cognitive 115, foundational 42). Many hits are pronouns for other people (gendered by kin terms), so the WARN over-counts.
Targeted checks for the real defect:
- 5 lines refer to "the narrator/storyteller" with he/she; 1 is a real slip (234 v4 "her son"). See narr_hits.json.
- 41 lines give he/she to a name that appears only inside quoted speech, i.e. the likely narrator (cognitive 22, core 5, expression 5, dynamics 4, foundational 3, situational 2). See narr2_hits.json.
Proposal for the combined repair: one Opus agent works through warns.txt, fixes only pronouns that refer to an ungendered narrator (replace with name/they), and re-validates with --mark.
