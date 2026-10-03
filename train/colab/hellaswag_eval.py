#!/usr/bin/env python3
"""HellaSwag (common-sense sentence endings, 4 choices, random = 25%) for a QuickTalk checkpoint or a Hugging Face model.
The model writes nothing: for each item we add up the log-probability of each ending after the context and pick the
most likely one. Reports acc (sum of log-probs) and acc_norm (log-probs divided by the ending's length in characters,
the number usually published). Separate from training: it only reads a finished checkpoint.

  python hellaswag_eval.py --workdir W [--ckpt W/checkpoints/pretrain_final.pt] [--limit 0] [--out result.json]
  python hellaswag_eval.py --hf-model HuggingFaceTB/SmolLM2-135M                  # same scorer, for comparison
  python hellaswag_eval.py --workdir W --jsonl items.jsonl                          # local file (ctx_a, ctx_b, ...)
"""
import argparse, json, os, re, sys, time

def preprocess(text):  # same clean-up as the common evaluation harness
    text = text.strip().replace(' [title]', '. ')
    text = re.sub(r'\[.*?\]', '', text)
    return text.replace('  ', ' ')

def items(a):
    if a.jsonl: rows = [json.loads(l) for l in open(a.jsonl, encoding='utf-8') if l.strip()]
    else:
        from datasets import load_dataset
        rows = load_dataset('Rowan/hellaswag', split='validation')
    for r in rows:
        ctx = r['ctx_a'] + ' ' + r['ctx_b'].capitalize()
        yield (preprocess(r['activity_label'] + ': ' + ctx), [preprocess(e) for e in r['endings']], int(r['label']))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--workdir'); ap.add_argument('--ckpt'); ap.add_argument('--hf-model')
    ap.add_argument('--jsonl'); ap.add_argument('--limit', type=int, default=0); ap.add_argument('--out')
    ap.add_argument('--batch', type=int, default=64, help='endings scored per forward pass')
    a = ap.parse_args()
    import torch
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    if a.hf_model:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        htok = AutoTokenizer.from_pretrained(a.hf_model)
        model = AutoModelForCausalLM.from_pretrained(a.hf_model, torch_dtype=torch.float32).to(dev).eval()
        encode_all = lambda texts: htok(texts, add_special_tokens=False).input_ids     # fast tokenizer: all cores
        logits_of = lambda x: model(x).logits
        block, name = 2048, a.hf_model
    else:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import quicktalk_lm as q
        tok = q.load_tok(a.workdir)
        path = a.ckpt or os.path.join(a.workdir, 'checkpoints', 'pretrain_final.pt')
        s = torch.load(path, map_location=dev, weights_only=False)
        model = q.build_model(s['cfg']).to(dev); model.load_state_dict(s['model']); model.eval()
        encode_all = lambda texts: [e.ids for e in tok.encode_batch(texts)]           # all CPU cores
        logits_of = lambda x: model(x)[0]
        block, name = s['cfg']['block'], path
    torch.set_num_threads(os.cpu_count())
    half = torch.bfloat16 if dev == 'cuda' and torch.cuda.is_bf16_supported() else torch.float16   # T4: float16
    amp = torch.autocast('cuda', dtype=half) if dev == 'cuda' else torch.autocast('cpu', enabled=False)
    data = list(items(a))
    if a.limit: data = data[:a.limit]
    # tokenize everything up front in one batch call per list (uses every CPU core)
    ctx_ids = encode_all([c for c, _, _ in data])
    full_ids = encode_all([c + ' ' + e for c, ends, _ in data for e in ends])
    rows = []                                       # (item index, ending index, tokens, first ending position, ending chars)
    for i, (c, ends, _) in enumerate(data):
        for j, e in enumerate(ends):
            full, cc = full_ids[4 * i + j], ctx_ids[i]
            k = 0                                   # ending tokens start where the context tokens stop matching
            while k < min(len(cc), len(full) - 1) and cc[k] == full[k]: k += 1
            k = max(1, k)
            if len(full) > block: cut = len(full) - block; full = full[cut:]; k = max(1, k - cut)
            rows.append((i, j, full, k, len(e)))
    ll = [[0.0] * 4 for _ in data]
    order = sorted(range(len(rows)), key=lambda r: len(rows[r][2]))      # similar lengths together: little padding
    t0 = time.time()
    for bi in range(0, len(order), a.batch):
        batch = [rows[r] for r in order[bi:bi + a.batch]]
        L = max(len(r[2]) for r in batch)
        x = torch.zeros(len(batch), L, dtype=torch.long)
        for b, r in enumerate(batch): x[b, :len(r[2])] = torch.tensor(r[2])   # right padding: causal, so it never
        x = x.to(dev)                                                           # changes the scored positions
        with torch.no_grad(), amp: lp = torch.log_softmax(logits_of(x).float(), -1)
        for b, (i, j, full, k, _) in enumerate(batch):
            tgt = x[b, k:len(full)]
            ll[i][j] = lp[b, k - 1:len(full) - 1].gather(1, tgt[:, None]).sum().item()
        if (bi // a.batch) % 50 == 0: print(f'{bi + len(batch)}/{len(rows)} endings scored, {time.time() - t0:.0f}s', flush=True)
    right = right_norm = 0
    for i, (_, ends, label) in enumerate(data):
        right += max(range(4), key=lambda j: ll[i][j]) == label
        right_norm += max(range(4), key=lambda j: ll[i][j] / max(1, len(ends[j]))) == label
    n = len(data)
    res = {'model': name, 'items': n, 'acc': round(right / n, 4), 'acc_norm': round(right_norm / n, 4)}
    print(json.dumps(res))
    if a.out: json.dump(res, open(a.out, 'w'), indent=1)

if __name__ == '__main__':
    main()
