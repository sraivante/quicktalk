#!/usr/bin/env python3
"""Re-validate newly finished generator outputs and commit them.
  python3 scripts/sync_out.py [--trailer "Co-Authored-By: ...\\nClaude-Session: ..."] [--no-push]
For every out/**/*.jsonl that has a .ok marker and is not yet committed (or changed): re-run validate_jsonl.py.
Pass -> git add the .jsonl + .ok. Fail -> move the .jsonl to .staging/needs_repair/<same path>, delete the .ok, and list it in .staging/needs_repair.txt (repair later with REPAIR_AGENT.md).
Then one commit + push to the current branch."""
import glob, os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
args = sys.argv[1:]
trailer = args[args.index('--trailer') + 1].replace('\\n', '\n') if '--trailer' in args else ''
def git(*a): return subprocess.run(['git', *a], capture_output=True, text=True)
changed = set(l[3:] for l in git('status', '--porcelain', '--untracked-files=all', 'out').stdout.splitlines())
ok, bad = [], []
for f in sorted(glob.glob('out/**/*.jsonl', recursive=True)):
    mark = f[:-6] + '.ok'
    if not os.path.exists(mark) or (f not in changed and mark not in changed): continue
    bj = re.sub(r'^out/', 'batches/', f)[:-6] + '.json'
    r = subprocess.run([sys.executable, 'scripts/validate_jsonl.py', bj, f], capture_output=True, text=True)
    if r.returncode == 0: ok.append(f); git('add', f, mark)
    else:
        bad.append(f); dest = os.path.join('.staging', 'needs_repair', f); os.makedirs(os.path.dirname(dest), exist_ok=True)
        os.replace(f, dest); os.remove(mark)
        open(os.path.join('.staging', 'needs_repair.txt'), 'a').write(bj + '\t' + f + '\n')
        print('RE-CHECK FAILED, moved to .staging/needs_repair/:', f, '|', r.stdout.strip().splitlines()[-1])
if ok:
    msg = f'Phase data: add {len(ok)} validated batch(es)\n\n' + '\n'.join(ok[:40]) + ('\n...' if len(ok) > 40 else '') + ('\n\n' + trailer if trailer else '')
    git('commit', '-q', '-m', msg)
    if '--no-push' not in args:
        br = git('rev-parse', '--abbrev-ref', 'HEAD').stdout.strip()
        p = git('push', '-q', 'origin', br); print('push:', 'ok' if p.returncode == 0 else p.stderr.strip())
print(f'committed {len(ok)} batch(es); failed re-check {len(bad)}')
