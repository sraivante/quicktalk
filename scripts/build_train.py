#!/usr/bin/env python3
"""Build the training and eval files under train/build/ from train/sources/, train/chat/, train/chat_r6/ and train/pilot/.
  python scripts/build_train.py [--seed 1234] [--chat-repeat 1]
Splits are by GROUP (all variants of one behaviour row, one chat example or shared source text stay together), so no
eval group leaks into training. Eval text is also removed from the pretraining corpus.
Writes (large files are split into parts under ~45 MB so they stay well inside GitHub's file limit):
  train/build/sft_train_NN.jsonl     all chat data mixed and shuffled (behaviour chats, 12 chat types, raga Q&A)
  train/build/eval/sft_eval_<type>.jsonl   held-out examples per chat type (and behaviour, raga)
  train/build/eval/sft_eval_all.jsonl      the same, combined
  train/build/pretrain_NN.txt        books + behaviour passages, shuffled by block, eval text removed
  train/build/eval/pretrain_eval.txt held-out book blocks and behaviour passages (for perplexity)
  train/build/manifest.json          seed, counts, mix, which groups went to eval
"""
import argparse, glob, hashlib, json, os, random, re, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(ROOT, 'train')
ap = argparse.ArgumentParser()
ap.add_argument('--seed', type=int, default=1234)
ap.add_argument('--chat-repeat', type=int, default=1, help='repeat the 12 chat-pattern types N times in sft_train (upsampling)')
ap.add_argument('--chat-eval', type=int, default=20, help='held-out examples per chat type')
ap.add_argument('--behaviour-eval-frac', type=float, default=0.02)
ap.add_argument('--book-eval-frac', type=float, default=0.01)
a = ap.parse_args()
OUT = os.path.join(T, 'build'); EV = os.path.join(OUT, 'eval')
os.makedirs(EV, exist_ok=True)
for f in glob.glob(os.path.join(OUT, '*.*')) + glob.glob(os.path.join(EV, '*.*')): os.remove(f)

def pick(key, frac):  # stable, seed-dependent choice of eval groups
    h = int(hashlib.sha256(f'{a.seed}:{key}'.encode()).hexdigest()[:12], 16)
    return h / 16 ** 12 < frac
def load(path):
    return [json.loads(l) for l in open(path, encoding='utf-8') if l.strip()]
norm = lambda s: re.sub(r'\s+', ' ', s).strip()

# ---- chat data -------------------------------------------------------------------------------
chat = collections.defaultdict(list)                       # type -> examples
for f in sorted(glob.glob(os.path.join(T, 'chat', '*.jsonl'))) + sorted(glob.glob(os.path.join(T, 'chat_r6', '*.jsonl'))) + sorted(glob.glob(os.path.join(T, 'chat_r7', '*.jsonl'))) + \
        sorted(glob.glob(os.path.join(T, 'pilot', '*.jsonl'))):   # chat_r6 = run 6 additions (1,000 per type)
    for r in load(f): chat[r['metadata']['type']].append(r)
behaviour = [r for f in sorted(glob.glob(os.path.join(T, 'sources', 'behaviour_chat_*.jsonl'))) for r in load(f)]
raga = load(os.path.join(T, 'sources', 'raga_qa.jsonl'))
for r in raga: r['metadata']['type'] = 'raga'
for r in behaviour: r['metadata']['type'] = 'behaviour'

train, evals, eval_groups = [], collections.defaultdict(list), collections.defaultdict(list)
rng = random.Random(a.seed)
for t, ex in sorted(chat.items()):
    groups = sorted({r['metadata']['group'] for r in ex}); rng.shuffle(groups)
    held, n = set(), 0
    by = collections.Counter(r['metadata']['group'] for r in ex)
    for g in groups:
        if n >= a.chat_eval: break
        held.add(g); n += by[g]
    tr = [r for r in ex if r['metadata']['group'] not in held]
    evals[t].extend(r for r in ex if r['metadata']['group'] in held)
    train.extend(tr * a.chat_repeat)
    eval_groups[t] = sorted(held)
for name, ex, frac in (('behaviour', behaviour, a.behaviour_eval_frac), ('raga', raga, 0.1)):
    for r in ex:
        g = r['metadata']['group']
        if pick(g, frac): evals[name].append(r); eval_groups[name].append(g)
        else: train.append(r)
    eval_groups[name] = sorted(set(eval_groups[name]))
rng.shuffle(train)

def write_parts(prefix, lines, ext, limit=45_000_000):
    parts, cur, size, k = [], [], 0, 1
    def flush():
        nonlocal cur, size, k
        if not cur: return
        p = f'{prefix}_{k:02d}.{ext}'; open(p, 'w', encoding='utf-8').write(''.join(cur)); parts.append(os.path.relpath(p, ROOT)); cur, size, k = [], 0, k + 1
    for l in lines:
        b = len(l.encode('utf-8'))
        if size + b > limit: flush()
        cur.append(l); size += b
    flush()
    return parts
sft_parts = write_parts(os.path.join(OUT, 'sft_train'), (json.dumps(r, ensure_ascii=False) + '\n' for r in train), 'jsonl')
for t, ex in evals.items():
    with open(os.path.join(EV, f'sft_eval_{t}.jsonl'), 'w', encoding='utf-8') as f:
        for r in ex: f.write(json.dumps(r, ensure_ascii=False) + '\n')
with open(os.path.join(EV, 'sft_eval_all.jsonl'), 'w', encoding='utf-8') as f:
    for t in sorted(evals):
        for r in evals[t]: f.write(json.dumps(r, ensure_ascii=False) + '\n')

# ---- pretraining corpus ----------------------------------------------------------------------
# text that appears in any eval example must not be in pretraining
eval_text = set()
for t, ex in evals.items():
    for r in ex:
        for m in r['messages']:
            if m['role'] == 'user':
                for c in re.split(r'\n\s*\n', m['content']):
                    if len(c.split()) >= 20: eval_text.add(norm(c))
eval_passages = {norm(r['messages'][0]['content'].split('\n\n', 1)[1].rsplit('\n\n', 1)[0]) for r in evals['behaviour']}
def has_eval(p):
    n = norm(p)
    return n in eval_passages or any(e in n for e in eval_text)
blocks, pre_eval, dropped = [], [], 0
for f in sorted(glob.glob(os.path.join(T, 'sources', 'books', '*.txt'))):
    if f.endswith('REPORT.txt'): continue
    paras = [p for p in open(f, encoding='utf-8').read().split('\n\n') if p.strip()]
    name = os.path.basename(f)[:-4]
    for b in range(0, len(paras), 40):                                 # blocks of 40 paragraphs keep local order
        chunk = paras[b:b + 40]
        if pick(f'{name}:{b}', a.book_eval_frac):
            pre_eval.append('\n\n'.join(chunk)); continue
        keep = [p for p in chunk if not has_eval(p)]; dropped += len(chunk) - len(keep)
        if keep: blocks.append('\n\n'.join(keep))
beh_paras = [p for p in open(os.path.join(T, 'sources', 'corpus_behaviour.txt'), encoding='utf-8').read().split('\n\n') if p.strip()]
for p in beh_paras:
    if norm(p) in eval_passages: pre_eval.append(p)
    elif has_eval(p): dropped += 1
    else: blocks.append(p)
rng.shuffle(blocks)
pre_parts = write_parts(os.path.join(OUT, 'pretrain'), (b + '\n\n' for b in blocks), 'txt')
open(os.path.join(EV, 'pretrain_eval.txt'), 'w', encoding='utf-8').write('\n\n'.join(pre_eval) + '\n')

# ---- manifest --------------------------------------------------------------------------------
cnt = collections.Counter(r['metadata']['type'] for r in train)
man = {'seed': a.seed, 'chat_repeat': a.chat_repeat,
       'sft_train': {'files': sft_parts, 'examples': len(train), 'by_type': dict(sorted(cnt.items())),
                     'share_pct': {k: round(100 * v / len(train), 2) for k, v in sorted(cnt.items())}},
       'sft_eval': {t: len(ex) for t, ex in sorted(evals.items())},
       'pretrain': {'files': pre_parts, 'blocks': len(blocks), 'words': sum(len(b.split()) for b in blocks),
                    'paragraphs_dropped_for_eval_overlap': dropped},
       'pretrain_eval': {'blocks': len(pre_eval), 'words': sum(len(b.split()) for b in pre_eval)},
       'eval_groups': eval_groups}
json.dump(man, open(os.path.join(OUT, 'manifest.json'), 'w'), indent=1)
print(json.dumps({k: v for k, v in man.items() if k != 'eval_groups'}, indent=1))
