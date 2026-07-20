# Demo Asset and Shot List

## Required submission assets

1. Project thumbnail or logo.
2. Three to five Devpost gallery screenshots.
3. Public YouTube demo under three minutes.
4. Public or judge-shared code repository.
5. `/feedback` Session ID from the primary build thread.

## Recommended screenshots

### Screenshot 1 — Product promise

- FlowPrint activation card
- short caption: “Compile completed AI work into one reusable Skill draft”
- show current version without personal file paths

### Screenshot 2 — Workflow selection

- Yueyang classification preview
- two candidates visible
- `needs_workflow_selection` visible
- no six-layer items

### Screenshot 3 — Fail-closed gate

- compiler exit `1`
- `gate: workflow_selection`
- target directory absent

### Screenshot 4 — Compiled draft

- generated `SKILL.md`
- manifest fields: selected candidate, `not_authorized`
- compile record: no install, no external action

### Screenshot 5 — Revision and real evaluation

Split composition:

- left: stale confirmation / receipt-gate revision result;
- right: blind A/B sheets and final `N=1` accepted output.

## Recording preparation

- Create a clean demo project directory.
- Increase terminal font size.
- Hide email, username, full Home path, auth status details, and unrelated Downloads files.
- Pre-run long tests; during recording, show the final concise `63 tests — OK` output.
- Disable notifications.
- Use one exact plugin version throughout the recording.
- Prepare an English narration track or English subtitles.
- Do not use copyrighted music or third-party trademarks without permission.

## Visual style direction

- dark terminal background with warm orange accent for FlowPrint;
- six classification layers use six restrained colors;
- selection state uses amber, accepted state uses green, blocked state uses red;
- avoid dense architecture slides—the terminal and generated artifacts should remain the main evidence.

