"""Answer the offline test with a Hugging Face chat model (reference baseline, e.g. SmolLM2-135M-Instruct).
Same questions, history and answer budgets as scripts/test_model_run.py: greedy decoding, repetition penalty 1.3,
300 new tokens for long categories, 200 otherwise. Output lines match test_model_run.py ({"id", "answer", ...}).
  python scripts/test_hf_model.py --model HuggingFaceTB/SmolLM2-135M-Instruct --testset T.jsonl --out A.jsonl
Note: the HF repetition penalty also counts prompt tokens (test_model_run.py counts only the answer so far)."""
import argparse, json, os, time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ap = argparse.ArgumentParser()
ap.add_argument('--model', default='HuggingFaceTB/SmolLM2-135M-Instruct')
ap.add_argument('--testset', required=True); ap.add_argument('--out', required=True)
ap.add_argument('--rep-penalty', type=float, default=1.3)
a = ap.parse_args()
LONG = {'story', 'writing', 'multi_question', 'multiline_complex', 'multiline_simple', 'gsm8k_test', 'laghumath_seen'}
dev = 'cuda' if torch.cuda.is_available() else 'cpu'
tok = AutoTokenizer.from_pretrained(a.model)
model = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=torch.float32).to(dev).eval()
items = [json.loads(l) for l in open(a.testset, encoding='utf-8')]
done = {json.loads(l)['id'] for l in open(a.out, encoding='utf-8')} if os.path.exists(a.out) else set()
t0 = time.time()
with open(a.out, 'a', encoding='utf-8') as f:
    for n, it in enumerate(items, 1):
        if it['id'] in done: continue
        msgs = it['history'] + [{'role': 'user', 'content': it['question']}]
        ids = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors='pt').to(dev)
        with torch.no_grad():
            out = model.generate(ids, max_new_tokens=300 if it['category'] in LONG else 200, do_sample=False,
                                 repetition_penalty=a.rep_penalty, pad_token_id=tok.eos_token_id)
        new = out[0, ids.shape[1]:]
        f.write(json.dumps({'id': it['id'], 'answer': tok.decode(new, skip_special_tokens=True).strip(),
                            'prompt_truncated': False, 'new_tokens': int(new.shape[0]),
                            'decoding': {'model': a.model, 'temperature': 0.0, 'rep_penalty': a.rep_penalty}},
                           ensure_ascii=False) + '\n'); f.flush()
        if n % 25 == 0: print(f'{n}/{len(items)} {time.time() - t0:.0f}s', flush=True)
print('done', len(items), f'{time.time() - t0:.0f}s')
