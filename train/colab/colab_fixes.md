# Colab training log: issues, fixes and results

One entry per change, newest at the bottom. Each entry: **issue** (what went wrong or what we wanted), **change**
(what was done, where), **output** (what happened when it ran). Update this file in the same commit as every change
to the Colab pipeline (`train/colab/quicktalk_lm.py`, `quicktalk_train.ipynb`) and after every Colab run.

Setup common to all runs: Colab A100-SXM4-40GB; code and data cloned from `sraivante/quicktalk`, branch
`claude/intelligent-ride-oxqjfy` (`train/build/`, `train/colab/`); state in Google Drive `MyDrive/quicktalk_run*`;
16,384-token BPE tokenizer; data = 13.66M pretraining tokens + 15.26M chat tokens (4.05M assistant tokens trained);
context 512; batch 64 x 512 tokens; sizing rule 10 training tokens per parameter.

---

## 2026-10-01 — Pipeline built (before first Colab run)
- **Issue:** train a from-scratch model on `train/build/` in Colab, A100 only, survive idle disconnects and crashes,
  size the model at 10 tokens per parameter (not Chinchilla's 20).
- **Change:** `quicktalk_lm.py` (tokenizer / prepare / plan / train / chat); every step skips itself if done; train
  checks for an A100; checkpoints every 5 min or 200 steps to Drive (atomic write, previous kept); resume from
  `<stage>_latest.pt`; training runs in the background (nohup) so a closed tab does not stop it; token files copied
  to local disk for speed (`--data-dir`). Notebook `quicktalk_train.ipynb` drives it. Tested on CPU in the container
  (resume after deleting the final checkpoint worked).
- **Output (local test):** tokenizer 16 s, prepare 42 s; plan for 4 + 2 passes = 85M tokens seen -> 8.9M parameters
  (d=256, 6 layers, 4 heads).

## Notebook v1 — Drive mount failed
- **Issue:** cell 2 `drive.mount` raised `ValueError: mount failed`.
- **Cause:** Google sign-in / permissions step (not the training code): usually a permission box left unticked, a
  different Google account, or blocked pop-ups/cookies.
- **Change (v2):** cell 2 skips mounting if Drive is already mounted, waits up to 5 min (`timeout_ms=300000`), and
  prints the fix steps on failure (same account, tick "Select all", allow pop-ups, or use the Mount Drive button).
- **Output:** v2 mounted fine.

## Run 1 (`quicktalk_run`, notebook v2) — first full run
- **Settings:** 8.9M parameters, 4 pretraining passes + 2 chat passes (1,668 + 932 steps).
- **Output:** finished in ~2 minutes at ~1.4M tokens/s. Pretraining eval loss 3.84; chat eval loss 3.76 (ppl 43).
- **Issue found:** cell 8 (loss chart) crashed: `x and y must have same first dimension` because `d.eval` is a
  pandas DataFrame method, not the "eval" column. Run all stopped before the chat cell.
- **Change:** chart reads columns by name (`d['eval_loss']`).

## Run 2 (`quicktalk_run2`, notebook v3) — bigger model within the 10x rule
- **Issue:** run 1 trained in 2 minutes; the model was very small.
- **Change:** 6 pretraining passes + 3 chat passes = 128M tokens seen -> 12.6M parameters (d=320, 6 layers,
  5 heads). Not 8 + 4 (17M): too much repetition of the same text. Run in its own folder; reuses run 1's tokenizer
  and token files; cell 9 asks every run the same questions; cell 10 compares runs.
- **Output:** pretraining 2,502 steps + chat 1,397 steps in ~3.5 min (~1.1M tokens/s). Pretraining eval loss 3.60;
  chat eval loss 3.31 (ppl 27.5) — best so far.
- **Issue found:** replies were fluent-ish but did not answer the user; they talked *about* a "she/he" as if
  describing a story, and one leaked a grammar-style "Why:" line.
- **Cause:** 94% of chat data is behaviour passage Q&A (questions about people in a passage); the 12 direct
  conversation patterns (2,400 examples) were only ~5%.

## Run 3 (`quicktalk_run3`, notebook v4) — upsample conversation patterns
- **Change:** `prepare --chat-repeat N` repeats the 12 conversation-pattern types N times in chat training. Run 3:
  N=8, 3 chat passes, starting from run 2's pretrained weights (pretraining not repeated). Patterns went from ~5% to
  29.4% of chats (65,312 chats, 17.0M tokens). Also: chat stage now takes the model shape from `pretrain_final.pt`
  (found when a local test loaded weights into a different-size model).
- **Output:** chat stage 1,559 steps in ~1 min. Train loss fell to ~2.1 but chat eval loss rose to 3.81 (worse than
  run 2). Replies looped on one topic ("small rain ... the rain was wet") across all questions.
- **Cause 1 (training):** overfitting — each pattern example was seen 8 x 3 = 24 times.
- **Cause 2 (test bug):** the chat cell sent all scripted questions as one running conversation, so earlier
  answers leaked into later ones (the "rain" topic carried over). Runs 1-3 replies in that test were unfair.

## Run 4 (`quicktalk_run4`, notebook v5) — lighter upsampling + fair chat test
- **Change:** chat-repeat 3 with 2 chat passes (~6 views per pattern example), from run 2's pretrained weights.
  `chat`: each scripted prompt now starts a fresh conversation (`--keep-history` to share one), and a repetition
  penalty (`--rep-penalty`, default 1.3) discourages word loops. Cell 9 uses temperature 0.6.
- **Output:** prepare: 53,312 chats, 15.76M tokens (patterns ~13% of chats); chat stage 962 steps in ~1 min.
  Chat eval loss 3.47 (ppl 32.2): better than run 3 (3.81), worse than run 2 (3.31; run 2 trained more on the
  behaviour chats that make up most of the eval set). No overfitting (train ~3.1 vs eval 3.47).
- **Chat test (fresh conversation per question, rep-penalty 1.3, temperature 0.6), all runs:** every run now picks
  the right *format* for the request (word question -> "It means ... It is a noun ... Example:"; grammar -> "Why:";
  note -> "Dear ..."), and run 4 does so most consistently, but the *content* is not meaningful in any run (wrong
  meaning for "diligent", grammar fix not applied, invented words like "bigure"). Run 1's earlier topic loops are
  gone, confirming the old test bug.
- **Verdict:** not good enough for real chat. Training settings are no longer the bottleneck: at 12.6M parameters
  and 29M unique tokens the model learns formats but not meaning. Best checkpoints: run 2 (lowest eval loss) and
  run 4 (best format following).
- **Next (proposed):** add a large amount of simple modern English pretraining text so the 10x rule allows a larger
  model (e.g. ~500M tokens -> ~50M parameters, about an hour on the A100). Pending user decision on sources.

## Notes for future changes
- Under the 10x rule, model size is capped by data: 29M unique tokens supports ~10-13M parameters at 4-6 passes.
  Expect fluent-but-loose replies at this size; a real quality jump needs more training text (a few hundred million
  tokens would allow a 50-100M model under the same rule).
- Judge runs by chat eval loss on the same eval set plus the fixed 6-question chat test; chat eval loss is only
  comparable between runs with the same eval file (all runs so far use `sft_eval_all.jsonl`).

## Run 5 (`quicktalk_run5`, notebook v6) — add simple English pretraining text (user approved)
- **Issue:** runs 1-4 showed the model is data/size-limited (formats learned, meaning not).
- **Change:** `quicktalk_lm.py fetch` downloads, in Colab (this container cannot reach Hugging Face), TinyStories
  (`roneneldan/TinyStories`, TinyStoriesV2-GPT4-train.txt; CDLA-Sharing-1.0) and Simple English Wikipedia
  (`wikimedia/wikipedia` 20231101.simple; CC BY-SA) into `/content/extra`, English only: lines with non-Latin
  scripts dropped, "(French: ...)"-style asides removed, accents folded to ASCII, references sections cut.
  `tokenizer --extra` adds a 150 MB sample of that text to tokenizer training (new tokenizer for this run).
  `prepare --extra --own-repeat 3` writes your books + behaviour passages 3x plus the extra text; tokenization now
  streams to disk (no 500M-token list in memory). Chat data unchanged (patterns 3x, 2 passes). Plan: 1 pretraining
  pass, 10 tokens/param, dropout 0; larger presets added (up to 768 x 12). Pretraining uses batch 128 x 512,
  checkpoint every 1,000 steps / 10 minutes (bigger checkpoints). Warmup = 1% of steps (min 200).
- **Local test (stand-in files):** English filter removed a French aside and a Hindi line and folded "Cafe";
  own text written 3x; streaming prepare, plan, pretrain, chat stage and chat all ran on CPU.
- **Expected:** ~0.6B pretraining tokens -> roughly 60-80M parameters; ~45-75 min training on the A100.
- **Notebook:** v6 in Drive: https://colab.research.google.com/drive/1QWI780xEzpjioZ9bzjqQPVhFZBnjdyID
- **Output:** fetch + tokenizer + prepare 03:56-04:10 (TinyStories 2,190 MB, Simple Wikipedia 155,858 articles / 202 MB;
  pretraining 633.0M tokens = own text 3x 42.4M + wiki 53.7M + TinyStories 537M; chat 53,312 chats, 16.06M tokens).
  Plan: 69.5M parameters (d=640, 12 layers, 10 heads), 665M tokens seen. Pretraining 9,660 steps 04:10-04:46 at
  ~318k tok/s (~36 min); eval loss on own held-out text 5.29 -> 3.29 (ppl 27.0), train ~1.4 (TinyStories is easy).
  Chat stage 981 steps 04:46-04:49; chat eval loss 2.76 (ppl 15.8; lowest 2.76 at step 400 too, so no overfitting
  trend but no gain after step 400). Not strictly comparable with runs 1-4 (new tokenizer, same vocab size), but
  clearly lower than run 2's 3.31.
- **Chat test (same 6 questions, temperature 0.6):** best so far. Replies are fluent, grammatical and mostly on topic:
  upset friend -> "tell your friend to stay calm"; exam nerves -> "breathe, drink water"; thank-you note is a coherent
  short note. Still wrong on facts/skills: "diligent" defined wrongly with invented words, the grammar fix not applied
  ("She likes them too much"), a stray "Why:" line after the exam answer, and "How was your day" drifts into a story.
- **Verdict:** clear step up from runs 1-4 (data size was the bottleneck); usable as the experiment's best checkpoint,
  not a reliable assistant. Next levers if wanted: more chat-pattern examples (word meanings, grammar fixes), or more
  pretraining text for a larger model under the same 10x rule.
- **Finish:** cell 11 had not been added to the running notebook, so no zip and no automatic disconnect right after
  the run; user then added and ran it. `MyDrive/quicktalk_run5_model.zip` saved 05:02, 258.5 MB (sft_final.pt,
  tokenizer.json, plan.json, quicktalk_lm.py, log_*.csv, train.log). The cell copies to Drive only after the local zip
  passes `testzip`, and disconnects only if the Drive copy also verifies; its printed output was not saved to the
  notebook (runtime disconnected before autosave), so the disconnect was not seen directly. Resumable checkpoints,
  `pretrain_final.pt` and token data stay in `MyDrive/quicktalk_run5/`.
- **Lesson:** add the finish cell before pressing Run all; a cell added after the run adds ~15 min of idle A100 time.

## Finish cell (cell 11) — zip model, verify, disconnect
- **Issue:** user wants the finished model zipped and the A100 runtime disconnected automatically; Claude can read
  Drive but cannot run cells or control the Colab runtime from the container.
- **Change:** new last cell: waits until `sft_final.pt` exists, zips the model + tokenizer + plan + code + logs, checks
  the zip (`testzip`), copies it to `MyDrive/<RUN>_model.zip`, re-checks size and integrity, offers a browser
  download, then calls `google.colab.runtime.unassign()` to disconnect. For run 5 (already running) the user adds
  this cell at the end and presses its play button; Colab queues it after the running cells.
- **Monitoring:** Claude polls Drive every ~5 min (train.log, notebook outputs) and judges the chat test.

## Finish cell fix — slow / broken browser download
- **Issue:** user reported the model download taking a long time. Cause: cell 11 called `files.download()`, which streams
  the 258 MB zip from the Colab runtime through the notebook connection to the browser (slow, often stalls for files
  this size), and the cell then disconnected the runtime 90 s later, which cuts that download off.
- **Change:** cell 11 no longer offers a browser download; download the zip from Google Drive instead. Before
  disconnecting it now calls `drive.flush_and_unmount()` so the Drive upload is complete before the runtime goes.
- **Output:** run 5 zip is intact in Drive (258.5 MB, 05:02); user to download it from drive.google.com.

## Run 5 offline test — 375 questions from the training material
- **Issue:** user asked for a thorough test of the run 5 model over many question patterns, using only training material.
- **Change:** `scripts/test_model_build.py` (test set: 10 categories, 375 questions, all from `sft_train` or story subjects
  from the training books/TinyStories), `scripts/test_model_run.py` (CPU, KV cache, greedy + repetition penalty 1.3),
  `scripts/test_model_report.py` (tables). Model rebuilt in the sandbox from 28 uploaded zip chunks (size and
  `testzip` verified). A first pass cut the start of 17 long prompts (answer budget too large); fixed (whole prompt
  kept, answer budget shrinks) and those 17 re-run. Every answer graded by reading it against the training reference.
- **Output:** overall 22% (28 correct, 111 partial, 236 wrong). Best: passage facts 58%, follow-up questions on a
  passage 35%, multi-turn replies 38% (on topic, rarely exact). Weak: word meanings 13%, idioms/usage 5%, literature
  facts 5%, arithmetic/reasoning 15%, instructions 13%, Hinglish 7%. Grammar: corrected sentence right 15/40, but the
  "Why:" line was wrong every time. Several questions in one message: 1% (answers at most one, often merging them).
  Full tables: `train/test_run5/report.md`, `results.csv`.
- **Reading:** the model learned the behaviour-passage format (94% of chat data) far better than the 12 chat patterns
  (2,400 examples), even though every test question was seen in training. It has fluent English but little stored
  knowledge, and it copies formats ("It is an adjective", "Why:") without the content.
