#!/usr/bin/env python3
"""Run a trained QuickTalk model over a test set (from test_model_build.py) and save its answers.
  python scripts/test_model_run.py --ckpt sft_final.pt --tokenizer tokenizer.json \
      [--testset train/test_run5/testset.jsonl] [--out train/test_run5/answers.jsonl] [--temperature 0]
Same prompt format and repetition penalty as `quicktalk_lm.py chat`, but with a KV cache so it runs fast on CPU.
--temperature 0 = greedy (deterministic, the default for testing). Resumes: items already in --out are skipped.
"""
import argparse, importlib.util, json, os, sys, time
import torch, torch.nn.functional as F
from tokenizers import Tokenizer
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('qlm', os.path.join(ROOT, 'train', 'colab', 'quicktalk_lm.py'))
qlm = importlib.util.module_from_spec(spec); spec.loader.exec_module(qlm)

ap = argparse.ArgumentParser()
ap.add_argument('--ckpt', required=True); ap.add_argument('--tokenizer', required=True)
ap.add_argument('--testset', default=os.path.join(ROOT, 'train', 'test_run5', 'testset.jsonl'))
ap.add_argument('--out', default=os.path.join(ROOT, 'train', 'test_run5', 'answers.jsonl'))
ap.add_argument('--temperature', type=float, default=0.0); ap.add_argument('--top-k', type=int, default=50)
ap.add_argument('--rep-penalty', type=float, default=1.3); ap.add_argument('--seed', type=int, default=1234)
ap.add_argument('--threads', type=int, default=os.cpu_count())
a = ap.parse_args()
torch.set_num_threads(a.threads); torch.manual_seed(a.seed)
LONG = {'story', 'writing', 'multi_question', 'multiline_complex', 'multiline_simple', 'gsm8k_test', 'laghumath_seen'}

s = torch.load(a.ckpt, map_location='cpu', weights_only=False)
cfg = s['cfg']; model = qlm.build_model(cfg)
model.load_state_dict({k: v.float() for k, v in s['model'].items()}); model.eval()
tok = Tokenizer.from_file(a.tokenizer)
END, EOT = tok.token_to_id('<|end|>'), tok.token_to_id('<|endoftext|>')

def rope(x, cos, sin):
    x1, x2 = x[..., ::2], x[..., 1::2]
    return torch.stack((x1 * cos - x2 * sin, x1 * sin + x2 * cos), -1).flatten(-2)

@torch.no_grad()
def step(ids, cache, pos):
    """Forward new tokens `ids` (1 x T) at positions pos..pos+T-1, appending K/V to `cache`; returns last logits."""
    x = model.emb(ids); T = ids.shape[1]
    cos, sin = model.cos[:, :, pos:pos + T], model.sin[:, :, pos:pos + T]
    for i, b in enumerate(model.blocks):
        B, _, C = x.shape
        q, k, v = b.qkv(b.n1(x)).split(C, -1)
        q, k, v = (t.view(B, T, b.h, C // b.h).transpose(1, 2) for t in (q, k, v))
        q, k = rope(q, cos, sin), rope(k, cos, sin)
        if i < len(cache): k = torch.cat([cache[i][0], k], 2); v = torch.cat([cache[i][1], v], 2); cache[i] = (k, v)
        else: cache.append((k, v))
        y = F.scaled_dot_product_attention(q, k, v, is_causal=(T > 1))   # prefill: causal; single step: sees all
        x = x + b.proj(y.transpose(1, 2).reshape(B, T, C))
        x = x + b.out(F.gelu(b.fc(b.n2(x))))
    return (model.norm(x[:, -1]) @ model.emb.weight.T)[0]

def generate(messages, max_new):
    text = ''.join(t for t, _ in qlm.chat_text(messages))[:-len('<|endoftext|>')] + '<|assistant|>\n'
    ids = tok.encode(text).ids
    truncated = len(ids) > cfg['block'] - 64             # keep the whole prompt whenever 64+ tokens are left to answer
    if truncated: ids = ids[-(cfg['block'] - 64):]
    max_new = min(max_new, cfg['block'] - len(ids))     # long prompts get a shorter answer budget instead of a cut prompt
    cache, out = [], []
    logits = step(torch.tensor([ids]), cache, 0); pos = len(ids)
    for _ in range(max_new):
        logits = logits.float().clone()
        if a.rep_penalty != 1.0 and out:
            seen = torch.tensor(sorted(set(out)))
            logits[seen] = torch.where(logits[seen] > 0, logits[seen] / a.rep_penalty, logits[seen] * a.rep_penalty)
        if a.temperature <= 0: nxt = int(logits.argmax())
        else:
            logits = logits / a.temperature
            v, _ = torch.topk(logits, a.top_k); logits[logits < v[-1]] = -float('inf')
            nxt = torch.multinomial(torch.softmax(logits, -1), 1).item()
        if nxt in (END, EOT): break
        out.append(nxt)
        logits = step(torch.tensor([[nxt]]), cache, pos); pos += 1
    return tok.decode(out).strip(), truncated, len(out)

items = [json.loads(l) for l in open(a.testset, encoding='utf-8')]
done = set()
if os.path.exists(a.out): done = {json.loads(l)['id'] for l in open(a.out, encoding='utf-8')}
t0 = time.time()
with open(a.out, 'a', encoding='utf-8') as f:
    for n, it in enumerate(items, 1):
        if it['id'] in done: continue
        msgs = it['history'] + [{'role': 'user', 'content': it['question']}]
        ans, trunc, ntok = generate(msgs, 300 if it['category'] in LONG else 200)
        f.write(json.dumps({'id': it['id'], 'answer': ans, 'prompt_truncated': trunc, 'new_tokens': ntok,
                            'decoding': {'temperature': a.temperature, 'rep_penalty': a.rep_penalty, 'top_k': a.top_k}},
                           ensure_ascii=False) + '\n'); f.flush()
        if n % 25 == 0: print(f'{n}/{len(items)} {time.time() - t0:.0f}s', flush=True)
print('done', len(items), f'{time.time() - t0:.0f}s')
