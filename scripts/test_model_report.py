#!/usr/bin/env python3
"""Score a model test run and write the accuracy tables.
  python scripts/test_model_report.py [--dir train/test_run5]
Reads <dir>/testset.jsonl, answers.jsonl and grades.jsonl ({"id", "grade": 1 | 0.5 | 0, "note"}; graded by a reviewer
reading each answer against the training reference). Writes <dir>/results.csv (one row per question) and
<dir>/report.md (summary by category and by type, then the per-question table).
Automatic measures, alongside the human grade:
  f1        content-word overlap (F1) between answer and training reference (0-1); multi_question: mean over sub-answers
  exact     grammar only: the corrected sentence matches the training correction (case/punctuation-insensitive)
"""
import argparse, collections, csv, json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser(); ap.add_argument('--dir', default=os.path.join(ROOT, 'train', 'test_run5')); a = ap.parse_args()
load = lambda n: [json.loads(l) for l in open(os.path.join(a.dir, n), encoding='utf-8') if l.strip()]
tests, answers = load('testset.jsonl'), {r['id']: r for r in load('answers.jsonl')}
grades = {r['id']: r for r in load('grades.jsonl')} if os.path.exists(os.path.join(a.dir, 'grades.jsonl')) else {}
STOP = set('a an the and or but if of to in on at for with by from is are was were be been am it its this that these those i you he she '
           'we they me him her us them my your his our their as so not no do does did can will would should could has have had '
           'there here what which who whom how why when where than then too very just also about into out up down over'.split())
words = lambda s: [w for w in re.findall(r"[a-z0-9']+", (s or '').lower()) if w not in STOP]
def f1(ans, ref):
    A, R = collections.Counter(words(ans)), collections.Counter(words(ref))
    if not A or not R: return 0.0
    c = sum((A & R).values())
    return 0.0 if c == 0 else 2 * c / (sum(A.values()) + sum(R.values()))
norm = lambda s: re.sub(r'[^a-z0-9 ]', '', re.sub(r'\s+', ' ', (s or '').lower())).strip()
first = lambda s: (s or '').strip().split('\n')[0]

rows = []
for t in tests:
    ans = answers.get(t['id'], {}).get('answer', '')
    if t['category'] == 'multi_question':
        sc = round(sum(max(f1(p, r) for p in [ans] + ans.split('\n')) for r in t['reference']) / len(t['reference']), 3)
    elif t['reference']: sc = round(f1(ans, t['reference']), 3)
    else: sc = ''
    ex = (int(norm(first(ans)) == norm(first(t['reference'])))) if t['category'] == 'grammar' else ''
    g = grades.get(t['id'], {})
    q = t['question'].replace('\n', ' ')
    rows.append({'id': t['id'], 'category': t['category'], 'type': t['type'], 'question': q[:110] + ('...' if len(q) > 110 else ''),
                 'answer': ans.replace('\n', ' / ')[:160], 'f1': sc, 'exact': ex, 'grade': g.get('grade', ''), 'note': g.get('note', '')})
with open(os.path.join(a.dir, 'results.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def summary(key):
    out = ['| ' + key + ' | n | accuracy | correct | partial | wrong | word overlap (F1) |', '|---|---|---|---|---|---|---|']
    groups = collections.defaultdict(list)
    for r in rows: groups[r[key]].append(r)
    groups['ALL'] = rows
    for k, rs in groups.items():
        gs = [r['grade'] for r in rs if r['grade'] != '']
        fs = [r['f1'] for r in rs if r['f1'] != '']
        acc = f'{100 * sum(gs) / len(gs):.0f}%' if gs else '-'
        c1, c0 = sum(1 for x in gs if x >= 1), sum(1 for x in gs if x <= 0); cp = len(gs) - c1 - c0
        f = f'{sum(fs) / len(fs):.2f}' if fs else '-'
        out.append(f'| {"**ALL**" if k == "ALL" else k} | {len(rs)} | {acc} | {c1} | {cp} | {c0} | {f} |')
    return '\n'.join(out)
gr = [r for r in rows if r['category'] == 'grammar']
for r in rows:   # finer groups for the breakdown table
    n = int(r['id'].rsplit('_', 1)[1])
    r['group'] = {'passage': 'passage: fact from the text' if n <= 40 else 'passage: follow-up (feelings, advice)',
                  'multi_question': f'multi_question: {2 + (n - 1) // 10} questions'}.get(r['category'], r['category'])
fixed = sum(1 for r in gr if r['note'].startswith(('correction right', 'acceptable fix')))
md = [f"# Run {os.path.basename(os.path.normpath(a.dir)).split('run')[-1]} model test: {len(tests)} questions from the training material", '',
      'Accuracy = mean grade (correct = 1, partial = 0.5, wrong = 0), graded by reading each answer against the training '
      'reference (stories: relevance, coherence and length). Word overlap = content-word F1 with the training answer.', '',
      '## By category', '', summary('category'), '',
      f'Grammar: the corrected sentence was right in {fixed}/{len(gr)} answers (exact match with the training correction: '
      f'{sum(r["exact"] for r in gr)}/{len(gr)}); the "Why:" explanation was right in none, which is why those answers score 0.5.', '',
      '## Breakdown', '', summary('group'), '',
      '## By training type', '', summary('type'), '', '## Every question', '',
      '| id | type | question | answer (start) | F1 | grade | note |', '|---|---|---|---|---|---|---|']
esc = lambda s: str(s).replace('|', '\\|')
for r in rows:
    md.append(f'| {r["id"]} | {r["type"]} | {esc(r["question"])} | {esc(r["answer"])} | {r["f1"]} | {r["grade"]} | {esc(r["note"])} |')
open(os.path.join(a.dir, 'report.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
print(summary('category'))
