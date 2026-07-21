# Judging Evidence Matrix

## Technological Implementation

**Judge question:** Does the project use Codex thoroughly and reflect a working, non-trivial implementation?

Evidence to show:

- Codex plugin structure with a packaged Agent Skill and local marketplace.
- GPT-5.6-driven workflow discovery and decontextualization.
- Deterministic Python validators, compiler, scope guard, dependency analysis, and revision receipts.
- 66 passing structural and regression tests for the pipeline; these do not establish generated-content quality.
- Real positive and fail-closed CLI traces on macOS and Windows.
- `/feedback` Session ID from the primary build thread.

Do not rely only on code volume or screenshots. Demonstrate the selection gate and compilation path in the video.

## Design

**Judge question:** Is this a coherent product rather than a technical proof of concept?

Evidence to show:

- activation card;
- scope-blocking message with a clear next action;
- workflow-candidate selection card;
- six-layer classification review;
- non-installed draft with manifest and compile record;
- revision flow that preserves the base draft;
- Mac and Windows installation instructions.

Current weakness to acknowledge: onboarding still requires a project root and local marketplace installation. The ChatGPT web surface is not supported.

## Potential Impact

**Primary audience:** heavy ChatGPT Work and Codex users who repeatedly perform content, design, operations, research, and development workflows.

Credible problem:

- useful process knowledge is trapped in conversations;
- prompt copying loses failure lessons and permission boundaries;
- raw transcript replay risks context pollution and privacy leakage;
- generated Skills can overgeneralize named-entity facts or merge adjacent deliverables.

Bounded evidence:

- one real held-out task showed improved compliance with an identity-defining boundary;
- the result required two user-guided correction cycles;
- no claim of statistical accuracy or field adoption.

## Quality of the Idea

Novel elements to emphasize:

- compilation rather than conversation replay;
- explicit workflow selection before classification;
- six-layer decontextualization;
- evidence-state and user-confirmation gates instead of model confidence;
- separate permissions for draft compilation, installation, and external actions;
- dependency-tracked, non-overwriting natural-language revisions;
- transparent `N=1` evaluation language.

## Claim control

### Safe claims

- “FlowPrint passed 66 structural and regression tests in the current repository; these tests do not establish generated-content quality.”
- “The unresolved multi-workflow fixture is rejected at the `workflow_selection` compiler gate.”
- “The tested Windows revision transaction preserved the base draft and required a matching receipt.”
- “One held-out real task was accepted after two user-guided correction cycles.”
- “Plugin activation and documented CLI paths were exercised on macOS and Windows.”

### Claims to avoid

- “FlowPrint accurately discovers every workflow.”
- “Generated Skills are proven to improve performance.”
- “FlowPrint is field-tested.”
- “The security model prevents a malicious local process from tampering with records.”
- “The local plugin works in ordinary ChatGPT web.”
- “All Node 8 behavior has been statistically validated across ChatGPT desktop and CLI.”
