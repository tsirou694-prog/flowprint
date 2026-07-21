# OpenAI Build Week Submission Checklist

Official deadline: **July 21, 2026 at 5:00 PM PT**  
Equivalent in Japan: **July 22, 2026 at 9:00 AM JST**

## P0 — Required to submit

| Item | Status | Next action |
|---|---|---|
| Working FlowPrint project | Ready with bounded evidence | Freeze one final demo version |
| Track | Chosen | Developer Tools |
| Devpost text description | Drafted | Edit for final tone and field limits |
| Public YouTube demo ≤3 minutes | Missing | Record, narrate, upload publicly |
| Audio explains project, Codex, and GPT-5.6 | Script drafted | Record English narration or include English translation |
| Code repository URL | Ready | https://github.com/tsirou694-prog/flowprint |
| README with setup and test path | Drafted | Verify from a clean clone |
| `/feedback` Codex Session ID | Missing | Run `/feedback` in the primary build thread and save the ID |
| Plugin installation instructions | Drafted | Test exact commands from clean extraction |
| Supported platforms | Drafted | Keep claims bounded to tested surfaces |
| Judge test without rebuilding | Ready in repository | Use included Node 8 fixtures and documented expected output |

Judge emails for a private repository:

```text
testing@devpost.com
build-week-event@openai.com
```

## P0 — Repository release hygiene

| Item | Status | Next action |
|---|---|---|
| License | Ready | MIT License, copyright 2026 SIROU Tang |
| Secrets and personal data scan | Findings confirmed | Sanitize personal Windows/macOS paths and login-status text in docs/evidence before publishing |
| Clean clone verification | Pending | Install and run judge path from a fresh directory |
| Final release archive hash | Existing for Node 8 package | Recompute if any repository file changes |
| Final plugin version consistency | Pending freeze | Match manifest, screenshots, video, and README |

## P1 — Strongly recommended before recording

- Record one latest-version Node 8 end-to-end host run from a narrow project root.
- Preserve the pre-selection preview showing two candidates.
- Show unresolved compilation failing with no output directory.
- Show one selected workflow compiling independently.
- Capture `flowprint-manifest.json` and `compile-record.json` fields used in the claim.
- Confirm the generated Skill bundle includes every referenced resource.
- Keep the held-out evaluation label at `N=1`.

## P1 — Devpost gallery

- [ ] Project thumbnail/logo
- [ ] Activation and scope-guard screenshot
- [ ] Workflow-selection screenshot
- [ ] Fail-closed compiler screenshot
- [ ] Compiled-draft screenshot
- [ ] Revision or held-out evaluation screenshot

## P2 — Later refinement, not a submission blocker

- Improve the generated Skill’s output templates.
- Add cross-character and cross-domain held-out evaluations.
- Add an evaluator independent from the generator.
- Improve desktop onboarding and distribution.
- Build a visual dependency and revision viewer.

## Submission copy controls

Before submitting, search all materials and remove or revise these unsupported phrases:

```text
proven
field-tested
always accurate
fully secure
works everywhere
validated end-to-end on every surface
```

Use bounded alternatives:

```text
passed 66 structural and regression tests; this does not establish generated-content quality
validated on the documented samples
tested on one held-out real task
accepted after two user-guided correction cycles
```

## Final five-minute check

1. Devpost project is in `Developer Tools`.
2. YouTube link is public and plays without login.
3. Video is no longer than three minutes and has audible narration.
4. Repository link opens for judges.
5. README installation commands work from a clean clone.
6. `/feedback` Session ID is copied from the primary build thread.
7. The submitted version matches the video and screenshots.
8. No personal data, secret, or unsupported claim remains.
9. Submit before the deadline; do not rely on last-minute edits.
