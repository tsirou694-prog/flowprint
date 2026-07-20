# FlowPrint Classification Contract

Use this contract when saving or validating `.flowprint/classification.json`.

## Root object

Required fields:

- `schema_version`: use `0.4` for new classifications. Legacy `0.2` and `0.3` remain readable for regression compatibility but do not provide workflow selection.
- `workflow.scope`: candidate-workflow inventory and selection state.
- `workflow.candidate_name`: selected human-readable name; it is `null` while multiple candidates await selection.
- `workflow.trigger`: reusable trigger summary, examples, and exclusions; required only after scope resolution.
- `source.type`: `current_task`.
- `source.raw_transcript_stored`: always `false`.
- `evidence_inventory`: booleans for `goal`, `result`, `corrections`, and `artifacts`.
- `items`: non-empty classification item array.
- `gates`: derived review decision and questions.

## Workflow scope gate (schema 0.4)

Segment independently reusable purposes and outputs before creating six-layer items. Use:

```json
{
  "workflow": {
    "candidate_name": null,
    "scope": {
      "status": "needs_user_selection",
      "candidates": [
        {
          "id": "trip-planning",
          "name": "Mixed-age family trip planning",
          "evidence": [
            {
              "source_type": "final_artifact",
              "locator": "conversation: accepted itinerary"
            }
          ],
          "rationale": "Produces an operational itinerary."
        },
        {
          "id": "trip-poster",
          "name": "Family trip invitation poster",
          "evidence": [
            {
              "source_type": "final_artifact",
              "locator": "conversation: accepted poster"
            }
          ],
          "rationale": "Produces a visual invitation with a different quality contract."
        }
      ],
      "selected_candidate_id": null,
      "selection_confirmation": null
    }
  },
  "items": [],
  "gates": {
    "decision": "needs_workflow_selection",
    "review_item_ids": [],
    "questions": [],
    "confirmations": []
  }
}
```

Allowed scope states:

- `single_candidate`: exactly one candidate; select it without inventing user confirmation.
- `needs_user_selection`: at least two candidates; leave the selected ID, candidate name, trigger, and items empty and stop.
- `user_selected`: at least two candidates plus an explicit user-bound `selection_confirmation` containing the selected ID, `confirmed_by: user`, `accepted: true`, and the user's actual answer.

After scope resolution, `workflow.candidate_name` must match the selected candidate and `workflow.trigger` must contain:

```json
{
  "summary": "Plan practical short family road trips for mixed-age groups.",
  "when_to_use": ["亲子游规划", "带老人和孩子安排短途自驾"],
  "do_not_use": ["旅行邀请函或海报设计"]
}
```

Every schema `0.4` classification item must include `workflow_candidate_id` equal to the selected candidate. Excluded-workflow items are invalid even when their six-layer classification would otherwise be plausible.

## Classification item

Each item requires:

```json
{
  "id": "item-core-anatomy",
  "workflow_candidate_id": "sticker-production",
  "statement": "Verify identity-defining anatomy against the active profile.",
  "layer": "core",
  "evidence": [
    {
      "source_type": "user_correction",
      "locator": "conversation: final character correction",
      "quote": "注意老三无尾或短尾的特征"
    }
  ],
  "rule_hits": ["R4", "R5"],
  "evidence_state": "supported",
  "impact": "medium",
  "review_required": false,
  "rationale": "The check generalizes while the concrete anatomy stays in Profile."
}
```

Allowed `layer` values:

- `core`
- `domain`
- `profile`
- `run_parameter`
- `failure_lesson`
- `permission_boundary`

Allowed `source_type` values:

- `user_instruction`
- `user_correction`
- `final_artifact`
- `workspace_file`
- `test_result`
- `visual_observation`
- `model_inference`

Allowed evidence states are `supported`, `ambiguous`, and `conflicting`. Allowed impacts are `low`, `medium`, and `high`.

A `failure_lesson` item also requires `abstracted_rule`. A `permission_boundary` must be high impact and require review.

## Deterministic risk gates

The validator enforces:

1. Numeric confidence, probability, or certainty fields are forbidden anywhere in the document.
2. Every item has at least one source and one enumerated rule hit.
3. `ambiguous`, `conflicting`, and `high`-impact items require review.
4. A `core` item cannot claim R1 named-entity stability.
5. A Profile supported only by visual observation/model inference requires review.
6. Permission boundaries are high impact and require review.
7. `gates.review_item_ids` exactly matches the items marked `review_required`.
8. `gates.decision` is `needs_review` when review items exist, otherwise `ready`.
9. The review card contains at most three questions.
10. Raw transcript storage remains false.
11. Schema `0.4` enumerates workflow candidates before six-layer classification.
12. Multiple candidates without an explicit user selection remain `needs_workflow_selection`, contain no classification items, and cannot compile.
13. A user-selected candidate is bound to the user's actual confirmation and every item is bound to that selected candidate.
14. Resolved schema `0.4` workflows provide explicit trigger and exclusion metadata so the generated Skill does not rely on a circular description.

## Confirmed result for compilation

Schema `0.4` preserves the resolved workflow scope, every review question, and explicit user confirmation records. Legacy schema `0.3` keeps its earlier confirmation behavior but has no workflow-scope protection:

```json
{
  "decision": "ready",
  "review_item_ids": ["item-profile-tail", "item-failure-tail-scope"],
  "questions": [
    {
      "id": "question-1",
      "item_ids": ["item-profile-tail", "item-failure-tail-scope"],
      "prompt": "Keep the tail rule only in the Laosan Profile?",
      "recommended_answer": "Yes — do not place it in Core."
    }
  ],
  "confirmations": [
    {
      "id": "confirmation-1",
      "question_id": "question-1",
      "item_ids": ["item-profile-tail", "item-failure-tail-scope"],
      "confirmed_by": "user",
      "accepted": true,
      "answer": "确认，只属于老三。"
    }
  ]
}
```

The validator derives `ready` only when accepted user confirmations cover every review item. A model assertion, missing question link, partial coverage, or `confirmed_by` value other than `user` cannot unlock compilation.

## Review question

```json
{
  "id": "question-1",
  "item_ids": ["item-profile-tail"],
  "prompt": "Keep the tail rule only in the Laosan Profile?",
  "recommended_answer": "Yes — do not place it in Core."
}
```

Questions must refer to review item IDs. Combine related items when more than three review items exist; never silently drop a high-impact item.

## User-facing rendering

Show the six layers, then status and review card. Evidence details can be compact, but the user must be able to see why an item was classified and which source supports it. Offer `接受全部` plus numbered overrides such as `2=Run Parameter`.
