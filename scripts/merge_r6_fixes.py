#!/usr/bin/env python3
"""Merge run-6 repair files into train/chat_r6/<type>.jsonl, replacing lines by id.
  python scripts/merge_r6_fixes.py [--dir train/chat] .staging/r6_repair/<type>_<first>-<last>.jsonl [...]
--dir picks the data folder (default train/chat_r6; also train/chat, train/pilot, train/chat_r7).
Each fixes file holds full corrected JSON lines (same id). Ids not in the target are reported and skipped. The target
is rewritten atomically and keeps its order. Run validate_chat.py on the target afterwards.
"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = sys.argv[1:]
ddir = os.path.join(ROOT, 'train', 'chat_r6')
if args and args[0] == '--dir': ddir = os.path.join(ROOT, args[1]); args = args[2:]
for fx in args:
    t = re.match(r'(.+?)_\d+-\d+\.jsonl$', os.path.basename(fx)).group(1)
    target = os.path.join(ddir, t + '.jsonl')
    fixes = {}
    for l in open(fx, encoding='utf-8'):
        if l.strip():
            r = json.loads(l); fixes[r['metadata']['id']] = json.dumps(r, ensure_ascii=False)
    lines = [l.rstrip('\n') for l in open(target, encoding='utf-8') if l.strip()]
    ids = [json.loads(l)['metadata']['id'] for l in lines]
    missing = [i for i in fixes if i not in ids]
    out = [fixes.get(i, l) for i, l in zip(ids, lines)]
    tmp = target + '.tmp'; open(tmp, 'w', encoding='utf-8').write('\n'.join(out) + '\n'); os.replace(tmp, target)
    print(f'{os.path.basename(fx)}: {len(fixes) - len(missing)} lines replaced in {t}.jsonl' + (f'; not found: {missing}' if missing else ''))
