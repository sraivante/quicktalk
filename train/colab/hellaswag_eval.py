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
    a = ap.parse_args()
    import torch
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    if a.hf_model:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        htok = AutoTokenizer.from_pretrained(a.hf_model)
        model = AutoModelForCausalLM.from_pretrained(a.hf_model, torch_dtype=torch.float32).to(dev).eval()
        encode = lambda s: htok(s, add_special_tokens=False).input_ids
        logits_of = lambda x: model(x).logits
        block, name = 2048, a.hf_model
    else:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import quicktalk_lm as q
        tok = q.load_tok(a.workdir)
        path = a.ckpt or os.path.join(a.workdir, 'checkpoints', 'pretrain_final.pt')
        s = torch.load(path, map_location=dev, weights_only=False)
        model = q.build_model(s['cfg']).to(dev); model.load_state_dict(s['model']); model.eval()
        encode = lambda t: tok.encode(t).ids
        logits_of = lambda x: model(x)[0]
        block, name = s['cfg']['block'], path
    n = right = right_norm = 0; t0 = time.time()
    half = torch.bfloat16 if dev == 'cuda' and torch.cuda.is_bf16_supported() else torch.float16   # T4: float16
    amp = torch.autocast('cuda', dtype=half) if dev == 'cuda' else torch.autocast('cpu', enabled=False)
    for ctx, ends, label in items(a):
        c = encode(ctx); scores, norms = [], []
        for e in ends:
            full = encode(ctx + ' ' + e)
            k = 0                                   # ending tokens start where the context tokens stop matching
            while k < min(len(c), len(full) - 1) and c[k] == full[k]: k += 1
            k = max(1, k)
            if len(full) > block: cut = len(full) - block; full = full[cut:]; k = max(1, k - cut)
            x = torch.tensor([full], device=dev)
            with torch.no_grad(), amp: lp = torch.log_softmax(logits_of(x)[0].float(), -1)
            tgt = x[0, k:]; ll = lp[k - 1:-1].gather(1, tgt[:, None]).sum().item()
            scores.append(ll); norms.append(ll / max(1, len(e)))
        n += 1; right += max(range(4), key=lambda i: scores[i]) == label; right_norm += max(range(4), key=lambda i: norms[i]) == label
        if n % 1000 == 0: print(f'{n} items  acc {right / n:.3f}  acc_norm {right_norm / n:.3f}  {time.time() - t0:.0f}s', flush=True)
        if a.limit and n >= a.limit: break
    res = {'model': name, 'items': n, 'acc': round(right / n, 4), 'acc_norm': round(right_norm / n, 4)}
    print(json.dumps(res))
    if a.out: json.dump(res, open(a.out, 'w'), indent=1)

if __name__ == '__main__':
    main()
