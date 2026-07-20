# FlowPrint Node 7 — Revision Transaction Design

## Outcome

Node 7 closes the previously unverified recovery path:

> natural-language correction → deterministic impact analysis → stale confirmation invalidation → explicit user reconfirmation → new non-overwriting draft

The language model may interpret the user's correction into `classification.next.json`; it does not decide whether an old confirmation remains valid and cannot directly edit a generated Skill.

## State machine

| State | Required evidence | Allowed next action | Forbidden shortcut |
|---|---|---|---|
| Compiled base | Existing draft and manifest | Prepare candidate revision | Editing generated files |
| Candidate | Valid classification candidate | Run `revise` | Treat old confirmation as current |
| Needs confirmation | Revision plan and impact report | Record explicit user response | Compile without receipt |
| Confirmed revision | Hash-bound classification and receipt | Compile to a new path | Overwrite base draft |
| Revised draft | Structural preflight passed | Separate future install decision | Infer install or publish authority |

## Deterministic gates

### Revision preparation

`prepare_revision.py`:

- runs the real classification validator;
- compares item fingerprints and document-level workflow name;
- rejects no-op revisions without creating a directory;
- binds the revision to the base manifest hash;
- marks affected generated artifacts stale;
- invalidates all review confirmations for Core, high-impact, or workflow-name changes;
- otherwise invalidates only questions linked to affected review items;
- emits a new revision directory atomically.

### Confirmation finalization

`finalize_revision.py`:

- requires one explicit overall user acceptance for every revision;
- requires an exact answer set for every question named by the revision plan;
- rejects missing, extra, wrong-revision, wrong-item, or non-user confirmations;
- rejects if the review classification or base manifest changed after preparation;
- writes the ready classification and receipt as one fail-closed commit;
- never authorizes installation or external actions.

### Revision compilation

`compile_skill.py --revision-receipt`:

- binds the ready classification to its receipt hash;
- checks the revision plan and user confirmation files are unchanged;
- rechecks the base manifest hash;
- refuses compilation without a receipt;
- refuses tampered inputs;
- writes a new draft version such as `0.1.0-draft.r1`;
- increments Profile version only when Profile dependencies changed;
- records revision gate results in `compile-record.json`;
- preserves `install_state: not_authorized` and both external-action flags as false.

## Claims supported by automated tests

The integration suite directly exercises:

- Profile edit → full revalidation → all prior review confirmations stale;
- low-impact Run Parameter edit → prior unrelated confirmations retained, but overall revision confirmation still required;
- missing or incomplete confirmation → no ready classification or receipt;
- missing revision receipt → no revised draft;
- classification tampering after confirmation → rejected;
- receipt tampering → rejected;
- changed base manifest → rejected;
- no-op revision → no revision directory;
- workflow-name-only change → document-level impact and full revalidation;
- successful revision → old draft unchanged, new draft created, Profile version incremented when appropriate;
- installation and external-action permissions remain false.

These tests prove the transaction and its structural safety properties in the tested fixtures. They do not prove that a language model will interpret every natural-language correction correctly or that a generated Skill is useful in real work.

## Known limitations

- Natural-language interpretation remains model-mediated and can misclassify the user's intended edit before the deterministic transaction begins.
- Confirmation records are local audit records, not cryptographic signatures or identity attestations.
- File hashes detect accidental or out-of-band mutation but do not defend against a malicious process that can rewrite every local record consistently.
- Field-tested usefulness, second-task reuse, and independent evaluation belong to the next Node 7 Prove/Field-test phase.

## Formal demo acceptance criteria

Before this Node 7 slice is called host-validated, one real Codex CLI session on the current candidate version must demonstrate:

1. compile a base draft from the confirmed schema `0.3` fixture;
2. prepare one Profile correction and show stale artifacts plus invalidated confirmations;
3. attempt compilation without a receipt and observe fail-closed rejection with no output;
4. record an explicit user confirmation tied to the shown revision ID;
5. finalize and compile to a new draft path;
6. verify the base manifest hash is unchanged;
7. verify revised Profile version, manifest revision metadata, compile record, and permission flags;
8. perform no installation, submission, upload, publication, or other external action.
