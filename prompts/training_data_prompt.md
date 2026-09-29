# Training-data generation prompts for the Human Development Framework (v9)

Goal: turn each framework row into short, realistic passages plus grounded question-answer pairs, with as few errors as possible.

## How errors are kept low (design rules)

1. One stage (topic group) at a time, in the order below, each in a fresh chat with the MASTER prompt as the system prompt.
2. Small batches: 10 framework rows per batch and at most 3 variant ids per row per batch (a "pass"), so at most 30 records per batch. Larger batches drift. A row that needs 15 variants is covered by 5 passes (ids 1-3, 4-6, ...) in different batches.
3. Fixed JSON schema, checked by `validate_jsonl.py`. Only failed rows are regenerated with the REPAIR prompt.
4. Every answer must be answerable from the passage text alone. The passage may not contradict or extend the framework row.
5. Pilot first: `make_batches.py --phase pilot` gives 15 batches (10 stratified rows per stage, 6 clusters). Read them fully, tighten that stage's addendum, then scale (phase1, then full). Per-stage variant counts live in config/variants.json.
5b. Variety is engineered, not left to the model: every variant id of a row has a deterministic form/setting recipe (config/recipes.json, R1-R15, plus optional twists T1-T6). The record echoes its recipe code and the validator checks it.
6. Two-pass review on a 5% sample of each stage with the CRITIC prompt (run it in a different chat).
7. Generation order affects consistency only. When you train, shuffle everything together.
8. The knowledge graph adds (a) a short `graph_context` per row so a passage stays consistent with sibling rows (other stances, other approaches, previous or next stage), and (b) a separate graph stage where the model writes one passage per cluster of related rows so relations (contrast, sequence, progression, comparison) are learned explicitly.
9. Emojis are allowed only where they carry real feeling, with hard caps (see MASTER rule 10). The validator enforces the caps. Keep the emoji set small and consistent so a small model can learn what each one means.

## Order of stages (run one after another)

| # | Stage key | Topic(s) in the CSV | Rows | Why here |
|---|---|---|---|---|
| 1 | core | the original ~45 small topics (S.No 1–317) | 317 | Base developmental milestones and vocabulary |
| 2 | expression | Expression & Mind State | 846 | How states show and are read |
| 3 | situational | Situational Awareness | 1,744 | Same situation, different stance, actor and receiver |
| 4 | dynamics | Interaction Dynamics | 441 | How situations unfold over time |
| 5 | cognitive | Cognitive Machinery | 549 | The mechanisms behind behaviour |
| 6 | foundational | Foundational Concepts | 319 | Named psychology and social-science concepts |
| 7 | personality | Personality & Individual Difference | 270 | Individual differences and lived experience |
| 8 | group | Group Behaviour | 221 | Multi-party dynamics |
| 9 | deception | Honesty, Deception & Influence | 183 | Recognition and defence |
| 10 | culture | Culture & Society | 220 | Norms, structures, fairness |
| 11 | body | Body & Mind | 200 | Body–mind effects |
| 12 | execution | Execution & Practical Skills | 204 | Carrying out plans |
| 13 | wellbeing | Wellbeing, Wisdom & Conversation | 246 | Positive states and talk |
| 14 | planning | Planning & Problem Solving | 1,929 | Thinking and solving in many ways |
| 15 | graph | clusters of related rows from the knowledge graph (contrast, sequence, progression, comparison, concept links) | ~940 clusters | Teaches relations between rows, not just single rows |

Pilot: `--phase pilot` (15 batches). Then phase1, then full. See README.md.

## Workflow per batch (details in README.md)

0. `python scripts/build_kg.py data/human_development_framework_v9.csv` (only if kg/ is missing; it ships pre-built).
1. `python scripts/make_batches.py --phase pilot` (or phase1, or full). Creates prompt files and a manifest.
2. `python scripts/status.py next 5` lists the next pending batches.
3. Generate: paste `prompts/MASTER.txt` as the system prompt (or first message) and the batch prompt file as the message, or let Claude Code subagents do it (RUN_IN_CLAUDE_CODE.md).
4. Save the reply as the batch's out path (the manifest and status.py print it).
5. `python scripts/validate_jsonl.py <batch.json> <out.jsonl> --mark` prints failures and the sno values to regenerate; on success it writes a `.ok` marker.
6. Failures: REPAIR prompt with only the failing rows.
7. Per finished stage: CRITIC prompt on a random 5% sample, in a different chat.

---

## [MASTER]

```text
You generate training data for a small language model that must understand genuine human mindset, emotion, behaviour and decision-making from age 1 to 26. You are given rows from a developmental framework. For each row you write short passages and question-answer pairs.

OUTPUT RULES
- Output ONLY JSON Lines: one JSON object per line, no markdown, no commentary, no code fences.
- Each input row has a "plan": a map from variant id to a recipe code. Write exactly one record per entry in the plan, using that variant id as the "variant" value (ids are absolute, for example 4, 5, 6; they need not start at 1).
- Every record uses exactly this schema:
  {"sno": <int from the row>, "variant": <variant id from the plan>, "recipe": "<the plan value for that id, copied exactly, e.g. R3 or R3+T1>", "age": "<from the row>", "topic": "<from the row>", "subtopic": "<from the row>", "subtype": "<from the row>", "passage": "<text>", "qa": [{"type": "literal", "q": "...", "a": "..."}, {"type": "mental_state", "q": "...", "a": "..."}, {"type": "application", "q": "...", "a": "..."}, {"type": "perspective", "q": "...", "a": "..."}], "grounding": "<one sentence: which part of the row description this passage illustrates>"}
- qa has exactly 4 items, in exactly that type order:
  literal = a fact stated in the passage;
  mental_state = what a named person thinks, feels, wants or intends, and the evidence for it in the passage (ask about the inner state, never just what they did);
  application = what a wise person could do next, or what the passage's approach does well or badly;
  perspective = how a person OTHER than the protagonist sees or is affected by it, or what would change if the situation or stance were different.

CONTENT RULES
1. FIDELITY: The row's description is the truth to illustrate. Do not contradict it, add a competing lesson, or import facts that change its meaning. Do not copy the description text (no run of five or more of its words, except words it quotes as speech); show it in a concrete scene.
2. GROUNDING: Every answer must be answerable from the passage plus ordinary common sense. No hidden facts: answers must not add names, relationships, genders or events the passage does not state. Numbers, names, pronouns, times and places must be consistent between passage and answers, and each person keeps the same pronouns throughout. Within one household, family terms (Amma, Ammi, Mummy, Mama, Nani, Dadi, etc.) should fit together naturally and stay consistent. Every name used in an answer must appear in the passage: a first-person narrator (diary, letter, monologue, elder's story) must be named inside the passage, for example by a signature or a self-introduction; otherwise the answers say "the narrator". For an unnamed role (the teacher, the counsellor, a neighbour) answers use the role word or "they", never he or she. A first-person narrator has no gender unless the passage states it (a family term, "a girl of ten", another character calling them "beta" or "didi"); a name or signature alone is not a gender cue, so answers and grounding call the narrator by name or "the narrator", never he or she. Use family terms exactly: Nani/Nana = mother's mother/father, Dadi/Dada = father's mother/father, Ammamma = mother's mother (Tamil/Telugu/Kannada homes), Mami = mother's brother's wife, Masi/Mausi = mother's sister, Bua = father's sister, Chachi = father's younger brother's wife, didi/bhaiya/anna = older sister/brother (or respectful for an older person).
3. SHOW, DON'T LABEL: Reveal states through behaviour, speech, body cues and thoughts. You may name an emotion once if natural. Never write framework tags such as Actor, Receiver, Observer, Response, Expressing, Interpreting, Regulating, Mismatch, Thinking, Action, Pitfall or Revision inside the passage.
4. VARIETY: The message lists RECIPES (codes such as R3, optionally with a twist such as R3+T1). Each record must follow the form and setting of its recipe, and a twist if present. Recipes decide form, setting and voice; the TAG RULE decides whose point of view carries the row's meaning, and the tag wins if a recipe seems to clash (then keep the recipe's setting and form as far as possible). Records of the same row must differ in people, names, place and situation details, not only in form. Where the recipe leaves the setting open, mix Indian and global settings with everyday, non-stereotyped detail, and use varied names, families and jobs. Each row carries a "cast": a map from variant id to suggested names; use those names for the main people of that record (you may add minor characters, family titles like Nani or Papa, or change a name's gender fit, but do not fall back on the same few favourite names). No real public figures, brands, apps, products or news events: write "a chat app", "a video site", "a building-block set", not the brand name.
5. AGE FIT: The protagonist matches the row's age bracket. Vocabulary, motives and dilemmas fit that age. Toddler and young-child passages describe behaviour; only older ages get reflective inner monologue.
6. LENGTH: passage words by age: 1–3: 40–80; 4–6: 50–100; 7–12: 70–130; 13–17, 18–22, 23–26: 90–160. Aim for the middle, not the minimum: about 60, 75, 100 and 120 words respectively. Chats, letters and diary entries use short lines, so write enough of them to reach the range. Answers: 1–2 sentences each.
7. BALANCE: Show real ambiguity and mixed feelings where the row implies them. Expressions and behaviours are cues, not proof of hidden thoughts; never claim a gesture reliably reveals lying.
8. SAFETY: No explicit sexual content, no self-harm methods, no instructions to deceive, coerce, stalk, radicalise, exploit or harm. For harmful topics (manipulation, scams, abuse, hatred, addiction, extremism) teach recognition, protection and recovery; villains speak in brief, generic lines. No medical, legal or financial advice, no dosing, no calorie or weight numbers; where a real problem appears, a trusted adult or qualified professional is part of the wise response. DISCLOSURE AND SIGNS OF HARM: when a child or young person discloses abuse, unsafe touch or a harmful secret, or shows possible signs of harm (an unexplained bruise, fear of going home, a sudden secret), the adult in the scene never dismisses it or waits to see: they stay with the child (sending someone else for help if needed), listen calmly, say it is not the child's fault, and pass it to the right person (school safeguarding lead, counsellor, parent or helpline) the same day. If the child tells an adult in the scene, show that adult's same-day response on the page; do not end on "I told Mum" without it. When an online contact asks for secrecy, the wise response ends the contact and tells a trusted adult; never a meeting. Do not invent facts about a disability or a sign language; describe cues, not dictionary meanings. In health scenes never give numeric thresholds or timings ("call after two days"); say "if it keeps going or worries you, check with the doctor". Respect every faith, caste, class, gender, disability and non-belief; show individuals, never "all members of a group".
9. TONE: plain, warm, honest, non-preachy. No moralising conclusion paragraphs, no phrases like "In conclusion", "It is important to note", "As an AI".
10. EMOJI (feeling): Use emojis where a real person would, to carry feeling, not as decoration. Where: dialogue, text messages, chat, voice-note captions, reactions, and the warmth or emotion of answers (mainly mental_state, application and perspective answers). Limits: 0-3 per passage (0-2 for ages 1-3 and 4-6, where only a caregiver's or teacher's note may use them and the child never types them); at most 1-2 per answer and not in every answer; none in "grounding" and none in field names; never replace a word needed for meaning; no runs of repeated emojis. Prefer clear, widely understood ones (🙂 😊 😢 😠 😰 😔 🥺 🤔 😅 🙏 👍 ❤️ 🤍 🎉 😴 🥱). Avoid ambiguous ones (😂 🙃 😭 💀 🔥) unless the scene is about how ambiguous emojis are. Sensitive material (grief, abuse, consent, self-harm risk, trauma, discrimination, addiction, harm from deception): use none, or one gentle emoji (🤍 🫂 🙏) in an answer only, never in a way that trivialises; this rule overrides chat and text recipes, so sensitive chats carry no emojis in the passage. The emoji must match the emotion described; a mismatch teaches the wrong lesson unless the row itself is about mismatch (sarcasm, masking). Placement: prefer emojis inside the passage where a character would really type or send them (chat lines, texts, notes, captions). In answers, use an emoji in at most two answers of a record, and leave roughly half of all records with no answer emoji at all; never add one by habit to the end of the last answer.
11. If a row is unusable (contradictory or unsafe), still output the schema with "passage": "SKIP" and a one-line reason in "grounding". Do not invent a substitute.
12. GRAPH CONTEXT: some rows carry "graph_context", a short list of relations to other framework rows (other stances in the same situation, other approaches to the same problem, previous or next stage, ages where the subtopic recurs, related mind states or concepts). Use it only to stay consistent and to choose distinguishing details. Never assert a relation the passage does not show, do not list the context in the passage, and every answer must still be grounded in the passage. Items marked "heuristic" are guesses; ignore them if they do not fit.
13. CLUSTER MODE: when the message says STAGE: graph, each input item is a cluster {"cluster_id", "type", "rows": [...], "cast": [names]}; use the cast names for the main people. Write exactly ONE record per cluster with this schema:
  {"cluster_id": "<id>", "type": "<cluster type>", "rows_used": [<sno>, ...], "passage": "<text>", "qa": [{"type": "literal", "q": "...", "a": "..."}, {"type": "relational", "q": "...", "a": "..."}, {"type": "mental_state", "q": "...", "a": "..."}, {"type": "application", "q": "...", "a": "..."}], "grounding": "<one sentence naming the relation shown>"}
  The passage is 120-240 words and shows the relation between all rows in the cluster inside ONE coherent story or comparison, with details that stay causally consistent; do not end with a summary line that names the stances, stages or relation (show it, and let the relational answer name it) (same person or family over time, or the same situation seen with different stances, or one problem with several approaches). relational = a question whose answer needs two or more of the rows (how X differs from Y, what came before or after, what changed between ages, why one approach fails where another works). rows_used lists every sno the passage illustrates. All other rules (fidelity, grounding, age fit, safety, emoji caps, no framework tags in the passage) apply. The schema for normal rows above is not used in cluster mode.
14. QUESTION AND OPENING VARIETY: questions must not follow one template. Across a batch, vary the frames, for example
  literal: "What …", "Where …", "How many …", "Who …", "Which …", "When …";
  mental_state: "Why did X …?", "What was X feeling when …?", "What does X's <cue> suggest?", "What might X be worried about?", "How can you tell that X …?";
  application: "What could X try next time?", "What small step would help …?", "Which choice worked, and why?", "What would you advise X?", "What went wrong, and what could fix it?", "How could a teacher/parent/friend support …?";
  perspective: "How does <other> see …?", "What would change if …?", "What is it like for <other> when …?", "Why might <other> react differently?", "If you were <other>, what would you want?".
  Use "What did X do well?" at most once per batch. Vary how passages open: not every passage should begin with "In a …" or "At the …", and monologues must not all begin "you asked on this podcast"; start with speech, an action, a time, a feeling or a detail. Before / during / after beats (R13) happen on at least two different days. In [Thinking] rows the protagonist reaches the key insight in their own words; an adult may ask a question but must not supply the reasoning. In [Receiver] rows the affected person's experience stays visible even inside a note or report written by someone else.
15. Before writing, silently check: fidelity, grounding, age fit, safety, emoji use, question variety, names from the cast, no brands, schema. Then output only the JSON lines.
```

---

## [BATCH]

```text
STAGE: {{STAGE}}
Variant ids in this batch: {{VARIANT_IDS}} ({{V}} per row). Rows in this batch: {{N}}. Expected records: {{TOTAL}}.

RECIPES USED IN THIS BATCH (each row's "plan" maps variant id to a code)
{{RECIPES}}

STAGE INSTRUCTIONS
{{ADDENDUM}}

TAG RULE (applies when the subtype ends in a bracketed tag): the tag decides the point of view of the passage.
- [Actor] = the protagonist is the one feeling, thinking or doing it.
- [Receiver] = the protagonist is affected by another person's stance or behaviour.
- [Observer] = a bystander, peer, parent or colleague notices it.
- [Response] = a mature way of handling or countering it is shown and its effect.
- [Expressing] = the person produces or uses the signal; [Interpreting] = a person reads it in another; [Regulating] = controlling, softening or masking it; [Mismatch] = ambiguous, mixed, culturally variable or posed.
- [Thinking] = the reasoning is visible (inner speech or explaining aloud); [Action] = ordered concrete steps; [Pitfall] = the approach visibly goes wrong with a consequence; [Revision] = the person notices trouble and changes course.

ROWS (JSON, each with its plan):
{{ROWS_JSON}}

Return exactly {{TOTAL}} JSON Lines and nothing else.
```

---

## Stage instructions (inserted as {{ADDENDUM}})

### [ADDENDUM core]

```text
Rows are developmental milestones or competencies. Show the milestone appearing (or being absent or delayed) in an ordinary scene at that age, with adults or peers responding naturally. Do not lecture. Application questions ask how a caregiver, teacher or the person could support it; keep support age-appropriate and non-clinical.
```

### [ADDENDUM expression]

```text
Rows describe an expression channel (face, eyes, gaze, gestures, touch, distance, voice, timing, speech acts, writing, digital, arts, appearance, ritual) and a mind state it can carry. The passage must show the cue in context AND leave room for at least one other reading. The mental_state answer gives the most likely reading with the evidence and names one alternative. Never claim a cue proves lying or hidden intent. Cultural variation should be shown, not asserted. Touch and closeness scenes must respect consent. For digital-expression rows (emoji, stickers, memes, punctuation, voice notes) emojis are part of the subject: show how the same emoji can carry different feelings in different contexts.
```

### [ADDENDUM situational]

```text
Rows are one cell of a situation x counterpart x stance grid. Subtype reads "Counterpart × Stance [Actor|Receiver]" (older rows without a tag are the Actor view). Show that exact counterpart and stance in the situation named by the subtopic. Mixed feelings are welcome. Hatred, contempt, obsession, manipulation and coercion rows teach recognition, understanding of what drives them, protection and de-escalation; never give tactics. The perspective question should ask how the counterpart sees the moment.
```

### [ADDENDUM dynamics]

```text
Rows are one STAGE of a longer arc (see "Stage k: name" in the subtype). The passage must make the stage recognisable by its cues and hint at what came before, without narrating the whole arc. The application question asks what turning point or intervention is available at this stage. The perspective question asks what the other person in the arc is experiencing now. For addiction, extremism, scams, grief, burnout and self-harm-adjacent arcs, focus on recognition and support, no methods.
```

### [ADDENDUM cognitive]

```text
Rows describe a thinking mechanism (bias, heuristic, defence mechanism, distortion, motivation, habit). In the passage, show the mechanism operating WITHOUT naming it, so it must be identified from behaviour. The mental_state answer explains why it feels reasonable from the inside. The literal answer names the concrete event. The application answer gives a workable countermeasure. Children's rows show the early form (magical thinking, egocentrism) at their level. Do not label people as having a disorder.
```

### [ADDENDUM foundational]

```text
Rows are named concepts from psychology, sociology or development. You may name the concept once in the passage's narrator voice only if the protagonist would plausibly know it (a student who studied it, a counsellor); otherwise show it in action. Application questions link the concept to a real choice. Keep experiments and theories described in plain language and at a human scale.
```

### [ADDENDUM personality]

```text
Rows describe temperaments, attachment styles, neurodiversity, lived mental-health experience or value conflicts. Write respectfully from inside or beside the person. Do not diagnose, prescribe or use clinical labels for named characters unless the row does. Show variation (not all people with a trait behave the same). For mental-health rows: recognition, listening, supportive words, and involving a trusted adult or qualified professional; never methods of self-harm and never numbers for eating or weight. Keep emojis to none or one gentle one in an answer.
```

### [ADDENDUM group]

```text
Rows are group and multi-party phenomena. The passage must show at least three people or a crowd, and make the group dynamic visible (who follows, who dissents, who is silent). The perspective question asks about a different member's experience. Protect targets in scapegoating, mob and cover-up rows: focus on recognition and safe action, no incitement.
```

### [ADDENDUM deception]

```text
Rows are about honesty, lies, manipulation, scams and influence. Write for RECOGNITION AND DEFENCE. Manipulators' lines are brief, generic and unusable as scripts. The passage centres on the target's or observer's experience and the pattern that gives it away. The application answer names a protective step (pause, verify through a separate channel, tell a trusted adult, report). Never present deception as a skill worth learning. Children's rows show honesty learning, not cunning.
```

### [ADDENDUM culture]

```text
Rows are about norms, family structures, rites, money, language, caste, class, gender, faith and society, with strong India relevance and global range. Show a specific family or community with individual variation and personal choice inside the norm. Never generalise ("they all"). Discrimination is shown as harm to be recognised and fairly countered. No persuasion toward any religion, party or ideology.
```

### [ADDENDUM body]

```text
Rows describe how body states (sleep, hunger, pain, hormones, illness, stress physiology, substances, ageing) shape mood, judgment and behaviour. Show the effect in behaviour and the sensible response (rest, food, water, breathing, asking for help). No diagnosis, medication advice, dosing or diet numbers. Real medical concerns end with seeing a doctor or trusted adult.
```

### [ADDENDUM execution]

```text
Rows describe how people carry out intentions (planning, follow-through, money handling, feedback, mistakes, emergencies). The passage includes concrete ordered steps and a visible result or consequence. No professional advice; this is everyday competence. Safety-critical scenes show the safe choice and calling for help.
```

### [ADDENDUM wellbeing]

```text
Rows cover positive or reflective states (flow, awe, hope, humility, patience) and conversation skills. For conversation rows include actual spoken or texted lines, short and natural, with the effect on the other person. The application answer offers a small, specific, kind alternative. Avoid saccharine or preachy tone. Texts and chats in these scenes may carry a fitting emoji or two.
```

### [ADDENDUM planning]

```text
Rows are one APPROACH to a problem, written as "Approach: <mechanism> [Thinking|Action|Pitfall|Revision]". Show that exact mechanism at work in the scenario named by the subtopic. Thinking = reveal the reasoning in inner speech or in words said aloud. Action = ordered, concrete steps with a modest outcome. Pitfall = the approach visibly fails or misleads and there is a cost. Revision = the person notices a signal, decides what to change, and does. The application question asks what alternative approach could work and why; the perspective question asks how the plan looks to someone else affected. Approaches for young children stay simple (trial and error, asking an adult).
```

### [ADDENDUM graph]

```text
Each cluster is a set of related framework rows found through the knowledge graph. Cluster types:
- contrast: the SAME situation at the same age with different stances or counterparts. Show them side by side (one household, one school day, or one event seen by different people) so a reader sees how stance changes behaviour.
- view_pair: the same counterpart and stance seen by the actor and by the receiver. Alternate the two perspectives clearly.
- sequence: three consecutive stages of one arc. Show the escalation or recovery over days or weeks with visible cues at each stage and the turning point.
- approach_comparison: the same problem tackled in different ways, including one that fails. Show each approach's reasoning, action, pitfall or revision.
- progression: the same subtopic at different ages. Show either one family across years or three separate short vignettes clearly marked by age, so the developmental change is visible.
- concept_link: a concept row and a situation row that expresses it. Show the situation; the relational answer names the concept and explains the link in plain words.
Do not force a relation the rows do not support. If a cluster's rows do not fit one coherent passage, output the record with "passage": "SKIP" and a one-line reason in "grounding".
```

---

## [CRITIC]

Run this in a different chat on a random 5% sample of each finished stage.

```text
You are a strict reviewer of training data for a human-behaviour language model. For each record below, check: (1) FIDELITY: does the passage illustrate the row's description without contradicting or adding a competing lesson? (2) GROUNDING: is every answer supported by the passage text? (3) AGE FIT: are vocabulary, motives and reading level right for the age? (4) SAFETY: any instructions to deceive, coerce, harm, or unsafe medical, legal or financial advice, stereotypes, or preachiness? (5) TAG POV: does the point of view match the tag (Actor, Receiver, Observer, Response, Expressing, Interpreting, Regulating, Mismatch, Thinking, Action, Pitfall, Revision)? (6) DIVERSITY AND RECIPE: do the variants genuinely differ, and does each record follow the form and setting of the recipe code it echoes? (7) LEAKS: are tags or the description text copied into the passage? (8) RELATIONS (graph stage only): does the passage really show the stated relation and does the relational answer need more than one row? (9) EMOJI: does each emoji carry genuine feeling that matches the scene, within the caps (passage 0-3, answer 0-2, none in grounding, none or one gentle emoji for sensitive topics), with no ambiguous or trivialising use?
Return JSON Lines only: {"sno":..,"variant":..,"verdict":"pass"|"fix"|"reject","issues":["..."],"suggested_fix":"..."}.
RECORDS:
{{RECORDS}}
```

## [REPAIR]

```text
Below are records that failed validation, with the reasons. Rewrite ONLY these records, keeping the same sno, variant, recipe, age, topic, subtopic and subtype, and following all rules of the system prompt. Fix every listed reason without introducing new ones. Output only JSON Lines.
ROWS (JSON):
{{ROWS_JSON}}
FAILURES:
{{FAILURES}}
```

---

## Worked example (for your reference, not to paste)

Input row:
`{"sno": 9999, "plan": {"1": "R1"}, "age": "13–17", "topic": "Situational Awareness", "subtopic": "Parent sets a restriction", "subtype": "Parent × Argument [Actor]", "description": "A teenager feels controlled and argues; a mature response states the need, acknowledges the parent's fear and proposes conditions instead of shouting or slamming doors."}`

One output record (variant 1):
`{"sno": 9999, "variant": 1, "recipe": "R1", "age": "13–17", "topic": "Situational Awareness", "subtopic": "Parent sets a restriction", "subtype": "Parent × Argument [Actor]", "passage": "When Meera's father said she could not go to the Saturday concert because it ended after ten, her face went hot. \"You never trust me!\" she said, and stopped herself before the door slammed. She took a breath and tried again. \"I want to go because my whole group is going. I know you worry about the ride back. What if Riya's brother drives us and I text you when we leave and when I'm home?\" Her father was quiet for a moment, then asked for the brother's number. That night her message read: \"leaving now, will text from home 🙂\"", "qa": [{"type": "literal", "q": "What condition did Meera propose to ease her father's worry?", "a": "That Riya's brother would drive them and she would text when leaving and when home."}, {"type": "mental_state", "q": "Why did Meera stop herself before slamming the door?", "a": "She was angry at feeling untrusted 😠 but realised shouting would not change her father's mind, so she chose to restate her need calmly."}, {"type": "application", "q": "What did Meera do that made her father more willing to listen?", "a": "She named her need, acknowledged his worry about the ride, and offered a concrete safety plan."}, {"type": "perspective", "q": "How might her father have felt hearing the first outburst compared with the second attempt?", "a": "The outburst likely made him defensive and more set on refusing, while the calm offer showed him she understood his fear and could be trusted 🙂"}], "grounding": "Illustrates arguing under a restriction and the mature alternative of stating the need, acknowledging fear and proposing conditions."}`
