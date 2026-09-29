# Situation x Stance grid: spec for row writers

Goal: build training rows for a small language model that must understand genuine, complex human mindset and behaviour up to age 26. Each row is one cell of a grid: a SITUATION, a COUNTERPART, a STANCE, and a PERSPECTIVE.

## Output format (strict)
One row per line, exactly 4 fields separated by the pipe character. No header, no blank lines, no numbering, no markdown.

    Age|Situation|Counterpart × Stance [Actor]|Description

- Age is exactly one of: 1–3, 4–6, 7–12, 13–17, 18–22, 23–26 (en dash).
- Situation: short concrete scenario, 2–6 words, identical wording across all rows of that situation so rows group.
- Third field: "Counterpart × Stance [Actor]" or "Counterpart × Stance [Receiver]".
  - [Actor] = the person is the one feeling or acting the stance (e.g. I hate my rival).
  - [Receiver] = the person is on the receiving end (e.g. I am being hated / worshipped / envied / manipulated / ignored / forgiven / betrayed by that counterpart).
- Description: 1–2 sentences, at most 260 characters, no pipe characters. Cover: (1) what is felt/thought inside, (2) what a mature, wise action looks like, and where useful (3) the immature or harmful pattern. Concrete, plain, culturally aware (India-friendly examples welcome but not required).

## Grid rule
For each situation, cover MANY counterparts and MANY stances, and for the strong stances write BOTH the Actor and the Receiver view. Aim for 6–14 rows per situation. Do not pad with near-duplicate rows; every row must teach a distinct mindset or action.

## Stance vocabulary (use any that fit; do not force all onto every situation)
affection/love, respect, admiration, worship/devotion, gratitude, trust, loyalty, protectiveness, compassion, pity, forgiveness, argument, anger, hatred, contempt, envy, jealousy, rivalry, fear, awe, guilt, shame, betrayal, manipulation, exploitation, indifference, neglect, dependence, obsession, resentment, disillusionment, humiliation, deceit/gaslighting, coercion, mockery, grief, indebtedness, pride, rejection, acceptance.

## Counterparts (examples)
parent, sibling, grandparent, child, spouse/partner, ex, crush, friend, best friend, rival, classmate, teacher, mentor, boss, colleague, junior, client, neighbour, stranger, authority/police, doctor, religious teacher/guru, God, faith community, political opponent, online stranger, celebrity/leader, institution, self.

## Safety and quality rules
- Age-appropriate. No explicit sexual content. For romance/intimacy keep to feelings, consent, boundaries, respect.
- Hatred, contempt, revenge, obsession, manipulation, abuse rows teach RECOGNITION, understanding of what drives them, protection, de-escalation and healthy response. Never give instructions for harming, stalking, coercing or deceiving anyone. No self-harm methods.
- Receiver rows for abuse/bullying/coercion: focus on recognizing it, it not being the victim's fault, seeking trusted help, safe boundaries.
- Worship/devotion rows: show genuine meaning and belonging AND the discernment needed against exploitation or blind obedience. Treat all faiths and non-belief respectfully; no religious or political persuasion.
- Balanced, non-preachy, honest about ambiguity. Real minds mix feelings (love + resentment, admiration + envy); include such mixed cases where relevant.
- Match cognitive level to the age bracket: a 2-year-old's rows describe behaviour and feeling, not reflection.
- Do not repeat combinations already in the existing file (see below). You may add missing stances or Receiver views to situations that already exist there, using the exact same Situation wording.

## Existing rows to avoid duplicating
/tmp/claude-0/-home-claude/2c2d6906-049c-5163-ac84-429754ca8697/scratchpad/human_development_framework_v5.csv
(rows where Topic = Situational Awareness; columns S.No, Age, Topic, Subtopic=Situation, Subtype=Counterpart × Stance, Description). Read only the rows for your age bracket.

## Delivery
Write your rows with the Write tool to the output file path you are given, one row per line. Do not print the rows in your reply. When done, reply with only: the file path, the number of rows, and the list of situations covered with row counts.
