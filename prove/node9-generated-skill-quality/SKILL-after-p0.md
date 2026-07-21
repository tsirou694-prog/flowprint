---
name: plan-family-trip
description: "Plan practical 1–3 day family self-drive trips for mixed-age groups, especially trips with elders and children. Use when the user asks for: 亲子游规划; 家庭短途自驾; 带老人和孩子安排行程. Do not use for: 旅行邀请函、海报或其他视觉设计."
---

# 适老亲子家庭短途旅行规划

## Inputs to collect

- Use this workflow requirement to identify the information that must be known before execution: Start by fixing the trip purpose, traveler composition, dates, transport, lodging, fixed commitments, pace, and non-negotiable constraints. (`item-core-brief`)
- Confirm or replace these source-task values for the current run: This run used July 18–19, eleven travelers, self-driving from Changsha County, a booked Yueyang guesthouse, and selected local stops. (`item-param-yueyang-run`)

## If information is missing

- Ask one compact batch of at most three questions only when the missing information would change the workflow, primary deliverable, safety, or permission boundary.
- For non-blocking gaps, continue with a reasonable assumption and disclose it under `Inputs and assumptions`.
- Verify time-sensitive facts required by the domain rules before presenting them as current. If verification is unavailable, label the value `not verified` instead of inventing certainty.

## Workflow

1. Start by fixing the trip purpose, traveler composition, dates, transport, lodging, fixed commitments, pace, and non-negotiable constraints. (`item-core-brief`)
2. Build each day around meals, check-in, rest, and booked anchors, then fit optional activities into the remaining travel-time and energy budget. (`item-core-energy-budget`)

## Output contract

- Primary deliverable: a complete `适老亲子家庭短途旅行规划` result.
- Include an `Inputs and assumptions` section that records confirmed parameters, defaults, and any explicit assumptions.
- Include a `Result` section that makes the selected workflow requirements observable:
  - Make this requirement observable in the result: Start by fixing the trip purpose, traveler composition, dates, transport, lodging, fixed commitments, pace, and non-negotiable constraints. (`item-core-brief`)
  - Make this requirement observable in the result: Build each day around meals, check-in, rest, and booked anchors, then fit optional activities into the remaining travel-time and energy budget. (`item-core-energy-budget`)
- Include a `Verification` section that reports each recorded domain rule as passed, failed, or not verified.
- Include a `Quality checks` section that reports each failure-derived acceptance check as passed or failed.

## Quality checks

### Domain rules

- Verify before delivery: Recheck weather, opening hours, ticket availability, travel time, and temporary restrictions before presenting them as current facts. (`item-domain-dynamic-data`)

### Must-pass acceptance checks

- Pass only if the result satisfies: Optimize the itinerary for group comfort and purpose before attraction count. (`item-failure-attraction-count`)

## Supporting files

- Read `references/domain-knowledge.md` before applying domain rules.
- Read `references/run-parameters.md` while collecting or reconfirming current inputs.
- Read `references/failure-lessons.md` before final quality assurance or recovery.
- Read `profiles/default.json` only after the named entity matches the request.
- Read `references/permission-boundaries.md` before any external, account-specific, or irreversible action.

## Permission boundary

- Preparing an itinerary does not authorize booking, payment, cancellation, or sending the plan to other people; obtain fresh authorization for each external action. (`item-permission-travel-actions`)

Preparing a result does not authorize an external, account-specific, or irreversible action. Before any action listed in `references/permission-boundaries.md`, obtain fresh and explicit authorization for that action. If authorization is absent or ambiguous, stop after preparing a preview.
