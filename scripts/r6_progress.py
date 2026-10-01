#!/usr/bin/env python3
"""Run-6 chat generation progress: examples written and repaired per type, overall percentage.
  python scripts/r6_progress.py [--append train/chat_r6/progress.log]
Target: 1,000 per type for 13 types. Repaired = id ranges with a repair log in train/chat_r6/critic/.
"""
import glob, os, re, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TYPES = ['comprehension', 'dont_know', 'grammar', 'hinglish_esl', 'instruct', 'multi_question', 'multiturn',
         'reasoning', 'rewrite', 'summary', 'usage', 'vocab', 'writing']
T = 1000
rows, wrote, fixed = [], 0, 0
for t in TYPES:
    p = os.path.join(ROOT, 'train', 'chat_r6', t + '.jsonl')
    n = min(T, sum(1 for l in open(p) if l.strip())) if os.path.exists(p) else 0
    r = 0
    for f in glob.glob(os.path.join(ROOT, 'train', 'chat_r6', 'critic', f'repair_{t}_*_log.jsonl')):
        a, b = map(int, re.search(r'_(\d+)-(\d+)_log', f).groups()); r += b - a + 1
    r = min(r, n); wrote += n; fixed += r
    rows.append(f'{t:15s} {n:5d}/{T} written  {r:5d} repaired')
total = T * len(TYPES)
pct = 100 * (wrote + fixed) / (2 * total)        # generation and repair weighted equally
line = (f'{time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())}  overall {pct:.0f}%  '
        f'(written {wrote:,}/{total:,} = {100 * wrote / total:.0f}%, repaired {fixed:,}/{total:,} = {100 * fixed / total:.0f}%)')
print(line); print('\n'.join(rows))
if '--append' in sys.argv:
    out = sys.argv[sys.argv.index('--append') + 1]
    open(os.path.join(ROOT, out), 'a').write(line + '\n')
