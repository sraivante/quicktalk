#!/usr/bin/env python3
"""Build maths chat data and a maths pretraining text (deterministic; no randomness).

Usage (from the pack root):
    python3 scripts/build_math_chat.py [--laghumath DIR] [--no-download]

Inputs
    /home/user/sraivante/laghumath/A0..A13.txt   (override with --laghumath)
    GSM8K train.jsonl / test.jsonl (MIT licence), downloaded once with curl and cached in .staging/math/

Outputs
    train/math/laghumath_chat.jsonl   stages 1..8 (A0 is skipped: its Q1/Q2 items are set-up/ASK/EXPECTED
                                      scripts and Q3 is shape drawings, not regular Q&A)
    train/math/gsm8k_chat.jsonl       GSM8K train (training use)
    train/math/gsm8k_test.jsonl       GSM8K test (NOT for training; for later testing)
    train/sources/math/laghumath.txt  full text of A0..A13, ASCII-normalised, lines with leftover non-ASCII dropped

Chat item rules
    D item  -> user: question; assistant: "Answer: ..." + blank line + "Teacher explains" text. The "Now you try:"
               part becomes a separate example when it is a run of questions each followed by a parenthesised answer.
    M item  -> user: instruction + lettered parts, one per line; assistant: answers a) b) ... one per line.
               Over 260 words -> split into chunks of up to 6 parts.
    ids     math-lm-A<stage>-<topic>-<D|M><n>[-try|-<k>]; group = base item id (D item, its try, and M chunks share it);
            metadata also has stage, topic_id; topic is "maths".
    Text is normalised to ASCII (rupee sign kept); items with other non-ASCII, or over 260 assistant words, are dropped
    and counted. A summary is printed at the end.
"""
import argparse, json, os, re, subprocess, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAXW = 260

MAP = {
    '×': 'x', '÷': '/', '−': '-', '–': '-', '—': '-', '≤': '<=', '≥': '>=',
    '≠': '!=', '≈': '~', '²': '^2', '³': '^3', '½': '1/2', '¼': '1/4', '¾': '3/4',
    'π': 'pi', '√': 'sqrt', '‘': "'", '’': "'", '“': '"', '”': '"', '…': '...',
    ' ': ' ',
    '°': ' degrees', '→': '->', '←': '<-', '∠': 'angle ', 'θ': 'theta', 'σ': 'sigma', 'α': 'alpha', 'β': 'beta',
    '⁰': '^0', '¹': '^1', '⁴': '^4', '⁵': '^5', '⁶': '^6', '⁷': '^7', '⁸': '^8', '⁹': '^9', '⁻': '^-',
    '₀': '_0', '₁': '_1', '₂': '_2', '₃': '_3', '₄': '_4', '₅': '_5', '₆': '_6', '₇': '_7', '₈': '_8', '₉': '_9',
    '±': '+/-', 'Σ': 'sum ', '∫': 'integral ', 'Δ': 'delta ', 'ⁿ': '^n', 'ˣ': '^x', 'ₙ': '_n', 'μ': 'mu', 'λ': 'lambda',
}
_TR = {ord(k): v for k, v in MAP.items()}


def norm(s):
    return s.translate(_TR)


def bad_chars(s):
    return [c for c in s if ord(c) > 127 and c != '₹']


def is_ascii_ok(s):
    return not bad_chars(s)


_BL = None


def blocked(text):
    """True if text has a term from config/blocklist.json (validate_chat.py FAILs on those)."""
    global _BL
    if _BL is None:
        _BL = [t.lower() for t in json.load(open(os.path.join(ROOT, 'config', 'blocklist.json')))['terms']]
    low = text.lower()
    return any(re.search(r'\b' + re.escape(b) + r'\b', low) for b in _BL)


def ws(s):
    return re.sub(r'\s+', ' ', s).strip()


def nwords(s):
    return len(s.split())


# ---------------------------------------------------------------- laghumath
ITEM_RE = re.compile(r'^([DM])(\d+)\.\s')
TOPIC_RE = re.compile(r'^TOPIC (\d+\.\d+)\b')
END_RE = re.compile(r'^(MIXED REVISION|END OF STAGE|REVISION TEST)')


def read_items(path):
    """Yield (topic_id, kind, n, lines) for every D/M item under a TOPIC."""
    lines = open(path, encoding='utf-8').read().split('\n')
    topic = None
    cur = None
    out = []
    def flush():
        nonlocal cur
        if cur:
            out.append(cur)
            cur = None
    for ln in lines:
        m = TOPIC_RE.match(ln)
        if m:
            flush(); topic = m.group(1); continue
        if END_RE.match(ln):
            flush(); topic = None; continue
        m = ITEM_RE.match(ln)
        if m and topic:
            flush()
            cur = [topic, m.group(1), int(m.group(2)), [ln]]
            continue
        if cur:
            if ln.strip() == '' or ln.startswith(' '):
                cur[3].append(ln)
            else:
                flush()
    flush()
    return out


def balanced_groups(s):
    """Return list of (start, end) of top-level parenthesised groups in s."""
    res, depth, st = [], 0, None
    for i, c in enumerate(s):
        if c == '(':
            if depth == 0:
                st = i
            depth += 1
        elif c == ')' and depth:
            depth -= 1
            if depth == 0:
                res.append((st, i + 1))
    return res


def parse_try(t):
    """t = text after 'Now you try:'. Return (question, answers_list) or None if answers are not clearly given."""
    t = ws(t)
    # an answer group is preceded by whitespace; a non-final one must also follow sentence punctuation, or be
    # followed by " and <word>" (not "and (" which would be a second bracket pair such as a point)
    gs = []
    for (a, b) in balanced_groups(t):
        if a == 0 or t[a - 1] != ' ' or not (b == len(t) or t[b] == ' '):
            continue
        if b < len(t):
            after = t[b:]
            if not (re.search(r'[.?!:;]$', t[:a].rstrip()) or re.match(r'\s+(and|or)\s+[^(\s]', after)):
                continue
        gs.append((a, b))
    if not gs or not t.endswith(')') or gs[-1][1] != len(t):
        return None
    q, ans, pos = '', [], 0
    for (a, b) in gs:
        seg = t[pos:a].rstrip()
        # each answer group must follow some question text
        if not re.search(r'\S', seg.replace('?', '').replace('.', '').replace(',', '')) and pos == 0:
            return None
        q += seg + ' '
        ans.append(t[a + 1:b - 1].strip())
        pos = b
    q = ws(q)
    if not q or any(not a for a in ans) or len(q.split()) < 2:
        return None
    # the question should have a real instruction/question, not only 'and'
    q = re.sub(r'\s+([?.,])', r'\1', q)
    return q, ans


def cap(s):
    return s[:1].upper() + s[1:] if s else s


def try_answer(ans):
    if len(ans) == 1:
        a = ans[0].rstrip('.')
        return 'The answer is %s.' % a
    return 'The answers are: %s.' % '; '.join(a.rstrip('.') for a in ans)


def split_parts(text, letters='abcdefghijklmnopqrstuvwxyz'):
    """Sequentially split 'a) ... b) ...' text. Return (prefix, [(letter, text)])."""
    pos, marks = 0, []
    for ch in letters:
        m = re.compile(r'(?<!\S)%s\)\s' % ch).search(text, pos)
        if not m:
            break
        marks.append((ch, m.start(), m.end()))
        pos = m.end()
    if not marks:
        return text, []
    prefix = text[:marks[0][1]]
    parts = []
    for i, (ch, st, en) in enumerate(marks):
        end = marks[i + 1][1] if i + 1 < len(marks) else len(text)
        parts.append((ch, ws(text[en:end])))
    return prefix, parts


def parse_m(lines):
    """Return (instruction, qparts, aparts, plain_answer) or an error string."""
    raw = [l.rstrip() for l in lines]
    idx = None
    for i, l in enumerate(raw):
        if re.match(r'^\s+Answers?\s*:', l) or re.match(r'^M\d+\.\s.*\bAnswers?:', l):
            idx = i
            break
    if idx is None:
        return 'no_answers'
    first = raw[idx]
    am = re.search(r'Answers?\s*:', first)
    qlines = raw[:idx] + ([first[:am.start()]] if not first.startswith(' ') else [])
    alines = [first[am.end():]] + raw[idx + 1:]
    qtxt = '\n'.join(qlines)
    qtxt = re.sub(r'^M\d+\.\s*', '', qtxt)
    # instruction = text before the first line-initial "a)"
    mm = re.search(r'(?m)^\s*a\)\s', qtxt)
    if not mm:
        # parts may start inline after the instruction
        mm = re.search(r'(?<!\S)a\)\s', qtxt)
    if not mm:
        return ws(qtxt), [], [], ws('\n'.join(alines))
    instr = ws(qtxt[:mm.start()])
    _, qparts = split_parts(ws(qtxt[mm.start():]))
    atxt = ws('\n'.join(alines))
    _, aparts = split_parts(atxt)
    if not aparts:
        return 'answers_unlabelled'
    if [p[0] for p in qparts] != [p[0] for p in aparts]:
        return 'parts_mismatch'
    if not instr:
        return 'no_instruction'
    return instr, qparts, aparts, None


def lm_example(id_, group, stage, topic_id, user, asst):
    return {'messages': [{'role': 'user', 'content': user}, {'role': 'assistant', 'content': asst}],
            'metadata': {'type': 'math', 'id': id_, 'group': group, 'source': 'laghumath:A%d' % stage,
                         'topic': 'maths', 'stage': stage, 'topic_id': topic_id}}


def build_laghumath(lmdir, stats):
    rows = []
    seen = set()
    for stage in range(1, 9):
        path = os.path.join(lmdir, 'A%d.txt' % stage)
        for topic, kind, n, lines in read_items(path):
            base = 'math-lm-A%d-%s-%s%d' % (stage, topic, kind, n)
            kk = 'D' if kind == 'D' else 'M'

            def emit(suffix, user, asst, k):
                user, asst = norm(user), norm(asst)
                if not user.strip() or not asst.strip():
                    stats['drop_parse']['empty_' + k] += 1
                    return False
                if blocked(user + ' ' + asst):
                    stats['drop_blocked'][k] += 1
                    return False
                key = re.sub(r'\W+', ' ', asst.lower()).strip()
                if len(key.split()) > 3 and key in seen:
                    stats['drop_dup_reply'][k] += 1
                    return False
                if not is_ascii_ok(user + asst):
                    stats['drop_nonascii'][k] += 1
                    for c in bad_chars(user + asst):
                        stats['badchars'][c] += 1
                    return False
                if nwords(asst) > MAXW:
                    stats['drop_long'][k] += 1
                    return False
                seen.add(key)
                rows.append(lm_example(base + suffix, base, stage, topic, user, asst))
                stats['count'][(stage, k)] += 1
                return True

            if any(re.search(r'-{3,}|={3,}', l) for l in lines) or \
                    (kind == 'D' and any(re.search(r'\S {3,}\S', l.strip()) for l in lines)):
                stats['drop_parse']['layout_diagram_or_table'] += 1
                continue
            text = ws(' '.join(l.strip() for l in lines))
            if kind == 'D':
                text = re.sub(r'^D\d+\.\s*', '', text)
                ma = re.search(r'\bAnswer:\s', text)
                if not ma:
                    stats['drop_parse']['D_no_answer'] += 1
                    continue
                q = text[:ma.start()].strip()
                rest = text[ma.end():]
                mt = re.search(r'\bTeacher explains:\s*', rest)
                if mt:
                    ans, expl = rest[:mt.start()].strip(), rest[mt.end():].strip()
                else:
                    ans, expl = rest.strip(), ''
                tryq = None
                mn = re.search(r'\bNow you try:\s*', expl) if expl else None
                if not mn and not expl:
                    mn = re.search(r'\bNow you try:\s*', ans)
                    if mn:
                        tryq, ans = ans[mn.end():], ans[:mn.start()].strip()
                elif mn:
                    tryq, expl = expl[mn.end():], expl[:mn.start()].strip()
                asst = 'Answer: ' + ans
                if expl:
                    asst += '\n\n' + expl
                emit('', q, asst, 'D')
                if tryq is not None:
                    pt = parse_try(tryq)
                    if pt:
                        tq, tans = pt
                        if len(tq.split()) < 6:   # elliptical prompt: give the original question as context
                            stats['try_with_context'] += 1
                            tuser = q + '\n\nNow you try: ' + tq
                        else:
                            tuser = 'Now you try: ' + tq
                        emit('-try', tuser, try_answer(tans), 'try')
                    else:
                        stats['drop_parse']['try_unclear'] += 1
            else:
                r = parse_m(lines)
                if isinstance(r, str):
                    stats['drop_parse']['M_' + r] += 1
                    continue
                instr, qp, ap, plain = r
                if plain is not None:
                    emit('', instr, plain, 'M')
                    continue
                user = instr + '\n' + '\n'.join('%s) %s' % p for p in qp)
                asst = '\n'.join('%s) %s' % p for p in ap)
                if nwords(norm(asst)) <= MAXW and nwords(norm(user)) <= 400:
                    emit('', user, asst, 'M')
                else:
                    stats['m_split'] += 1
                    for k, i in enumerate(range(0, len(qp), 6), 1):
                        cq, ca = qp[i:i + 6], ap[i:i + 6]
                        u = instr + '\n' + '\n'.join('%s) %s' % p for p in cq)
                        a = '\n'.join('%s) %s' % p for p in ca)
                        emit('-%d' % k, u, a, 'M')
    return rows


# ---------------------------------------------------------------- full text
def build_fulltext(lmdir, outpath, stats):
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    kept = dropped = 0
    out = []
    for stage in range(0, 14):
        for ln in open(os.path.join(lmdir, 'A%d.txt' % stage), encoding='utf-8').read().split('\n'):
            ln = norm(ln).rstrip()
            if bad_chars(ln):
                dropped += 1
                continue
            kept += 1
            out.append(ln)
    text = re.sub(r'\n{3,}', '\n\n', '\n'.join(out)).strip() + '\n'
    with open(outpath, 'w', encoding='ascii' if not re.search('₹', text) else 'utf-8') as f:
        f.write(text)
    stats['text_lines'] = (kept, dropped, len(text.split()))


# ---------------------------------------------------------------- GSM8K
URL = 'https://raw.githubusercontent.com/openai/grade-school-math/master/grade_school_math/data/%s.jsonl'


def fetch(name, nodl):
    d = os.path.join(ROOT, '.staging', 'math')
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name + '.jsonl')
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        if nodl:
            sys.exit('missing ' + p)
        cmd = ['curl', '-sS', '-f', '-L', '-o', p, URL % name]
        ca = '/root/.ccr/ca-bundle.crt'
        if os.path.exists(ca):
            cmd[1:1] = ['--cacert', ca]
        subprocess.run(cmd, check=True)
    return p


def convert_gsm(path, split, stats):
    rows = []
    for i, ln in enumerate(open(path, encoding='utf-8')):
        if not ln.strip():
            continue
        o = json.loads(ln)
        q = norm(o['question']).strip()
        body, _, fin = o['answer'].rpartition('####')
        fin = fin.strip()
        if not fin:
            stats[split]['drop_noanswer'] += 1
            continue
        body = re.sub(r'<<[^>]*>>', '', body)
        body = '\n'.join(l.strip() for l in norm(body).split('\n') if l.strip())
        asst = '%s\nThe answer is %s.' % (body, fin)
        if blocked(q + ' ' + asst):
            stats[split]['drop_blocked'] += 1
            continue
        if not (is_ascii_ok(q) and is_ascii_ok(asst)):
            stats[split]['drop_nonascii'] += 1
            continue
        if nwords(asst) > MAXW:
            stats[split]['drop_long'] += 1
            continue
        id_ = 'math-gsm-%s-%05d' % (split, i)
        rows.append({'messages': [{'role': 'user', 'content': q}, {'role': 'assistant', 'content': asst}],
                     'metadata': {'type': 'math', 'id': id_, 'group': id_, 'source': 'gsm8k:' + split,
                                  'topic': 'maths'}})
        stats[split]['kept'] += 1
    return rows


def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')


def wstats(rows):
    w = sorted(nwords(r['messages'][1]['content']) for r in rows)
    if not w:
        return 'none'
    return 'n=%d min=%d median=%d mean=%.1f p95=%d max=%d' % (len(w), w[0], w[len(w) // 2], sum(w) / len(w),
                                                              w[int(len(w) * .95)], w[-1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--laghumath', default='/home/user/sraivante/laghumath')
    ap.add_argument('--no-download', action='store_true')
    a = ap.parse_args()
    os.chdir(ROOT)
    st = {'count': Counter(), 'drop_nonascii': Counter(), 'drop_long': Counter(), 'drop_blocked': Counter(), 'drop_dup_reply': Counter(), 'drop_parse': Counter(),
          'badchars': Counter(), 'm_split': 0, 'try_with_context': 0, 'train': Counter(), 'test': Counter()}

    rows = build_laghumath(a.laghumath, st)
    ids = [r['metadata']['id'] for r in rows]
    assert len(ids) == len(set(ids)), 'duplicate ids'
    write_jsonl('train/math/laghumath_chat.jsonl', rows)
    build_fulltext(a.laghumath, 'train/sources/math/laghumath.txt', st)

    tr = convert_gsm(fetch('train', a.no_download), 'train', st)
    te = convert_gsm(fetch('test', a.no_download), 'test', st)
    write_jsonl('train/math/gsm8k_chat.jsonl', tr)
    write_jsonl('train/math/gsm8k_test.jsonl', te)

    print('laghumath: A0 skipped (irregular Q1/Q2 set-up/ASK format, Q3 shape drawings)')
    print('laghumath rows:', len(rows), ' word stats:', wstats(rows))
    for s in range(1, 9):
        print('  A%d: ' % s + ', '.join('%s=%d' % (k, st['count'][(s, k)]) for k in ('D', 'try', 'M')))
    tot = {k: sum(st['count'][(s, k)] for s in range(1, 9)) for k in ('D', 'try', 'M')}
    print('  total by kind:', tot)
    print('  try prompts given the original question as context (under 6 words):', st['try_with_context'])
    print('  M items split (over %d words): %d' % (MAXW, st['m_split']))
    print('  dropped non-ASCII:', dict(st['drop_nonascii']), ' dropped too long:', dict(st['drop_long']))
    print('  dropped blocked-term:', dict(st['drop_blocked']), ' dropped duplicate assistant reply:', dict(st['drop_dup_reply']))
    print('  dropped parse:', dict(st['drop_parse']))
    print('  top leftover non-ASCII chars:', [(c, n) for c, n in st['badchars'].most_common(12)])
    k, d, w = st['text_lines']
    print('laghumath.txt: lines kept %d, dropped (leftover non-ASCII) %d, words %d' % (k, d, w))
    print('gsm8k train: %s  words: %s' % (dict(st['train']), wstats(tr)))
    print('gsm8k test: %s  words: %s' % (dict(st['test']), wstats(te)))


if __name__ == '__main__':
    main()
