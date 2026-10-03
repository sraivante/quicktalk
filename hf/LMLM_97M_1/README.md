---
language:
- en
license: apache-2.0
library_name: pytorch
pipeline_tag: text-generation
tags:
- small-language-model
- from-scratch
- chat
- gpt
- rope
- rmsnorm
- education
- custom-code
datasets:
- HuggingFaceFW/fineweb-edu
- roneneldan/TinyStories
- wikimedia/wikipedia
- allenai/soda
- openai/gsm8k
model-index:
- name: LMLM_97M_1
  results:
  - task:
      type: text-generation
    dataset:
      name: HellaSwag (validation, 10,042 items)
      type: Rowan/hellaswag
      split: validation
    metrics:
    - type: acc_norm
      value: 33.6
      name: acc_norm (chat model)
    - type: acc_norm
      value: 33.4
      name: acc_norm (base model)
---

# LMLM_97M_1

A **97.6M-parameter language model trained from scratch**, then fine-tuned for short, polite, everyday English
conversation. It is a small, open research and learning model: you can read every line of its training code, run it
on a laptop CPU, and see exactly where a model of this size is good and where it fails.

- Base model: pretrained on **8.23 billion tokens** of English text (one pass, ~9 h 50 min on one A100).
- Chat model: fine-tuned on **101,691 conversations** (18.3M tokens), mostly written for this project.
- **HellaSwag 33.6%** (acc_norm). That is above GPT-2 small (~30%) and below SmolLM2-135M (43.1%), which saw
  about 250x more training text.
- The custom PyTorch code is included. The model does **not** use `transformers`; see [How to use](#how-to-use).

This is QuickTalk run 8. "LMLM_97M_1" is its published name.

---

## Purpose and use cases

1. **Learning and teaching how LLMs work.** It is a complete, small, from-scratch GPT, with its training code, data recipe and honest test results.
2. **Research baseline for small models.** Compare data mixes, tokenizers or fine-tuning tricks against a known ~100M model.
3. **Polite everyday English chat.** It handles greetings, small talk and short behaviour or etiquette questions.
4. **Answering from a given text.** It can read a short notice, note or passage and answer a question about it.
5. **Saying "I don't know" safely.** For live facts (news, timetables, results) and for medical questions, it says it cannot know and points to the right person or place.
6. **Simple grammar correction.** It corrects one-error sentences and names the error type.
7. **Understanding messy questions.** It copes with typos, SMS spelling and Indian-English phrasing ("wat 2 do if…").
8. **Simple JSON extraction.** It turns one sentence into JSON with the keys you name. Check the output.
9. **On-device and offline experiments.** At 390 MB (fp32), it runs on a CPU, phone-class hardware or a Raspberry Pi-class board.
10. **Starting point for further fine-tuning.** The base model can be fine-tuned for a narrow task such as a domain FAQ, a classroom helper or a game NPC.

**In short:** LMLM_97M_1 is a teaching and research model, not a general assistant. It was built to answer one
question: how far a ~100M model trained from scratch, on a modest budget, can get at *short, safe, well-mannered
everyday conversation*. Its strengths are the six skills it was tuned for: messy questions, JSON from a sentence,
answering from a given text, greetings, polite "I don't know", and passage questions. On those it more than doubled
the previous version (52% vs 23% on held-out questions). It is weak at arithmetic, factual recall and long reasoning.
Use it to learn, to compare, to experiment and to fine-tune, and always check what it says.

---

## Comparison tables

### HellaSwag (common-sense sentence endings)

Every model below was scored with the same scorer (`hellaswag_eval.py`, included in the training repo) on all
10,042 validation items, except the rows marked "published". The model chooses the most likely of 4 endings, so
random guessing scores 25%. **acc_norm** (length-normalised) is the number usually published.

| Model | Parameters | Training tokens | acc | **acc_norm** |
|---|---|---|---|---|
| Random guessing | - | - | 25.0% | 25.0% |
| GPT-2 small (published) | 124M | ~10B | - | **~30%** |
| Pythia-160M (published) | 160M | 300B | - | ~30% |
| QuickTalk run 7 (chat, earlier version) | 97.6M | ~2B | 27.95% | 29.8% |
| QuickTalk run 7c (chat, earlier version) | 97.6M | ~2B | 27.76% | 29.7% |
| **LMLM_97M_1 base** | 97.6M | 8.23B | 30.12% | **33.4%** |
| **LMLM_97M_1 chat** | 97.6M | 8.23B + chat | 30.47% | **33.6%** |
| MobileLLM-125M (published) | 125M | 1T | - | ~39% |
| SmolLM2-135M (base) | 135M | ~2T | 35.47% | **43.1%** |
| SmolLM2-135M-Instruct | 135M | ~2T | 34.97% | **42.9%** |

What the table shows:
- LMLM_97M_1 beats GPT-2 small with ~20% fewer parameters and about the same amount of training text.
- SmolLM2-135M is ~10 points higher. It is a similar size, so the gap comes almost entirely from training data
  (~2 trillion tokens, about 250x more) and data curation. Our scorer gives SmolLM2 43.1%, which matches its
  published ~42%, so the scorer is fair.
- Chat fine-tuning does not change HellaSwag much, for our model or for SmolLM2.

### Held-out conversation test (210 new questions, blind grading)

These questions were written after training and never seen by the model. Three anonymised answer sets were graded
blind (correct = 1, partial = 0.5, wrong = 0). Decoding was greedy with repetition penalty 1.3.

| Category | n | run 7 | run 7c | **LMLM_97M_1** |
|---|---|---|---|---|
| Messy / misspelt question | 30 | 2% | 12% | **28%** |
| JSON output | 30 | 0% | 0% | **22%** (valid JSON 90%) |
| Answer from a given text | 30 | 17% | 15% | **67%** |
| Greeting / small talk | 20 | 25% | 28% | **75%** |
| Polite "I don't know" | 20 | 80% | 75% | **90%** |
| Passage questions | 20 | 37% | 50% | **50%** |
| Grammar correction | 15 | 23% | 13% | **37%** |
| Multi-turn memory | 15 | 17% | 27% | 23% |
| Short story | 15 | 20% | 25% | 20% |
| Several questions in one message | 15 | 20% | 30% | 30% |
| **Six focus skills** | 150 | 23% | 27% | **52%** |
| **All** | 210 | 23% | 26% | **46%** |

### Older 375-question test (questions in the style of the training material)

| Category | n | LMLM_97M_1 |
|---|---|---|
| Simple one-line question | 50 | 20% |
| Complex one-line question | 50 | 16% |
| Multi-line, simple | 30 | 15% |
| Multi-line, complex | 40 | 36% |
| Several questions at once | 40 | 4% |
| Multi-turn | 25 | 22% |
| Story | 25 | 14% |
| Writing task | 15 | 30% |
| Grammar | 40 | 34% |
| Passage (fact from the text: 82%) | 60 | 67% |
| **All** | 375 | **28%** |

On the same test: run 7 29%, run 7c 25%, and SmolLM2-135M-Instruct about 9%. SmolLM2 was not trained on this
style of question, and it was run with a different repetition-penalty setting, so treat that comparison only as a
rough guide.

### Maths (430 auto-graded word problems)

| Set | n | run 7 | LMLM_97M_1 |
|---|---|---|---|
| GSM8K test | 200 | 2% | 1% |
| Easy, new problems | 100 | 1% | 2% |
| Curriculum problems (seen style) | 80 | 18% | 12% |
| Easy (seen style) | 50 | 16% | 6% |
| **All** | 430 | 6% | **4%** |

Maths does not work. The model writes the right format ("Because 29 + 34 = …"), but the arithmetic is usually
wrong. Do not use it for calculations.

### Training loss

| Stage | Steps | Eval loss (start → end) |
|---|---|---|
| Pretraining (8.23B tokens) | 125,600 × 64 × 1,024 tokens | 4.69 → 3.18 |
| Chat fine-tuning | 558 (best checkpoint at step 500) | 2.06 → 1.887 |

---

## Sample questions and answers

These are real outputs from the held-out test: greedy decoding, repetition penalty 1.3, unedited. Good and bad
answers are both shown on purpose.

**Greeting** ✅
> **User:** hi there, good morning
> **Model:** Good morning! It's nice to meet you. How can I help?

**Greeting** ❌ (mistakes small talk for a live-data question)
> **User:** hey, how's it going?
> **Model:** I don't know how it is going, as I can't see live weather. A local news page or a weather website will have the latest update.

**Answer from a given text** ✅
> **User:** Read the text and answer. *Notice from the Green Park Residents' Association: The water supply will be stopped on Sunday from 9 am to 2 pm because the main tank is being cleaned. …* Question: Why will the water be stopped on Sunday?
> **Model:** The main tank is being cleaned.

**Answer from a given text** ✅
> **User:** *Hi Leo, I've left the house key under the blue flower pot by the back door, not the front one. … - Hannah* Where did Hannah leave the key?
> **Model:** She left it under the blue flower pot by the back door.

**Answer from a given text** ❌ (the answer, aloo paratha with curd, was in the text)
> **User:** *Weekend menu at Hilltop Cafe: … Sunday special is aloo paratha with curd. …* Question: What is the Sunday special?
> **Model:** The text doesn't say, and I don't know what the Sunday special is. The menu board or a call to it would tell you.

**Messy question / safety** ✅
> **User:** i hav sharp pain in left side of stomach since 2 days which medicin i take
> **Model:** You have sharp pain in your left side of the stomach since 2 days. I'm not sure what medicine is right for that area, and it depends on how you feel. Please tell a doctor or pharmacist if it feels heavy or painful.

**Messy question** ✅
> **User:** wats the train timing for chennai to madurai tmrw morning
> **Model:** You want to know when the train timing for Chennai will be on time. I can't check live timetables, so please ask a railway official or call them at your station.

**Messy question** ❌ (understands the question but gives no help)
> **User:** wat 2 do if my fon fall in watr
> **Model:** You want to know what a do if your fon fall in watr. I can't give exact figures, so please ask an adult or the school office about them. …

**Polite "I don't know"** ✅
> **User:** Who won yesterday's city council election?
> **Model:** I don't know, because I can't see recent results. The election commission's website or a local news report will have the latest figures.

**JSON output** ⚠️ (valid JSON, but uses the key `place` instead of the requested `venue`)
> **User:** Pull out the event details as JSON (keys: event, date, time, venue). Notice: The annual science fair will be held on 14 November at 10 am in the school assembly hall. …
> **Model:** `{"event": "science fair", "date": "14 November", "time": "10 am", "place": "school assembly hall"}`

**Grammar** ✅
> **User:** Please correct this: My sister play badminton every evening.
> **Model:** My sister plays badminton every evening. Why: verb form ("play" -> "plays").

**Grammar** ❌ (changed the year and kept the wrong preposition)
> **User:** Correct the sentence: I was born on 2005 in Lucknow.
> **Model:** I was born on 2015 in Lucknow.

**Passage** ✅
> **User:** *…an old man named Mr Chen repairs watches under a single yellow bulb. He has worked at the same spot for thirty years. …* How long has Mr Chen worked at the same spot?
> **Model:** He has worked there for thirty years.

**Multi-turn memory** ✅
> *(Earlier: "My cousin Tanvi is visiting from Jaipur next week." … "she loves sweets and old buildings.")*
> **User:** What was the name of my cousin I mentioned?
> **Model:** Your cousin is Tanvi, and she lives in Jaipur. You could share a few sweets with her first time visiting you.

**Story** ❌ (fluent sentences, but the plot doesn't hold together)
> **User:** Tell me a story about a girl who loses her kite, with a happy ending.
> **Model:** When the kite was lost in a storm, Kavya held her breath. She had never seen it before and felt very sad. Her mother found a long string and tied it to the kite. … Then she let go of the string and flew up, higher than anyone else.

**Two questions at once** ❌
> **User:** What does 'fragile' mean? Also, how do you spell the word for the day after today?
> **Model:** 1. Fragile means hard to break or repair, so it is not strong enough. 2. It should be: Today's work is a fragrance. …

---

## Knowledge covered, and to what level

| Area | Level | Notes |
|---|---|---|
| Everyday English conversation (greetings, small talk, politeness) | **Good** for its size | 75% on held-out greetings |
| Social behaviour and etiquette, ages 1-26 (home, school, college, first job) | **Basic to fair** | Main topic of the fine-tuning data; advice is simple and sometimes muddled |
| Reading comprehension of a short given text | **Fair** | 67% on new notices and notes; 82% on direct fact questions about a passage |
| Knowing when it can't know (live news, timetables, results, medical questions) | **Good** | 90%; sometimes over-used, e.g. on small talk |
| English grammar (single-error sentences: agreement, tense, articles) | **Basic** (school level) | Fixes about 4 in 10; the explanation is often wrong |
| Vocabulary and word meanings | **Basic** | WordNet in pretraining; common words are fine, rarer ones are often wrong |
| Typos, SMS spelling, Indian-English / Hinglish phrasing | **Basic** | Usually understands; the help it gives is weak |
| JSON from one sentence | **Basic** | Valid JSON 90%, but it often adds or renames keys |
| General common sense | **Low** (GPT-2-small level) | HellaSwag 33.6% |
| World facts (science, history, geography) | **Very low** | Small model; mostly forgotten or mixed up |
| Short stories | **Low** | Fluent sentences, weak plots (TinyStories style) |
| Arithmetic and maths word problems | **None in practice** | 4%; usually wrong even when the format is right |
| Literature, multi-step reasoning, code | **None** | Not trained for these |
| Medical, legal, financial advice | **Deliberately none** | Trained to refer you to a doctor, adult or official |

- Language: English only. It understands some Hinglish and Indian-English spellings but always answers in English.
- Knowledge cut-off: the FineWeb-Edu and Wikipedia snapshots (Wikipedia 2023-11-01). It has no live data.
- Context window: 1,024 tokens.

---

## Datasets used

**No training data is uploaded with this model.** Links to the public sources:

| Dataset | Used for | Amount in pretraining | Link |
|---|---|---|---|
| FineWeb-Edu, `sample-10BT` (10 shards) | Educational web text | ~7.2B tokens | https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu |
| TinyStories (V2, GPT-4 stories) | Simple stories, fluent basic English | 546M tokens | https://huggingface.co/datasets/roneneldan/TinyStories |
| SODA | Everyday social dialogues | 282M tokens | https://huggingface.co/datasets/allenai/soda |
| Simple English Wikipedia (`20231101.simple`) | Basic facts in simple English | 60M tokens | https://huggingface.co/datasets/wikimedia/wikipedia |
| WordNet (via NLTK) | Word meanings and usage | 5.4M tokens × 3 | https://wordnet.princeton.edu/ · https://www.nltk.org/howto/wordnet.html |
| GSM8K (train split) | Maths word problems in chat fine-tuning | small share of the chat data | https://huggingface.co/datasets/openai/gsm8k |
| Public-domain books (10 Gutenberg novels; Ramayana, Griffith tr.; Mahabharata, Ganguli tr.; Panchatantra, Ryder tr.) + QuickTalk behaviour passages | Pretraining, repeated 3x | ~0.1B tokens (with repeats) | https://www.gutenberg.org/ (books); behaviour passages not released |
| QuickTalk chat data (not released) | Chat fine-tuning: 101,691 conversations | 18.3M tokens | - |

The project's own chat data was written for this project and reviewed by separate critic passes. It covers behaviour Q&A for ages
1-26, conversation patterns, grammar, comprehension, summaries, rewriting, a maths curriculum, and run 8's focus
types: messy questions, JSON output, answering from a given text, greetings, "I don't know", multi-turn chats and
multi-question messages. The chat mix is 24.6% behaviour, 13.1% maths and 29.2% focus types (repeated 3x).

---

## Model details

| | |
|---|---|
| Architecture | Decoder-only transformer (GPT-style), custom PyTorch |
| Parameters | 97,555,968 (84,973,056 non-embedding) |
| Layers / width / heads | 12 / 768 / 12 (head size 64) |
| Feed-forward | 4 × 768, GELU |
| Normalisation | RMSNorm (pre-norm) |
| Positions | Rotary embeddings (RoPE) |
| Attention | PyTorch scaled-dot-product attention (causal) |
| Embeddings | Input and output embeddings tied |
| Context | 1,024 tokens |
| Tokenizer | Byte-level BPE, 16,384 tokens, numbers split into single digits |
| Special tokens | `<|endoftext|>`, `<|user|>`, `<|assistant|>`, `<|end|>`, `<|pad|>` |
| Weights | float32 safetensors (390 MB each); trained in bfloat16 mixed precision |

**Training.** Pretraining ran for 125,600 steps × batch 64 × 1,024 tokens = 8.23B tokens (one epoch) at peak
learning rate 6e-4 and ~238k tokens/s on a single A100. Chat fine-tuning ran for 2 epochs (558 steps). Loss was
computed on assistant replies only, and the best checkpoint by eval loss (step 500) was kept. Model size followed a
"10 tokens per parameter" budget.

**Chat format:**
```
<|user|>
Hello!<|end|>
<|assistant|>
Hello! It's nice to meet you.<|end|>
<|endoftext|>
```

## Files

| File | What it is |
|---|---|
| `model.safetensors` | Chat model (use this) |
| `base_model.safetensors` | Base model after pretraining, before chat fine-tuning |
| `config.json` | Model shape (`vocab`, `d`, `layers`, `heads`, `block`, `dropout`) |
| `tokenizer.json` | Tokenizer (load with the `tokenizers` library) |
| `quicktalk_lm.py` | Model code and the full training pipeline |
| `inference.py` | Ready-to-run chat script |

## How to use

```bash
pip install torch tokenizers safetensors huggingface_hub
```

```python
from huggingface_hub import snapshot_download
import sys
path = snapshot_download("<your-username>/LMLM_97M_1")   # the repo this card belongs to
sys.path.insert(0, path)
from inference import load, reply

model, cfg, tok = load("model.safetensors")
print(reply(model, cfg, tok, [{"role": "user", "content": "Good morning! How are you today?"}]))
```

From the command line, inside the downloaded folder:
```bash
python inference.py                                   # interactive chat (keeps the conversation)
python inference.py "Please correct this: She go to school."
python inference.py --temperature 0.6 "Tell me a short story about a cat."
python inference.py --base "The water cycle is"       # plain text continuation with the base model
```

The defaults are greedy decoding with repetition penalty 1.3, as used in the tests above. For stories, try
temperature 0.6-0.8.

## Limitations and risks

- **It makes things up.** It often states wrong facts confidently. It also adds extra JSON keys, changes numbers
  in grammar fixes, and gets arithmetic wrong. Check every answer.
- **It is not an advisor.** It is trained to refuse medical, legal and financial advice and to refer you to a
  doctor, adult or official. Do not rely on it for safety-critical decisions.
- **It over-uses "I don't know".** It sometimes gives this answer to small talk or to questions answerable from the given text.
- **It has a short memory.** The context is 1,024 tokens, and multi-turn recall is weak (23%).
- **Its data has biases.** Web text and the project's own data carry their biases; the behaviour data reflects
  mostly Indian and general English-speaking settings.
- Treat it as a research and teaching artefact, and do not deploy it to give real people advice without human review.

## License

Weights and code: Apache-2.0. The training datasets keep their own licenses; see the links above.
