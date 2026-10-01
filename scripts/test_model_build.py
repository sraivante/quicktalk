#!/usr/bin/env python3
"""Build a fixed test set for a trained QuickTalk model, using ONLY material the model was trained on.
  python scripts/test_model_build.py [--seed 7] [--out train/test_run5/testset.jsonl]
Questions come from train/build/sft_train_*.jsonl (the chat data the model was fine-tuned on); story requests also
use subjects from the pretraining books / TinyStories. Each item keeps the training answer as its reference.
Categories:
  simple_oneliner    short one-line questions (vocab, usage, raga, literature)
  complex_oneliner   longer one-line requests (reasoning, instruct, hinglish_esl)
  multiline_simple   multi-line messages to rewrite
  multiline_complex  passage + question (comprehension), passage to summarise (summary)
  multi_question     2-5 training one-liners asked together on one line
  multiturn          a conversation from training; the model gives the last reply (earlier turns are the training ones)
  story              training story prompts + "Tell me a story about ..." from the training books
  writing            other writing requests (notes, letters, diary entries)
  grammar            correct a sentence
  passage            behaviour passages: "Read this: ..." + question; first question, or a later one with history
"""
import argparse, collections, glob, json, os, random
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument('--seed', type=int, default=7)
ap.add_argument('--out', default=os.path.join(ROOT, 'train', 'test_run5', 'testset.jsonl'))
a = ap.parse_args()
rng = random.Random(a.seed)

by, seen = collections.defaultdict(list), set()
for f in sorted(glob.glob(os.path.join(ROOT, 'train', 'build', 'sft_train_*.jsonl'))):
    for l in open(f, encoding='utf-8'):
        r = json.loads(l); k = (r['metadata']['type'], r['messages'][0]['content'])
        if k in seen: continue                      # chat patterns appear 3x in training; keep one copy
        seen.add(k); by[r['metadata']['type']].append(r)
for t in by: rng.shuffle(by[t])
used = set()
def take(t, n, cond=lambda r: True):
    out = []
    for r in by[t]:
        if len(out) == n: break
        if id(r) in used or not cond(r): continue
        used.add(id(r)); out.append(r)
    assert len(out) == n, (t, n, len(out))
    return out
single = lambda r: sum(m['role'] == 'user' for m in r['messages']) == 1
oneline = lambda r: single(r) and '\n' not in r['messages'][0]['content'].strip()
items = []
def add(cat, r, history, question, reference, **extra):
    items.append({'id': f'{cat}_{sum(i["category"] == cat for i in items) + 1:03d}', 'category': cat,
                  'type': r['metadata']['type'] if r else extra.pop('type'), 'source_id': r['metadata'].get('id') if r else None,
                  'history': history, 'question': question, 'reference': reference, **extra})
def first(cat, r): add(cat, r, [], r['messages'][0]['content'], r['messages'][1]['content'])

for t, n in (('vocab', 15), ('usage', 10), ('raga', 15), ('literature', 10)):
    for r in take(t, n, lambda r: oneline(r) and len(r['messages'][0]['content'].split()) <= 12): first('simple_oneliner', r)
for t, n in (('reasoning', 20), ('instruct', 15), ('hinglish_esl', 15)):
    for r in take(t, n, oneline): first('complex_oneliner', r)
for r in take('rewrite', 30, lambda r: single(r) and r['messages'][0]['content'].count('\n') >= 2): first('multiline_simple', r)
for t in ('comprehension', 'summary'):
    for r in take(t, 20, single): first('multiline_complex', r)
pool = {t: [r for r in by[t] if id(r) not in used and oneline(r) and r['messages'][0]['content'].rstrip().endswith('?')]
        for t in ('vocab', 'usage', 'raga', 'literature', 'reasoning')}
flat = [r for t in pool for r in pool[t]]; rng.shuffle(flat)
for k in (2, 3, 4, 5):
    for _ in range(10):
        qs = [flat.pop() for _ in range(k)]
        for r in qs: used.add(id(r))
        add('multi_question', None, [], ' '.join(r['messages'][0]['content'].strip() for r in qs),
            [r['messages'][1]['content'] for r in qs], type='mixed', n_questions=k,
            sub_questions=[r['messages'][0]['content'] for r in qs], sub_types=[r['metadata']['type'] for r in qs])
for r in take('multiturn', 25, lambda r: sum(m['role'] == 'user' for m in r['messages']) >= 2):
    m = r['messages']; add('multiturn', r, m[:-2], m[-2]['content'], m[-1]['content'])
stories = take('writing', 13, lambda r: 'story' in r['messages'][0]['content'].lower())
for r in stories: first('story', r)
for s in ['the monkey and the crocodile', 'the snake and the ants', 'the lion and the carpenter', 'a jackal who wanted to be king',
          'Hanuman crossing the sea to Lanka', 'Arjuna and the bird\'s eye', 'Alice falling down the rabbit hole',
          'a little girl who finds a lost puppy', 'a boy who loses his red ball in the park', 'a small bird who learns to fly',
          'two friends who share their lunch', 'a cat who is afraid of the rain']:
    add('story', None, [], f'Tell me a story about {s}.', None, type='story_free',
        source_note='subject from pretraining books / TinyStories')
for r in take('writing', 15, lambda r: 'story' not in r['messages'][0]['content'].lower()): first('writing', r)
for r in take('grammar', 40): first('grammar', r)
beh = take('behaviour', 60)
for r in beh[:40]: first('passage', r)
for r in beh[40:]:
    k = rng.choice([1, 2, 3]); m = r['messages']               # ask question k+1 with the earlier turns as history
    add('passage', r, m[:2 * k], m[2 * k]['content'], m[2 * k + 1]['content'], turn=k + 1)

os.makedirs(os.path.dirname(a.out), exist_ok=True)
with open(a.out, 'w', encoding='utf-8') as f:
    for it in items: f.write(json.dumps(it, ensure_ascii=False) + '\n')
print(len(items), dict(collections.Counter(i['category'] for i in items)))
