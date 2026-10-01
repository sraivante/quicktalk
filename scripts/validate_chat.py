#!/usr/bin/env python3
"""Validate chat-pattern JSONL files (train/spec/CHAT_PATTERNS.md).
  python scripts/validate_chat.py <file.jsonl> [--type <type>] [--no-arithmetic]
--no-arithmetic: reasoning examples may not contain digits (run 6 onward: everyday reasoning only, no sums).
--short-why: grammar "Why:" line must be at most 15 words (run 7 style); dont_know may not be about maths.
Prints FAIL lines (must fix) and WARN lines (look at it). Exit code 1 if any FAIL.
"""
import json, os, re, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TYPES = {  # type: (min pairs, max pairs, min words per assistant turn, max words per assistant turn)
    'grammar': (1, 1, 8, 75), 'multiturn': (2, 5, 3, 100), 'vocab': (1, 1, 12, 80), 'rewrite': (1, 1, 4, 150),
    'comprehension': (1, 1, 3, 65), 'writing': (1, 1, 20, 180), 'usage': (1, 1, 12, 90), 'hinglish_esl': (1, 3, 4, 110),
    'summary': (1, 1, 6, 90), 'literature': (1, 1, 5, 75), 'instruct': (1, 1, 2, 120), 'reasoning': (1, 1, 10, 90),
    'multi_question': (1, 1, 15, 200), 'dont_know': (1, 1, 8, 70),
    'math': (1, 1, 1, 260),   # run 7: converted maths Q&A (laghumath curriculum, GSM8K word problems)
}
UNSURE = re.compile(r"\b(i don't know|i do not know|i'm not sure|i am not sure|i can't (see|check|know|tell|look up|be sure)|"
                    r"i cannot (see|check|know|tell|look up|be sure)|i have no way|i don't have|i do not have|"
                    r"(not|isn't) something i can (see|check|know|tell|look up)|no way (for me )?to (know|see|check|tell)|"
                    r"i wouldn't know|i'm unable to (see|check|know|tell))\b", re.I)
BL = [t.lower() for t in json.load(open(os.path.join(ROOT, 'config', 'blocklist.json')))['terms']]
BAD_OPEN = re.compile(r'^(great question|good question|sure[,!]|certainly[,!]|of course[,!]|absolutely[,!]|as an ai)', re.I)
SIGNOFF = re.compile(r'(hope this helps|happy learning|let me know if)', re.I)
NONASCII = re.compile('[^\x00-\x7F\u2014\u2013\u20b9]')  # allow em/en dash and the rupee sign
EMOJI = re.compile('[\U0001F300-\U0001FAFF☀-➿]')
args = sys.argv[1:]
if not args: sys.exit(__doc__)
path = args[0]; want = args[args.index('--type') + 1] if '--type' in args else None
no_arith = '--no-arithmetic' in args
short_why = '--short-why' in args
run8 = '--run8' in args   # run 8 data: rule-name Why, multiturn 3-5 pairs, stories 80-150 words, 2-question multi_question
RULES = ['subject-verb agreement', 'past tense', 'present tense', 'future tense', 'perfect tense', 'continuous tense',
         'verb form', 'article', 'plural', 'uncountable noun', 'preposition', 'pronoun', 'possessive', 'word order',
         'comparative', 'superlative', 'question form', 'negative', 'spelling', 'capital letter', 'punctuation',
         'apostrophe', 'missing word', 'extra word', 'word choice', 'conjunction']
RULE_WHY = re.compile(r'^Why: (?:' + '|'.join(map(re.escape, RULES)) + r') \([^()\n]+ -> [^()\n]+\)(?:; (?:'
                      + '|'.join(map(re.escape, RULES)) + r') \([^()\n]+ -> [^()\n]+\))*\.$', re.M)
fails = warns = 0; ids = set(); opens = collections.Counter(); topics = collections.Counter(); asst_seen = collections.Counter()
def F(i, m):
    global fails; fails += 1; print(f'FAIL line {i}: {m}')
def W(i, m):
    global warns; warns += 1; print(f'WARN line {i}: {m}')
n = 0
for i, line in enumerate(open(path, encoding='utf-8'), 1):
    if not line.strip(): continue
    n += 1
    try: r = json.loads(line)
    except Exception as e: F(i, f'bad JSON: {e}'); continue
    md, msgs = r.get('metadata') or {}, r.get('messages') or []
    t = md.get('type')
    if t not in TYPES: F(i, f'metadata.type {t!r} unknown'); continue
    if want and t != want: F(i, f'type {t} but file is for {want}')
    for k in ('id', 'group', 'source', 'topic'):
        if not md.get(k): F(i, f'metadata.{k} missing')
    if md.get('id') in ids: F(i, f'duplicate id {md.get("id")}')
    ids.add(md.get('id')); topics[md.get('topic')] += 1
    src = str(md.get('source', ''))
    if not (src == 'generated' or re.match(r'^(book:[A-Za-z0-9_]+|behaviour:\d+-\d+|behaviour:C\d+|laghumath:A\d+|gsm8k:(train|test))$', src)): F(i, f'metadata.source {src!r} not generated/book:<file>/behaviour:<id>')
    if src.startswith('book:') and not os.path.exists(os.path.join(ROOT, 'train', 'sources', 'books', src[5:] + '.txt')): F(i, f'book file for {src} not found')
    if not msgs or any(set(m) != {'role', 'content'} or not str(m['content']).strip() for m in msgs): F(i, 'messages must be non-empty {role, content}'); continue
    roles = [m['role'] for m in msgs]
    if roles != ['user', 'assistant'] * (len(msgs) // 2) or len(msgs) % 2: F(i, f'roles must alternate user/assistant and end with assistant: {roles}'); continue
    lo, hi, wmin, wmax = TYPES[t]
    if not lo <= len(msgs) // 2 <= hi: F(i, f'{t} needs {lo}-{hi} user/assistant pairs, has {len(msgs) // 2}')
    for j, m in enumerate(msgs):
        c = m['content']; low = c.lower()
        for b in BL:
            if re.search(r'\b' + re.escape(b) + r'\b', low): F(i, f'blocked term {b!r} in message {j}')
        if EMOJI.search(c): F(i, f'emoji in message {j}')
        odd = sorted(set(NONASCII.findall(c)))
        if odd: F(i, f'non-ASCII character in message {j}: {odd[:5]}')
        if m['role'] == 'assistant':
            w = len(c.split())
            if w < wmin or w > wmax: F(i, f'assistant turn {j} has {w} words ({t}: {wmin}-{wmax})')
            if BAD_OPEN.search(c.strip()): F(i, f'assistant turn {j} opens with filler: {c[:30]!r}')
            if SIGNOFF.search(c): W(i, f'assistant turn {j} has a sign-off phrase')
            if re.search(r'\b(as an ai|language model)\b', low): F(i, 'assistant mentions being an AI')
            asst_seen[re.sub(r'\W+', ' ', low).strip()] += 1
    opens[' '.join(msgs[0]['content'].lower().split()[:4])] += 1
    u0, a0 = msgs[0]['content'], msgs[1]['content']
    if t == 'grammar':
        if not re.search(r'\bwhy\b', a0, re.I): F(i, 'grammar answer must give the reason ("Why: ...")')
        mw = re.search(r'Why:(.*)', a0, re.S)
        if short_why and not run8 and mw and len(mw.group(1).split()) > 15: F(i, f'"Why:" is {len(mw.group(1).split())} words (max 15, run 7 style)')
        if run8:
            wl = [l for l in a0.split('\n') if l.startswith('Why:')]
            if len(wl) != 1 or not RULE_WHY.match(wl[0]): F(i, 'run 8: one line "Why: <rule> (<trigger> -> <fix>); ...." with rules from the list')
            elif len(wl[0].split()) - 1 > 20: F(i, f'run 8: "Why:" is {len(wl[0].split()) - 1} words (max 20)')
    if t == 'dont_know' and short_why and (md.get('topic') in ('maths', 'math', 'numbers') or re.search(r'\d+\s*[-+*/x%]\s*\d|\d+\s*%', u0)):
        F(i, 'run 7: dont_know is not used for maths')
    if t == 'reasoning' and not re.search(r'\bbecause\b', a0, re.I): F(i, 'reasoning answer must explain with "Because ..."')
    if t == 'reasoning' and no_arith and re.search(r'\d', u0 + a0): F(i, 'no arithmetic in new reasoning examples (digits found)')
    if t == 'multi_question':
        k = md.get('n_questions')
        nums = re.findall(r'(?m)^(\d)\. ', a0)
        if k not in (2, 3, 4, 5): F(i, 'multi_question needs metadata.n_questions 2-5')
        elif nums != [str(x) for x in range(1, k + 1)]: F(i, f'multi_question answer must number its answers 1.-{k}. at line starts, in order (found {nums})')
        if re.search(r'\d\s*[-+*/x]\s*\d', u0): F(i, 'no arithmetic questions in multi_question')
    if run8 and t == 'multiturn':
        if not 3 <= len(msgs) // 2 <= 5: F(i, 'run 8: multiturn needs 3-5 pairs')
        if md.get('n_pairs') != len(msgs) // 2: F(i, 'run 8: metadata.n_pairs must equal the number of pairs')
        if not all(15 <= len(m['content'].split()) <= 70 for m in msgs if m['role'] == 'assistant'): F(i, 'run 8: multiturn assistant turns 15-70 words')
    if run8 and t == 'writing' and md.get('kind') == 'story':
        if not 80 <= len(a0.split()) <= 150: F(i, f'run 8: story has {len(a0.split())} words (80-150)')
    if run8 and t == 'multi_question' and md.get('n_questions') != 2: F(i, 'run 8: multi_question has exactly 2 questions')
    if t == 'dont_know' and not UNSURE.search(a0): F(i, 'dont_know answer must say plainly that it does not know / cannot check')
    if t in ('vocab', 'usage') and len(re.findall(r'[.!?]', a0)) < 2: W(i, f'{t} answer should include an example sentence')
    if t in ('comprehension', 'summary', 'rewrite') and src.startswith('book:'):
        book = open(os.path.join(ROOT, 'train', 'sources', 'books', src[5:] + '.txt'), encoding='utf-8').read()
        norm = lambda x: re.sub(r'\s+', ' ', x)
        bnorm = norm(book)
        chunks = [norm(c.strip()) for m in msgs if m['role'] == 'user' for c in re.split(r'\n\s*\n', m['content']) if len(c.split()) >= 20]
        found = [c for c in chunks if c in bnorm]
        if chunks and not found: F(i, 'no book excerpt found verbatim in the book file (copy the whole excerpt exactly, in its own paragraph)')
        for c in found:
            if c.count('"') % 2: F(i, 'book excerpt cuts a quotation open (unbalanced double quotes); start and end on whole sentences')
    if t == 'multiturn' and len(msgs) >= 4 and all(m['content'].rstrip().endswith('?') for m in msgs if m['role'] == 'assistant'): W(i, 'every assistant turn ends with a question')
for o, k in opens.items():
    if k > 1: W(0, f'{k} examples open with the same 4 words: {o!r}')
for tp, k in topics.items():
    if n >= 10 and k > max(4, n // 5): W(0, f'topic {tp!r} used {k} times of {n}')
for a, k in asst_seen.items():
    if k > 1 and len(a.split()) > 3: F(0, f'identical assistant reply used {k} times: {a[:50]!r}')
print(f'{path}: {n} examples, {fails} FAIL, {warns} WARN')
sys.exit(1 if fails else 0)
