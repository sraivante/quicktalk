#!/usr/bin/env python3
"""Merge validated outputs into training files under export/.
  python scripts/export_dataset.py [--include-pilot] [--all]
Default: only batches with a .ok marker. --all also takes unmarked .jsonl files (validate them first!).
Writes: export/records.jsonl (everything, deduped by (sno,variant) / cluster_id), export/pretrain.jsonl ({"text": passage}),
        export/qa.jsonl ({"context","question","answer","type",meta}), export/report.txt (counts, near-duplicates).
Records listed in config/export_exclude.txt (cluster id like C0830, or sno-variant) are left out.
"""
import glob, json, os, re, sys
from collections import Counter, defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = sys.argv[1:]
dirs = [os.path.join(ROOT, 'out')] + ([os.path.join(ROOT, 'pilot', 'out')] if '--include-pilot' in args else [])
STOP = set('the a an and or of to in on at for with is was were be been it that this he she they his her their as by from but not so if then than'.split())
cw = lambda s: {w for w in re.findall(r"[a-z']+", s.lower()) if w not in STOP and len(w) > 2}
recs, seen, skipped, files = {}, set(), 0, 0
# ids dropped after review (one per line: C0830 or sno-variant; text after # is the reason)
xp = os.path.join(ROOT, 'config', 'export_exclude.txt')
EXCL = {l.split('#')[0].strip() for l in open(xp, encoding='utf-8')} - {''} if os.path.exists(xp) else set()
excluded = 0
for d in dirs:
    for f in sorted(glob.glob(os.path.join(d, '**', '*.jsonl'), recursive=True)):
        if '--all' not in args and not os.path.exists(re.sub(r'\.jsonl$', '', f) + '.ok'): continue
        files += 1
        for l in open(f, encoding='utf-8'):
            if not l.strip(): continue
            r = json.loads(l)
            if str(r.get('passage', '')).strip() == 'SKIP': skipped += 1; continue
            k = ('c', r['cluster_id']) if 'cluster_id' in r else (r['sno'], r['variant'])
            if (r['cluster_id'] if k[0] == 'c' else f"{r['sno']}-{r['variant']}") in EXCL: excluded += 1; continue
            recs[k] = r
os.makedirs(os.path.join(ROOT, 'export'), exist_ok=True)
E = lambda n: open(os.path.join(ROOT, 'export', n), 'w', encoding='utf-8')
fr, fp, fq = E('records.jsonl'), E('pretrain.jsonl'), E('qa.jsonl'); nq = 0
for k, r in recs.items():
    fr.write(json.dumps(r, ensure_ascii=False) + '\n'); fp.write(json.dumps({'text': r['passage']}, ensure_ascii=False) + '\n')
    meta = {'id': f"c{r['cluster_id']}" if 'cluster_id' in r else f"{r['sno']}-{r['variant']}", 'topic': r.get('topic'), 'age': r.get('age'), 'subtype': r.get('subtype') or r.get('type')}
    for q in r['qa']:
        fq.write(json.dumps({'context': r['passage'], 'question': q['q'], 'answer': q['a'], 'type': q['type'], **meta}, ensure_ascii=False) + '\n'); nq += 1
for f in (fr, fp, fq): f.close()
by = defaultdict(list)
for k, r in recs.items():
    if k[0] != 'c': by[k[0]].append(r)
near = []
for sno, rs in by.items():
    for i in range(len(rs)):
        for j in range(i + 1, len(rs)):
            a, b = cw(rs[i]['passage']), cw(rs[j]['passage'])
            if a and b and len(a & b) / len(a | b) > 0.5: near.append((sno, rs[i]['variant'], rs[j]['variant'], round(len(a & b) / len(a | b), 2)))
dup = [t for t, c in Counter(r['passage'] for r in recs.values()).items() if c > 1]
L = [f'files used: {files}', f'records: {len(recs)}', f'qa pairs: {nq}', f'SKIP records dropped: {skipped}', f'excluded after review: {excluded}', f'distinct rows covered: {len(by)}', f'exact duplicate passages: {len(dup)}', f'near-duplicate variant pairs (Jaccard>0.5): {len(near)}'] + [f'  sno {s} v{a} v{b} {j}' for s, a, b, j in near[:50]]
open(os.path.join(ROOT, 'export', 'report.txt'), 'w', encoding='utf-8').write('\n'.join(L) + '\n'); print('\n'.join(L[:8]))
