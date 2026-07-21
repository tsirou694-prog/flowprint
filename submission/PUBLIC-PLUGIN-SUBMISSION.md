# FlowPrint Public Plugin Submission

Use this document to populate the OpenAI Platform plugin submission portal. FlowPrint is a **skills-only** plugin and does not require an MCP server.

## Submission type

- Type: Skills only
- Initial submission: Yes
- Plugin name: FlowPrint
- Submitted plugin version: `0.1.0+codex.20260721013104`
- Developer identity: SIROU Tang — **must be verified in the submitting OpenAI Platform organization**
- Category: Developer Tools
- Availability: **publisher must select supported countries or regions in the portal**
- Logo source: [`assets/flowprint-logo-1024.png`](../assets/flowprint-logo-1024.png)

## Public listing

### Short description

Turn completed AI work into one guarded, reusable Agent Skill draft.

### Long description

FlowPrint starts after an AI task is complete. It separates adjacent reusable workflows, stops for explicit user selection when multiple candidates exist, classifies the selected workflow into six evidence-aware layers, and compiles a non-installed Agent Skill draft behind deterministic validation and confirmation gates. Later corrections use dependency-aware impact analysis, stale-state invalidation, fresh confirmation, and non-overwriting revision receipts.

FlowPrint does not record or replay the raw conversation, invent numerical confidence, silently install generated Skills, or treat draft creation as permission for external actions.

## Public URLs

- Website: https://github.com/tsirou694-prog/flowprint
- Support: https://github.com/tsirou694-prog/flowprint/blob/main/SUPPORT.md
- Privacy policy: https://github.com/tsirou694-prog/flowprint/blob/main/PRIVACY.md
- Terms: https://github.com/tsirou694-prog/flowprint/blob/main/TERMS.md

These URLs become valid only after the three policy files are merged into `main`.

## Upload artifact

- Bundle type: skills-only ZIP
- Required top-level directory: `flowprint/`
- Required contents: `SKILL.md`, `agents/`, `references/`, and `scripts/`
- Exclusions: repository tests, evidence logs, generated drafts, credentials, caches, and Python bytecode
- Integrity: record the final filename, byte size, and SHA-256 after packaging; do not rebuild the ZIP after recording the hash

## Starter prompts

1. Turn the completed task in this conversation into a reusable Agent Skill draft. Show me the classification before compiling anything.
2. Detect whether the work we just finished contains multiple reusable workflows. Stop for my selection instead of merging them.
3. Classify the selected completed workflow into Core, Domain, Profile, Run Parameters, Failure Lessons, and Permission Boundaries.
4. Compile the confirmed classification into a non-installed Skill draft and report the validation and permission states.
5. Analyze my correction to this FlowPrint draft, show the affected items and stale artifacts, and wait for confirmation before compiling a new version.

## Release notes

Initial public submission of FlowPrint, a skills-only plugin for workflow-scoped, evidence-aware Agent Skill drafting. The submitted version includes deterministic scope, classification, workflow-selection, compilation, generated-output-contract, and revision gates. The repository currently passes 66 structural and regression tests; these tests do not establish generated-content quality, statistical workflow-discovery accuracy, field adoption, or Field-tested status.

## Portal attestations to verify manually

- The submitting role has Apps Management write access.
- The selected developer identity is verified and matches SIROU Tang.
- The final uploaded Skill ZIP matches the tested file tree.
- The public URLs resolve without authentication.
- The logo is final and owned by the publisher.
- Exactly five positive and three negative test cases are entered.
- Country and region availability is intentionally selected.
- The listing makes no statistical accuracy or Field-tested claim.
- The public Work-mode test cases have been executed against the exact uploaded bundle, or any unexecuted case is disclosed rather than reported as passed.
