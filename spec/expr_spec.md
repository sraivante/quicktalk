# Expression and mind-state rows: spec for row writers

Context: a framework of human development (ages 1–26) is being built as training data for a small language model. It already has developmental milestones and a situation x stance grid. It is missing explicit coverage of HOW mind states are expressed and read: faces, eyes, body, gestures, touch, distance, voice, timing, speech acts, figurative language, written/digital/artistic/appearance/collective expression, interpretive mind-state labels, and mixed or masked displays.

Source taxonomy (70 categories): /root/.claude/uploads/2c2d6906-049c-5163-ac84-429754ca8697/af19b0fe-attachment.txt
Columns: No. | Group | Category | Expressions / examples. You are given a range of category numbers. Cover EVERY listed expression or example in your categories at least once, in some row (one row may cover a close cluster, e.g. "grin / beam").

## Output format (strict)
One row per line, exactly 4 pipe-separated fields. No header, blank lines, numbering, or markdown.

    Age|Category|Facet [Tag]|Description

- Age: exactly one of 1–3, 4–6, 7–12, 13–17, 18–22, 23–26 (en dash).
- Category: the exact Category text from the source table for that number (same wording every row, so rows group).
- Facet [Tag]: a short specific facet, then one tag:
  - [Expressing] = how the person produces or uses it at that age, and what mind state it usually carries.
  - [Interpreting] = the receiving end: how the person reads it in others, including the limits of mind-reading.
  - [Regulating] = controlling, softening, amplifying or masking one's own display.
  - [Mismatch] = ambiguous, mixed, incongruent, culturally variable, or deliberately posed displays.
- Description: 1–2 sentences, at most 260 characters, no pipe characters, neutral third person (for example "A toddler...", "A teenager...", "A manager..."; do not use I or you). Include: the mind state(s) it can signal, how meaning shifts with context, and the wise reading or use versus a common pitfall where useful.

## Coverage rule
For each category write about 8–14 rows spread across the age brackets where it genuinely applies (toddler rows describe behaviour and reflexive signals; sarcasm, irony, satire, innuendo, ultimatums, negotiation etc. start only in the older brackets). Across a category cover: development over ages, what mind states it signals (with ambiguity: the same signal can mean several states), reading it accurately, self-regulation or masking, cultural and contextual variation (India-relevant examples such as head wobble, namaste, touching elders' feet, eye-contact norms with elders, are welcome, alongside other cultures), and the modern or digital equivalent where relevant.

## Quality and safety
- Honest about uncertainty: expressions are cues, not proof. Do NOT claim that any gesture, gaze or micro-expression reliably reveals lying or hidden thoughts.
- Touch, closeness and boundary rows: teach consent, the right to refuse, safe versus unsafe touch, and telling a trusted adult; no sexual content.
- Conflict, threat, contempt, insult and coercion rows teach recognition, de-escalation and protection, not how to do them well.
- Avoid stereotyping any culture, gender, religion or disability. Signed languages are full languages; describe them respectfully.
- Do not duplicate rows within your file. Vary counterparts and contexts.
- Interpretive mind-state label categories (61–67): give every listed label its own row with an age-appropriate description of the inner experience, how it typically shows, and healthy handling. Categories 68–70: cover each listed reaction or style dimension.

## Delivery
Write your rows with the Write tool to the output file path you are given, one row per line. Do not print rows in your reply. When done reply only with: the file path, the row count, and per-category row counts.
