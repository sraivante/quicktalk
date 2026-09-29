#!/usr/bin/env python3
"""Build batch json + paste-ready prompt files for a phase.
  python scripts/make_batches.py --phase pilot
  python scripts/make_batches.py --phase phase1
  python scripts/make_batches.py --phase full            (adds variant ids AFTER phase1 by default)
Options: --after phase1|pilot|none  --stage planning (one stage only)  --rows 10
Outputs (relative to the pack root):
  pilot  -> pilot/batches/NN_stage/vXX-YY_bNNNN.{json,txt}   outputs go to pilot/out/...
  others -> batches/NN_stage/...                              outputs go to out/...
  manifest_<phase>.csv next to the batches; prompts/MASTER.txt is (re)written.
"""
import argparse, csv, hashlib, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda *p: os.path.join(ROOT, *p)
ap = argparse.ArgumentParser()
ap.add_argument('--phase', required=True, choices=['pilot', 'phase1', 'full'])
ap.add_argument('--after', default=None, help='phase whose variant counts are already done (default: phase1 for full, none otherwise)')
ap.add_argument('--stage', default=None)
ap.add_argument('--csv', default=J('data', 'human_development_framework_v9.csv'))
ap.add_argument('--kg', default=J('kg'))
ap.add_argument('--prompts', default=J('prompts', 'training_data_prompt.md'))
ap.add_argument('--rows', type=int, default=None)
a = ap.parse_args()
cfg = json.load(open(J('config', 'variants.json'), encoding='utf-8'))
rec = json.load(open(J('config', 'recipes.json'), encoding='utf-8'))
AGES = rec['age_order']; RECIPES = rec['recipes']; TWISTS = rec['twists']
NAMES = json.load(open(J('config', 'names.json'), encoding='utf-8'))
def cast_for(key, recipe, n=2, used=None):
    """Deterministic names; `used` (a dict name->count for the current batch) keeps any name to at most 2 uses per batch."""
    pool = NAMES['global'] if recipe.split('+')[0] == 'R8' else NAMES['india']
    h = int(hashlib.sha1(str(key).encode()).hexdigest(), 16)
    out, i = [], 0
    while len(out) < n:
        nm = pool[(h + i * 7919) % len(pool)]; i += 1
        if nm in out or (used is not None and used.get(nm, 0) >= 2 and i < 10 * len(pool)): continue
        out.append(nm)
    if used is not None:
        for nm in out: used[nm] = used.get(nm, 0) + 1
    return out
RPB = a.rows or cfg['rows_per_batch']; PASS = cfg['pass_size']
after = a.after if a.after is not None else ('phase1' if a.phase == 'full' else 'none')
STAGES = [('core', None), ('expression', 'Expression & Mind State'), ('situational', 'Situational Awareness'), ('dynamics', 'Interaction Dynamics'), ('cognitive', 'Cognitive Machinery'), ('foundational', 'Foundational Concepts'), ('personality', 'Personality & Individual Difference'), ('group', 'Group Behaviour'), ('deception', 'Honesty, Deception & Influence'), ('culture', 'Culture & Society'), ('body', 'Body & Mind'), ('execution', 'Execution & Practical Skills'), ('wellbeing', 'Wellbeing, Wisdom & Conversation'), ('planning', 'Planning & Problem Solving'), ('graph', None)]
topic2stage = {t: k for k, t in STAGES if t}
tier_of = {s: t for t, d in cfg['tiers'].items() for s in d['stages']}
def count(phase, stage):
    return 0 if phase == 'none' else cfg['phases'][phase][tier_of[stage]]

md = open(a.prompts, encoding='utf-8').read()
def block(h):
    m = re.search(r'#+ \[' + re.escape(h) + r'\]\s*```text\n(.*?)\n```', md, re.S)
    if not m: sys.exit(f'missing prompt section [{h}]')
    return m.group(1)
master = block('MASTER'); batch_t = block('BATCH')
open(J('prompts', 'MASTER.txt'), 'w', encoding='utf-8').write(master)
ctx = {}
p = os.path.join(a.kg, 'row_context.jsonl')
if os.path.exists(p):
    for l in open(p, encoding='utf-8'):
        o = json.loads(l); ctx[o['sno']] = o['graph_context']
clusters = []
p = os.path.join(a.kg, 'clusters.jsonl')
if os.path.exists(p): clusters = [json.loads(l) for l in open(p, encoding='utf-8')]
else: print('note: kg/clusters.jsonl missing; graph stage skipped')

def recipe_for(sno, age, v):
    elig = [c for c, d in RECIPES.items() if AGES.index(d['min_age']) <= AGES.index(age)]
    h = int(hashlib.sha1(str(sno).encode()).hexdigest(), 16) % len(elig)
    code = elig[(h + v - 1) % len(elig)]
    t = (v - 1) // len(elig)
    return code if t == 0 else f'{code}+T{t}'
def recipe_lines(codes):
    out = {}
    for c in codes:
        b, _, t = c.partition('+')
        out[c] = RECIPES[b]['text'] + (' TWIST: ' + TWISTS[t] if t else '')
    return '\n'.join(f'{c}: {out[c]}' for c in sorted(out))
def passes(lo, hi):
    ids = list(range(lo, hi + 1))
    return [ids[i:i + PASS] for i in range(0, len(ids), PASS)]

rows = list(csv.DictReader(open(a.csv, encoding='utf-8-sig')))
by = {k: [] for k, _ in STAGES}
for r in rows:
    k = 'core' if int(r['S.No']) <= 317 else topic2stage.get(r['Topic'])
    if k is None: sys.exit('unmapped topic ' + r['Topic'])
    by[k].append(r)

def pilot_sample(rs, n):
    """stratified: round-robin over ages present, evenly spread inside each age (deterministic)"""
    groups = {g: [r for r in rs if r['Age'] == g] for g in AGES}
    groups = {g: v for g, v in groups.items() if v}
    picks = {}
    for g, v in groups.items():
        step = max(1, len(v) // n)
        picks[g] = [v[(i * step + len(v) // (2 * n)) % len(v)] for i in range(min(n, len(v)))]
    out, seen, i = [], set(), 0
    while len(out) < min(n, len(rs)) and i < 50:
        for g in groups:
            if i < len(picks[g]) and picks[g][i]['S.No'] not in seen and len(out) < n:
                seen.add(picks[g][i]['S.No']); out.append(picks[g][i])
        i += 1
    return sorted(out, key=lambda r: int(r['S.No']))

base = J('pilot') if a.phase == 'pilot' else ROOT
bdir = J('pilot', 'batches') if a.phase == 'pilot' else J('batches')
odir = J('pilot', 'out') if a.phase == 'pilot' else J('out')
manifest = []
def rel(p): return os.path.relpath(p, ROOT)
for si, (k, _) in enumerate(STAGES, 1):
    if a.stage and k != a.stage: continue
    hi = count(a.phase, k); lo = count(after, k) + 1
    if hi < lo: continue
    d = os.path.join(bdir, f'{si:02d}_{k}'); os.makedirs(d, exist_ok=True)
    if k == 'graph':
        if not clusters: continue
        cs = clusters
        if a.phase == 'pilot':
            seen, cs = set(), []
            for c in clusters:
                if c['type'] not in seen: seen.add(c['type']); cs.append(c)
        add = block('ADDENDUM graph')
        for bi in range(0, len(cs), cfg['clusters_per_batch']):
            chunk = cs[bi:bi + cfg['clusters_per_batch']]; n = bi // cfg['clusters_per_batch'] + 1
            _seen = {}
            chunk = [dict(c, cast=cast_for(c['cluster_id'], 'R1', 3, used=_seen)) for c in chunk]
            name = f'g_b{n:04d}'
            json.dump({'kind': 'cluster', 'stage': 'graph', 'variant_ids': [1], 'clusters': chunk}, open(os.path.join(d, name + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            pr = batch_t.replace('{{STAGE}}', 'graph (clusters of related framework rows)').replace('{{VARIANT_IDS}}', 'n/a (one record per cluster)').replace('{{V}}', '1').replace('{{N}}', str(len(chunk))).replace('{{TOTAL}}', str(len(chunk))).replace('{{RECIPES}}', 'not used in cluster mode').replace('{{ADDENDUM}}', add).replace('{{ROWS_JSON}}', '\n'.join(json.dumps(x, ensure_ascii=False) for x in chunk))
            open(os.path.join(d, name + '.txt'), 'w', encoding='utf-8').write(pr)
            manifest.append([a.phase, si, k, name, len(chunk), 1, len(chunk), chunk[0]['cluster_id'], chunk[-1]['cluster_id'], rel(os.path.join(d, name + '.txt')), rel(os.path.join(d, name + '.json')), rel(os.path.join(odir, f'{si:02d}_{k}', name + '.jsonl'))])
        continue
    add = block('ADDENDUM ' + k)
    rs = by[k] if a.phase != 'pilot' else pilot_sample(by[k], cfg['pilot_rows_per_stage'])
    for ids in passes(lo, hi):
        tag = f'v{ids[0]:02d}-{ids[-1]:02d}'
        for bi in range(0, len(rs), RPB):
            chunk = rs[bi:bi + RPB]; n = bi // RPB + 1; name = f'{tag}_b{n:04d}'
            recs, used, seen_names = [], [], {}
            for r in chunk:
                sno = int(r['S.No']); plan = {str(v): recipe_for(sno, r['Age'], v) for v in ids}; used += plan.values()
                cast = {v: cast_for(f'{sno}-{v}', c, used=seen_names) for v, c in plan.items()}
                o = {'sno': sno, 'plan': plan, 'cast': cast, 'age': r['Age'], 'topic': r['Topic'], 'subtopic': r['Subtopic'], 'subtype': r['Subtype'], 'description': r['Human Learning & Development']}
                if ctx.get(sno): o['graph_context'] = ctx[sno]
                recs.append(o)
            json.dump({'stage': k, 'variant_ids': ids, 'rows': recs}, open(os.path.join(d, name + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            total = len(recs) * len(ids)
            pr = batch_t.replace('{{STAGE}}', k).replace('{{VARIANT_IDS}}', ', '.join(map(str, ids))).replace('{{V}}', str(len(ids))).replace('{{N}}', str(len(recs))).replace('{{TOTAL}}', str(total)).replace('{{RECIPES}}', recipe_lines(set(used))).replace('{{ADDENDUM}}', add).replace('{{ROWS_JSON}}', '\n'.join(json.dumps(x, ensure_ascii=False) for x in recs))
            open(os.path.join(d, name + '.txt'), 'w', encoding='utf-8').write(pr)
            manifest.append([a.phase, si, k, name, len(recs), len(ids), total, recs[0]['sno'], recs[-1]['sno'], rel(os.path.join(d, name + '.txt')), rel(os.path.join(d, name + '.json')), rel(os.path.join(odir, f'{si:02d}_{k}', name + '.jsonl'))])
mp = os.path.join(bdir, f'manifest_{a.phase}.csv')
os.makedirs(bdir, exist_ok=True)
with open(mp, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['phase', 'stage_no', 'stage', 'batch', 'items', 'variants', 'records', 'first', 'last', 'prompt', 'batch_json', 'out']); w.writerows(manifest)
print(f'{a.phase}: {len(manifest)} batches, {sum(m[6] for m in manifest)} records expected. Manifest: {rel(mp)}')
