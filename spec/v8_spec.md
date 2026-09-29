# v8 gap blocks: spec for row writers

Context: a human development framework (ages 1–26) is being built as training data for a small language model that must understand genuine, complex human mindset and action. Existing content: developmental milestones, a situation x stance grid (actor and receiver views), and expression / mind-state rows. You are writing one NEW block that fills a gap. You are given a block name, its scope and an output path.

## Output format (strict)
One row per line, exactly 4 pipe-separated fields. No header, blank lines, numbering or markdown.

    Age|Subtopic|Subtype [Tag]|Description

- Age: exactly one of 1–3, 4–6, 7–12, 13–17, 18–22, 23–26 (en dash). Use only ages where the row genuinely applies; abstract topics start later (for example most cognitive biases start at 7–12 or later; toddler rows describe behaviour only).
- Subtopic: a concise name of the item (a bias, an arc, a group phenomenon, a condition, a skill). Use identical wording across all rows of that item so they group.
- Subtype [Tag]: a specific facet, then exactly one tag:
  - [Actor] = the person doing, feeling or exhibiting it.
  - [Receiver] = the person on the receiving end or affected by it.
  - [Observer] = a bystander, peer, teacher, parent or colleague who notices it.
  - [Response] = a mature, wise way to handle, counter or recover from it.
- Description: 1–2 sentences, at most 260 characters, no pipe characters, neutral third person (a child, a teenager, a manager...; never I or you). Say what is happening inside (thought, feeling, motive), what it looks like in behaviour, and where useful the wise action versus the harmful pattern. Concrete, plain language, culturally aware (India-relevant examples welcome, not required).

## Coverage rule
Aim for depth and distinctness over padding. For each item write several rows across ages and views (Actor, Receiver, Observer, Response). Every row must teach a distinct mindset or action. Mixed and contradictory states are welcome (love with resentment, duty with desire).

## Quality and safety
- Honest and non-preachy. Describe how minds actually work, including uncomfortable truths.
- Harmful topics (deception, manipulation, cults, abuse, addiction, extremism, hatred, self-harm risk) are written for RECOGNITION, understanding of what drives them, protection, and recovery. Never provide operational steps for deceiving, coercing, stalking, radicalising, exploiting or harming anyone. No self-harm methods.
- Mental-health and neurodiversity rows describe lived experience, how it looks from outside, respectful support, and when to seek qualified help. No diagnosing, no treatment or medication advice, no dosing. Never pathologise normal variation. Avoid numbers for calories, weight or fasting.
- Body and health rows: describe effects on mood, judgment and behaviour and sensible habits; recommend qualified medical help for real problems.
- Culture, religion, caste, class, gender, disability and politics: non-stereotyping, respectful of all faiths and non-belief, no persuasion toward any side; teach recognition of discrimination and how to act fairly.
- Match cognitive level to age.

## Delivery
Write rows with the Write tool to the output path you are given. Do not print rows in your reply. When done reply only with: the file path, the row count, and the list of items covered with row counts.
