#!/usr/bin/env python3
"""Chat with LMLM_97M_1 (QuickTalk run 8). Needs: torch, tokenizers, safetensors.

  python inference.py                         # interactive chat
  python inference.py "Good morning!"         # one question
  python inference.py --base "Once upon a time"   # plain text continuation with the base model

Default decoding is the one used in the published tests: greedy (temperature 0), repetition penalty 1.3.
"""
import argparse, json, os, sys
import torch
from tokenizers import Tokenizer
from safetensors.torch import load_file

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from quicktalk_lm import build_model, chat_text

def load(weights):
    cfg = json.load(open(os.path.join(HERE, 'config.json')))
    model = build_model(cfg); model.load_state_dict(load_file(os.path.join(HERE, weights))); model.eval()
    return model, cfg, Tokenizer.from_file(os.path.join(HERE, 'tokenizer.json'))

@torch.no_grad()
def generate(model, cfg, tok, ids, max_new=200, temperature=0.0, top_k=50, rep_penalty=1.3, stop=()):
    max_new = min(max_new, cfg['block'] - len(ids))
    x = torch.tensor([ids]); out = []
    for _ in range(max_new):
        logits = model(x)[0][0, -1].float()
        if rep_penalty != 1.0 and out:                    # discourage tokens already used in this reply
            seen = torch.tensor(sorted(set(out)))
            logits[seen] = torch.where(logits[seen] > 0, logits[seen] / rep_penalty, logits[seen] * rep_penalty)
        if temperature <= 0: nxt = int(logits.argmax())
        else:
            logits = logits / temperature
            v, _ = torch.topk(logits, top_k); logits[logits < v[-1]] = -float('inf')
            nxt = torch.multinomial(torch.softmax(logits, -1), 1).item()
        if nxt in stop: break
        out.append(nxt); x = torch.cat([x, torch.tensor([[nxt]])], 1)
    return tok.decode(out).strip()

def reply(model, cfg, tok, history, **kw):
    """history: list of {'role': 'user'|'assistant', 'content': str}, ending with the user's turn."""
    text = ''.join(t for t, _ in chat_text(history))[:-len('<|endoftext|>')] + '<|assistant|>\n'
    ids = tok.encode(text).ids[-(cfg['block'] - 64):]
    stop = (tok.token_to_id('<|end|>'), tok.token_to_id('<|endoftext|>'))
    return generate(model, cfg, tok, ids, stop=stop, **kw)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('prompt', nargs='*'); ap.add_argument('--base', action='store_true', help='use base_model.safetensors')
    ap.add_argument('--temperature', type=float, default=0.0); ap.add_argument('--rep-penalty', type=float, default=1.3)
    ap.add_argument('--max-new', type=int, default=200)
    a = ap.parse_args()
    kw = dict(temperature=a.temperature, rep_penalty=a.rep_penalty, max_new=a.max_new)
    if a.base:
        model, cfg, tok = load('base_model.safetensors')
        print(generate(model, cfg, tok, tok.encode(' '.join(a.prompt)).ids, stop=(tok.token_to_id('<|endoftext|>'),), **kw))
        sys.exit()
    model, cfg, tok = load('model.safetensors')
    if a.prompt:
        print(reply(model, cfg, tok, [{'role': 'user', 'content': ' '.join(a.prompt)}], **kw)); sys.exit()
    history = []
    while True:
        q = input('you> ').strip()
        if not q: break
        history.append({'role': 'user', 'content': q})
        r = reply(model, cfg, tok, history, **kw); print('model>', r)
        history.append({'role': 'assistant', 'content': r})
