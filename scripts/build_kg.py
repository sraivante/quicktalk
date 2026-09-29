#!/usr/bin/env python3
"""Build a knowledge graph from the framework CSV.

Usage: python scripts/build_kg.py   (defaults: data/...v9.csv -> kg/)

Outputs (in --out):
  nodes.csv, edges.csv           entity/relation tables (row nodes included)
  concept_graph.graphml          graph without row nodes (situations, stances, mechanisms, states, concepts, ages)
  <csv stem>_kg.csv              framework CSV plus normalised columns
  row_context.jsonl              short relation strings per row, used by make_batches.py
  clusters.jsonl                 related-row clusters for the graph stage (contrast, sequence, progression, comparison)
  stats.txt                      coverage and connectivity report
"""
import argparse, csv, json, os, random, re
from collections import defaultdict, Counter
import networkx as nx

ap = argparse.ArgumentParser()
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap.add_argument('csv', nargs='?', default=os.path.join(ROOT,'data','human_development_framework_v9.csv')); ap.add_argument('--out', default=os.path.join(ROOT,'kg')); ap.add_argument('--seed', type=int, default=7)
a = ap.parse_args()
random.seed(a.seed)
os.makedirs(a.out, exist_ok=True)
AGES = ['1–3', '4–6', '7–12', '13–17', '18–22', '23–26']
AO = {x: i for i, x in enumerate(AGES)}

# ---------- vocabularies ----------
STANCE_MAP = [
    ('indebtedness', r'indebted|obligat'), ('gratitude', r'gratitude|grateful|thank'),
    ('humiliation', r'humiliat'), ('shame', r'shame|embarrass'), ('guilt', r'guilt|remorse|regret'),
    ('hatred', r'hatr|\bhate|loath'), ('contempt', r'contempt|disdain|scorn|sneer'),
    ('jealousy', r'jealous'), ('envy', r'\benvy|envious'), ('rivalry', r'rival|compet'),
    ('resentment', r'resent|bitter|grudge'), ('anger', r'anger|angry|\brage|fury|furious|irritat|frustrat|outrage|indign'),
    ('fear', r'fear|afraid|anxi|terror|scared|dread|wari|alarm|worr|panic'),
    ('betrayal', r'betray|disloyal'), ('deceit', r'deceit|deceiv|\blie|lying|dishonest|gaslight'),
    ('manipulation', r'manipul|love-bomb|guilt-trip|emotional blackmail|triangulat'),
    ('coercion', r'coerc|pressure|forc(e|ed)|threat|blackmail|control'),
    ('exploitation', r'exploit|abus'), ('mockery', r'mock|teas(e|ing)|ridicul|taunt'),
    ('rejection', r'reject|exclu|ostrac|ghost'), ('acceptance', r'accept|belong|welcom|inclu'),
    ('disillusionment', r'disillusion|disappoint|let down'), ('grief', r'grief|griev|sorrow|mourn|\bloss\b|sadness|heartbreak'),
    ('worship', r'worship|devot|reveren|faith|awe-struck'), ('admiration', r'admir|idoli[sz]|hero'),
    ('respect', r'respect|deferen|honou?r'), ('affection', r'affection|\blove|loving|tender|fond|warmth'),
    ('trust', r'\btrust|reliance|confid(e|ing)'), ('distrust', r'distrust|suspic|skeptic|sceptic'),
    ('loyalty', r'loyal|allegian'), ('protectiveness', r'protect|defen[cd]|guard'),
    ('pity', r'\bpity'), ('compassion', r'compassion|sympath|empath|\bkind|concern|care\b|caring'),
    ('forgiveness', r'forgiv|reconcil|mercy'), ('argument', r'argu|dispute|quarrel|conflict|disagree'),
    ('dependence', r'depend|clinging|cling'), ('obsession', r'obsess|fixat|infatuat'),
    ('indifference', r'indiffer|apath|ignor|detach'), ('neglect', r'neglect|abandon'),
    ('pride', r'pride|proud'), ('curiosity', r'curio|interest|wonder'), ('awe', r'\bawe|amaz|astonish'),
    ('hope', r'\bhope|optimis'), ('loneliness', r'lonel|isolat'), ('confusion', r'confus|puzzl'),
    ('insecurity', r'insecur'), ('comparison', r'compar'), ('honesty', r'honest|truth|integrity'),
    ('fairness', r'\bfair|justice'), ('prejudice', r'prejud|stereotyp|\bbias'), ('temptation', r'tempt'),
    ('generosity', r'generos|shar(e|ing)|giving'), ('comfort', r'comfort|sooth|reassur'),
    ('hurt', r'\bhurt|\bpain|wound'), ('favouritism', r'favou?rit'),
]
MECH_MAP = [
    ('pre-mortem', r'pre-?mortem|imagin\w+ (it )?fail|what could go wrong'), ('working backward', r'backward|reverse (plan|engineer)|start(s|ing)? from the (goal|end|deadline)'),
    ('means-end analysis', r'means-end|gap between'), ('task decomposition', r'break(s|ing)?\s.{0,25}(down|into)|decompos|step by step|small steps|smaller (steps|tasks|parts)|chunk'),
    ('trial and error', r'trial[- ]and[- ]error|try (one|another|different)|tries? (again|different)|experiment(s|ing)? with'), ('satisficing', r'satisfic|good enough|first (option|choice) that'),
    ('decision matrix', r'decision matrix|weighted|scor(e|ing) (each|the) option|compar\w+ (options|offers) (on|by)'), ('pros and cons', r'pros[- ]and[- ]cons|pros and cons|list(s|ed)? (the )?(pros|advantages)'),
    ('prioritising', r'priorit|urgent|important first|eisenhower'), ('time-boxing', r'time-?box|timer|pomodoro|fixed (slot|block|time)'),
    ('checklist', r'checklist|check-?list|tick(s|ing)? off'), ('if-then plan', r'if-then|implementation intention|if .{2,40} then i'),
    ('mental simulation', r'mental(ly)? (simulat|rehears)|rehears|visuali[sz]|imagin(es|ing) (the|how)|walks? through .{0,20} in (their|his|her) (head|mind)'),
    ('contingency planning', r'contingen|plan b|backup|fallback|alternate plan'), ('buffer and slack', r'buffer|slack|extra time|margin'),
    ('minimum viable version', r'minimum viable|prototype|pilot|first version|small version|iterat'), ('experiment and measure', r'experiment|measure|a/b|track(s|ing)? (results|data|numbers)|test(s|ing)? (it|the idea|a small)'),
    ('first principles', r'first.principles|from scratch|basic (facts|truths)'), ('inversion', r'invers|opposite|what would (make|cause)|worst'),
    ('root cause analysis', r'five whys|5 whys|root cause|why did'), ('brainstorming', r'brainstorm|list(s|ed)? (many|all) (ideas|options)|generat\w+ (many|several) (ideas|options)'),
    ('lateral thinking', r'lateral|reframe|reframing|look(s|ing)? at (it|the problem) (differently|another)|new angle'), ('constraint-based thinking', r'constraint|limit(ed)? (budget|resources)|only (had|have) '),
    ('externalising on paper', r'sketch|storyboard|diagram|write(s)? (it|everything) (down|out)|notebook|whiteboard|mind.?map'), ('sleeping on it', r'sleep on it|incubat|overnight|next morning|takes a break|step(s|ping)? away'),
    ('seeking advice', r'advice|expert|mentor|ask(s|ing)? (a|an|the|his|her|their) (teacher|senior|elder|doctor|parent|friend|counsellor|professor|lawyer|adviser)'), ('crowdsourcing', r'crowdsourc|poll(s|ed)?|ask(s|ing)? (around|several|many|a few people)'),
    ('delegation', r'delegat|hand(s|ing)? (it )?(over|off)|assign(s|ing)? (the|a) task'), ('negotiation', r'negotiat|win-win|compromise|bargain|counter-?offer'),
    ('values-first planning', r'values|what matters (most|to)|principle'), ('emotion-aware planning', r'mood|energy level|calm(s|ing)? (down|first)|breath|manag\w+ (stress|anxiety|emotion)'),
    ('resource and budget planning', r'budget|resources|cost(s|ing)? out|money (plan|set aside)|allocate'), ('critical path', r'critical path|dependenc|depends on|bottleneck|before .{2,30} can (start|begin)'),
    ('batching', r'\bbatch'), ('commitment device', r'commitment device|deadline|penalt|public(ly)? commit|lock(s|ed)? (away|the)|pledge'),
    ('accountability partner', r'accountab|study buddy|check(s|ing)? in with'), ('learning from past failure', r'last time|earlier mistake|past (failure|mistake)|lessons? learned|post-?mortem'),
    ('adaptive replanning', r'replan|re-plan|revis(e|es|ed|ing) the plan|adjust(s|ed|ing)? the plan|change(s|d)? (course|approach|tack)|switch(es|ed)? (to|approach)'), ('cutting losses', r'cut(s|ting)? (their |his |her |the )?loss|sunk cost|walk(s|ed)? away from|stop(s|ped)? (investing|spending)|quit'),
    ('impulsive action', r'impuls|without (thinking|planning|checking)|jump(s|ed)? (in|straight)|rush(es|ed)?'), ('rigid persistence', r'rigid|stubborn|keeps? (doing|repeating|trying) the same|refus(es|ed)? to (change|adapt)'),
    ('analysis paralysis', r'paralysis|over-?analy|cannot decide|keeps? (comparing|researching)|endless (research|comparison)'), ('overplanning', r'over-?plan|elaborate plan|too (detailed|many details)|perfect plan'),
    ('magical thinking', r'magical|wish(es|ing)?|hope(s|d)? (it|things) (will|would) (work|sort|fix)|superstit|lucky'), ('avoidance and procrastination', r'avoid|procrastin|put(s|ting)? (it )?off|delay(s|ing)? (starting|the)|hid(es|ing)'),
    ('copying without fit', r'cop(y|ies|ied|ying) (a|the|what|his|her|their|others)|same as (a|the) (friend|topper|senior)|imitat'), ('planning fallacy', r'planning fallacy|underestimat|takes? (longer|more time) than'),
    ('groupthink planning', r'groupthink|everyone agrees|nobody (questions|objects)|go(es)? along with the group'), ('analogy', r'analog|similar (to|problem|situation)|like (the|when)|precedent|reminds'),
    ('forward planning', r'forward|schedule(s|d)? (the|each|every)|plans? (out )?(the )?(week|day|days|steps)|timetable|routine'),
    ('trial by imitation', r'imitat|copies? (the )?(caregiver|parent|adult|sibling|friend)|watch(es|ing)'), ('asking an adult', r'ask(s|ed|ing)? (an? )?(adult|mother|father|mum|mom|teacher|caregiver|grandmother|grandfather|parent)|calls? (for )?(mummy|papa|mama|help)'),
]
STATE_MAP = [
    ('joy', r'\bjoy|delight|happy|glad|cheerful|thrill'), ('amusement', r'amus|laugh|giggl|funny|humou?r'), ('playfulness', r'playful|silly|fun\b'),
    ('affection', r'affection|tender|fond|love|warmth|hug'), ('gratitude', r'gratitude|grateful|thank'), ('admiration', r'admir|respect'),
    ('sadness', r'\bsad|sorrow|tearful|cry|weep|unhappy'), ('grief', r'grief|griev|mourn|bereave'), ('disappointment', r'disappoint|let down'),
    ('anger', r'anger|angry|furious|\brage|irritat|annoy|frustrat'), ('hostility', r'hostil|defian|aggress'), ('contempt', r'contempt|scorn|disdain'),
    ('disgust', r'disgust|revuls'), ('fear', r'\bfear|afraid|frighten|scared|terror|dread'), ('anxiety', r'anxi|nervous|worr|apprehens|uneasy'),
    ('shame', r'shame|ashamed'), ('embarrassment', r'embarrass|awkward|self-conscious'), ('guilt', r'guilt|remorse'),
    ('shyness', r'\bshy|timid|bashful'), ('curiosity', r'curio|inquisitive|wonder'), ('interest', r'interest|attentive|engag'),
    ('confusion', r'confus|puzzl|perplex'), ('doubt', r'doubt|skeptic|sceptic|suspici'), ('hope', r'\bhope|optimis'), ('excitement', r'excit|eager|enthusias'),
    ('surprise', r'surpris|astonish|shock|startl'), ('relief', r'relie[fv]'), ('pride', r'\bpride|proud|triumph'), ('boredom', r'bore(d|dom)|restless'),
    ('tiredness', r'tired|weary|exhaust|fatigue|drained'), ('detachment', r'detach|numb|withdraw|impassive|aloof'), ('calm', r'\bcalm|serene|peace|relax'),
    ('envy', r'\benvy|envious'), ('jealousy', r'jealous'), ('loneliness', r'lonel|isolat'), ('overwhelm', r'overwhelm|swamp|flood'), ('awe', r'\bawe|wonder|amaz'),
    ('contentment', r'content(ed|ment)|satisf'), ('nostalgia', r'nostalg|homesick|longing|yearn'), ('resentment', r'resent|bitter|grudge'),
    ('humiliation', r'humiliat|degrad'), ('trust', r'\btrust|secure|safe'), ('insecurity', r'insecur|inadequa|inferior'), ('determination', r'determin|resolve|persever|grit'),
    ('empathy', r'empath|sympath|compassion'), ('relief from stress', r'de-?stress|unwind|breath'), ('hurt', r'\bhurt|wound|pain'), ('regret', r'regret'), ('dread', r'existential|mortality'),
]
FAMILY_MAP = [
    ('act impulsively', r'impuls|rush|panic|first idea|random|jump|without (thinking|checking|planning|asking)|react'),
    ('avoid or give up', r'avoid|ignor|hid(e|ing)|giv(e|ing) up|do nothing|quit|procrastin|delay|den(y|ial)|dismiss|blam|alone|silence|stay(s|ing)? silent|sulk'),
    ('copy or follow others', r'copy|copies|imitat|go(es)? along|obey|everyone|follow(s|ing)? (the )?(crowd|group|others|topper)'),
    ('seek help or advice', r'\bask|advice|consult|tell(s|ing)? (a |an |the |their |his |her )?(trusted|adult|parent|teacher|friend|elder)|support|help|mentor|counsel|buddy|caregiver|senior|expert|doctor|lawyer|team|group'),
    ('communicate and negotiate', r'talk|convers|discuss|negotiat|honest|apolog|explain|request|inform|i-statement|thank|\bsay|\btell|offer|propos|counter'),
    ('protect and reduce risk', r'safety|\bsafe|backup|contingen|insur|emergency|secure|report|block|boundar|limit|fallback|buffer|reserve|precaution'),
    ('regulate self', r'breath|calm|rest\b|pause|sleep|stress|self-care|wait|patien|slow|cool|mood|emotion'),
    ('gather information', r'research|check|verif|learn|read|observ|investigat|find out|question|notic|compar|track|record|review|retrac|look(s|ing)? (up|at)|search|understand|what the'),
    ('try and adapt', r'\btry|\btest|experiment|adjust|chang|revis|rework|retry|pilot|iterat|pivot|switch|adapt|refin|trial'),
    ('plan and structure', r'plan|schedul|list|step|routine|goal|roles|checklist|timetable|prepar|priorit|break|organi[sz]|map|budget|milestone|sequence|structur'),
    ('creative reframing', r'reframe|creativ|idea|imagin|new way|alternativ|brainstorm|angle|lateral|invent'),
]
def first_match(text, table):
    t = text.lower()
    for name, rx in table:
        if re.search(rx, t): return name
    return None
def all_matches(text, table):
    t = text.lower()
    return [name for name, rx in table if re.search(rx, t)]

# ---------- load ----------
rows = list(csv.DictReader(open(a.csv, encoding='utf-8-sig')))
D = 'Human Learning & Development'
for r in rows:
    r['sno'] = int(r['S.No']); r['desc'] = r[D]
    m = re.search(r'\[(.*?)\]\s*$', r['Subtype'])
    r['view'] = m.group(1) if m else ''
    r['subtype_base'] = re.sub(r'\s*\[.*?\]\s*$', '', r['Subtype']).strip()
    r['stance_core'] = r['counterpart'] = r['mech_core'] = r['stage_k'] = r['family'] = ''
    r['concept_sim'] = ''
    r['states'] = []
    if r['Topic'] == 'Situational Awareness':
        parts = r['subtype_base'].split(' × ', 1)
        if len(parts) == 2:
            r['counterpart'] = parts[0].strip().lower()
            raw = parts[1].strip()
            fm = first_match(raw, STANCE_MAP)
            r['stance_core'] = fm or re.sub(r'[^a-z\- ]', '', raw.lower()).strip()
            r['stance_mapped'] = bool(fm)
    if r['Topic'] == 'Planning & Problem Solving':
        lab = re.sub(r'^Approach:\s*', '', r['subtype_base'])
        r['mech_core'] = first_match(lab, MECH_MAP) or first_match(r['desc'], MECH_MAP) or 'other'
        r['mech_from_label'] = bool(first_match(lab, MECH_MAP))
        r['family'] = first_match(lab, FAMILY_MAP) or 'unclassified'
    if r['Topic'] == 'Interaction Dynamics':
        m = re.match(r'Stage (\d+):\s*(.*)', r['subtype_base'])
        if m: r['stage_k'] = int(m.group(1)); r['stage_name'] = m.group(2)
    r['states'] = all_matches(r['Subtype'] + ' ' + r['desc'], STATE_MAP)
CONCEPT_TOPICS = {'Cognitive Machinery', 'Foundational Concepts'}
concepts = {}
for r in rows:
    if r['Topic'] in CONCEPT_TOPICS:
        lab = re.sub(r'\(.*?\)', '', r['Subtopic']).strip().lower()
        if len(lab) >= 6: concepts.setdefault(lab, r['Subtopic'])
concept_rx = {lab: re.compile(r'\b' + re.escape(lab) + r'\b') for lab in concepts}
for r in rows:
    txt = (r['Subtopic'] + ' ' + r['desc']).lower()
    r['concepts'] = [lab for lab, rx in concept_rx.items() if rx.search(txt) and not (r['Topic'] in CONCEPT_TOPICS and re.sub(r'\(.*?\)', '', r['Subtopic']).strip().lower() == lab)]

# ---------- graph ----------
G = nx.MultiDiGraph(); nodes = {}
def node(id_, typ, label, **kw):
    if id_ not in nodes: nodes[id_] = {'id': id_, 'type': typ, 'label': label}
    G.add_node(id_, type=typ, label=label, **kw); return id_
edge_rows = []
def edge(s, rel, d, **kw):
    G.add_edge(s, d, rel=rel, **kw); edge_rows.append({'src': s, 'rel': rel, 'dst': d, 'detail': json.dumps(kw, ensure_ascii=False) if kw else ''})
for x in AGES: node('age:' + x, 'AgeBand', x)
sub_ages = defaultdict(set)
for r in rows:
    rid = node('row:%d' % r['sno'], 'Row', 'S%d' % r['sno'], age=r['Age'])
    tid = node('topic:' + r['Topic'], 'Topic', r['Topic'])
    sid = node('sub:%s|%s' % (r['Topic'], r['Subtopic']), 'Concept' if r['Topic'] in CONCEPT_TOPICS else 'Subtopic', r['Subtopic'], topic=r['Topic'])
    edge(rid, 'IN_TOPIC', tid); edge(rid, 'AT_AGE', 'age:' + r['Age']); edge(rid, 'ABOUT', sid)
    sub_ages[sid].add(r['Age']); r['sid'] = sid
    if r['view']: edge(rid, 'VIEW', node('view:' + r['view'], 'View', r['view']))
    if r['stance_core']:
        st = node('stance:' + r['stance_core'], 'Stance', r['stance_core']); edge(rid, 'FEATURES_STANCE', st)
        cp = node('cp:' + r['counterpart'], 'Counterpart', r['counterpart']); edge(rid, 'FEATURES_COUNTERPART', cp)
        edge(cp, 'HOLDS_STANCE', st, sno=r['sno'], situation=r['Subtopic'], age=r['Age'], view=r['view'])
        edge(sid, 'HAS_STANCE', st, age=r['Age'], view=r['view'])
    if r['mech_core']:
        mc = node('mech:' + r['mech_core'], 'Mechanism', r['mech_core']); edge(rid, 'USES_MECHANISM', mc)
        fam_n = node('family:' + r['family'], 'StrategyFamily', r['family']); edge(rid, 'IN_FAMILY', fam_n)
        rel = {'Pitfall': 'FAILS_IN', 'Revision': 'REVISED_IN'}.get(r['view'], 'SOLVES')
        edge(mc, rel, sid, sno=r['sno'], age=r['Age'])
    for s in r['states']: edge(rid, 'MENTIONS_STATE', node('state:' + s, 'MindState', s))
    for c in r['concepts']: edge(rid, 'MENTIONS_CONCEPT', 'sub:%s|%s' % (next(x['Topic'] for x in rows if x['Topic'] in CONCEPT_TOPICS and re.sub(r'\(.*?\)', '', x['Subtopic']).strip().lower() == c), concepts[c]))
# concept similarity (heuristic): TF-IDF cosine between a row and each concept's pooled text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
cdoc = defaultdict(list)
for r in rows:
    if r['Topic'] in CONCEPT_TOPICS: cdoc[r['Subtopic']].append(r['Subtopic'] + ' ' + r['desc'])
cnames = sorted(cdoc); cvec = TfidfVectorizer(stop_words='english', min_df=2, max_df=0.3, sublinear_tf=True)
targets = [r for r in rows if r['Topic'] not in CONCEPT_TOPICS and r['Topic'] in ('Situational Awareness', 'Planning & Problem Solving', 'Interaction Dynamics', 'Group Behaviour', 'Honesty, Deception & Influence', 'Personality & Individual Difference', 'Execution & Practical Skills', 'Wellbeing, Wisdom & Conversation', 'Culture & Society', 'Body & Mind')]
X = cvec.fit_transform([' '.join(cdoc[c]) for c in cnames] + [r['Subtopic'] + ' ' + r['desc'] for r in targets])
S = linear_kernel(X[len(cnames):], X[:len(cnames)])
SIM_MIN = 0.22; nsim = 0
for i, r in enumerate(targets):
    j = int(S[i].argmax())
    if S[i][j] >= SIM_MIN:
        r['concept_sim'] = cnames[j]; r['concept_sim_score'] = float(S[i][j]); nsim += 1
        edge('row:%d' % r['sno'], 'RELATED_CONCEPT', 'sub:%s|%s' % (next(x['Topic'] for x in rows if x['Subtopic'] == cnames[j] and x['Topic'] in CONCEPT_TOPICS), cnames[j]), weight=round(float(S[i][j]), 3), heuristic=True)
# aggregated relations
sig = defaultdict(Counter)
for r in rows:
    if r['Topic'] == 'Expression & Mind State':
        for s in r['states']: sig[r['sid']][s] += 1
for sid, c in sig.items():
    for s, w in c.items():
        if w >= 2: edge(sid, 'SIGNALS', 'state:' + s, weight=w)
by_arc = defaultdict(dict)
for r in rows:
    if r['stage_k'] != '': by_arc[(r['sid'], r['Age'])].setdefault(r['stage_k'], r)
for (sid, age), st in by_arc.items():
    ks = sorted(st)
    for k1, k2 in zip(ks, ks[1:]):
        node('stage:%s|%s|%d' % (sid, age, k1), 'Stage', 'stage %d: %s' % (k1, st[k1]['stage_name'])); node('stage:%s|%s|%d' % (sid, age, k2), 'Stage', 'stage %d: %s' % (k2, st[k2]['stage_name']))
        edge('stage:%s|%s|%d' % (sid, age, k1), 'NEXT_STAGE', 'stage:%s|%s|%d' % (sid, age, k2))
    for k in ks: edge('row:%d' % st[k]['sno'], 'STAGE_OF', 'stage:%s|%s|%d' % (sid, age, k)) if G.has_node('stage:%s|%s|%d' % (sid, age, k)) else None
for sid, ages in sub_ages.items():
    ol = sorted(ages, key=AO.get)
    for x, y in zip(ol, ol[1:]): edge(sid, 'DEVELOPS_INTO', sid, from_age=x, to_age=y)

# ---------- write tables ----------
cnt = Counter(e['dst'] for e in edge_rows) + Counter(e['src'] for e in edge_rows)
with open(os.path.join(a.out, 'nodes.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['id', 'type', 'label', 'degree']); w.writeheader()
    for n in nodes.values(): w.writerow({**n, 'degree': cnt[n['id']]})
with open(os.path.join(a.out, 'edges.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['src', 'rel', 'dst', 'detail']); w.writeheader(); w.writerows(edge_rows)
H = nx.MultiDiGraph(G.subgraph([n for n, d in G.nodes(data=True) if d['type'] != 'Row']))
nx.write_graphml(nx.DiGraph(H), os.path.join(a.out, 'concept_graph.graphml'))
stem = os.path.splitext(os.path.basename(a.csv))[0]
cols = list(rows[0].keys())[:6]
with open(os.path.join(a.out, stem + '_kg.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f); w.writerow(['S.No', 'Age', 'Topic', 'Subtopic', 'Subtype', D, 'View', 'Counterpart', 'StanceCore', 'MechanismCore', 'States', 'Concepts', 'StrategyFamily', 'RelatedConceptHeuristic'])
    for r in rows: w.writerow([r['sno'], r['Age'], r['Topic'], r['Subtopic'], r['Subtype'], r['desc'], r['view'], r['counterpart'], r['stance_core'], r['mech_core'], ';'.join(r['states']), ';'.join(r['concepts']), r['family'], r['concept_sim']])

# ---------- row context ----------
sit = defaultdict(list); plan = defaultdict(list); pair = defaultdict(list)
for r in rows:
    if r['stance_core']: sit[(r['Age'], r['Subtopic'])].append(r); pair[(r['Age'], r['Subtopic'], r['counterpart'], r['stance_core'])].append(r)
    if r['mech_core']: plan[(r['Age'], r['Subtopic'])].append(r)
ctx = {}
for r in rows:
    c = []
    if r['stance_core']:
        o = sorted({x['stance_core'] for x in sit[(r['Age'], r['Subtopic'])] if x['stance_core'] != r['stance_core'] and x.get('stance_mapped')})
        if o: c.append('same situation, other stances at this age: ' + ', '.join(o[:6]))
        pv = [x for x in pair[(r['Age'], r['Subtopic'], r['counterpart'], r['stance_core'])] if x['sno'] != r['sno'] and x['view'] != r['view']]
        if pv: c.append('paired view exists: %s (S%d)' % (pv[0]['view'], pv[0]['sno']))
    if r['mech_core']:
        o = sorted({x['mech_core'] for x in plan[(r['Age'], r['Subtopic'])] if x['mech_core'] != r['mech_core'] and x['mech_core'] != 'other'})
        if o: c.append('same problem, other approaches: ' + ', '.join(o[:6]))
    if r['stage_k'] != '':
        st = by_arc[(r['sid'], r['Age'])]; ks = sorted(st)
        if r['stage_k'] - 1 in st: c.append('previous stage: ' + st[r['stage_k'] - 1]['stage_name'])
        if r['stage_k'] + 1 in st: c.append('next stage: ' + st[r['stage_k'] + 1]['stage_name'])
    ages = sorted(sub_ages[r['sid']], key=AO.get)
    if len(ages) > 1: c.append('this subtopic also appears at ages: ' + ', '.join(x for x in ages if x != r['Age']))
    if r['states']: c.append('related mind states: ' + ', '.join(r['states'][:4]))
    if r['concepts']: c.append('related concepts: ' + ', '.join(r['concepts'][:3]))
    elif r['concept_sim']: c.append('possibly related concept (heuristic): ' + r['concept_sim'])
    ctx[r['sno']] = c[:6]
with open(os.path.join(a.out, 'row_context.jsonl'), 'w', encoding='utf-8') as f:
    for s, c in ctx.items(): f.write(json.dumps({'sno': s, 'graph_context': c}, ensure_ascii=False) + '\n')

# ---------- clusters ----------
def rj(r): return {'sno': r['sno'], 'age': r['Age'], 'topic': r['Topic'], 'subtopic': r['Subtopic'], 'subtype': r['Subtype'], 'description': r['desc']}
clusters = []
def add(t, rs, cap, bucket):
    if len(bucket) < cap: bucket.append({'type': t, 'rows': [rj(x) for x in rs]})
B = defaultdict(list)
keys = sorted(sit); random.shuffle(keys)
for k in keys:  # contrast: same situation, different stances
    rs = [x for x in sit[k] if x.get('stance_mapped')]
    seen, pick = set(), []
    for x in rs:
        if x['stance_core'] not in seen: seen.add(x['stance_core']); pick.append(x)
    if len(pick) >= 3: add('contrast', random.sample(pick, min(4, len(pick))), 350, B['contrast'])
pk = sorted(pair); random.shuffle(pk)
for k in pk:  # view pair
    g = pair[k]; acts = [x for x in g if x['view'] == 'Actor']; recs = [x for x in g if x['view'] == 'Receiver']
    if acts and recs: add('view_pair', [acts[0], recs[0]], 150, B['view_pair'])
ak = sorted(by_arc); random.shuffle(ak)
for k in ak:  # sequence: three consecutive stages
    st = by_arc[k]; ks = sorted(st)
    used = 0
    for i in range(0, len(ks) - 2, 3):
        if ks[i + 1] == ks[i] + 1 and ks[i + 2] == ks[i] + 2 and used < 2:
            add('sequence', [st[ks[i]], st[ks[i + 1]], st[ks[i + 2]]], 200, B['sequence']); used += 1
pk2 = sorted(plan); random.shuffle(pk2)
for k in pk2:  # comparison of approaches, incl. pitfall and revision
    g = plan[k]; good = [x for x in g if x['view'] in ('Thinking', 'Action')]; pit = [x for x in g if x['view'] == 'Pitfall']; rev = [x for x in g if x['view'] == 'Revision']
    mech = {}
    for x in good: mech.setdefault(x['mech_core'], x)
    if len(mech) >= 2 and pit:
        pick = list(mech.values())[:2] + [pit[0]] + ([rev[0]] if rev else [])
        add('approach_comparison', pick, 300, B['approach_comparison'])
prog = defaultdict(list)
for r in rows:
    if r['Topic'] not in ('Situational Awareness', 'Planning & Problem Solving', 'Interaction Dynamics'): prog[(r['sid'], r['view'])].append(r)
pk3 = sorted(prog); random.shuffle(pk3)
for k in pk3:  # progression across ages
    g = prog[k]; byage = {}
    for x in g: byage.setdefault(x['Age'], x)
    if len(byage) >= 2:
        ol = sorted(byage, key=AO.get); pick = [byage[ol[0]], byage[ol[-1]]] if len(ol) == 2 else [byage[ol[0]], byage[ol[len(ol) // 2]], byage[ol[-1]]]
        add('progression', pick, 250, B['progression'])
byconcept = {}
for r in rows:
    if r['Topic'] in CONCEPT_TOPICS: byconcept.setdefault(re.sub(r'\(.*?\)', '', r['Subtopic']).strip().lower(), r)
cl = [(r, c) for r in rows if r['Topic'] not in CONCEPT_TOPICS for c in r['concepts'][:1]]
random.shuffle(cl)
for r, c in cl:
    if c in byconcept and abs(AO[byconcept[c]['Age']] - AO[r['Age']]) <= 2: add('concept_link', [byconcept[c], r], 150, B['concept_link'])
n = 0
with open(os.path.join(a.out, 'clusters.jsonl'), 'w', encoding='utf-8') as f:
    for t, lst in B.items():
        for c in lst:
            n += 1; c['cluster_id'] = 'C%04d' % n; f.write(json.dumps(c, ensure_ascii=False) + '\n')

# ---------- stats ----------
def pct(x, y): return '%.1f%%' % (100.0 * x / max(y, 1))
sit_rows = [r for r in rows if r['stance_core']]; pl = [r for r in rows if r['mech_core']]
und = Counter(r['stance_core'] for r in sit_rows if not r.get('stance_mapped'))
Ugraph = nx.Graph(); Ugraph.add_nodes_from(G.nodes); Ugraph.add_edges_from((u, v) for u, v in G.edges())
comps = sorted(nx.connected_components(Ugraph), key=len, reverse=True)
L = []
L.append('KNOWLEDGE GRAPH STATS')
L.append('nodes %d, edges %d' % (G.number_of_nodes(), G.number_of_edges()))
L.append('node types: ' + ', '.join('%s %d' % kv for kv in Counter(d['type'] for _, d in G.nodes(data=True)).most_common()))
L.append('edge types: ' + ', '.join('%s %d' % kv for kv in Counter(e['rel'] for e in edge_rows).most_common()))
L.append('connected components: %d (largest %d nodes = %s)' % (len(comps), len(comps[0]), pct(len(comps[0]), G.number_of_nodes())))
L.append('situational rows mapped to a core stance: %s (%d distinct core stances, %d unmapped labels)' % (pct(sum(1 for r in sit_rows if r.get('stance_mapped')), len(sit_rows)), len({r['stance_core'] for r in sit_rows if r.get('stance_mapped')}), len(und)))
L.append('planning rows mapped to a named mechanism from the label: %s; from label or description: %s (%d distinct mechanisms)' % (pct(sum(1 for r in pl if r['mech_from_label']), len(pl)), pct(sum(1 for r in pl if r['mech_core'] != 'other'), len(pl)), len({r['mech_core'] for r in pl}) - 1))
L.append('planning rows given a strategy family: %s' % pct(sum(1 for r in pl if r['family'] != 'unclassified'), len(pl)))
L.append('heuristic concept-similarity links: %d rows (threshold %.2f)' % (nsim, SIM_MIN))
L.append('rows with >=1 mind state mention: %s' % pct(sum(1 for r in rows if r['states']), len(rows)))
L.append('rows mentioning a concept from Cognitive/Foundational blocks: %s' % pct(sum(1 for r in rows if r['concepts']), len(rows)))
L.append('concepts total %d; concepts referenced by at least one other row: %d' % (len(concepts), len({c for r in rows for c in r['concepts']})))
L.append('clusters: ' + ', '.join('%s %d' % (t, len(v)) for t, v in B.items()) + '; total %d' % n)
L.append('top unmapped stance labels: ' + ', '.join('%s (%d)' % kv for kv in und.most_common(15)))
L.append('top stance cores: ' + ', '.join('%s %d' % kv for kv in Counter(r['stance_core'] for r in sit_rows if r.get('stance_mapped')).most_common(12)))
L.append('top mechanisms: ' + ', '.join('%s %d' % kv for kv in Counter(r['mech_core'] for r in pl).most_common(14)))
L.append('top mind states: ' + ', '.join('%s %d' % kv for kv in Counter(s for r in rows for s in r['states']).most_common(12)))
open(os.path.join(a.out, 'stats.txt'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('\n'.join(L))
