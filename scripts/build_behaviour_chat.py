#!/usr/bin/env python3
"""Turn the committed behaviour records into training sources under train/sources/.
  python scripts/build_behaviour_chat.py
Reads data/rows/*.jsonl and data/clusters/*.jsonl (already validated; config/export_exclude.txt ids are skipped).
Writes:
  train/sources/behaviour_chat_NN.jsonl one chat per record (split into parts of 15,000 to stay well under GitHub's file limit): the passage plus its questions as a multi-turn conversation
                                        {"messages":[{"role","content"}...], "metadata":{id, group, ...}}
  train/sources/corpus_behaviour.txt    every passage once, separated by a blank line (pretraining text)
`metadata.group` is the S.No (or cluster id): all variants of a row share it, so train/eval splits must split by group.
"""
import glob, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
xp = os.path.join(ROOT, 'config', 'export_exclude.txt')
EXCL = {l.split('#')[0].strip() for l in open(xp, encoding='utf-8')} - {''} if os.path.exists(xp) else set()
out = os.path.join(ROOT, 'train', 'sources'); os.makedirs(out, exist_ok=True)
files = sorted(glob.glob(os.path.join(ROOT, 'data', 'rows', '*.jsonl'))) + sorted(glob.glob(os.path.join(ROOT, 'data', 'clusters', '*.jsonl')))
n = nq = skipped = 0
PART = 15000
for old in glob.glob(os.path.join(out, 'behaviour_chat*.jsonl')): os.remove(old)
fc = None
with open(os.path.join(out, 'corpus_behaviour.txt'), 'w', encoding='utf-8') as fp:
    for f in files:
        for line in open(f, encoding='utf-8'):
            if not line.strip(): continue
            r = json.loads(line)
            p = r['passage'].strip()
            rid = r['cluster_id'] if 'cluster_id' in r else f"{r['sno']}-{r['variant']}"
            if p == 'SKIP' or rid in EXCL: skipped += 1; continue
            msgs = []
            for i, q in enumerate(r['qa']):
                msgs.append({'role': 'user', 'content': f"Read this:\n\n{p}\n\n{q['q']}" if i == 0 else q['q']})
                msgs.append({'role': 'assistant', 'content': q['a']})
            meta = {'source': 'behaviour', 'id': rid, 'group': r.get('cluster_id') or f"sno{r['sno']}",
                    'age': r.get('age'), 'topic': r.get('topic'), 'subtype': r.get('subtype') or r.get('type'),
                    'qa_types': [q['type'] for q in r['qa']]}
            if n % PART == 0:
                if fc: fc.close()
                fc = open(os.path.join(out, f'behaviour_chat_{n // PART + 1:02d}.jsonl'), 'w', encoding='utf-8')
            fc.write(json.dumps({'messages': msgs, 'metadata': meta}, ensure_ascii=False) + '\n')
            fp.write(p + '\n\n')
            n += 1; nq += len(r['qa'])
if fc: fc.close()
print(f'behaviour chats: {n} (qa turns {nq}); skipped {skipped}')
