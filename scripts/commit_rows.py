#!/usr/bin/env python3
"""Commit validated data to a git repo, ONE FILE AND ONE COMMIT PER FRAMEWORK ROW.
  python scripts/commit_rows.py --repo ../quicktalk [--push-every 25] [--dry-run] [--include-pilot] [--limit N]
For every S.No that has validated records (batches with a .ok marker) it writes/merges
  <repo>/data/rows/<S.No zero-padded to 5>.jsonl      one record per line, all variants of that row, sorted by variant id
and makes a separate commit for that file. Re-running is safe: files are merged by variant id, and a row whose file did not
change gets no commit. Graph-stage records (no S.No) go to data/clusters/<cluster_id>.jsonl, one commit each.
Push happens every --push-every commits and at the end (branch --branch, default main).
"""
import argparse, glob, json, os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument('--repo', required=True); ap.add_argument('--branch', default='main')
ap.add_argument('--push-every', type=int, default=25); ap.add_argument('--limit', type=int, default=0)
ap.add_argument('--dry-run', action='store_true'); ap.add_argument('--include-pilot', action='store_true')
ap.add_argument('--no-push', action='store_true')
ap.add_argument('--trailer', default=os.environ.get('COMMIT_TRAILER', ''), help='text appended to every commit message, e.g. Co-Authored-By and Claude-Session lines for the current session')
a = ap.parse_args()
TRAILER = ('\n\n' + a.trailer.replace('\\n', '\n').strip() + '\n') if a.trailer.strip() else '\n'
def git(*args, check=True):
    r = subprocess.run(['git', '-C', a.repo, *args], capture_output=True, text=True)
    if check and r.returncode: sys.exit(f'git {" ".join(args)} failed: {r.stderr.strip()}')
    return r
if not os.path.isdir(os.path.join(a.repo, '.git')): sys.exit('--repo must be a git clone')
dirs = [os.path.join(ROOT, 'out')] + ([os.path.join(ROOT, 'pilot', 'out')] if a.include_pilot else [])
rows, clus = {}, {}
for d in dirs:
    for f in sorted(glob.glob(os.path.join(d, '**', '*.jsonl'), recursive=True)):
        if not os.path.exists(re.sub(r'\.jsonl$', '', f) + '.ok'): continue
        for l in open(f, encoding='utf-8'):
            if not l.strip(): continue
            r = json.loads(l)
            if str(r.get('passage', '')).strip() == 'SKIP': continue
            if 'cluster_id' in r: clus[r['cluster_id']] = r
            else: rows.setdefault(r['sno'], {})[r['variant']] = r
if not a.dry_run:
    if git('rev-parse', '--verify', 'HEAD', check=False).returncode == 0:
        git('checkout', a.branch, check=False)
        if not a.no_push: git('pull', '--rebase', 'origin', a.branch, check=False)
    else: git('checkout', '-B', a.branch)
    if not git('config', 'user.name', check=False).stdout.strip():
        git('config', 'user.name', 'Claude'); git('config', 'user.email', 'noreply@anthropic.com')
work = [(f'data/rows/{s:05d}.jsonl', f'row {s:05d}', rows[s]) for s in sorted(rows)] + [(f'data/clusters/{c}.jsonl', f'cluster {c}', {1: clus[c]}) for c in sorted(clus)]
commits = pushed = 0
def push():
    global pushed
    if a.no_push or a.dry_run or commits == pushed: return
    r = git('push', 'origin', f'HEAD:{a.branch}', check=False)
    if r.returncode: sys.exit('push failed (already-committed rows are safe locally; rerun to retry): ' + r.stderr.strip())
    pushed = commits
for rel, label, recs in work:
    path = os.path.join(a.repo, rel); merged = {}
    if os.path.exists(path):
        for l in open(path, encoding='utf-8'):
            if l.strip():
                o = json.loads(l); merged[o.get('variant', 1)] = o
    before = dict(merged); merged.update(recs)
    if merged == before: continue
    new = sorted(set(merged) - set(before)); ids = ', '.join(map(str, new))
    if a.dry_run: print(f'would commit {rel}: +variants {ids} (total {len(merged)})'); commits += 1
    else:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            for k in sorted(merged): f.write(json.dumps(merged[k], ensure_ascii=False) + '\n')
        git('add', rel); git('commit', '-m', f'{label}: add variants {ids} ({len(merged)} total)' + TRAILER); commits += 1
        if commits - pushed >= a.push_every: push()
    if a.limit and commits >= a.limit: break
push()
print(f'{commits} commit(s) made' + ('' if a.dry_run or a.no_push else f', {pushed} pushed to {a.branch}') + f'; rows with data: {len(rows)}, clusters: {len(clus)}')
