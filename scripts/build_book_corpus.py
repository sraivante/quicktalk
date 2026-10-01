#!/usr/bin/env python3
"""Clean the source book zips in compressdata/ into English-only pretraining text under train/sources/books/.
  python scripts/build_book_corpus.py
For every book:
  - Project Gutenberg header/footer and licence text are removed;
  - sentences in another language (French, Italian, Latin, German, Spanish) are removed, as are lines in a non-Latin script;
  - accents are stripped (Ráma -> Rama) and curly quotes made straight;
  - headings, tables of contents, page numbers, [Illustration] tags and _italic_ marks are removed;
  - hard-wrapped prose is re-joined into paragraphs; verse keeps its line breaks;
  - the Panchatantra OCR prints two book pages side by side, so each spread is split back into left page then right page.
Writes one file per book (paragraphs separated by a blank line) plus train/sources/books/REPORT.txt with counts.
The raga Q&A (already chat format) is copied to train/sources/raga_qa.jsonl.
"""
import collections, json, os, re, unicodedata, zipfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZD = os.path.join(ROOT, 'compressdata')
OUT = os.path.join(ROOT, 'train', 'sources', 'books'); os.makedirs(OUT, exist_ok=True)

FOREIGN = {  # function words that are not English words
    'fr': 'le la les des du une est que qui pas vous je il elle nous mais pour avec sur dans ce cette mon ma mes son sa ses au aux ne sont été très oui non comme tout plus qu c est n y moi toi lui leur leurs nos vos notre votre ici voilà dieu bon bonne donc alors aussi bien faire fait avez avons êtes suis sommes ont était cher chère quand rien homme femme monsieur madame mademoiselle merci voir aime contente sot allez voulez manger danser connaissez beau charmant charme ou',
    'it': 'il lo gli della delle degli di che non per una sono è si mi ti ci al alla nel nella con ma come più questo quella del dei ed poi già ancora',
    'la': 'et est non ad cum sed quod qui quae ut ab ex enim vero etiam autem sunt esse ille illud ideo nullum aliud ei sit hic haec atque',
    'de': 'der die das und ist nicht ich du er sie wir ihr mit von zu den dem des ein eine einen auf für sich auch noch nur wie aber',
    'sa': 'iti cha ca eva api yatha tatha tasya yasya tena sah asti bhavati tvam aham',
    'es': 'el los las del que y es un una por con para no se su sus al como pero más muy está estoy',
}
AMBIG = set('pour beau ca lo er non para o e und sich nur ne monsieur madame mademoiselle c n y come ma mi ti ci si al con per di sit ad ex hic son plus die den dem also no es un sur ce sa ne au tout il ed poi'.split())  # also English words, or note names
FOREIGN = {k: set(v.split()) - AMBIG for k, v in FOREIGN.items()}
EN = set('the and of to a in that is was he for it with as his on be at by i had not are but from or have an they which you were her she there their this my me we him so all would what will been one if no when who them said'.split())

def ascii_fold(s):
    s = s.replace('‘', "'").replace('’', "'").replace('“', '"').replace('”', '"').replace(' ', ' ')
    s = ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
    s = s.replace('æ', 'ae').replace('Æ', 'Ae').replace('œ', 'oe').replace('Œ', 'Oe').replace('ß', 'ss')
    return re.sub(r'[©®™°•·§¶]', '', s)

def non_latin(s):
    return any(ord(c) > 0x24f and unicodedata.category(c).startswith('L') for c in s)

def is_foreign(sent):
    w = re.findall(r"[a-zà-ÿ]+", sent.lower())
    if not w: return False
    e = sum(x in EN for x in w)
    if 2 <= len(w) <= 6:  # short phrase of 2+ words: one foreign function word and no English one is enough
        h = max(sum(x in fw for x in w) for fw in FOREIGN.values())
        fh = h + (sum(bool(re.search(r'[éèêçàùôîâœ]', x)) for x in w) if h else 0)
        return (h >= 1 and e == 0) or (fh >= 2 and fh > e)
    if len(w) < 2: return False
    acc = sum(bool(re.search(r'[éèêëçàùôîâœ]', x)) for x in w)  # accents count only next to a foreign function word (names: Pétya, Adèle; poetry: belovéd)
    return any(h >= 1 and h + acc >= 2 and h + acc > e for h in (sum(x in fw for x in w) for fw in FOREIGN.values()))

def strip_gutenberg(t):
    m = re.search(r'\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG[^\n]*\n', t)
    if m: t = t[m.end():]
    m = re.search(r'\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG', t)
    if m: t = t[:m.start()]
    m = re.search(r'\n\s*End of (the )?Project Gutenberg', t, re.I)
    if m: t = t[:m.start()]
    return t

HEAD = re.compile(r'^\s*(chapter|book|canto|part|volume|section|stave|letter|parva|appendix|contents|index|preface|footnotes?|notes?)\b[^a-z]{0,8}[\w .,:;\'"-]{0,70}$', re.I)

def split_spreads(t):
    """Panchatantra OCR: a header line holding two page numbers starts a two-page spread; re-order it left page then right page."""
    lines = t.split('\n'); out, block = [], []
    def flush():
        if not block: return
        starts = [m.end() for l in block for m in [re.search(r'\S\s{4,}(?=\S)', l)] if m]
        if len(starts) < 3: out.extend(block); block.clear(); return
        B = collections.Counter(s // 4 * 4 for s in starts if s > 30).most_common(1)
        if not B: out.extend(block); block.clear(); return
        B = B[0][0]; left, right = [], []
        for l in block:
            cut = None
            for m in re.finditer(r'\s{3,}(?=\S)', l):
                if abs(m.end() - B) <= 10 and m.start() > 0 and l[:m.start()].strip(): cut = m.end(); break
            if cut: left.append(l[:cut].rstrip()); right.append(l[cut:])
            elif len(l) - len(l.lstrip()) >= B - 10 and l.strip(): right.append(l.strip())
            else: left.append(l)
        out.extend(left + [''] + right); block.clear()
    for l in lines:
        if re.search(r'\d{2,3}\s.*PANCHATANTRA|PANCHATANTRA.*\s\d{2,3}\s*$|^\s*\d{2,3}\s{3,}\S.*\S\s{3,}\S*\s*\d{2,3}\s*$', l):
            flush(); continue  # header line of a spread: drop it, start a new block
        block.append(l)
    flush()
    return '\n'.join(out)

def paragraphs(t, narrow=False):
    for para in re.split(r'\n\s*\n', t):
        ls = [l.rstrip().replace(' _', ' ') for l in para.split('\n') if l.strip().strip('_')]
        ls = [re.sub(r'^(\s*)_', r'\1', l) for l in ls]
        ls = [l for l in ls if not re.fullmatch(r'\s*[\divxlcIVXLC.\-*\s]{1,12}\s*', l)]  # page numbers, rule lines
        if not ls: continue
        verse = len(ls) >= 2 and sum(len(l.strip()) for l in ls) / len(ls) < 48
        if verse and narrow:  # narrow page columns (Panchatantra): a long line is wrapped prose, a short one is verse
            txt = ''
            for l in ls:
                l = l.strip()
                if not txt: txt = l
                elif txt.endswith('-') and l[:1].islower(): txt = txt[:-1] + l
                elif len(txt.split('\n')[-1]) >= 40 and not re.search(r'[.!?:"]$', txt): txt += ' ' + l
                else: txt += '\n' + l
        elif verse: txt = '\n'.join(l.strip() for l in ls)
        else:
            txt = ''
            for l in ls:
                l = l.strip()
                if txt.endswith('-') and l[:1].islower() and not txt.endswith('--'): txt = txt[:-1] + l
                else: txt = (txt + ' ' + l) if txt else l
        yield txt

def clean_para(p, stats, lang_filter=True, epic=False):
    ls = p.split('\n')
    if len(ls) >= 4 and sum(bool(HEAD.match(l)) for l in ls) >= len(ls) * 0.6: stats['table of contents'] += 1; return None
    if epic and re.match(r'\d{1,4}\.? ', p): stats['footnote'] += 1; return None  # numbered notes in the epics, often Sanskrit
    p = re.sub(r'\[(Illustration|Footnote|Sidenote)[^\]]*\]', '', p, flags=re.I)
    p = re.sub(r'\[\d+\]', '', p).replace('_', '')
    p = re.sub(r'[ \t]+', ' ', p).strip()
    if not p or not re.search(r'[a-z]', p): stats['heading/blank'] += 1; return None
    if HEAD.match(p) and len(p) < 90: stats['heading/blank'] += 1; return None
    if re.search(r'gutenberg|ebook|transcriber|produced by', p, re.I): stats['gutenberg/transcriber'] += 1; return None
    lines_out = []
    for line in p.split('\n'):
        keep = []
        for s in re.split(r'(?<=[.!?;:])\s+', line):
            if non_latin(s) or (lang_filter and is_foreign(s)): stats['foreign sentence'] += 1; continue
            parts = re.split(r'(\s*[,;:()\u2014"*\u201c\u201d]\s*|\s+--\s*|(?<=\s)[\'\u2018]|[\'\u2019](?=\s|$|[,.!?]))', s)  # clauses and quoted bits
            if len(parts) > 1:
                bad = [i for i in range(0, len(parts), 2) if is_foreign(parts[i])]
                for i in bad: parts[i] = ''
                if bad: stats['foreign phrase'] += len(bad)
                s = re.sub(r'\s{2,}', ' ', ''.join(parts)).strip()
                s = re.sub(r'(^|\s)[,;:]\s*', r'\1', s); s = re.sub(r"''|\"\"", '', s).strip()
            if s and re.search(r'[A-Za-z]', s): keep.append(s)
        if keep: lines_out.append(' '.join(keep))
    p = ascii_fold('\n'.join(lines_out)).strip()
    if len(re.findall(r'[A-Za-z]+', p)) < 3: stats['too short'] += 1; return None
    junk = len(re.findall(r'[^A-Za-z0-9\s.,;:!?\'"()\-—–]', p))
    if junk > max(3, len(p) * 0.03): stats['ocr junk'] += 1; return None
    return p

BOOKS = [  # (zip, member regex, output name)
    ('english_big_vocabulary_novels_txt.zip', r'downloads/(\d\d_.*)\.txt$', None),
    ('complete_ramayana_mahabharata_english_txt.zip', r'package/(?:Ramayana|Mahabharata)/(.*)\.txt$', None),
    ('complete_panchatantra_english_stories_with_morals.zip', r'package/(?:Full_Text_OCR_Sections|Index_and_Morals)/(.*)\.txt$', 'Panchatantra_Ryder'),
    ('indian_raga_teaching_english_with_qa.zip', r'package/Book/(.*)\.txt$', 'Raga_Teaching_Book'),
]
report, combined = [], collections.defaultdict(list)
for zname, pat, merged in BOOKS:
    z = zipfile.ZipFile(os.path.join(ZD, zname))
    for m in sorted(z.namelist()):
        mm = re.search(pat, m)
        if not mm: continue
        raw = z.read(m).decode('utf-8', errors='replace').replace('\r\n', '\n')
        t = strip_gutenberg(raw)
        if 'panchatantra' in zname: t = split_spreads(t)
        stats = collections.Counter(); kept = []
        for para in paragraphs(t, narrow='panchatantra' in zname):
            c = clean_para(para, stats, lang_filter='raga' not in zname, epic='ramayana' in zname)  # raga book: note names (Sa Re Ga Ma) are not a language
            if c: kept.append(c)
        name = merged or re.sub(r'^\d\d_', '', mm.group(1))
        combined[name].extend(kept)
        report.append(f"{name:<55} {mm.group(1)[:40]:<40} words_in={len(raw.split()):>8} paras_kept={len(kept):>6} words_kept={sum(len(k.split()) for k in kept):>8} dropped={dict(stats)}")
for old in os.listdir(OUT):
    if old.endswith('.txt'): os.remove(os.path.join(OUT, old))
tot = 0
for name, paras in combined.items():
    open(os.path.join(OUT, name + '.txt'), 'w', encoding='utf-8').write('\n\n'.join(paras) + '\n')
    tot += sum(len(p.split()) for p in paras)
report.append(f'TOTAL words kept: {tot}')
open(os.path.join(OUT, 'REPORT.txt'), 'w', encoding='utf-8').write('\n'.join(report) + '\n')
z = zipfile.ZipFile(os.path.join(ZD, 'indian_raga_teaching_english_with_qa.zip'))
with open(os.path.join(ROOT, 'train', 'sources', 'raga_qa.jsonl'), 'w', encoding='utf-8') as f:
    for i, l in enumerate(z.read('package/Question_Answers/Raga_Teaching_QA_Assistant_Format.jsonl').decode('utf-8').splitlines()):
        if not l.strip(): continue
        r = json.loads(l); r.setdefault('metadata', {}); r['metadata'].update({'source': 'raga', 'id': f'raga-{i}', 'group': f'raga-{i // 10}'})
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print('\n'.join(report[-1:]))
