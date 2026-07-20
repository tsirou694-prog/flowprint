# FlowPrint Node 8 — Workflow Selection Gate

## Outcome

Node 8 adds a fail-closed boundary between completed-task evidence and six-layer classification. A conversation that contains multiple independently reusable purposes or outputs no longer compiles into one broad Skill by default.

The implementation preserves legacy schema `0.2/0.3` behavior and introduces schema `0.4` for new workflow-scoped classifications.

## Why this node exists

The Yueyang family-trip test contained two accepted deliverables:

1. a mixed-age family trip-planning workflow;
2. a family invitation/poster workflow.

The previous schema exposed only `workflow.candidate_name`, so it could not represent “two candidates, no user selection.” The generated draft merged itinerary planning with visual-publishing steps. That result is evidence of a missing product state, not proof that the six-layer classifier alone can solve workflow segmentation.

## New state model

Schema `0.4` adds `workflow.scope`:

- `single_candidate`: exactly one candidate; classification may continue without a fabricated selection confirmation.
- `needs_user_selection`: two or more candidates; `candidate_name`, trigger metadata, and `items` remain empty.
- `user_selected`: two or more candidates plus an explicit user-bound selection record.

Every schema `0.4` item must contain `workflow_candidate_id` equal to the selected candidate.

## Deterministic gates

The validator rejects:

- multiple candidates mislabeled as `single_candidate`;
- a model-authored selection confirmation;
- a selected name that does not match the selected candidate ID;
- a classification item bound to an excluded workflow;
- a multi-candidate routing document containing premature six-layer items.

The compiler accepts legacy confirmed `0.3` and resolved `0.4` inputs. It rejects a valid unresolved `0.4` routing document with:

```json
{
  "status": "rejected",
  "gate": "workflow_selection"
}
```

A rejected build leaves no requested output directory.

## Generated Skill corrections

Node 8 also removes two forms of compiler-template leakage found in the same test:

- Generated descriptions no longer claim that the workflow is “validated.” Schema `0.4` supplies explicit trigger examples and exclusions.
- The generated Safety boundary no longer hardcodes installation and deployment language. It refers to the selected workflow's own permission-boundary reference.

## Dependency and revision behavior

Generated manifests record:

- candidate IDs;
- selected candidate ID;
- scope status;
- whether user selection is bound;
- a workflow scope/trigger fingerprint.

Changing workflow scope or trigger metadata marks `SKILL.md` and `agents/openai.yaml` stale and requires full revalidation. The base draft remains immutable under the Node 7 receipt transaction.

## Automated evidence

The repository test suite covers:

- unresolved Yueyang multi-workflow routing;
- explicit selection of the trip-planning workflow;
- explicit selection of the invitation/poster workflow;
- one-candidate schema `0.4` behavior;
- legacy `0.2/0.3` compatibility;
- model self-selection rejection;
- excluded-workflow item rejection;
- compiler fail-closed behavior;
- workflow trigger revision impact;
- all earlier evidence-scope, compiler, and revision tests.

## Known residual risk

Workflow discovery still depends on model language understanding. The deterministic gate guarantees that a **declared** multi-workflow result cannot compile silently; it cannot prove that the model found every workflow in the evidence. Evaluation language must preserve this limitation.

## Current status

Implementation and local automated validation are complete. Writable Windows Codex CLI and ChatGPT desktop/Work runtime validation must be recorded separately before claiming cross-surface completion.
