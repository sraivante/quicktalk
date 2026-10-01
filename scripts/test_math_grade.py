"""Grade maths answers automatically: the model's final number vs the gold number.
Usage: python scripts/test_math_grade.py --testset train/test_math/testset.jsonl --answers A.jsonl [--answers B.jsonl ...]
The model's number: after "The answer is" if present, else after "Answer:", else the first number in the first line
(easy-sum style "24. Because ..."). Prints accuracy per category and run."""
import argparse, json, re
from collections import defaultdict

ap = argparse.ArgumentParser(); ap.add_argument('--testset', required=True); ap.add_argument('--answers', action='append', required=True)
a = ap.parse_args()
NUM = r'-?\d[\d,]*(?:\.\d+)?'
def pick(ans):
    for pat in (r'The answer is\s*\$?\s*(' + NUM + ')', r'Answer:\s*\$?\s*(' + NUM + ')'):
        m = re.search(pat, ans)
        if m: return m.group(1)
    m = re.search(r'(?:Rs\.?\s*|\$)?(' + NUM + ')', ans.split('\n')[0])
    return m.group(1) if m else None
tests = {json.loads(l)['id']: json.loads(l) for l in open(a.testset, encoding='utf-8')}
cats = list(dict.fromkeys(t['category'] for t in tests.values()))
print('| answers | ' + ' | '.join(cats) + ' | ALL |'); print('|---' * (len(cats) + 2) + '|')
for p in a.answers:
    s = defaultdict(list)
    for l in open(p, encoding='utf-8'):
        r = json.loads(l); t = tests[r['id']]; v = pick(r['answer'])
        s[t['category']].append(v is not None and abs(float(v.replace(',', '')) - t['gold']) < 1e-6)
    al = [x for c in cats for x in s[c]]
    print(f'| {p} | ' + ' | '.join(f'{sum(s[c]) / len(s[c]):.0%} ({sum(s[c])}/{len(s[c])})' for c in cats) + f' | {sum(al) / len(al):.0%} |')
