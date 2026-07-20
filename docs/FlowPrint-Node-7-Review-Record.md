# FlowPrint Node 7 Review Record

## 1. Review conclusion

Node 7 is accepted with bounded claims.

The revision mechanism has been validated through both automated integration tests and one real Windows Codex CLI transaction. The verified path is:

> natural-language correction → deterministic impact plan → stale confirmation invalidation → explicit user reconfirmation → receipt-gated non-overwriting recompilation

This is an engineering acceptance result for the tested transaction. It is not a claim that arbitrary natural-language corrections are always classified correctly, nor that the compiled business workflow is already Field-tested.

## 2. Candidate under test

| Field | Value |
|---|---|
| Plugin | FlowPrint |
| Version | `0.1.0+codex.20260720111640` |
| Host | Windows Codex CLI |
| Authentication | Logged in with ChatGPT |
| Project root | Narrow FlowPrint project directory under Downloads |
| Test workflow | Laosan sticker workflow Profile correction |

## 3. Automated evidence

The packaged candidate was extracted into a clean temporary directory and passed:

- 51 Python tests with zero failures;
- Python bytecode compilation for all packaged scripts;
- Agent Skill quick structural validation;
- Codex plugin structural validation.

Ten Node 7 integration tests cover high- and low-impact edits, incomplete confirmation, missing receipt, classification mutation, receipt mutation, changed base manifest, no-op revisions, document-level workflow-name changes, Profile versioning, and non-overwriting compilation.

## 4. Package and installation evidence

The user independently verified the downloaded package:

- package SHA-256: `7A5E7D644A41BCDB2F9A0091E5CF73B99B265098B66C29C28AB6303866F1A747`;
- hash match: true;
- manifest version: `0.1.0+codex.20260720111640`;
- marketplace root changed to the new extracted project;
- plugin installed and enabled at the same version.

No prior package result was substituted for the current candidate.

## 5. Current-version base compilation

The current candidate compiled the confirmed schema `0.3` fixture on the real Windows host:

| Check | Result |
|---|---|
| Classification validator exit | `0` |
| Compiler exit | `0` |
| `SKILL.md` | exists |
| `flowprint-manifest.json` | exists |
| `compile-record.json` | exists |
| Base Profile version | `1` |
| `install_state` | `not_authorized` |
| `install_performed` | `false` |
| `external_action_performed` | `false` |

Immutable base manifest SHA-256:

`ECEF011C30D13D8432F1123626AA00067C9CD5AD6BCCEC67A2B9051D0E757DEA`

## 6. Revision preparation evidence

The user supplied the natural-language correction that Laosan should be represented as having no visible tail, replacing the prior “no visible tail or very short tail” formulation.

The real FlowPrint revision preparation returned:

| Field | Result |
|---|---|
| Scope preflight | `allowed_project_scope` |
| Classification validator exit | `0` |
| Revise exit | `0` |
| Revision ID | `rev-9edc5bdd9fb948ee` |
| Changed items | `item-profile-tail` |
| Stale artifacts | `SKILL.md`, `profiles/default.json` |
| Stale confirmations | `confirmation-1`, `confirmation-2` |
| Required questions | `question-1`, `question-2` |
| Full revalidation | `true` |
| State | `needs_confirmation` |

`classification.review.json`, `impact-report.json`, and `revision-plan.json` existed. `classification.ready.json` and `revision-receipt.json` did not yet exist. This demonstrates that the system did not silently reuse earlier confirmations or compile before the user reconfirmed the changed boundary.

## 7. Broad-root safety result

The first confirmation attempt began from `C:\Users\demo-user\Downloads`, not from the project root. FlowPrint returned a blocked scope result and did not search Downloads for the missing project.

It created no confirmation JSON, did not finalize or compile, and performed no installation or external action.

This is recorded as a passed fail-closed boundary test, not discarded as operator noise. It also demonstrates a usability limitation: users must launch Codex from the actual project root or provide exact authorized sources.

## 8. Confirmation and receipt-gated compilation

After restarting Codex from the exact project root, the user explicitly accepted revision `rev-9edc5bdd9fb948ee` and both required question recommendations.

| Check | Result |
|---|---|
| Confirm exit | `0` |
| Confirm status | `confirmed_revision` |
| Compile without receipt | exit `1`, gate `revision_receipt` |
| Rejected output directory | absent |
| Compile with correct receipt | exit `0`, `compiled_draft` |
| Base manifest before/after | identical |
| Old Profile version | `1` |
| New Profile version | `2` |
| Revision sequence | `1` |
| New draft path | separate from base |
| `install_state` | `not_authorized` |
| `install_performed` | `false` |
| `external_action_performed` | `false` |

The revised draft contains `SKILL.md`, `flowprint-manifest.json`, and `compile-record.json`. The base draft was not overwritten.

## 9. What this proves

Within the tested fixture and Windows host workflow, the evidence supports these claims:

- a high-impact Profile correction invalidates prior confirmations;
- deterministic impact analysis identifies affected generated artifacts;
- the workflow stops until a user explicitly confirms the prepared revision;
- the ready classification is bound to one revision receipt;
- missing receipt compilation fails closed without a partial output;
- correct receipt compilation creates a separately versioned draft;
- Profile dependency version increments when the Profile changes;
- the base draft remains immutable;
- compilation does not imply installation or external-action authorization;
- broad personal roots are blocked before evidence discovery.

## 10. What this does not prove

Node 7 does not prove:

- statistical accuracy across diverse natural-language corrections;
- macOS execution of the new revision transaction;
- usefulness of the generated Skill on a second different-object task;
- independent evaluator agreement or absence of same-model bias;
- Field-tested status;
- ordinary ChatGPT web or ChatGPT GUI installation and distribution;
- cryptographic user identity or tamper resistance against a malicious process able to rewrite every local record coherently.

## 11. Recommended external wording

Use:

> FlowPrint's revision transaction passed 51 automated tests and one real Windows Codex CLI workflow. In that tested workflow, a high-impact correction invalidated stale confirmations, required explicit user reconfirmation, rejected compilation without a matching receipt, preserved the base draft, and produced a separately versioned non-installed draft.

Do not use:

> FlowPrint automatically understands and safely updates any workflow on Windows and macOS.

The second sentence exceeds the evidence in natural-language accuracy, platform coverage, and general reliability.

## 12. Residual risks and next node

The next phase is Prove/Field-test, not another repetition of installation or schema-gate testing. It should answer:

1. Does the compiled Skill improve a second real task involving a different object?
2. Can deterministic checks separate structural compliance from business usefulness?
3. Can blinded evaluation plus explicit user acceptance reduce same-model self-scoring bias?
4. How should successful uses accumulate from `Tested on N=1` toward a transparent Field-tested history?

Until those questions are tested, the generated Skill remains a validated draft rather than a Field-tested workflow.
