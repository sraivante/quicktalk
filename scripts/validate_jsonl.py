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

# --- review-driven WARN checks (P1-P5); advisory only, they never fail a batch ---
FEEL=re.compile(r"\b((?:un|over|self-|dis|in)?(?:stubborn|grief|hollow|longing|miss(?=es\b|ed\b|ing\b|\b)|desperat|astonish|distress|tempt|enjoy|tension|efficient|approval|rage|enrag|amaz|aching|cornered|crowded|unheard|hate herself|hate himself|reluct|unwelcome|left behind|afraid|felt used|petty|felt held|steadier|attacked|felt controlled|wonder|curiosit|impress|mourn|felt steady|felt grounded|grown[- ]up(?!s)|connected|terribl|awful|panic|dread|grump|sulk|moody|cranky|fussy|clingy|whiny|teary|tearful|irritable|troubl|anger|burn|resign|defeated|small|hurt|scared|fright|fear|terrif|nervous|anxi|worr|uneas|tense|panick|dread|shaken|sad|unhapp|down|low|lonel|alone|hurt|griev|heartbr|miser|glum|gloom|upset|disappoint|let down|deflat|crush|angr|mad|furious|annoy|irritat|frustrat|resent|bitter|indign|outrag|cross|jealous|envi|envy|embarrass|asham|shame|humiliat|guilt|sorry|regret|remorse|self-conscious|awkward|shy|exposed|small|happy|glad|joy|delight|pleas|thrill|excit|elat|chuffed|cheer|content|proud|pride|relie|calm|peace|settled|safe|secure|comfort|grateful|thank|touched|warm|lov|fond|tender|affection|car(?:ed|ing)|hope|hopeful|eager|curious|intrigu|interest|amus|surpris|shock|stun|startl|confus|puzzl|unsure|uncertain|torn|conflict|ambival|doubt|hesit|overwhelm|stress|pressur|tired|exhaust|drained|numb|empty|hopeless|helpless|trapped|stuck|defeat|discourag|confident|brave|bold|determin|resolv|motivat|inspir|reassur|validat|understood|seen|respect|valued|accepted|included|left out|excluded|rejected|betray|abandon|neglect|ignored|dismiss|belittl|insult|offend|wound|protective|defensive|suspici|wary|cautious|guarded|distrust|trust|shaky|flustered|rattled|restless|impatient|bored|lost|homesick|nostalg|wistful|bittersweet|mixed|sheepish|moved|awe|smug|superior|vindicat|triumph|satisf|fulfil|at ease|free|lighter|heavy|sting|pang|ache|dismay|horror|disgust|revuls|appall|reluct|resign|defiant|rebell|hostile|contempt|scorn|pity|sympath|empath|compassion|concern|alarm|agitat|uncomfort|discomfort|insecure|vulnerab|inadequa|useless|worthless|stupid|foolish|silly|dumb|unwanted|unloved|misunderstood|invisible|trapped|torn|mortif|flatter|admir|appreciat|encourag|energ|alive|giddy|bubbly|nervy|jittery|edgy|on edge|heartened|comforted|soothed|safe)\w*)\b",re.I)
DIAG=re.compile(r"\b(autis\w*|adhd|ocd|bipolar|depress(?:ed|ion)|dyslex\w*|dyspraxi\w*|ptsd|schizo\w*|anorexi\w*|bulimi\w*|eating disorder|narcissis\w*|psychopath\w*|sociopath\w*|anxiety disorder|panic disorder|borderline)\b",re.I)
AGEW={'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10,'eleven':11,'twelve':12,'thirteen':13,'fourteen':14,'fifteen':15,'sixteen':16,'seventeen':17,'eighteen':18,'nineteen':19,'twenty':20,'twenty-one':21,'twenty-two':22,'twenty-three':23,'twenty-four':24,'twenty-five':25,'twenty-six':26}
AGE_RE=re.compile(r"\b(\d{1,2}|"+'|'.join(sorted(AGEW,key=len,reverse=True))+r")[- ]years?[- ]old\b|\baged (\d{1,2})\b",re.I)
CAPN=re.compile(r"\b[A-Z][a-z]+(?:-[a-z]+)?\b")
def ms_feel_warn(key, q):
    if isinstance(q,dict) and q.get('a') and not FEEL.search(str(q['a'])+' '+str(q.get('q',''))): print(f'WARN {key}: mental_state answer names no feeling; name the emotion (e.g. anxious, ashamed, relieved)')
SUBJ=re.compile(r"^(?:How|What|Why|When|Which)\s+(?:might|would|could|did|does|do|was|is|were|will|may)\s+([A-Z][a-z]+(?:-[a-z]+)?)\b(?!['’]s)")
def same_person_warn(key, qm, qp, names):
    a=SUBJ.match(str(qm.get('q','')).strip()); b=SUBJ.match(str(qp.get('q','')).strip())
    if a and b and a.group(1)==b.group(1) and a.group(1) in names: print(f'WARN {key}: mental_state and perspective questions both centre {a.group(1)}; centre different people')
def diag_warn(key, r):
    p=str(r.get('passage','')); txt=' '.join(str(q.get('a','')) for q in (r.get('qa') or []) if isinstance(q,dict))+' '+str(r.get('grounding',''))
    for m in DIAG.finditer(txt):
        if not re.search(r'\b'+re.escape(m.group(0)[:5]),p,re.I): print(f'WARN {key}: diagnostic label "{m.group(0)}" in answers/grounding but not in the passage')
def age_warn(key, r, age):
    if str(r.get('recipe','')).split('+')[0] in ('R14','R4','R12') or age not in ('4–6','7–12','13–17'): return
    lo,hi=[int(x) for x in age.split('–')]; got=[]
    for m in AGE_RE.finditer(str(r.get('passage',''))):
        v=m.group(1) or m.group(2); got.append(int(v) if v.isdigit() else AGEW[v.lower()])
    if len(got)==1 and not lo-1<=got[0]<=hi+1: print(f'WARN {key}: passage states age {got[0]} but the row is {age}')
def signoff_warn(key, r):
    if str(r.get('recipe','')).split('+')[0] not in ('R11','R14'): return
    tail=str(r.get('passage','')).strip().splitlines()[-1] if str(r.get('passage','')).strip() else ''
    if re.match(r"^\s*(?:[-–—]\s*)?(?:(?:your|yours|love|with love|regards|warmly)[^\n]{0,30},?\s*)?[A-Z][a-z]+(?: [A-Z][a-z]+)?\.?\s*$",tail) or re.search(r"\b(Yours|Your (?:friend|colleague|sister|brother|didi|bhaiya)|With love|Regards),?\s*$",tail): print(f'WARN {key}: spoken recipe {r.get("recipe")} ends with a letter-style sign-off; name the speaker inside the speech')
def narrator_pron_hits(x):
    """P5: pronoun sentences in answers/grounding of a first-person passage, minus those whose names the passage genders"""
    P=str(x.get('passage','')); toks=re.findall(r"[A-Za-z'-]+",P)
    cued=set()
    for i,t in enumerate(toks):
        if t[:1].isupper():
            win=' '.join(toks[max(0,i-4):i+5])
            if GCUE.search(re.sub(r'\b(he|she|him|his|her|hers|himself|herself)\b','',win,flags=re.I)): cued.add(t)
    txt=' '.join(str(q.get('a',''))+' '+str(q.get('q','')) for q in (x.get('qa') or []) if isinstance(q,dict))+' '+str(x.get('grounding',''))
    hits=[]
    for sent in re.split(r'(?<=[.?!;])\s+',txt):
        if not GPRON.search(sent): continue
        if GCUE.search(re.sub(r'\b(he|she|him|his|her|hers|himself|herself)\b','',sent,flags=re.I)): continue
        ns=[n for n in CAPN.findall(sent) if n in NAMESET]
        if ns and all(n in cued for n in ns): continue
        hits.append(sent.strip())
    return hits
EMOQUOTA=0.6
GPRON=re.compile(r"\b(he|she|him|his|her|hers|himself|herself)\b",re.I)
GCUE=re.compile(r"\b(he|she|him|his|her|hers|himself|herself|boy|girl|man|woman|men|women|son|daughter|brother|sister|mother|father|mom|mum|dad|papa|mama|amma|appa|ammi|abbu|nani|nana|dadi|dada|aunt|aunty|auntie|uncle|didi|bhaiya|bhai|anna|akka|grandma|grandpa|grandmother|grandfather|wife|husband|girlfriend|boyfriend|sir|madam|ma'am|mr|mrs|ms|miss(?=es\b|ed\b|ing\b|\b)|lady|gentleman|beta|beti|nephew|niece|bhabhi|chacha|chachi|mami|masi|mausi|bua|khala|apa|api|maasi|mumma|mamma|mummy|mommy|ma|maa|mai|baba|bapu|pitaji|mataji|dadaji|nanaji|dadiji|naniji|chachaji|chithi|mamaji|bhaiyya|bhaiji|didu|behna|mausa|atya|atte|phuppo|phupho|phupi|chachu|mamu|mama-ji|jiju|behen|bahen|bhabi|nanu|nanima|thakuma|thakurda|dida|dadima|ajji|ajja|ajoba|aaji|periamma|chithi|chitappa|periappa|athai|mami-ji|veerji|paaji|bibi|begum|miyan|amma-ji|papa-ji|dadu|paati|thatha|ammamma|grandson|granddaughter|bride|groom|actress|waiter|waitress|queen|king|prince|princess)\b",re.I)
def ungendered_pronoun(r):
    """answers/grounding use he/she although the passage has no gender cue at all"""
    if GCUE.search(r.get('passage','')): return False
    txt=' '.join(str(q.get('a',''))+' '+str(q.get('q','')) for q in r.get('qa',[]) if isinstance(q,dict))+' '+str(r.get('grounding',''))
    return bool(GPRON.search(txt))
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
        ms_feel_warn(cid, qa[2]); diag_warn(cid, r)  # clusters have no perspective question, so no same-person check
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
    if ungendered_pronoun(r): f.append(f'v{r.get("variant")}: he/she used in questions/answers/grounding but the passage states no gender; use the name, the role or "they"')
    ans_names=set(re.findall(r'\b[A-Z][a-z]+(?:-[a-z]+)?\b',' '.join(q['q']+' '+q['a'] for q in qa)))&NAMESET
    missing=sorted(n for n in ans_names if not re.search(r'\b'+re.escape(n)+r'\b',p))
    if missing: f.append(f'v{r.get("variant")}: name(s) {missing} used in questions/answers but not in the passage')
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
    qa_=x.get('qa'); key_=f'{x.get("sno")} v{x.get("variant")}'
    if isinstance(qa_,list) and len(qa_)>1 and not MSCUE.search(str(qa_[1].get('q',''))): print(f'WARN {key_}: mental_state question may be plain recall: {qa_[1].get("q")}')
    if isinstance(qa_,list) and len(qa_)==4 and all(isinstance(q,dict) for q in qa_):
        ms_feel_warn(key_, qa_[1]); same_person_warn(key_, qa_[1], qa_[3], NAMESET)
    diag_warn(key_, x); age_warn(key_, x, rows.get(x.get('sno'),{}).get('age')); signoff_warn(key_, x)
for x in allrecs:
    ps=re.sub(r'"[^"]*"|“[^”]*”','',str(x.get('passage','')))  # narration only, not quoted speech
    if len(re.findall(r"\bI\b|\bI'm\b|\bmy\b",ps))>=4 and not GPRON.search(ps):
        h=narrator_pron_hits(x)
        if h: print(f'WARN {x.get("sno")} v{x.get("variant")}: first-person passage and he/she in questions/answers/grounding with no gender cue for that person; check the narrator is not gendered unless the passage states it: "{h[0][:90]}"')
last_emo=sum(1 for x in allrecs if isinstance(x.get('qa'),list) and len(x['qa'])==4 and ecount(str(x['qa'][3].get('a','')))>0)
if allrecs and last_emo>max(2,len(allrecs)//4): fails['batch'].append(f'{last_emo}/{len(allrecs)} records put an emoji on the last answer (max 25%); place emojis where the feeling is, not by habit at the end')
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
