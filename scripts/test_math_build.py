"""Build an auto-gradable maths test (run 7+): unseen GSM8K test problems, fresh easy word problems, and seen items.
Usage: python scripts/test_math_build.py --out train/test_math/testset.jsonl
Each line: id, category, question, history [], gold (number), reference (training answer or worked answer)."""
import argparse, glob, json, os, random, re

ap = argparse.ArgumentParser(); ap.add_argument('--out', default='train/test_math/testset.jsonl'); ap.add_argument('--seed', type=int, default=7)
a = ap.parse_args(); R = random.Random(a.seed)
NUM = r'-?\d[\d,]*(?:\.\d+)?'
def num(s): return float(s.replace(',', ''))
def rows(p): return [json.loads(l) for l in open(p, encoding='utf-8')]
seen_q = set()
for p in glob.glob('train/chat*/*.jsonl') + glob.glob('train/math/*_chat.jsonl') + glob.glob('train/pilot/*.jsonl'):
    for r in rows(p): seen_q.add(r['messages'][0]['content'].strip().lower())
out = []
def add(cat, i, q, gold, ref): out.append({'id': f'{cat}_{i:03d}', 'category': cat, 'history': [], 'question': q, 'gold': gold, 'reference': ref})

# 1. GSM8K test (never trained on): gold = number after "The answer is"
gsm = rows('train/math/gsm8k_test.jsonl'); R.shuffle(gsm)
for i, r in enumerate(gsm[:200], 1):
    ref = r['messages'][1]['content']; add('gsm8k_test', i, r['messages'][0]['content'], num(re.search(r'The answer is (' + NUM + ')', ref).group(1)), ref)

# 2. Fresh easy word problems (same kind as the run 7 easy sums, new names/numbers, checked not in training)
names = ['Asha', 'Ben', 'Chen', 'Dev', 'Ella', 'Farah', 'Gopal', 'Hana', 'Ivan', 'Jaya', 'Kofi', 'Lina', 'Manu', 'Nora']
things = ['apples', 'stickers', 'marbles', 'books', 'pencils', 'shells', 'cards', 'stamps', 'beads', 'buttons']
T = [('add', lambda n, t, x, y: (f'{n} has {x} {t} and gets {y} more. How many {t} does {n} have now?', x + y)),
     ('sub', lambda n, t, x, y: (f'{n} had {x + y} {t} and gave away {y}. How many {t} are left?', x)),
     ('mul', lambda n, t, x, y: (f'{n} has {x % 9 + 2} bags with {y % 11 + 2} {t} in each bag. How many {t} are there in all?', (x % 9 + 2) * (y % 11 + 2))),
     ('div', lambda n, t, x, y: (f'{n} shares {(x % 9 + 2) * (y % 9 + 2)} {t} equally among {x % 9 + 2} friends. How many {t} does each friend get?', y % 9 + 2)),
     ('money', lambda n, t, x, y: (f'{n} buys a book for Rs {x} and a pen for Rs {y}. How much does {n} spend in all?', x + y))]
i = 0
while i < 100:
    k, f = T[i % len(T)]; q, g = f(R.choice(names), R.choice(things), R.randint(5, 60), R.randint(3, 40))
    if q.lower() in seen_q: continue
    i += 1; add('easy_fresh', i, q, float(g), f'{g}')

# 3. Seen in training: laghumath items whose answer line is a single number; run 7 easy sums
lm = [r for r in rows('train/math/laghumath_chat.jsonl') if re.fullmatch(r'Answer: (' + NUM + r')[^\d\n]{0,25}', r['messages'][1]['content'].split('\n')[0])
      and len(r['messages']) == 2]
R.shuffle(lm)
for i, r in enumerate(lm[:100], 1):
    ref = r['messages'][1]['content']; add('laghumath_seen', i, r['messages'][0]['content'], num(re.match(r'Answer: (' + NUM + ')', ref).group(1)), ref)
r7 = rows('train/chat_r7/reasoning.jsonl'); R.shuffle(r7)
for i, r in enumerate(r7[:50], 1):
    ref = r['messages'][1]['content']; add('easy_seen', i, r['messages'][0]['content'], num(re.search(NUM, ref).group(0)), ref)

os.makedirs(os.path.dirname(a.out), exist_ok=True)
with open(a.out, 'w', encoding='utf-8') as f:
    for r in out: f.write(json.dumps(r, ensure_ascii=False) + '\n')
from collections import Counter; print(len(out), dict(Counter(r['category'] for r in out)))
