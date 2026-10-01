#!/usr/bin/env python3
"""Train a small GPT-style model from scratch on train/build/ (pretraining text, then chat fine-tuning).

Every step is resumable: run the same command again after a crash or a Colab disconnect and it continues from the
last checkpoint. All state lives in --workdir (put it on Google Drive).

  python quicktalk_lm.py tokenizer --data train/build --workdir W        # BPE tokenizer (skips if done)
  python quicktalk_lm.py prepare   --data train/build --workdir W        # token .bin files (skips if done)
  python quicktalk_lm.py plan      --workdir W                           # token counts -> model size (10 tokens/param)
  python quicktalk_lm.py train     --workdir W --stage pretrain          # resumes automatically
  python quicktalk_lm.py train     --workdir W --stage sft               # starts from pretrain_final.pt
  python quicktalk_lm.py chat      --workdir W                           # try the model

Sizing rule (the user's "10x" rule instead of Chinchilla's 20x): tokens seen in training = 10 x parameters.
Tokens seen = epochs_pretrain x pretrain tokens + epochs_sft x sft tokens.
"""
import argparse, glob, json, math, os, random, re, shutil, sys, time

SPECIALS = ['<|endoftext|>', '<|user|>', '<|assistant|>', '<|end|>', '<|pad|>']

# ----------------------------------------------------------------------------------------------- helpers
def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)

def atomic_json(path, obj):
    tmp = path + '.tmp'; json.dump(obj, open(tmp, 'w'), indent=1); os.replace(tmp, path)

def chat_text(messages):
    """Render a chat; returns list of (text, trainable) pieces. Only assistant replies (and their end tag) train."""
    pieces = []
    for m in messages:
        tag = '<|user|>' if m['role'] == 'user' else '<|assistant|>'
        pieces.append((f'{tag}\n', False))
        pieces.append((m['content'].strip() + '<|end|>\n', m['role'] == 'assistant'))
    pieces.append(('<|endoftext|>', False))
    return pieces

def iter_jsonl(paths):
    for p in paths:
        with open(p, encoding='utf-8') as f:
            for line in f:
                if line.strip(): yield json.loads(line)

def files(data, pattern):
    return sorted(glob.glob(os.path.join(data, pattern)))

# ----------------------------------------------------------------------------------------------- fetch extra text
LANG_PAREN = re.compile(r'\s*\((?:[^()]*?\b(?:French|German|Spanish|Latin|Italian|Hindi|Sanskrit|Arabic|Greek|Japanese|'
                        r'Chinese|Mandarin|Russian|Portuguese|Dutch|Korean|Persian|Urdu|Bengali|Tamil|Telugu|Marathi|'
                        r'Gujarati|Punjabi|Hebrew|Turkish|Polish|Swedish|Norwegian|Danish|Finnish|Czech|Hungarian|'
                        r'Vietnamese|Thai|Indonesian|Malay|Swahili|Irish|Welsh|Scots|Gaelic|pronounced|IPA|lit\.)[^()]*)\)')

def english_clean(text):
    """English only: drop lines with non-Latin scripts, remove '(French: ...)'-style asides, fold accents to ASCII."""
    import unicodedata
    out = []
    for line in text.split('\n'):
        if any(ord(c) > 0x24f and unicodedata.category(c).startswith('L') for c in line): continue
        line = LANG_PAREN.sub('', line)
        line = line.replace('\u2018', "'").replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"')
        line = ''.join(c for c in unicodedata.normalize('NFKD', line) if not unicodedata.combining(c))
        line = ''.join(c for c in line if ord(c) < 128 or c in '\u2014\u2013')
        out.append(line.rstrip())
    return '\n'.join(out).strip()

POS = {'n': 'a noun', 'v': 'a verb', 'a': 'an adjective', 's': 'an adjective', 'r': 'an adverb'}

def fetch_wordnet(out):
    """WordNet definitions written as plain sentences: one paragraph per word, up to 3 senses."""
    import nltk
    nltk.download('wordnet', quiet=True); nltk.download('omw-1.4', quiet=True)
    from nltk.corpus import wordnet as wn
    n = 0
    with open(out + '.tmp', 'w', encoding='utf-8') as w:
        for lemma in sorted(set(wn.all_lemma_names())):
            word = lemma.replace('_', ' ')
            if not re.fullmatch(r"[a-z][a-z' -]*", word) or len(word.split()) > 3: continue
            senses = wn.synsets(lemma)[:3]
            if not senses: continue
            lines = []
            for k, sy in enumerate(senses):
                gloss = sy.definition().strip().rstrip('.;')
                if not gloss: continue
                pos = POS.get(sy.pos(), 'a word')
                lead = f'"{word.capitalize()}" is {pos}. It means {gloss}.' if k == 0 else f'As {pos}, it can also mean {gloss}.'
                ex = [e for e in sy.examples() if lemma.split('_')[0] in e.lower()][:1]
                lines.append(lead + (f' Example: "{ex[0][0].upper() + ex[0][1:]}."' if ex else ''))
            if lines: w.write(english_clean(' '.join(lines)) + '\n\n'); n += 1
    os.replace(out + '.tmp', out); log(f'wordnet: {n:,} words')

def fetch_fineweb_edu(out, mb):
    """A sample of FineWeb-Edu (educational web text, score >= 3), streamed until about `mb` MB of text."""
    from datasets import load_dataset
    ds = load_dataset('HuggingFaceFW/fineweb-edu', name='sample-10BT', split='train', streaming=True)
    n, size = 0, 0
    with open(out + '.tmp', 'w', encoding='utf-8') as w:
        for row in ds:
            if row.get('int_score', 3) < 3 or row.get('language', 'en') != 'en': continue
            text = english_clean(row['text'])
            paras = [q.strip() for q in text.split('\n') if len(q.split()) >= 8]
            if len(' '.join(paras).split()) < 80: continue
            doc = '\n'.join(paras) + '\n\n'; w.write(doc); n += 1; size += len(doc)
            if n % 20000 == 0: log(f'  fineweb_edu: {n:,} documents, {size / 1e6:,.0f} / {mb:,} MB')
            if size >= mb * 1_000_000: break
    os.replace(out + '.tmp', out); log(f'fineweb_edu: {n:,} documents')

def fetch_soda(out):
    """SODA social dialogues (allenai/soda): the situation, then the conversation, one dialogue per block."""
    from datasets import load_dataset
    ds = load_dataset('allenai/soda', split='train')
    n = 0
    with open(out + '.tmp', 'w', encoding='utf-8') as w:
        for row in ds:
            turns = [f'{sp}: {ut.strip()}' for sp, ut in zip(row['speakers'], row['dialogue']) if ut.strip()]
            if len(turns) < 2: continue
            doc = english_clean(row['narrative'].strip() + '\n' + '\n'.join(turns))
            if doc: w.write(re.sub(r'\n\s*\n+', '\n', doc) + '\n\n'); n += 1
    os.replace(out + '.tmp', out); log(f'soda: {n:,} dialogues')

def cmd_fetch(a):
    """Download extra English text as plain text into --out (one document per block, blank line between).
    --sets picks which: tinystories, simplewiki (run 5), wordnet, fineweb_edu, soda (run 6). Existing files are kept."""
    os.makedirs(a.out, exist_ok=True)
    sets = a.sets.split(',')
    for name, fn in (('wordnet', lambda o: fetch_wordnet(o)), ('fineweb_edu', lambda o: fetch_fineweb_edu(o, a.fineweb_mb)),
                     ('soda', lambda o: fetch_soda(o))):
        if name not in sets: continue
        o = os.path.join(a.out, name + '.txt')
        if os.path.exists(o): log('exists, skipping', o)
        else: fn(o)
        log(f'{name}.txt: {os.path.getsize(o) / 1e6:,.0f} MB')
    if 'tinystories' not in sets and 'simplewiki' not in sets: return
    ts = os.path.join(a.out, 'tinystories.txt')
    if 'tinystories' in sets and not os.path.exists(ts):
        from huggingface_hub import hf_hub_download
        src = hf_hub_download('roneneldan/TinyStories', 'TinyStoriesV2-GPT4-train.txt', repo_type='dataset',
                              local_dir=os.path.join(a.out, '_hf'))
        n = 0
        with open(src, encoding='utf-8', errors='replace') as f, open(ts + '.tmp', 'w', encoding='utf-8') as w:
            buf = []
            for line in f:
                if line.strip() == '<|endoftext|>':
                    story = english_clean(''.join(buf)); buf = []
                    story = re.sub(r'\n\s*\n+', '\n', story)            # one story = one document
                    if len(story.split()) >= 20: w.write(story + '\n\n'); n += 1
                else: buf.append(line)
        os.replace(ts + '.tmp', ts); log(f'tinystories: {n:,} stories')
    else: log('exists, skipping', ts)
    sw = os.path.join(a.out, 'simplewiki.txt')
    if 'simplewiki' in sets and not os.path.exists(sw):
        from datasets import load_dataset
        ds = load_dataset('wikimedia/wikipedia', '20231101.simple', split='train')
        n = 0
        with open(sw + '.tmp', 'w', encoding='utf-8') as w:
            for row in ds:
                body = row['text'].split('\nReferences')[0].split('\nRelated pages')[0].split('\nOther websites')[0]
                paras = [q.strip() for q in english_clean(body).split('\n') if len(q.split()) >= 8]
                if len(' '.join(paras).split()) >= 40:
                    w.write(row['title'] + '\n' + '\n'.join(paras) + '\n\n'); n += 1
        os.replace(sw + '.tmp', sw); log(f'simplewiki: {n:,} articles')
    else: log('exists, skipping', sw)
    for f in (ts, sw):
        if os.path.exists(f): log(f'{os.path.basename(f)}: {os.path.getsize(f) / 1e6:,.0f} MB')

# ----------------------------------------------------------------------------------------------- tokenizer
def cmd_tokenizer(a):
    from tokenizers import Tokenizer, models, pre_tokenizers, decoders, trainers
    out = os.path.join(a.workdir, 'tokenizer.json')
    if os.path.exists(out): log('tokenizer exists, skipping:', out); return
    os.makedirs(a.workdir, exist_ok=True)
    def texts():
        for p in files(a.data, 'pretrain_*.txt'):
            with open(p, encoding='utf-8') as f:
                buf = []
                for line in f:
                    buf.append(line)
                    if len(buf) >= 200: yield ''.join(buf); buf = []
                if buf: yield ''.join(buf)
        for r in iter_jsonl(files(a.data, 'sft_train_*.jsonl')):
            yield ''.join(t for t, _ in chat_text(r['messages']))
        for p in (sorted(glob.glob(os.path.join(a.extra, '*.txt'))) if a.extra else []):   # sample of extra text
            with open(p, encoding='utf-8') as f:
                got = 0
                while got < a.extra_sample_mb * 1_000_000:
                    chunk = f.read(1_000_000)
                    if not chunk: break
                    got += len(chunk); yield chunk
    tok = Tokenizer(models.BPE())
    tok.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    tok.decoder = decoders.ByteLevel()
    tr = trainers.BpeTrainer(vocab_size=a.vocab, min_frequency=2, special_tokens=SPECIALS,
                             initial_alphabet=pre_tokenizers.ByteLevel.alphabet())
    log(f'training BPE tokenizer, vocab {a.vocab}')
    tok.train_from_iterator(texts(), trainer=tr)
    tok.save(out + '.tmp'); os.replace(out + '.tmp', out)
    log('saved', out)

def load_tok(workdir):
    from tokenizers import Tokenizer
    return Tokenizer.from_file(os.path.join(workdir, 'tokenizer.json'))

# ----------------------------------------------------------------------------------------------- prepare
def cmd_prepare(a):
    import numpy as np
    tok = load_tok(a.workdir); d = os.path.join(a.workdir, 'data'); os.makedirs(d, exist_ok=True)
    eot = tok.token_to_id('<|endoftext|>')
    assert tok.get_vocab_size() < 65535

    def write_text(name, paths):
        """Stream paragraphs (blank-line separated) through the tokenizer into a uint16 file; low memory."""
        out = os.path.join(d, name + '.bin')
        if os.path.exists(out): log('exists, skipping', out); return
        total = 0
        with open(out + '.tmp', 'wb') as w:
            def flush(paras):
                nonlocal total
                if not paras: return
                ids = []
                for enc in tok.encode_batch(paras): ids.extend(enc.ids); ids.append(eot)
                np.array(ids, dtype=np.uint16).tofile(w); total += len(ids)
            for p in paths:
                paras, cur = [], []
                with open(p, encoding='utf-8') as f:
                    for line in f:
                        if line.strip(): cur.append(line); continue
                        if cur: paras.append(''.join(cur).strip()); cur = []
                        if len(paras) >= 5000: flush(paras); paras = []
                if cur: paras.append(''.join(cur).strip())
                flush(paras)
                log(f'  {name}: {os.path.basename(p)} done, {total:,} tokens so far')
        os.replace(out + '.tmp', out)
        log(f'{name}: {total:,} tokens')

    def write_chat(name, paths, repeat=1, cap=()):
        out = os.path.join(d, name + '.bin')
        if os.path.exists(out): log('exists, skipping', out); return
        ids, mask, starts, types = [], [], [], []
        caps = dict((k, int(v)) for k, v in (x.split('=') for x in cap))      # e.g. behaviour=15000 math=0 (training set only)
        def records():
            rows = list(iter_jsonl(paths))
            if caps:                                   # keep a fixed random sample of the capped types (seeded, so re-runs match)
                rng, keep = random.Random(0), {}
                for t, n in caps.items():
                    idx = [i for i, r in enumerate(rows) if r.get('metadata', {}).get('type') == t]
                    keep[t] = set(rng.sample(idx, min(n, len(idx))))
                rows = [r for i, r in enumerate(rows) if r.get('metadata', {}).get('type') not in caps
                        or i in keep[r['metadata']['type']]]
                log(f'{name}: capped ' + ', '.join(f'{t} to {len(keep[t]):,}' for t in caps))
            for r in rows:
                t = r.get('metadata', {}).get('type', '?')
                for _ in range(repeat if t not in ('behaviour', 'raga', 'math') else 1): yield r   # upsample conversation patterns (not behaviour, raga or the large math set)
        for r in records():
            starts.append(len(ids)); types.append(r.get('metadata', {}).get('type', '?'))
            for text, train in chat_text(r['messages']):
                t = tok.encode(text).ids
                ids.extend(t); mask.extend([1 if train else 0] * len(t))
        np.array(mask, dtype=np.uint8).tofile(os.path.join(d, name + '_mask.bin'))
        np.array(starts, dtype=np.int64).tofile(os.path.join(d, name + '_starts.bin'))
        json.dump(types, open(os.path.join(d, name + '_types.json'), 'w'))
        np.array(ids, dtype=np.uint16).tofile(out + '.tmp'); os.replace(out + '.tmp', out)
        log(f'{name}: {len(starts):,} chats, {len(ids):,} tokens, {sum(mask):,} trained (assistant) tokens')

    own = files(a.data, 'pretrain_*.txt') * a.own_repeat                       # your text, repeated so it is not drowned out
    extra = sorted(glob.glob(os.path.join(a.extra, '*.txt'))) if a.extra else []
    reps = dict((k, int(v)) for k, v in (x.split('=') for x in a.extra_repeat))   # e.g. wordnet.txt=3
    extra = [p for p in extra for _ in range(reps.get(os.path.basename(p), 1))]
    if not a.sft_only:                                                       # --sft-only: chat data only (chat-only re-run)
        write_text('pretrain_train', own + extra)
        write_text('pretrain_val', [os.path.join(a.data, 'eval', 'pretrain_eval.txt')])
    write_chat('sft_train', files(a.data, 'sft_train_*.jsonl'), repeat=a.chat_repeat, cap=a.cap)
    write_chat('sft_val', [os.path.join(a.data, 'eval', 'sft_eval_all.jsonl')])

# ----------------------------------------------------------------------------------------------- model
def model_params(vocab, d, L):
    return vocab * d + L * (12 * d * d + 4 * d) + 2 * d   # tied embeddings; attention+MLP(4x)+norms

PRESETS = [  # (d_model, layers, heads)
    (128, 4, 4), (192, 4, 4), (256, 4, 4), (256, 6, 4), (320, 6, 5), (384, 6, 6), (384, 8, 6),
    (448, 8, 7), (512, 8, 8), (512, 10, 8), (576, 10, 9), (576, 12, 9), (640, 10, 10), (640, 12, 10),
    (768, 10, 12), (768, 12, 12),
]

def build_model(cfg):
    import torch, torch.nn as nn, torch.nn.functional as F

    class RMSNorm(nn.Module):
        def __init__(s, d): super().__init__(); s.w = nn.Parameter(torch.ones(d))
        def forward(s, x): return s.w * x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + 1e-6)

    def rope(x, cos, sin):
        x1, x2 = x[..., ::2], x[..., 1::2]
        return torch.stack((x1 * cos - x2 * sin, x1 * sin + x2 * cos), -1).flatten(-2)

    class Block(nn.Module):
        def __init__(s, d, h, drop):
            super().__init__(); s.h = h
            s.n1, s.n2 = RMSNorm(d), RMSNorm(d)
            s.qkv, s.proj = nn.Linear(d, 3 * d, bias=False), nn.Linear(d, d, bias=False)
            s.fc, s.out = nn.Linear(d, 4 * d, bias=False), nn.Linear(4 * d, d, bias=False)
            s.drop = drop
        def forward(s, x, cos, sin):
            B, T, C = x.shape
            q, k, v = s.qkv(s.n1(x)).split(C, -1)
            q, k, v = (t.view(B, T, s.h, C // s.h).transpose(1, 2) for t in (q, k, v))
            q, k = rope(q, cos, sin), rope(k, cos, sin)
            y = F.scaled_dot_product_attention(q, k, v, is_causal=True, dropout_p=s.drop if s.training else 0.0)
            x = x + s.proj(y.transpose(1, 2).reshape(B, T, C))
            return x + s.out(F.gelu(s.fc(s.n2(x))))

    class GPT(nn.Module):
        def __init__(s, c):
            super().__init__(); s.c = c
            s.emb = nn.Embedding(c['vocab'], c['d'])
            s.blocks = nn.ModuleList(Block(c['d'], c['heads'], c['dropout']) for _ in range(c['layers']))
            s.norm = RMSNorm(c['d'])
            hd = c['d'] // c['heads']
            inv = 1.0 / (10000 ** (torch.arange(0, hd, 2).float() / hd))
            f = torch.outer(torch.arange(c['block']).float(), inv)
            s.register_buffer('cos', f.cos()[None, None], persistent=False)
            s.register_buffer('sin', f.sin()[None, None], persistent=False)
            s.apply(s._init)
            for n, p in s.named_parameters():
                if n.endswith('proj.weight') or n.endswith('out.weight'):
                    nn.init.normal_(p, 0.0, 0.02 / math.sqrt(2 * c['layers']))
        def _init(s, m):
            if isinstance(m, (nn.Linear, nn.Embedding)): nn.init.normal_(m.weight, 0.0, 0.02)
        def forward(s, idx, targets=None, mask=None):
            T = idx.shape[1]
            x = s.emb(idx)
            for b in s.blocks: x = b(x, s.cos[:, :, :T], s.sin[:, :, :T])
            logits = s.norm(x) @ s.emb.weight.T
            if targets is None: return logits, None
            loss = F.cross_entropy(logits.float().view(-1, logits.size(-1)), targets.reshape(-1), reduction='none')
            if mask is None: return logits, loss.mean()
            m = mask.reshape(-1).float()
            return logits, (loss * m).sum() / m.sum().clamp(min=1)
    return GPT(cfg)

# ----------------------------------------------------------------------------------------------- plan
def counts(workdir):
    import numpy as np
    d = os.path.join(workdir, 'data')
    n = lambda f, dt=np.uint16: (os.path.getsize(os.path.join(d, f)) // np.dtype(dt).itemsize
                                 if os.path.exists(os.path.join(d, f)) else 0)    # no pretrain files in a chat-only run
    return {'pretrain_tokens': n('pretrain_train.bin'), 'sft_tokens': n('sft_train.bin'),
            'sft_trained_tokens': int(np.fromfile(os.path.join(d, 'sft_train_mask.bin'), dtype=np.uint8).sum()),
            'pretrain_val_tokens': n('pretrain_val.bin'), 'sft_val_tokens': n('sft_val.bin')}

def cmd_plan(a):
    tok = load_tok(a.workdir); V = tok.get_vocab_size()
    c = counts(a.workdir)
    seen = a.pretrain_epochs * c['pretrain_tokens'] + a.sft_epochs * c['sft_tokens']
    target = seen / a.tokens_per_param
    best = min(PRESETS, key=lambda p: abs(math.log(model_params(V, p[0], p[1]) / target)))
    if a.shape: best = tuple(int(x) for x in a.shape.split(','))      # keep a fixed model size (e.g. continue run 5)
    d, L, H = best; P = model_params(V, d, L)
    plan = dict(c, vocab=V, pretrain_epochs=a.pretrain_epochs, sft_epochs=a.sft_epochs, tokens_seen=seen,
                tokens_per_param=a.tokens_per_param, target_params=int(target), d=d, layers=L, heads=H,
                params=P, non_embedding_params=P - V * d, block=a.block, dropout=a.dropout)
    atomic_json(os.path.join(a.workdir, 'plan.json'), plan)
    for k, v in plan.items(): print(f'  {k:>22}: {v:,}' if isinstance(v, int) else f'  {k:>22}: {v}')
    log(f'model: {P / 1e6:.1f}M params (target {target / 1e6:.1f}M = {seen / 1e6:.0f}M tokens seen / {a.tokens_per_param})')

# ----------------------------------------------------------------------------------------------- train
class Data:
    def __init__(s, d, name, chat, block, seed):
        import numpy as np
        s.ids = np.memmap(os.path.join(d, name + '.bin'), dtype=np.uint16, mode='r')
        s.mask = np.memmap(os.path.join(d, name + '_mask.bin'), dtype=np.uint8, mode='r') if chat else None
        s.starts = np.fromfile(os.path.join(d, name + '_starts.bin'), dtype=np.int64) if chat else None
        s.block, s.rng = block, np.random.default_rng(seed)
    def batch(s, B, device):
        import numpy as np, torch
        hi = len(s.ids) - s.block - 1
        if s.starts is not None:   # chat: windows begin at a chat start
            st = s.rng.choice(s.starts[s.starts < hi], B)
        else:
            st = s.rng.integers(0, hi, B)
        x = np.stack([s.ids[i:i + s.block] for i in st]).astype(np.int64)
        y = np.stack([s.ids[i + 1:i + 1 + s.block] for i in st]).astype(np.int64)
        m = np.stack([s.mask[i + 1:i + 1 + s.block] for i in st]) if s.mask is not None else None
        t = lambda z: torch.from_numpy(z).to(device, non_blocking=True)
        return t(x), t(y), (t(m) if m is not None else None)

def save_ckpt(path, state):
    import torch
    tmp = path + '.tmp'; torch.save(state, tmp)
    if os.path.exists(path): os.replace(path, path.replace('.pt', '_prev.pt'))
    os.replace(tmp, path)

def cmd_train(a):
    import numpy as np, torch
    plan = json.load(open(os.path.join(a.workdir, 'plan.json')))
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    if dev == 'cuda':
        name = torch.cuda.get_device_name(0)
        if 'A100' not in name and not a.allow_any_gpu: sys.exit(f'GPU is {name}, not an A100. Change the runtime type to A100.')
        torch.backends.cuda.matmul.allow_tf32 = True; torch.backends.cudnn.allow_tf32 = True
    elif not a.allow_cpu: sys.exit('No GPU. Set the Colab runtime to A100 (or pass --allow-cpu for a local test).')
    ck = os.path.join(a.workdir, 'checkpoints'); os.makedirs(ck, exist_ok=True)
    latest, final = os.path.join(ck, f'{a.stage}_latest.pt'), os.path.join(ck, f'{a.stage}_final.pt')
    if os.path.exists(final) and not a.force: log(f'{a.stage} already finished: {final}'); return
    cfg = dict(vocab=plan['vocab'], d=plan['d'], layers=plan['layers'], heads=plan['heads'], block=plan['block'],
               dropout=plan['dropout'] if a.stage == 'pretrain' else 0.0)
    chat = a.stage == 'sft'
    src_ck = os.path.join(ck, 'pretrain_final.pt')
    if chat and os.path.exists(src_ck):   # chat stage: model shape always comes from the pretrained weights
        pc = torch.load(src_ck, map_location='cpu', weights_only=False)['cfg']
        cfg.update({k: pc[k] for k in ('vocab', 'd', 'layers', 'heads', 'block')})
    tokens = plan['pretrain_tokens'] * plan['pretrain_epochs'] if not chat else plan['sft_tokens'] * plan['sft_epochs']
    B = a.batch; steps = a.max_steps or max(1, math.ceil(tokens / (B * cfg['block'])))
    lr = a.lr if a.lr else (6e-4 if not chat else 1e-4)
    warm = min(max(200, steps // 100) if not chat else 50, steps // 10 + 1)
    model = build_model(cfg).to(dev)
    decay = [p for n, p in model.named_parameters() if p.dim() >= 2]
    other = [p for n, p in model.named_parameters() if p.dim() < 2]
    opt = torch.optim.AdamW([{'params': decay, 'weight_decay': 0.1}, {'params': other, 'weight_decay': 0.0}],
                            lr=lr, betas=(0.9, 0.95), fused=(dev == 'cuda'))
    step, best = 0, float('inf')
    if os.path.exists(latest):
        s = torch.load(latest, map_location=dev, weights_only=False)
        model.load_state_dict(s['model']); opt.load_state_dict(s['opt']); step, best = s['step'], s.get('best', best)
        random.setstate(s['py_rng']); torch.set_rng_state(s['torch_rng'])
        log(f'resumed {a.stage} from step {step}/{steps}')
    elif a.init_from and not chat:
        src = torch.load(a.init_from, map_location=dev, weights_only=False)
        if any(src['cfg'][k] != cfg[k] for k in ('vocab', 'd', 'layers', 'heads', 'block')):
            sys.exit(f'--init-from shape {src["cfg"]} does not match plan {cfg}; use plan --shape d,layers,heads')
        model.load_state_dict(src['model']); log(f'pretrain continues from {a.init_from} (weights only, new schedule)')
    elif chat:
        src = os.path.join(ck, 'pretrain_final.pt')
        if not os.path.exists(src): sys.exit('pretrain_final.pt not found: run --stage pretrain first')
        model.load_state_dict(torch.load(src, map_location=dev, weights_only=False)['model'])
        log('sft starts from pretrain_final.pt')
    dd = a.data_dir or os.path.join(a.workdir, 'data')   # --data-dir: a local copy of workdir/data (faster than Drive)
    train = Data(dd, 'sft_train' if chat else 'pretrain_train', chat, cfg['block'], seed=1000 + step)
    val = Data(dd, 'sft_val' if chat else 'pretrain_val', chat, cfg['block'], seed=7)
    cmodel = torch.compile(model) if (dev == 'cuda' and not a.no_compile) else model
    amp = torch.autocast('cuda', dtype=torch.bfloat16) if dev == 'cuda' else torch.autocast('cpu', enabled=False)
    def lr_at(i):
        if i < warm: return lr * (i + 1) / warm
        return lr * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * min(1.0, (i - warm) / max(1, steps - warm)))))
    @torch.no_grad()
    def evaluate():
        cmodel.eval(); ls = []
        for _ in range(a.eval_batches):
            x, y, m = val.batch(B, dev)
            with amp: ls.append(cmodel(x, y, m)[1].item())
        cmodel.train(); return sum(ls) / len(ls)
    def state():
        return {'model': model.state_dict(), 'opt': opt.state_dict(), 'step': step, 'best': best, 'cfg': cfg,
                'stage': a.stage, 'py_rng': random.getstate(), 'torch_rng': torch.get_rng_state()}
    logf = open(os.path.join(a.workdir, f'log_{a.stage}.csv'), 'a')
    log(f'{a.stage}: {steps} steps x {B} x {cfg["block"]} tokens, lr {lr}, device {dev}')
    t_ck, t0 = time.time(), time.time()
    cmodel.train()
    while step < steps:
        for g in opt.param_groups: g['lr'] = lr_at(step)
        x, y, m = train.batch(B, dev)
        with amp: loss = cmodel(x, y, m)[1]
        opt.zero_grad(set_to_none=True); loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
        step += 1
        if step % a.log_every == 0:
            tps = a.log_every * B * cfg['block'] / (time.time() - t0); t0 = time.time()
            log(f'{a.stage} step {step}/{steps} loss {loss.item():.4f} lr {lr_at(step):.2e} {tps / 1e3:.0f}k tok/s')
        if step % a.eval_every == 0 or step == steps:
            v = evaluate(); best = min(best, v)
            log(f'  eval loss {v:.4f} (ppl {math.exp(min(v, 20)):.1f})')
            logf.write(f'{step},{loss.item():.4f},{v:.4f}\n'); logf.flush()
        if step % a.ckpt_every == 0 or time.time() - t_ck > a.ckpt_minutes * 60:
            save_ckpt(latest, state()); t_ck = time.time(); log(f'  checkpoint saved at step {step}')
    save_ckpt(latest, state())
    torch.save({'model': model.state_dict(), 'cfg': cfg, 'stage': a.stage, 'step': step}, final + '.tmp'); os.replace(final + '.tmp', final)
    log(f'{a.stage} finished: {final}')

# ----------------------------------------------------------------------------------------------- chat
def cmd_chat(a):
    import torch
    tok = load_tok(a.workdir); ck = os.path.join(a.workdir, 'checkpoints')
    path = a.ckpt or next((p for p in (os.path.join(ck, 'sft_final.pt'), os.path.join(ck, 'sft_latest.pt'),
                                       os.path.join(ck, 'pretrain_final.pt')) if os.path.exists(p)), None)
    if not path: sys.exit('no checkpoint found')
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    s = torch.load(path, map_location=dev, weights_only=False)
    model = build_model(s['cfg']).to(dev); model.load_state_dict(s['model']); model.eval()
    end = tok.token_to_id('<|end|>'); eot = tok.token_to_id('<|endoftext|>')
    log('loaded', path)
    prompts = list(a.prompt or []); scripted = bool(prompts)
    history = []
    while True:
        q = prompts.pop(0) if prompts else (None if scripted else input('you> ').strip())
        if not q: break
        if scripted and not a.keep_history: history = []   # scripted test prompts are independent questions
        history.append({'role': 'user', 'content': q})
        text = ''.join(t for t, _ in chat_text(history))[:-len('<|endoftext|>')] + '<|assistant|>\n'
        ids = tok.encode(text).ids[-(s['cfg']['block'] - a.max_new):]
        x = torch.tensor([ids], device=dev); out = []
        with torch.no_grad():
            for _ in range(a.max_new):
                logits = model(x[:, -s['cfg']['block']:])[0][0, -1].float()
                if a.rep_penalty != 1.0 and out:            # discourage tokens already used in this reply
                    seen = torch.tensor(sorted(set(out)), device=dev)
                    logits[seen] = torch.where(logits[seen] > 0, logits[seen] / a.rep_penalty, logits[seen] * a.rep_penalty)
                logits = logits / a.temperature
                v, _ = torch.topk(logits, a.top_k); logits[logits < v[-1]] = -float('inf')
                nxt = torch.multinomial(torch.softmax(logits, -1), 1).item()
                if nxt in (end, eot): break
                out.append(nxt); x = torch.cat([x, torch.tensor([[nxt]], device=dev)], 1)
        reply = tok.decode(out).strip(); print('model>', reply)
        history.append({'role': 'assistant', 'content': reply})

# ----------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd', required=True)
    def common(p, data=False):
        p.add_argument('--workdir', required=True)
        if data: p.add_argument('--data', required=True)
    p = sub.add_parser('tokenizer'); common(p, True); p.add_argument('--vocab', type=int, default=16384)
    p.add_argument('--extra', help='folder of extra text; a sample is used to train the tokenizer')
    p.add_argument('--extra-sample-mb', type=int, default=150)
    p = sub.add_parser('prepare'); common(p, True)
    p.add_argument('--chat-repeat', type=int, default=1, help='repeat the 12 conversation-pattern types N times in sft_train')
    p.add_argument('--extra', help='folder of extra English pretraining text (*.txt) from the fetch command')
    p.add_argument('--own-repeat', type=int, default=1, help='repeat your own pretraining text N times')
    p.add_argument('--extra-repeat', action='append', default=[], help='repeat one extra file, e.g. wordnet.txt=3')
    p.add_argument('--cap', action='append', default=[], help='keep at most N chats of a type, e.g. behaviour=15000 (math=0 drops it)')
    p.add_argument('--sft-only', action='store_true', help='write only the chat token files (chat-only re-run)')
    p = sub.add_parser('fetch'); p.add_argument('--out', required=True)
    p.add_argument('--sets', default='tinystories,simplewiki', help='comma list: tinystories,simplewiki,wordnet,fineweb_edu,soda')
    p.add_argument('--fineweb-mb', type=int, default=1600, help='MB of FineWeb-Edu text to keep (~4 MB per 1M tokens)')
    p = sub.add_parser('plan'); common(p)
    p.add_argument('--tokens-per-param', type=float, default=10.0)
    p.add_argument('--pretrain-epochs', type=int, default=4); p.add_argument('--sft-epochs', type=int, default=2)
    p.add_argument('--block', type=int, default=512); p.add_argument('--dropout', type=float, default=0.1)
    p.add_argument('--shape', help='fix the model shape "d,layers,heads" instead of sizing it from the data')
    p = sub.add_parser('train'); common(p)
    p.add_argument('--stage', choices=['pretrain', 'sft'], required=True)
    p.add_argument('--batch', type=int, default=64); p.add_argument('--lr', type=float, default=0)
    p.add_argument('--max-steps', type=int, default=0, help='override the step count (for tests)')
    p.add_argument('--log-every', type=int, default=20); p.add_argument('--eval-every', type=int, default=200)
    p.add_argument('--eval-batches', type=int, default=20)
    p.add_argument('--ckpt-every', type=int, default=200); p.add_argument('--ckpt-minutes', type=float, default=5)
    p.add_argument('--no-compile', action='store_true'); p.add_argument('--force', action='store_true')
    p.add_argument('--allow-cpu', action='store_true'); p.add_argument('--allow-any-gpu', action='store_true')
    p.add_argument('--data-dir', help='read token files from here instead of <workdir>/data')
    p.add_argument('--init-from', help='pretrain stage: start from these weights (e.g. run 5 pretrain_final.pt)')
    p = sub.add_parser('chat'); common(p); p.add_argument('--ckpt')
    p.add_argument('--prompt', action='append'); p.add_argument('--max-new', type=int, default=150)
    p.add_argument('--temperature', type=float, default=0.8); p.add_argument('--top-k', type=int, default=40)
    p.add_argument('--rep-penalty', type=float, default=1.3, help='>1 discourages repeating tokens within a reply')
    p.add_argument('--keep-history', action='store_true', help='scripted prompts share one conversation')
    a = ap.parse_args()
    {'fetch': cmd_fetch, 'tokenizer': cmd_tokenizer, 'prepare': cmd_prepare, 'plan': cmd_plan, 'train': cmd_train, 'chat': cmd_chat}[a.cmd](a)

if __name__ == '__main__':
    main()
