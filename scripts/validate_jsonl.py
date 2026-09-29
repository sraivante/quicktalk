#!/usr/bin/env python3
"""Validate a generated JSONL file against its batch json.
Usage: python scripts/validate_jsonl.py <batch.json> <out.jsonl> [--mark]
Prints failures and the sno values (or cluster ids) to regenerate. Exit code 1 if any failure.
--mark writes <out>.ok when everything passed (status.py counts only marked batches).
"""
import json, re, sys, difflib
from collections import defaultdict
ARGS=[x for x in sys.argv[1:] if not x.startswith('--')]; MARK='--mark' in sys.argv
bj=json.load(open(ARGS[0],encoding='utf-8')); IDS=bj['variant_ids']; V=len(IDS); rows={r['sno']:r for r in bj.get('rows',[])}
OUT=ARGS[1]
def finish(code):
    if code==0 and MARK: open(re.sub(r'\.jsonl$','',OUT)+'.ok','w').write('ok\n')
    sys.exit(code)
WORDS={'1–3':(40,80),'4–6':(50,100),'7–12':(70,130),'13–17':(90,160),'18–22':(90,160),'23–26':(90,160)}
TYPES=['literal','mental_state','application','perspective']
TAGS=r'\b(Actor|Receiver|Observer|Response|Expressing|Interpreting|Regulating|Mismatch|Pitfall|Revision)\b'
BAD=['in conclusion','it is important to note','as an ai','as a language model']
EMO=re.compile('[\U0001F300-\U0001FAFF\u2600-\u27BF\u2764\u2B50\u2B55]')
AMBIG=set('😂🙃😭💀🔥🤣')
SENSITIVE={'personality','deception','body'}
def ecount(t): return len(EMO.findall(t))
STOP=set('the a an and or of to in on at for with is was were be been it that this he she they his her their as by from but not so if then than'.split())
def cw(s): return {w for w in re.findall(r"[a-z']+",s.lower()) if w not in STOP and len(w)>2}

if bj.get('kind')=='cluster':
    CT=['literal','relational','mental_state','application']; SENS_T={'Personality & Individual Difference','Honesty, Deception & Influence','Body & Mind'}
    cl={c['cluster_id']:c for c in bj['clusters']}; cf=defaultdict(list); seen=defaultdict(int)
    for i,l in enumerate([x for x in open(OUT,encoding='utf-8').read().splitlines() if x.strip()],1):
        try: r=json.loads(l)
        except Exception: cf['line%d'%i].append('invalid JSON'); continue
        cid=r.get('cluster_id')
        if cid not in cl: cf['line%d'%i].append(f'unknown cluster_id {cid}'); continue
        seen[cid]+=1; f=cf[cid]; c=cl[cid]; snos={x['sno'] for x in c['rows']}
        if r.get('type')!=c['type']: f.append('type altered')
        p=r.get('passage','')
        if p.strip()=='SKIP': f.append('model skipped: '+str(r.get('grounding'))); continue
        ru=r.get('rows_used')
        if not isinstance(ru,list) or not set(ru)<=snos or len(set(ru))<2: f.append('rows_used must list at least 2 snos from the cluster')
        n=len(p.split())
        if not 102<=n<=276: f.append(f'passage {n} words, want 120-240')
        if re.search(TAGS,p): f.append('framework tag word in passage')
        if any(b in p.lower() for b in BAD): f.append('banned phrase')
        for x in c['rows']:
            if difflib.SequenceMatcher(None,p.lower(),x['description'].lower()).ratio()>0.6: f.append(f'passage copies description of S{x["sno"]}')
        sens=any(x['topic'] in SENS_T for x in c['rows']); young=all(x['age'] in ('1–3','4–6') for x in c['rows'])
        pmax=1 if sens else (2 if young else 3)
        if ecount(p)>pmax: f.append(f'{ecount(p)} emojis in passage, max {pmax}')
        if any(ch in AMBIG for ch in p): f.append('ambiguous emoji in passage')
        if EMO.search(str(r.get('grounding',''))): f.append('emoji in grounding')
        qa=r.get('qa')
        if not isinstance(qa,list) or [q.get('type') for q in qa if isinstance(q,dict)]!=CT: f.append(f'qa must be 4 items typed {CT}'); continue
        for q in qa:
            if not q.get('q','').strip() or not q.get('a','').strip(): f.append('empty q/a')
            if ecount(q['a'])>(1 if sens else 2): f.append('too many emojis in an answer')
            if ecount(q['q'])>0: f.append('emoji in a question')
            if len(q['a'].split())>70: f.append('answer too long')
        if sum(ecount(q['a'])>0 for q in qa)==4: f.append('emoji in every answer')
        pw=cw(p)
        for k in (0,1):
            a_=cw(qa[k]['a'])
            if a_ and len(a_&pw)/len(a_)<0.4: f.append(f'{CT[k]} answer not supported by passage')
        if not r.get('grounding','').strip(): f.append('missing grounding')
    for cid in cl:
        if seen[cid]!=1: cf[cid].append(f'expected 1 record, got {seen[cid]}')
    for k,v in cf.items():
        for m_ in v: print(f'FAIL {k}: {m_}')
    bad=sorted(k for k,v in cf.items() if v)
    print(f'\n{len(cl)-len(bad)}/{len(cl)} clusters passed.'+(f' Regenerate: {bad}' if bad else ''))
    finish(1 if bad else 0)
fails=defaultdict(list); got=defaultdict(list)
lines=[l for l in open(OUT,encoding='utf-8').read().splitlines() if l.strip()]
for i,l in enumerate(lines,1):
    try: r=json.loads(l)
    except Exception as e: fails['line%d'%i].append('invalid JSON'); continue
    s=r.get('sno'); 
    if s not in rows: fails['line%d'%i].append(f'unknown sno {s}'); continue
    key=(s,r.get('variant')); got[s].append(r); f=fails[s]
    src=rows[s]
    if r.get('variant') not in IDS: f.append(f'variant {r.get("variant")} not in this batch ids {IDS}'); continue
    want=src['plan'].get(str(r.get('variant')))
    if r.get('recipe')!=want: f.append(f'v{r.get("variant")}: recipe is {r.get("recipe")!r}, plan says {want!r}')
    for k in ('age','topic','subtopic','subtype'):
        if r.get(k)!=src[k]: f.append(f'v{r.get("variant")}: {k} altered')
    p=r.get('passage','')
    if p.strip()=='SKIP': f.append(f'v{r.get("variant")}: model skipped: {r.get("grounding")}'); continue
    n=len(p.split()); lo,hi=WORDS[src['age']]
    if not lo*0.85<=n<=hi*1.15: f.append(f'v{r.get("variant")}: passage {n} words, want {lo}-{hi}')
    if re.search(TAGS,p): f.append(f'v{r.get("variant")}: framework tag word in passage')
    if any(b in p.lower() for b in BAD): f.append(f'v{r.get("variant")}: banned phrase')
    if difflib.SequenceMatcher(None,p.lower(),src['description'].lower()).ratio()>0.6: f.append(f'v{r.get("variant")}: passage copies description')
    ep=ecount(p); pmax=2 if src['age'] in ('1–3','4–6') else 3
    if bj['stage'] in SENSITIVE: pmax=1
    if ep>pmax: f.append(f'v{r.get("variant")}: {ep} emojis in passage, max {pmax}')
    if any(c in AMBIG for c in p) and bj['stage']!='expression': f.append(f'v{r.get("variant")}: ambiguous emoji in passage')
    if EMO.search(str(r.get('grounding',''))): f.append(f'v{r.get("variant")}: emoji in grounding')
    qa=r.get('qa')
    if not isinstance(qa,list) or [q.get('type') for q in qa if isinstance(q,dict)]!=TYPES: f.append(f'v{r.get("variant")}: qa must be 4 items typed {TYPES}'); continue
    for q in qa:
        if not q.get('q','').strip() or not q.get('a','').strip(): f.append(f'v{r.get("variant")}: empty q/a')
    amax=1 if bj['stage'] in SENSITIVE else 2
    for q in qa:
        if ecount(q['a'])>amax: f.append(f'v{r.get("variant")}: {ecount(q["a"])} emojis in an answer, max {amax}')
        if ecount(q['q'])>0: f.append(f'v{r.get("variant")}: emoji in a question')
    if sum(ecount(q['a'])>0 for q in qa)==4: f.append(f'v{r.get("variant")}: emoji in every answer')
    lit=qa[0]['a']; pw=cw(p)
    if cw(lit) and len(cw(lit)&pw)/len(cw(lit))<0.5: f.append(f'v{r.get("variant")}: literal answer not found in passage')
    for q in qa:
        if len(q['a'].split())>60: f.append(f'v{r.get("variant")}: answer too long')
    if not r.get('grounding','').strip(): f.append(f'v{r.get("variant")}: missing grounding')
for s in rows:
    rs=got.get(s,[])
    if len(rs)!=V: fails[s].append(f'expected {V} records, got {len(rs)}')
    vs=[x.get('variant') for x in rs]
    if sorted(vs)!=sorted(IDS) and len(rs)==V: fails[s].append(f'variant numbers wrong, want {IDS}')
    for a in range(len(rs)):
        for b in range(a+1,len(rs)):
            wa,wb=cw(rs[a].get('passage','')),cw(rs[b].get('passage',''))
            if wa and wb and len(wa&wb)/len(wa|wb)>0.55: fails[s].append(f'variants {a+1} and {b+1} too similar')
bad=sorted(k for k,v in fails.items() if v and isinstance(k,int))
for k,v in fails.items():
    for m in v: print(f'FAIL {k}: {m}')
tot=len(rows)
print(f'\n{tot-len(bad)}/{tot} rows passed. Regenerate sno: {bad}' if bad or any(isinstance(k,str) for k in fails if fails[k]) else f'\nAll {tot} rows passed.')
finish(1 if any(fails.values()) else 0)
