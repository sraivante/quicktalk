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
def stem(w): return w[:-1] if len(w)>3 and w.endswith('s') and not w.endswith('ss') else w
def cw(s): return {stem(w) for w in re.findall(r"[a-z]+(?:'[a-z]+)?",s.lower().replace('\u2019',"'")) if w not in STOP and len(w)>2}
import os as _os
_CFG=_os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),'config')
try: BLOCK=json.load(open(_os.path.join(_CFG,'blocklist.json'),encoding='utf-8'))['terms']
except Exception: BLOCK=[]
BLOCK_RE=re.compile(r'(?<![A-Za-z])('+'|'.join(re.escape(t) for t in BLOCK)+r')(?![A-Za-z])',re.I) if BLOCK else None
try:
    _N=json.load(open(_os.path.join(_CFG,'names.json'),encoding='utf-8')); NAMEMAX=_N['max_records_per_name']; NAMESET=set(_N['india'])|set(_N['global'])|set(_N['overused'])
except Exception: NAMEMAX,NAMESET=10**9,set()
def _toks(t): return re.findall(r"[a-z]+(?:'[a-z]+)?",t.lower().replace('\u2019',"'"))
def copied(passage, desc, n=5):
    d=re.sub(r'"[^"]*"|\u201c[^\u201d]*\u201d','',desc)
    dt=_toks(d); pt=_toks(passage)
    dg={tuple(dt[i:i+n]) for i in range(len(dt)-n+1)}
    return [' '.join(g) for g in {tuple(pt[i:i+n]) for i in range(len(pt)-n+1)}&dg]
MSCUE=re.compile(r"\b(feel|felt|think|thought|want|worr|afraid|scared|hope|intend|mean|suggest|show|reveal|why|mind|believe|sure|realis|realiz|expect|wish|proud|upset|angry|happy|sad|nervous|anxious|embarrass|asham|guilt|relie|seem|emotion|mood|made)",re.I)
EMOQUOTA=0.6
def rectext(r): return r.get('passage','')+' '+' '.join(q.get('q','')+' '+q.get('a','') for q in r.get('qa',[]) if isinstance(q,dict))
def batch_checks(recs, fails, key='batch'):
    cnt={}
    for r in recs:
        for nm in set(re.findall(r'\b[A-Z][a-z]+(?:-[a-z]+)?\b',rectext(r)))&NAMESET: cnt[nm]=cnt.get(nm,0)+1
    for nm,c in sorted(cnt.items()):
        if c>NAMEMAX: fails[key].append(f'name {nm} used in {c} records (max {NAMEMAX}); use the cast names')
    op={}
    for r in recs:
        k=' '.join(r.get('passage','').split()[:2]).lower()
        if k: op[k]=op.get(k,0)+1
    for k,c in op.items():
        if c>max(5,len(recs)//5): print(f'WARN {key}: {c} passages open with "{k}"')

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
        if not 114<=n<=276: f.append(f'passage {n} words, want 120-240')
        if re.search(TAGS,p): f.append('framework tag word in passage')
        if BLOCK_RE and BLOCK_RE.search(rectext(r)): f.append('real brand/public figure: '+BLOCK_RE.search(rectext(r)).group(0))
        if any(b in p.lower() for b in BAD): f.append('banned phrase')
        for x in c['rows']:
            if difflib.SequenceMatcher(None,p.lower(),x['description'].lower()).ratio()>0.6: f.append(f'passage copies description of S{x["sno"]}')
            cp=copied(p,x['description'])
            if cp: f.append(f'passage copies wording of S{x["sno"]}: "{cp[0]}"')
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
        if sum(ecount(q['a'])>0 for q in qa)>2: f.append('emoji in more than 2 answers')
        pw=cw(p); lab=cw(' '.join(x['subtopic']+' '+x['subtype'] for x in c['rows']))
        for k in (0,1):
            a_=cw(qa[k]['a']); vocab=pw|lab if k==1 else pw
            if a_ and len(a_&vocab)/len(a_)<0.4: f.append(f'{CT[k]} answer not supported by passage')
        if not r.get('grounding','').strip(): f.append('missing grounding')
    for cid in cl:
        if seen[cid]!=1: cf[cid].append(f'expected 1 record, got {seen[cid]}')
    _recs=[json.loads(x) for x in open(OUT,encoding='utf-8').read().splitlines() if x.strip().startswith('{')]
    batch_checks(_recs, cf)
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
    if not lo*0.95<=n<=hi*1.15: f.append(f'v{r.get("variant")}: passage {n} words, want {lo}-{hi}')
    if re.search(TAGS,p): f.append(f'v{r.get("variant")}: framework tag word in passage')
    if BLOCK_RE and BLOCK_RE.search(rectext(r)): f.append(f'v{r.get("variant")}: real brand/public figure: {BLOCK_RE.search(rectext(r)).group(0)}')
    if any(b in p.lower() for b in BAD): f.append(f'v{r.get("variant")}: banned phrase')
    if difflib.SequenceMatcher(None,p.lower(),src['description'].lower()).ratio()>0.6: f.append(f'v{r.get("variant")}: passage copies description')
    cp=copied(p,src['description'])
    if cp: f.append(f'v{r.get("variant")}: passage copies row wording: "{cp[0]}"')
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
    if sum(ecount(q['a'])>0 for q in qa)>2: f.append(f'v{r.get("variant")}: emoji in more than 2 answers')
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
allrecs=[x for v in got.values() for x in v]
batch_checks(allrecs, fails)
for x in allrecs:
    qa_=x.get('qa')
    if isinstance(qa_,list) and len(qa_)>1 and not MSCUE.search(str(qa_[1].get('q',''))): print(f'WARN {x.get("sno")} v{x.get("variant")}: mental_state question may be plain recall: {qa_[1].get("q")}')
emo_recs=sum(1 for x in allrecs if isinstance(x.get('qa'),list) and any(isinstance(q,dict) and ecount(str(q.get('a','')))>0 for q in x['qa']))
if allrecs and emo_recs>EMOQUOTA*len(allrecs): fails['batch'].append(f'{emo_recs}/{len(allrecs)} records have an answer emoji (max {int(EMOQUOTA*100)}%); leave about half with none')
dw=sum(1 for x in allrecs if isinstance(x.get('qa'),list) and len(x['qa'])>2 and 'do well' in str(x['qa'][2].get('q','')).lower())
if dw>1: fails['batch'].append(f'"do well" application question used {dw} times (max 1 per batch); vary the frames')
bad=sorted(k for k,v in fails.items() if v and isinstance(k,int))
for k,v in fails.items():
    for m in v: print(f'FAIL {k}: {m}')
tot=len(rows)
print(f'\n{tot-len(bad)}/{tot} rows passed. Regenerate sno: {bad}' if bad or any(isinstance(k,str) for k in fails if fails[k]) else f'\nAll {tot} rows passed.')
finish(1 if any(fails.values()) else 0)
