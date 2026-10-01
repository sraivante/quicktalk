#!/usr/bin/env python3
"""Find repeated or near-repeated user questions between run-6 chat files and all earlier chat data.
  python scripts/check_r6_dupes.py [type ...]      (default: every train/chat_r6/*.jsonl)
Compares the first user turn of each run-6 example with train/chat/, train/pilot/ and the rest of train/chat_r6/
(all types). Exact = same text after normalising; near = word-set overlap (Jaccard) >= 0.8 on turns of 6+ words.
Prints the run-6 ids to fix, one per line with what it matches.
"""
import glob, json, os, re, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(ROOT, 'train')
norm = lambda s: re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', s.lower())).strip()
def load(paths):
    for p in paths:
        for l in open(p, encoding='utf-8'):
            if l.strip():
                r = json.loads(l); yield r['metadata']['id'], norm(r['messages'][0]['content'])
r6_files = sorted(glob.glob(os.path.join(T, 'chat_r6', '*.jsonl'))) + sorted(glob.glob(os.path.join(T, 'chat_r7', '*.jsonl'))) + sorted(glob.glob(os.path.join(T, 'chat_r8', '*.jsonl')))
want = sys.argv[1:] or sorted({os.path.basename(p)[:-6] for p in r6_files})
old = list(load(sorted(glob.glob(os.path.join(T, 'chat', '*.jsonl'))) + sorted(glob.glob(os.path.join(T, 'pilot', '*.jsonl')))))
new = list(load(r6_files))
pool = old + new
index = collections.defaultdict(set)                 # word -> entries, for fast near-duplicate candidates
sets = [set(t.split()) for _, t in pool]
for k, s in enumerate(sets):
    for w in s: index[w].add(k)
exact = collections.defaultdict(list)
for k, (i, t) in enumerate(pool): exact[t].append(k)
n = 0
for k0, (i, t) in enumerate(pool):
    if k0 < len(old) or re.split(r'-r[678][ms]?-', i)[0] not in want: continue
    s = sets[k0]; hits = set()
    for k in exact[t]:
        if k != k0 and (k < k0 or k < len(old)): hits.add((pool[k][0], 'exact'))
    if len(s) >= 6:
        cand = collections.Counter(k for w in s for k in index[w] if k != k0)
        for k, c in cand.items():
            if (k < k0 or k < len(old)) and c / len(s | sets[k]) >= 0.8 and pool[k][1] != t: hits.add((pool[k][0], 'near'))
    for other, kind in sorted(hits):
        print(f'{i}\t{kind}\t{other}'); n += 1
print(f'# {n} repeats found', file=sys.stderr)
