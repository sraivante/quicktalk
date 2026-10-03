#!/usr/bin/env python3
"""Answer a QuickTalk test set with a local Hugging Face causal model that uses BOS/role-token chat format
(e.g. the 11M "English discussion" GPT-2: [BOS] then per turn <|user|>/<|assistant|> + content + <|eos|>).
Decoding matches scripts/test_model_run.py exactly: greedy, repetition penalty on the answer's own tokens only
(not the prompt), 300 new tokens for long categories and 200 otherwise, prompt kept whole while 64+ tokens are left.
  python scripts/test_hf_local_run.py --model-dir DIR --testset T.jsonl --out A.jsonl [--rep-penalty 1.3]
Resumes: items already in --out are skipped."""
import argparse, json, os, time
import torch
from tokenizers import Tokenizer
from transformers import AutoModelForCausalLM

ap = argparse.ArgumentParser()
ap.add_argument('--model-dir', required=True); ap.add_argument('--testset', required=True); ap.add_argument('--out', required=True)
ap.add_argument('--rep-penalty', type=float, default=1.3); ap.add_argument('--threads', type=int, default=os.cpu_count())
a = ap.parse_args()
torch.set_num_threads(a.threads)
LONG = {'story', 'writing', 'multi_question', 'multiline_complex', 'multiline_simple', 'gsm8k_test', 'laghumath_seen'}
tok = Tokenizer.from_file(os.path.join(a.model_dir, 'tokenizer.json')); tok.encode_special_tokens = True
model = AutoModelForCausalLM.from_pretrained(a.model_dir, local_files_only=True, dtype=torch.float32).eval()
BLOCK = model.config.n_positions
S = {n: tok.token_to_id(n) for n in ('<|bos|>', '<|eos|>', '<|user|>', '<|assistant|>')}
ROLE = {'user': S['<|user|>'], 'assistant': S['<|assistant|>']}

def prompt_ids(messages):
    ids = [S['<|bos|>']]
    for m in messages: ids += [ROLE[m['role']]] + tok.encode(m['content'].strip(), add_special_tokens=False).ids + [S['<|eos|>']]
    return ids + [S['<|assistant|>']]

@torch.no_grad()
def generate(messages, max_new):
    ids = prompt_ids(messages)
    truncated = len(ids) > BLOCK - 64
    if truncated: ids = [S['<|bos|>']] + ids[-(BLOCK - 65):]
    max_new = min(max_new, BLOCK - len(ids))
    o = model(torch.tensor([ids]), use_cache=True); past, logits = o.past_key_values, o.logits[0, -1]
    out = []
    for _ in range(max_new):
        logits = logits.float().clone()
        if a.rep_penalty != 1.0 and out:
            seen = torch.tensor(sorted(set(out)))
            logits[seen] = torch.where(logits[seen] > 0, logits[seen] / a.rep_penalty, logits[seen] * a.rep_penalty)
        nxt = int(logits.argmax())
        if nxt in (S['<|eos|>'], S['<|bos|>']): break
        out.append(nxt)
        o = model(torch.tensor([[nxt]]), past_key_values=past, use_cache=True); past, logits = o.past_key_values, o.logits[0, -1]
    return tok.decode(out, skip_special_tokens=True).strip(), truncated, len(out)

items = [json.loads(l) for l in open(a.testset, encoding='utf-8')]
done = {json.loads(l)['id'] for l in open(a.out, encoding='utf-8')} if os.path.exists(a.out) else set()
t0 = time.time()
with open(a.out, 'a', encoding='utf-8') as f:
    for n, it in enumerate(items, 1):
        if it['id'] in done: continue
        msgs = it.get('history', []) + [{'role': 'user', 'content': it['question']}]
        ans, trunc, ntok = generate(msgs, 300 if it['category'] in LONG else 200)
        f.write(json.dumps({'id': it['id'], 'answer': ans, 'prompt_truncated': trunc, 'new_tokens': ntok,
                            'decoding': {'temperature': 0.0, 'rep_penalty': a.rep_penalty}}, ensure_ascii=False) + '\n'); f.flush()
        if n % 50 == 0: print(f'{n}/{len(items)} {time.time() - t0:.0f}s', flush=True)
print('done', len(items), f'{time.time() - t0:.0f}s')
