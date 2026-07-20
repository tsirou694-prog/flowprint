# FlowPrint Demo Video Script

Target length: **2:45–2:55**  
Required output: public YouTube video, English narration or an included English translation.

## Recording principles

- Record the product working; do not make the video a slide presentation.
- Use large terminal text and hide personal paths, email addresses, tokens, and unrelated files.
- Pre-open the project root and prepare commands so typing does not consume the three-minute limit.
- Keep the FlowPrint version visible once.
- Show one success path and at least one fail-closed path.
- Do not call the generated Skill “proven” or “field-tested.”

## Timeline and narration

### 0:00–0:18 — Problem

**Screen:** Title card, then a completed AI conversation with two outputs: a family itinerary and a trip poster.

**English narration:**

> Useful AI workflows disappear inside long conversations. Copying the transcript into memory mixes reusable methods with one-off values, named-entity facts, failed attempts, and permissions. FlowPrint turns completed AI work into one reusable Agent Skill draft without recording the conversation.

### 0:18–0:38 — Activation and evidence scope

**Screen:** Run `$flowprint activation check`, then briefly show a broad Home-folder scope check returning blocked.

**English narration:**

> FlowPrint is a Codex plugin built with GPT-5.6. Before reading files, a deterministic scope check blocks broad personal folders. The user must open a real project or provide exact sources, preventing the agent from searching Home, Downloads, shell history, or unrelated memory to reconstruct missing evidence.

### 0:38–1:08 — Multi-workflow selection

**Screen:** Render `yueyang-needs-selection-v0.4.json`. Highlight two candidates and `needs_workflow_selection`. Show that six-layer items are absent.

**English narration:**

> GPT-5.6 interprets the completed task and discovers reusable workflow candidates. This conversation produced both a family-trip planner and a poster workflow. Earlier versions merged them. Schema zero-point-four now stops at `needs_workflow_selection`; the model cannot choose for the user or classify both into one Skill.

### 1:08–1:28 — Fail-closed compiler

**Screen:** Attempt to compile the unresolved input. Show exit `1`, gate `workflow_selection`, and absent output directory.

**English narration:**

> This is a real compiler gate, not just chat wording. Compiling before selection exits nonzero and leaves no partial draft.

### 1:28–1:53 — Selected workflow compilation

**Screen:** Compile the user-selected trip workflow. Open the generated `SKILL.md`, manifest, and compile record. Highlight `trip-planning`, `not_authorized`, and no external action.

**English narration:**

> After the user selects trip planning, FlowPrint classifies only that workflow into core method, domain knowledge, profile, run parameters, failure lessons, and permission boundaries. Deterministic validation then emits a non-installed Skill draft. Installation and external actions remain separately unauthorized.

### 1:53–2:20 — Safe revision

**Screen:** Show a prepared correction impact report, stale confirmations, a missing-receipt rejection, then a separately versioned revised draft.

**English narration:**

> Natural-language corrections are handled as revision transactions. FlowPrint computes affected artifacts, invalidates stale confirmation, and requires fresh user acceptance. A missing or changed receipt fails closed, the base draft remains immutable, and the revised Skill receives a new version.

### 2:20–2:38 — Real evaluation

**Screen:** Show the blind A/B sticker sheets and final accepted eight-image sheet. Display `Tested on N=1`.

**English narration:**

> I also tested one generated workflow on a held-out real task. It prevented an identity-breaking anatomy error, but its first pass still repeated expressions and needed two user correction cycles. FlowPrint reports this honestly as tested on N equals one, not field-tested.

### 2:38–2:55 — Codex, GPT-5.6, and close

**Screen:** Briefly show test output: `Ran 63 tests — OK`, then architecture or repository tree.

**English narration:**

> Codex accelerated the entire build: plugin scaffolding, debugging, cross-platform tests, and mechanism changes from review feedback. GPT-5.6 performs language understanding; deterministic Python owns the gates. FlowPrint preserves successful AI work while keeping the user in control of what becomes reusable.

## Optional English subtitle closing card

```text
FlowPrint
From completed AI work to one reusable, guarded Agent Skill draft.
63 automated tests · macOS + Windows Codex CLI · Held-out evaluation N=1
```

