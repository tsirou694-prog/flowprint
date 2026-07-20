# FlowPrint Draft Compiler Contract

Use this reference for Node 5 compilation and Node 7 revision transactions.

## Input gate

- New input is `.flowprint/classification.json` with `schema_version: 0.4`; legacy confirmed `0.3` remains accepted for backward compatibility.
- Schema `0.4` must resolve `workflow.scope` to `single_candidate` or `user_selected`. A valid `needs_workflow_selection` routing document is rejected by the compiler at the `workflow_selection` gate.
- When multiple candidates exist, `user_selected` must include a user-bound selection record, the selected candidate name must match, and every classification item must reference only that candidate.
- `gates.decision` is `ready` only when explicit user confirmations cover every review item.
- The compiler itself runs `validate_classification.py` as a subprocess and checks its exit code.
- Missing validator, invalid JSON, nonzero validation, `needs_review`, or unsupported schema fails closed.
- On Windows, use `scripts/run_flowprint.ps1`; it discovers a working interpreter rather than trusting a possibly broken WindowsApps alias. It never installs Python.

Do not copy a chat preview into a draft while skipping the machine-readable gate.

## Draft output

The compiler writes to a private staging directory, validates the complete draft, and publishes the requested output directory only after preflight passes. A rejected build leaves no requested output directory.

Generated structure:

```text
<skill-name>/
├── SKILL.md
├── agents/openai.yaml
├── profiles/default.json
├── references/
│   ├── domain-knowledge.md
│   ├── run-parameters.md
│   ├── failure-lessons.md
│   └── permission-boundaries.md
├── flowprint-manifest.json
└── compile-record.json
```

`flowprint-manifest.json` records classification item fingerprints, Profile version, item-to-artifact edges, artifact hashes, validation requirements, and separate draft/install/external-action permission states.
For schema `0.4`, it also records candidate IDs, the selected workflow ID, selection status, selection binding state, and a workflow-definition fingerprint used by revision impact analysis.

## Permission states

- `compile_state: draft` means files were generated.
- `install_state: not_authorized` means the draft is not installed or active.
- `installation_authorized: false` is not changed by draft generation.
- `external_actions_authorized: false` is not changed by classification, confirmation, compilation, or installation.

Only a separate, explicit user request may begin a later installation step. Authorization to install never authorizes submission, upload, publication, deployment, messaging, deletion, or another external action.

## Impact rules

Edits are made to a new classification candidate. `analyze_impact.py` compares item fingerprints with the manifest and returns:

- changed, added, and removed item IDs;
- stale generated artifacts;
- whether the Profile is stale;
- whether full revalidation is required;
- tests to rerun.

Any Core change, high-impact change, or removal of such an item requires full revalidation. The deterministic diff reports impact; it does not decide that a natural-language edit is semantically harmless.

## Revision transaction

Natural-language interpretation produces a new classification candidate; it never edits generated files. From that point onward, the recovery path is deterministic and fail-closed:

1. `prepare_revision.py` validates the candidate and compares it with the base manifest.
2. It creates a new revision directory containing `classification.review.json`, `impact-report.json`, and `revision-plan.json`. It never changes the base draft.
3. Core, high-impact, and workflow-name changes invalidate all prior review-question confirmations. Lower-risk changes invalidate only questions whose item IDs are affected. Every non-empty revision still requires one explicit overall user confirmation.
4. `finalize_revision.py` accepts a confirmation record only when its `revision_id`, question IDs, and item IDs exactly match the prepared plan. It records the user's actual response and emits `classification.ready.json` plus `revision-receipt.json` atomically.
5. `compile_skill.py` rejects a revision classification unless `--revision-receipt` is supplied and the receipt matches the classification hash, revision plan, confirmation record, and unchanged base manifest.
6. The revised draft must use a new output directory. The base draft is immutable. A Profile change increments the Profile version; unrelated changes preserve it.

Example preparation:

```powershell
& <skill-root>\scripts\run_flowprint.ps1 revise `
  .flowprint\drafts\<base>\flowprint-manifest.json `
  .flowprint\classification.next.json `
  .flowprint\revisions\<revision-id>
```

The confirmation input is a machine-readable record created only after an explicit user response:

```json
{
  "revision_id": "rev-...",
  "confirmed_by": "user",
  "accepted": true,
  "answer": "The user's actual overall response",
  "questions": [
    {
      "question_id": "question-1",
      "item_ids": ["item-profile-tail"],
      "confirmed_by": "user",
      "accepted": true,
      "answer": "The user's actual answer"
    }
  ]
}
```

Then finalize and compile to a new draft:

```powershell
& <skill-root>\scripts\run_flowprint.ps1 confirm `
  .flowprint\revisions\<revision-id> `
  .flowprint\revision-confirmation.json

& <skill-root>\scripts\run_flowprint.ps1 compile `
  .flowprint\revisions\<revision-id>\classification.ready.json `
  .flowprint\drafts\<new-draft-name> `
  --skill-name <skill-name> `
  --revision-receipt .flowprint\revisions\<revision-id>\revision-receipt.json
```

Never infer `confirmed_by: user`, silently upgrade an old classification, reuse a receipt for another revision, modify the base draft, or describe stale artifacts as current before the revised draft passes preflight.

## Validation claims

`validate_generated_skill.py` is a FlowPrint structural preflight, not official marketplace certification. During development, also run the available official Skill structure validator. Do not describe either check as proof that the workflow is useful or generally reliable.

Workflow candidate detection still relies on model language understanding. The deterministic gate prevents a declared multi-workflow result from compiling silently; it cannot prove that the model enumerated every workflow present in the evidence. Keep this residual risk explicit in evaluation reports.
