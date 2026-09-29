# Planning and problem-solving block: spec for row writers

Context: a human development framework (ages 1–26) is being built as training data for a small language model that must understand genuine human thinking and action. This block teaches HOW people plan, generate ideas and solve problems: the thinking mechanism, the concrete actions, how the plan fails, and how it is revised. Key idea: the SAME problem is solved in DIFFERENT ways by different people (or by the same person at different moments), and each way has its own mechanism, strengths and failure modes.

## Output format (strict)
One row per line, exactly 4 pipe-separated fields. No header, blank lines, numbering or markdown.

    Age|Scenario|Approach: <mechanism> [Tag]|Description

- Age: exactly one of 1–3, 4–6, 7–12, 13–17, 18–22, 23–26 (en dash). Use only ages where the scenario and mechanism genuinely fit the cognitive level.
- Scenario: a concrete problem or planning situation, 2–7 words, identical wording across all rows of that scenario so they group (for example "Planning a school project", "Handling a sudden money shortfall").
- Approach: after the literal text "Approach: " give the planning or problem-solving mechanism in plain words (see vocabulary below), then exactly one tag:
  - [Thinking] = the inner reasoning: what the mind does (compares options, works backward, imagines the outcome, uses an analogy, feels its way, avoids...).
  - [Action] = the concrete steps taken as the plan is carried out.
  - [Pitfall] = how this approach typically fails or misleads (bias, overplanning, impulsivity, rigidity, avoidance, groupthink...).
  - [Revision] = how the person notices trouble and adapts, recovers or switches approach.
- Description: 1–2 sentences, at most 260 characters, no pipe characters, neutral third person (a child, a student, a manager; never I or you). Concrete, plain language, with specific details of the situation, what the person decides and why. India-relevant contexts are welcome.

## Coverage rule
For each scenario write several different approaches (typically 3–5) to the same problem, and show for some approaches the full loop: Thinking, Action, Pitfall, Revision. Approaches must genuinely differ in mechanism, not just wording. Include both effective and ineffective ways, since real minds use both. Every row must teach something distinct. Aim for about 8–14 rows per scenario.

## Mechanism vocabulary (use any that fit, and others you can justify)
Task decomposition, means-end analysis, working backward from the goal, forward planning, analogy and precedent, trial and error, heuristics and satisficing, maximising with a decision matrix, pros-and-cons lists, prioritising (urgent vs important), time-boxing and scheduling, checklists and routines, implementation intentions (if-then), mental simulation and rehearsal, pre-mortem (imagine failure first), scenario and contingency planning, buffer and slack planning, minimum viable version and iteration, experiment and measure, first-principles reasoning, inversion (what would make it worse), root-cause analysis and five whys, divergent brainstorming then convergent selection, lateral thinking and reframing, constraint-based creativity, sketching, storyboarding and externalising thought on paper, sleeping on it and incubation, seeking advice or an expert, crowdsourcing, delegation, negotiation and win-win planning, values-first planning, emotion-aware planning (managing mood, energy), resource and budget planning, dependency and critical-path thinking, batching, deadlines and commitment devices, accountability partners, learning from past failures, adaptive replanning, cutting losses, plus dysfunctional modes: impulsive action, rigid persistence, analysis paralysis, overplanning, magical thinking, avoidance and procrastination, copying others without fit, planning fallacy, groupthink.

## Quality and safety
- Honest about trade-offs: no single method is best; show what each is good and bad at.
- Ethical: plans should not involve harming, defrauding, stalking, coercing or deceiving anyone. In dilemma and crisis scenarios show lawful, protective, considered handling (asking a trusted adult, authorities, professionals).
- Health, legal and money scenarios: general reasoning about how people plan, not personal medical, legal or financial advice; no dosing.
- Match cognitive level to age: toddler rows describe simple trial-and-error and using a caregiver as a tool; abstract mechanisms such as pre-mortem, critical path or first principles begin in the teens or later.
- Respectful of culture, gender, disability and family context; non-stereotyping.

## Delivery
Write rows with the Write tool to the output path you are given. Do not print rows in your reply. When done reply only with: the file path, the row count, and the scenarios covered with row counts.
