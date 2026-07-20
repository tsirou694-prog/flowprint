# FlowPrint Prove Report — Held-out Task N=1

## 1. Result

FlowPrint is **Tested on 1 held-out real task**. It is not Field-tested.

The generated Skill improved compliance with the character's structural identity boundary, but did not win the first-pass comparison on every quality dimension. User feedback and two correction cycles were required before final acceptance.

## 2. Held-out task

The user requested a static Chinese sticker pack based on a new “Laosan tangyuan avatar” reference image.

Frozen brief:

- eight static stickers;
- exact texts: 收到、好滴、谢谢、辛苦啦、哈哈哈、让我想想、不愧是我、晚安;
- same reference image and same generation tool for both arms;
- one generation attempt per arm before user review;
- final target: independent 240 × 240 transparent PNG files.

This is a different asset form from the source task: a round head-only static text pack rather than a full-body animated sticker workflow. It remains the same named character, so it does not test cross-character Profile isolation.

## 3. Blind A/B protocol

The user saw only labels A and B before judging.

- Arm A used the FlowPrint-generated workflow constraints: identity consistency, no invented anatomy, expression-to-text mapping, small-size text legibility, clean export edges, and explicit permission boundaries.
- Arm B used only the frozen user brief and reference image.
- Both arms used the same image-generation capability and were generated once without repair before the blind review.

Because both arms used the same model family and image generator, this is not an independent-model evaluation. Blinding reduces presentation bias but does not eliminate same-source model bias.

## 4. First-pass findings

| Dimension | Arm A: with Skill | Arm B: baseline |
|---|---|---|
| Eight exact texts | Pass | Pass |
| Character resemblance | Strong | Strong |
| No invented limbs | Pass | Fail |
| Expression diversity | Partial: items 1 and 2 too similar | Strong |
| User first-pass acceptance | Not accepted | Not accepted |

The user's blind feedback was:

- A was lively overall, but the first two expressions were too similar.
- B gave all eight stickers distinct expressions, but the generated hands were structurally wrong because the avatar is a tangyuan version of Laosan; the tangyuan itself cannot become hands.

After the blind feedback, the assignments were revealed. A was the with-Skill arm; B was the baseline.

## 5. What the Skill improved

The Skill prevented the baseline's most serious identity error: adding hand anatomy to an avatar whose round tangyuan form is the complete body boundary.

This supports a bounded claim:

> In this task, the generated Skill improved adherence to an identity-defining structural constraint.

It does not support the stronger claim that the Skill produced the best overall first-pass image. Its conservative anatomy constraint coincided with insufficient differentiation between two expressions.

## 6. Corrections and decontextualization

User-specific Profile fact:

> The Laosan tangyuan avatar is one integrated round avatar form and must not grow hands, feet, a tail, or other limb extensions.

Reusable Failure Lesson:

> Do not invent anatomy to increase expressiveness. Use eyes, eyebrows, mouth shape, ear angle, head tilt, and external symbols when the established character structure does not include limbs.

Reusable quality rule:

> Expression diversity must be evaluated from the core facial structure, not only from labels or small decorative icons.

The concrete tangyuan anatomy remains bound to this named avatar Profile and must not be generalized to all corgis or all sticker characters.

## 7. Revision sequence

1. A/B review identified baseline anatomy contamination and insufficient differentiation between 收到 and 好滴.
2. Revision C preserved the no-limb boundary and differentiated the first two expressions.
3. The user identified a second collision: 收到 and 辛苦啦 still shared a similar open-eye smile structure.
4. Revision D changed only 辛苦啦 to a distinctly sympathetic expression.
5. The user accepted D as the final direction.

The accepted sheet was converted into eight independent transparent PNGs. QA confirmed 240 × 240 dimensions, 8-bit RGBA, and transparent corner pixels for every file.

## 8. Status

| Field | Value |
|---|---|
| Held-out tasks | `N=1` |
| Real user task | yes |
| Blind first-pass comparison | yes |
| Deterministic checks | text count, text accuracy, dimensions, alpha, corner transparency |
| User acceptance | yes, after two correction cycles |
| Cross-character validation | no |
| Independent model evaluator | no |
| Field-tested | no |

Recommended product label:

> Tested on 1 held-out task. Accepted after 2 user-guided correction cycles. Validate on another real character before treating the workflow as Field-tested.

## 9. Next evidence needed

Before upgrading the status beyond N=1:

1. run the workflow on a different named character with a separate Profile;
2. verify that Laosan's tangyuan anatomy does not leak into that character;
3. repeat the blind baseline/with-Skill comparison;
4. add an evaluator that is independent of the generator when available;
5. keep the user's final acceptance as the authority for usefulness.
