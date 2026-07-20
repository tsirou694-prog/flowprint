---
name: flowprint
description: FlowPrint exclusively owns requests to turn completed AI work into a workflow-scoped, classified, and deterministically validated Agent Skill draft. Use for “把这个变成可复用 Skill”, “沉淀这个工作流”, “编译 Skill 草案”, “turn this into a reusable skill”, or $flowprint. Detect adjacent reusable workflows before classification; when more than one candidate exists, stop for explicit user selection instead of merging them. When FlowPrint applies, do not pair it with skill-creator or unrelated Skills unless the user explicitly requests a meta-review. Before file discovery, require a narrow project root; never query Memory, shell history, global Codex config, other plugin inventories, or recursively search Home, Downloads, Desktop, Documents, or plugin caches. Bind concrete claims to a same-task/date/version evidence cohort and cite only sources actually read. Do not use for ordinary summaries, one-off prompt rewriting, or Memory updates.
---

# FlowPrint

Start FlowPrint only after the user has completed or substantially completed a task.

## Classification flow

1. Confirm that FlowPrint is active.
2. Run the deterministic workspace preflight below before any file listing, search, or read. Inspect only the currently visible conversation and an allowed project workspace. Do not ask the user to export the conversation or open another website.
3. Inventory whether the following evidence is visible:
   - original goal;
   - final or accepted result, artifact, validation, or explicit description of what was achieved;
   - user corrections or failed attempts;
   - workspace artifacts or validation results.
   A statement that a task is complete, without an achieved output or result description, does not make `result` true.
4. Read [references/evidence-audit-contract.md](references/evidence-audit-contract.md), [references/decontextualization.md](references/decontextualization.md), and [references/classification-contract.md](references/classification-contract.md) before classifying any item. Keep an in-memory ledger of discovered paths, files actually read, and FlowPrint rules actually read.
5. Segment the completed work by independently reusable purpose and output before assigning any six-layer item:
   - one candidate: record `single_candidate`, select it deterministically, and continue;
   - two or more candidates: record every candidate with evidence and rationale, return `needs_workflow_selection`, leave `items` empty, and stop;
   - after the user explicitly selects one candidate: preserve the actual answer in `selection_confirmation`, mark `user_selected`, and classify only that candidate. Never copy excluded-workflow steps into the selected Skill.
6. Separate selected-workflow candidates into Core Workflow, Domain Knowledge, Profile, Run Parameters, Failure Lessons, and Permission Boundaries.
   Exclude current-session controls such as “only preview” or “do not compile”; obey them directly instead of persisting or re-confirming them. A durable Permission Boundary needs completed-task evidence or an existing FlowPrint contract; the current prompt alone is not enough.
7. Attach `workflow_candidate_id`, source evidence, rule hits, evidence state, impact, rationale, and `review_required` to every selected-workflow item. Never create or use a model confidence score.
8. Apply the risk gates in [references/classification-contract.md](references/classification-contract.md). High-impact, ambiguous, conflicting, vision-only Profile, and permission items must not pass silently.
9. Bind versioned or dated evidence to one cohort before extracting concrete values. Older or different-version evidence may support a labeled Failure Lesson but cannot fill missing current results.
10. Return a compact workflow-scope/classification preview followed by the required Evidence scope audit. Cite only visible statements or exact files recorded as actually read. Workflow selection is separate from the maximum of three item-review questions.
11. Stop after classification unless the user explicitly asks to compile a draft. Never treat classification or workflow selection as permission to install.

Use this user-facing shape:

```markdown
FlowPrint classification preview
Candidate workflow: <short name>
Evidence: goal <yes/no> · result <yes/no> · corrections <yes/no> · artifacts <yes/no>

Workflow scope
- <single candidate, or 2+ candidates requiring one explicit selection>

Core Workflow
- <general method>

Domain Knowledge
- <platform or format rule>

Profile
- <stable named-entity fact>

Run Parameters
- <changeable input>

Failure Lessons
- <abstracted prevention rule>

Permission Boundaries
- <external or irreversible action boundary>

Status: ready | needs_review | needs_workflow_selection
Review: <0–3 numbered questions with recommended answers>
Next capability: Skill compiler
```

If no completed task is visible, say that FlowPrint is installed but needs a completed task to extract. Ask for neither a transcript export nor a manual SOP.

## Evidence scope gate

Before any workspace discovery, run:

```powershell
& <skill-root>\scripts\run_flowprint.ps1 scope
```

On non-Windows hosts:

```bash
python3 scripts/check_evidence_scope.py
```

Resolve the script relative to this Skill directory. Do not list files before
the preflight returns. A blocked result forbids recursive discovery; continue
from visible conversation only or ask the user to open the actual project
directory. When the user explicitly names and authorizes an exact source, pass
each exact file with `--exact-source`; this permits only those files and never
their parent or siblings.

After a successful preflight, fix the allowed roots to:

1. the currently visible conversation;
2. the validated project working directory and its descendants, or only the exact user-named files returned by preflight;
3. this FlowPrint Skill directory, only for its own references and scripts.

Do not widen the search merely because evidence is missing. Unless the user explicitly names a source and authorizes its use for the current task, do not read or search:

- `MEMORY.md`, personal memory stores, or summaries from other sessions;
- shell history such as `~/.bash_history` or `~/.zsh_history`;
- global Codex config, auth state, environment variables, or marketplace/plugin inventories;
- the user's home directory, `~/Library`, unrelated repositories, or other plugins and Skills.

Never run home-wide `find`, `rg`, `rg --files`, `Get-ChildItem -Recurse`, or equivalent discovery to reconstruct a completed task. Treat Home, Downloads, Desktop, Documents, drive/filesystem roots, shared temporary roots, and installed plugin caches as unsafe roots even when one is the current working directory. Missing evidence remains `no`, `ambiguous`, or `needs_completed_task`; it is not permission to cross the evidence boundary. Do not deliberately invoke another Skill or plugin to help classify the task. If the host preloads an unrelated meta-Skill, do not use its contents as evidence.

Follow [references/evidence-audit-contract.md](references/evidence-audit-contract.md). A discovered filename is metadata, not evidence. Do not cite a contract, rule, script, or workspace file unless its contents were actually read in this run. If the final audit and tool trace disagree, remove or downgrade the claim, set `Status: needs_review`, and do not compile.

## Machine-readable validation

When the user asks to save, validate, or compile the classification, write `.flowprint/classification.json` using schema `0.4` from the contract reference. A multi-candidate routing document is valid for preview and audit but cannot compile. On Windows PowerShell, prefer the bundled launcher because a WindowsApps `python3` alias may exist but be unusable:

```powershell
& <skill-root>\scripts\run_flowprint.ps1 validate .flowprint\classification.json
& <skill-root>\scripts\run_flowprint.ps1 render .flowprint\classification.json
```

On other hosts, run:

```bash
python3 scripts/validate_classification.py .flowprint/classification.json
python3 scripts/render_classification.py .flowprint/classification.json
```

Resolve both script paths relative to this Skill directory when invoking from another working directory. A validation failure means `Needs Review`; never repair it by deleting evidence or weakening a risk gate.

## Node 5 draft compilation

Read [references/compiler-contract.md](references/compiler-contract.md) before compiling.

1. Compile only after the user explicitly asks to generate a Skill draft.
2. Use schema `0.4` for new classifications. Preserve workflow candidates, bind the selected candidate to the user's actual answer when selection was required, preserve review questions, and record actual answers in `gates.confirmations`. Never write `confirmed_by: user` without an explicit user response. Legacy schema `0.3` remains compiler-compatible but does not provide the multi-workflow gate.
3. Run `validate_classification.py` and stop on any nonzero exit. A chat preview is not a substitute for this execution.
4. Run the compiler with paths resolved relative to this Skill directory:

```powershell
& <skill-root>\scripts\run_flowprint.ps1 compile `
  .flowprint\classification.json `
  .flowprint\drafts\<skill-name> `
  --skill-name <skill-name>
```

On non-Windows hosts:

```bash
python3 scripts/compile_skill.py \
  .flowprint/classification.json \
  .flowprint/drafts/<skill-name> \
  --skill-name <skill-name>
```

5. Return the draft path, classification validator exit code, dependency manifest path, and `install_state`. Clearly say that no installation occurred.
6. Do not overwrite an existing draft. Propose a new draft name or ask the user whether to revise the source classification.

Compilation produces a non-installed draft only. Never call a plugin/Skill install command, copy into a personal Skills directory, submit, upload, publish, deploy, delete, or message as part of compilation.

## Changes and impact analysis

For a natural-language correction to an existing FlowPrint draft:

1. Apply the proposed change to a new classification candidate, not directly to generated files. Preserve the user's actual wording as evidence and never invent a confirmation.
2. Validate the candidate.
3. Run the deterministic revision preparation command:

```powershell
& <skill-root>\scripts\run_flowprint.ps1 revise `
  .flowprint\drafts\<skill-name>\flowprint-manifest.json `
  .flowprint\classification.next.json `
  .flowprint\revisions\<revision-name>
```

On non-Windows hosts:

```bash
python3 scripts/prepare_revision.py \
  .flowprint/drafts/<skill-name>/flowprint-manifest.json \
  .flowprint/classification.next.json \
  .flowprint/revisions/<revision-name>
```

4. Show changed item IDs, stale artifacts, invalidated confirmation IDs, Profile version impact, and required tests. Stop and ask only the questions listed in the revision plan. Core, high-impact, and workflow-name changes require full revalidation.
5. Only after the user explicitly answers, record the actual response in a separate confirmation JSON and run `confirm`. Do not treat the edit request itself as approval of the generated classification boundary unless the user explicitly accepts that boundary.
6. Compile `classification.ready.json` with its matching `revision-receipt.json` into a new draft directory. Never overwrite the base draft. Report the base and revised versions separately.

The deterministic compiler rejects missing, mismatched, stale, or tampered revision receipts. Compilation still does not authorize installation or any external action.

## Safety and scope boundary

Read and classify the current context only. Do not send, publish, delete, deploy, overwrite unrelated user work, or install generated Skills. Creating FlowPrint state and a draft under `.flowprint/` is allowed only when the user asks to save, validate, compile, or analyze an edit. A compiled draft is not an installed or field-tested Skill.
