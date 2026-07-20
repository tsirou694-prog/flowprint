# FlowPrint Node 7 — Revision Transaction Validation

## Candidate

- Plugin version: `0.1.0+codex.20260720111640`
- Validation date: 2026-07-20
- Scope: deterministic revision transaction and local structural safety

## Automated result

The complete suite passed: **51 tests, 0 failures**.

Node 7 contributes ten revision integration tests covering:

1. high-impact Profile edit invalidates prior confirmations;
2. low-impact parameter edit preserves unrelated review confirmations but still requires overall revision acceptance;
3. incomplete confirmation fails closed;
4. missing receipt fails closed;
5. classification mutation after confirmation fails closed;
6. receipt mutation fails closed;
7. base manifest mutation invalidates the prepared revision;
8. no-op revision creates no revision directory;
9. workflow-name-only change is tracked as a document-level full revalidation;
10. successful recompilation preserves the base draft and emits a new Profile version and revision metadata.

The full suite also reran all Node 4 classification, Node 5 compiler, and Node 6 evidence-scope tests.

## Structural validators

- FlowPrint full Python suite: pass
- Python bytecode compilation for all packaged scripts: pass
- Agent Skill quick structure validator: pass
- Codex plugin structure validator: pass

## Evidence strength

This result supports the following bounded statement:

> In the tested fixtures, FlowPrint's revision transaction deterministically invalidates affected confirmations, binds fresh user confirmation to one revision, rejects missing or altered receipts, preserves the base draft, and emits a separately versioned non-installed draft.

It does not yet support these claims:

- arbitrary natural-language corrections are always interpreted correctly;
- the current candidate has completed a real Windows or macOS Codex CLI revision transaction;
- the generated workflow is useful on a second real task;
- the Skill is Field-tested;
- ChatGPT GUI distribution is supported.

## Windows host validation result

The bounded Windows test passed on a logged-in Codex CLI using plugin version `0.1.0+codex.20260720111640`:

- the current candidate compiled the confirmed base fixture successfully;
- a natural-language Profile correction produced one changed item, stale artifacts, two invalidated confirmations, and full revalidation;
- the revision stopped at `needs_confirmation` without creating a ready classification or receipt;
- the first confirmation attempt was started from the broad `Downloads` root and was correctly blocked before discovery or writes;
- after restarting from the exact project root, explicit user confirmation finalized the same revision;
- compilation without `--revision-receipt` exited nonzero at `revision_receipt` and left no output directory;
- compilation with the matching receipt succeeded to a new path;
- the base manifest hash remained `ECEF011C30D13D8432F1123626AA00067C9CD5AD6BCCEC67A2B9051D0E757DEA` before and after;
- Profile version advanced from `1` to `2`;
- `install_state` remained `not_authorized`, while installation and external-action records remained false.

Node 7 may therefore be described as **revision transaction validated in the tested automated fixtures and one real Windows Codex CLI workflow**. It must not be generalized into statistical natural-language accuracy, cross-platform revision validation, or field-tested business usefulness.
