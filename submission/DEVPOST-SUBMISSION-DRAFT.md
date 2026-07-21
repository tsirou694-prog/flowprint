# Devpost Submission Draft — FlowPrint

## Project name

FlowPrint

## Tagline

Turn completed AI work into one reusable, revision-safe Agent Skill draft—without recording the conversation.

## Track

Developer Tools

## Short description

FlowPrint is a Codex plugin that extracts reusable workflows from completed AI tasks. It scopes evidence, separates adjacent workflows, stops for explicit user selection, classifies the selected workflow into six layers, and compiles a non-installed Agent Skill draft behind deterministic validation and revision gates.

## Inspiration

The best AI workflows often disappear inside long conversations. Saving the whole transcript is noisy and risky: one-off values look like permanent rules, named-character facts leak into general instructions, failed attempts disappear, and separate deliverables are merged into one broad workflow.

I wanted a way to preserve **how a successful task was done** without preserving the conversation itself.

## What it does

FlowPrint starts after a user has substantially completed a task.

It first checks whether the current workspace is a safe evidence root. It then uses GPT-5.6 in Codex to identify independently reusable workflow candidates. If a conversation produced more than one reusable output, FlowPrint stops and asks the user which one to preserve. It does not classify or compile until that selection is explicit.

The selected workflow is separated into:

1. Core Workflow
2. Domain Knowledge
3. Profile
4. Run Parameters
5. Failure Lessons
6. Permission Boundaries

Deterministic Python validators then check the classification, user confirmations, workflow binding, permission state, and generated draft structure. The compiler creates a non-installed Agent Skill draft with a dependency-tracked manifest. Later natural-language corrections create an impact plan, invalidate stale confirmations, and require a matching revision receipt before a separately versioned draft can be compiled.

## How I built it

FlowPrint is packaged as a local Codex plugin with one Agent Skill, four reference contracts, and deterministic Python scripts for evidence-scope checks, classification validation, rendering, compilation, dependency analysis, and receipt-gated revisions.

GPT-5.6 performs the language-dependent work: interpreting completed-task evidence, finding workflow candidates, decontextualizing rules, and analyzing user corrections. Python owns the state machine and fail-closed gates.

I built and iterated on the project in Codex. Codex helped scaffold the plugin, inspect runtime failures, implement validators, create adversarial fixtures, run regression tests, and translate professional review feedback into mechanism changes rather than wording changes.

## Key product decisions

- Replace model self-rated confidence with explicit evidence states and review gates.
- Never store or replay the raw transcript.
- Treat compile, install, and external actions as separate permissions.
- Block recursive evidence discovery from broad personal folders.
- Represent multiple reusable outputs as a first-class state instead of silently merging them.
- Keep base drafts immutable and require receipt-bound revisions.
- Report evaluation honestly as `N=1` rather than calling a draft “proven” or “field-tested.”

## Challenges

The hardest problem was not generating a Skill file. It was deciding what **must not** become reusable.

Early versions exposed three failures:

- a model-generated confidence score could hide a wrong classification;
- an implicit trigger searched Memory, shell history, and broad user folders to reconstruct missing evidence;
- one completed travel conversation produced both an itinerary and a poster, but the schema could represent only one workflow and merged both into one Skill.

Each failure changed the mechanism: evidence-state gates replaced confidence, a deterministic workspace preflight constrained discovery, and schema `0.4` added workflow candidates plus a user-selection gate.

## Accomplishments

- 66 structural and regression tests currently pass; they verify the pipeline and deterministic gates, not generated-content quality.
- Valid and invalid compiler paths fail closed without installing a Skill.
- The tested revision transaction preserves the base draft and rejects missing or altered receipts.
- The workflow-selection gate rejects unresolved multi-workflow inputs without creating an output directory.
- Real macOS and Windows Codex CLI tests exercised installation, activation, compilation, and rejection paths on the documented samples.
- One held-out real task was accepted after two user-guided correction cycles; the report remains explicitly labeled `N=1` and not Field-tested.

## What I learned

Reusable AI workflows need a boundary between probabilistic understanding and deterministic state transitions. The model is good at interpreting intent and language, but it should not be allowed to silently confirm its own interpretation, broaden its evidence scope, or convert one successful run into a universal rule.

I also learned that honest evidence labels improve the product. “Tested on one held-out task” is less impressive than “Proven,” but it tells the user what they can actually trust.

## What's next

- test workflow discovery across more real multi-output conversations;
- run held-out tasks with different named entities to detect Profile leakage;
- add an evaluator independent from the generator where available;
- accumulate transparent successful-use history toward a Field-tested label;
- improve ChatGPT desktop distribution and onboarding;
- add a human-readable dependency and revision viewer.

## Built with

- Codex
- GPT-5.6
- Python
- Agent Skills
- Codex Plugins and local marketplace
- JSON and Markdown

## Supported platforms

- macOS Codex CLI
- Windows Codex CLI
- ChatGPT desktop Work mode: plugin activation and scope guard observed on macOS; use the documented Codex CLI path for the complete judge test
- Not supported: local plugin installation in ordinary ChatGPT web

## Testing instructions

See the repository README for installation, sample inputs, expected gates, and the complete test command. Judges can run the included `yueyang-needs-selection-v0.4.json` fixture to observe a two-workflow selection stop, then compile either independently user-selected workflow without rebuilding the project.

## Submission links — fill before submission

- Public GitHub repository: `https://github.com/tsirou694-prog/flowprint`
- Public YouTube demo: `TBD`
- `/feedback` Codex Session ID: `TBD`
- Optional project website or documentation: `TBD`
