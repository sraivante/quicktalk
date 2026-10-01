# Training on Google Colab (A100)

Open `quicktalk_train.ipynb` in Colab (File > Open notebook > GitHub, or upload it), set the runtime to A100, and
Run all. Details are in the notebook's first cell.

- `quicktalk_lm.py`: the whole pipeline (tokenizer, token files, size plan, training with resume, chat). Works from
  the command line too; `--allow-cpu` lets you smoke-test it without a GPU.
- State lives in `MyDrive/quicktalk_run/`: `tokenizer.json`, `data/*.bin`, `plan.json`, `checkpoints/`
  (`<stage>_latest.pt` every 5 min / 200 steps, previous one kept as `_prev`, `<stage>_final.pt` at the end),
  `log_<stage>.csv`, `train.log`.
- Size rule: tokens seen = 10 x parameters. With the current data (13.7M pretraining + 15.3M chat tokens, 16k BPE
  vocab), 4 pretraining passes + 2 chat passes = 85M tokens -> ~8.5M target -> 8.9M-parameter model (d=256, 6 layers,
  4 heads, 512 context).
- Chat format: `<|user|>\n...<|end|>\n<|assistant|>\n...<|end|>\n ... <|endoftext|>`; loss only on assistant text.
