#!/usr/bin/env python3
"""Progress and next work.
  python scripts/status.py                       summary per phase and stage
  python scripts/status.py next 5 [--phase phase1] [--stage core]   list next pending batches (prompt path, out path)
A batch counts as done only when its .ok marker exists (written by validate_jsonl.py --mark).
"""
import csv, glob, os, sys, re
from collections import defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = sys.argv[1:]
def opt(n):
    return args[args.index(n) + 1] if n in args else None
mans = sorted(glob.glob(os.path.join(ROOT, 'pilot', 'batches', 'manifest_*.csv')) + glob.glob(os.path.join(ROOT, 'batches', 'manifest_*.csv')))
if not mans: sys.exit('No manifests. Run scripts/make_batches.py --phase pilot first.')
items = []
for m in mans:
    for r in csv.DictReader(open(m, encoding='utf-8')):
        r['done'] = os.path.exists(os.path.join(ROOT, re.sub(r'\.jsonl$', '', r['out']) + '.ok')); r['has_out'] = os.path.exists(os.path.join(ROOT, r['out'])); items.append(r)
ph, st = opt('--phase'), opt('--stage')
if args and args[0] == 'next':
    n = int(args[1]) if len(args) > 1 and args[1].isdigit() else 5
    todo = [r for r in items if not r['done'] and (not ph or r['phase'] == ph) and (not st or r['stage'] == st)]
    order = {'pilot': 0, 'phase1': 1, 'full': 2}
    todo.sort(key=lambda r: (order[r['phase']], int(r['stage_no']), r['batch']))
    for r in todo[:n]:
        print(f"{r['phase']}\t{r['stage']}\t{r['batch']}\t{r['records']} records\tprompt={r['prompt']}\tbatch_json={r['batch_json']}\tout={r['out']}" + ('\t(output exists but not validated)' if r['has_out'] else ''))
    print(f'{len(todo)} pending in total')
    sys.exit(0)
agg = defaultdict(lambda: [0, 0, 0, 0])
for r in items:
    a = agg[(r['phase'], int(r['stage_no']), r['stage'])]; a[0] += 1; a[1] += r['done']; a[2] += int(r['records']); a[3] += int(r['records']) * r['done']
cur = None
for (p, no, s), a in sorted(agg.items(), key=lambda kv: ({'pilot': 0, 'phase1': 1, 'full': 2}[kv[0][0]], kv[0][1])):
    if p != cur: print(f'\n== {p} =='); cur = p
    print(f'  {no:02d} {s:<13} batches {a[1]:>4}/{a[0]:<4} records {a[3]:>6}/{a[2]:<6}')
for p in ['pilot', 'phase1', 'full']:
    b = [r for r in items if r['phase'] == p]
    if b: print(f"\n{p}: {sum(r['done'] for r in b)}/{len(b)} batches validated, {sum(int(r['records']) for r in b if r['done'])}/{sum(int(r['records']) for r in b)} records")
