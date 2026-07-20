# FlowPrint Decontextualization Rules

Use these rules to decide where a candidate belongs. Classification is based on scope and causal source, not on data type. A color, size, date, or sentence can belong to different layers depending on why it exists and whether it should change next time.

Before applying the layers, separate independently reusable purposes and outputs. An itinerary planner and an invitation-poster designer may occur in the same conversation and share facts, but they have different triggers, steps, and success criteria. Shared evidence is not evidence that they belong in one Skill. When more than one workflow remains plausible, stop for user selection before classifying any item.

## Layers

- `core`: Entity-independent steps, decisions, quality gates, recovery paths, and safety rules that improve similar tasks.
- `domain`: Platform, file-format, legal, regulatory, or professional constraints loaded only for the relevant domain.
- `profile`: Stable facts or preferences tied to a named person, character, brand, organization, or user.
- `run_parameter`: Values a reasonable user may change on the next run, such as count, date, theme, input file, color, or output destination.
- `failure_lesson`: A failed approach plus the abstract prevention or recovery rule learned from it.
- `permission_boundary`: External, irreversible, account-specific, or high-impact actions that require fresh authorization.

Current-session controls such as “only preview”, “do not compile”, or “do not save in this turn” are execution-scope instructions, not reusable workflow candidates. Obey them directly and exclude them from all six persisted layers unless the completed workflow itself contains an external or irreversible authorization boundary.

## Enumerated rules

### R1 — Named-entity stability

Put stable facts tied to a named person, character, brand, organization, or user in `profile`. Do not copy the concrete fact into `core`.

Example: `老三没有可见尾巴` is Profile. `Verify identity-defining anatomy against the active profile` is Core.

### R2 — Domain authority

Put constraints caused by a platform, file format, law, standard, or professional domain in `domain`.

Example: a WeChat-required export dimension is Domain. The instruction to verify dimensions before delivery is Core.

### R3 — Next-run variability

Put a value in `run_parameter` when a reasonable next task may change it without changing the workflow.

Examples: sticker count, current theme, date range, input file, destination folder, and this run's background color.

### R4 — Entity-independent method

Put an item in `core` only when removing the named entity and current run values still leaves a useful method, decision, quality gate, or recovery step.

### R5 — Failure decomposition

Split a concrete failure into:

1. an entity-independent prevention or recovery rule;
2. any stable entity fact in Profile;
3. any changeable value in Run Parameters.

Example: `老三尾巴画错` becomes a Core anatomy check plus the Profile value `tail_visibility: absent`.

### R6 — Single-occurrence restraint

Do not promote a one-time preference or observation into Core or a user-level Profile without stability evidence. Keep it as a candidate Run Parameter or mark it `ambiguous` and require review.

### R7 — Temporal language signals

Treat `以后`, `始终`, `品牌规定`, and `必须` as evidence of persistence. Treat `这次`, `本批`, `本周`, and `临时` as evidence of a run parameter. These are signals, not deterministic truth; check later corrections and task evidence.

### R8 — Evidence and impact gate

Record evidence state and impact instead of a numeric model confidence score. High-impact, ambiguous, or conflicting items require review even when the model's rationale sounds certain.

Do not promote an explicit current-session denial into `permission_boundary` merely to ask whether the user wants to reverse it. Permission Boundary is for an action boundary worth preserving in the reusable workflow, such as submission, publication, deployment, messaging, deletion, or account access. A local preview/compile/save instruction controls the present FlowPrint run and should not be persisted.

## Evidence states

- `supported`: Direct, current evidence supports the classification and no material contradiction is visible.
- `ambiguous`: Evidence is incomplete, single-source, indirect, or allows more than one reasonable layer.
- `conflicting`: Two or more visible sources materially disagree, including an earlier instruction superseded by a later correction when order cannot be established.

Do not use percentages, probabilities, confidence scores, or synonyms that imply calibrated certainty.

## Impact levels

- `low`: A mistake is local, easy to notice, and easy to reverse.
- `medium`: A mistake affects output quality or repeated work but remains reversible.
- `high`: A mistake can pollute multiple tasks, alter identity/brand facts, expose sensitive data, or cause an external, irreversible, or account-specific action.

High-impact items always appear in the review card.

## Source preference

Prefer evidence in this order when sources agree with task chronology:

1. explicit user correction or final instruction;
2. accepted final artifact and deterministic test result;
3. earlier user instruction;
4. workspace file or metadata;
5. visual observation;
6. model inference.

Visual observation and model inference can support a question, but cannot alone create a permanent Profile fact.

Set evidence inventory `result: yes` only when a final or accepted output, artifact, validation result, or explicit description of the achieved result is visible. The phrase “this task is complete” or a list of requirements without an achieved output is not sufficient result evidence.

## Known residual risks

Rule matching still depends on model language understanding. It is more auditable than self-reported confidence, but it is not deterministic. Known failure modes include:

- negation, sarcasm, and quoted examples mistaken for instructions;
- a sample value mistaken for a permanent rule;
- a later correction failing to override an earlier request;
- long-context compression hiding the final decision;
- platform requirements confused with brand preferences;
- one image treated as a permanent character or brand fact;
- `usually`, `prefer`, and `must` treated as the same strength;
- a named entity leaking into Core through an example or rationale;
- a permission granted once being treated as durable authorization.
- two adjacent deliverables being merged into one broad Skill because they appeared in the same conversation.
- a real secondary workflow being missed, leaving the deterministic multi-workflow gate with only one declared candidate.

When evidence is missing or the rule match is uncertain, keep the item visible, mark it `ambiguous`, and use the conservative layer. Never claim that the residual risk is eliminated.

## Color and size example

| Candidate | Correct layer | Why |
|---|---|---|
| Verify dimensions before export | Core | Entity-independent quality gate |
| WeChat requires a specific sticker dimension | Domain | Platform-caused constraint |
| Brand A always uses muted red | Profile | Stable named-brand preference |
| Use red for this poster | Run Parameter | Reasonably changes next run |
