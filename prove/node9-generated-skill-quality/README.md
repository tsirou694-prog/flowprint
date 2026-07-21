# Node 9: Generated Skill Execution Contract

This comparison uses the exact same confirmed classification input and Skill name before and after the P0 compiler-template upgrade.

## Fixed inputs

- Classification: `tests/fixtures/classification/yueyang-trip-selected-v0.4.json`
- Classification SHA-256: `4d544d85349f4bdc3a0b39b0424423f92588ddd2e93993fb35543a055d020308`
- Skill name: `plan-family-trip`

## Artifacts

| Artifact | SHA-256 |
|---|---|
| `SKILL-before-p0.md` | `1a0a60e0d7a5f9ee3cbc021c201ecb705e4d15dfc9fd04b1f743a94b13cb0061` |
| `SKILL-after-p0.md` | `3fb5964856c06c04b4d9a77b4e73ad9d846edaec0dfd05ffbf2413b38c95cfc4` |

## Observable difference

| Concern | Before P0 | After P0 |
|---|---|---|
| Inputs | Implicit inside one workflow sentence | Dedicated input collection grounded in Core and Run Parameters |
| Missing information | No policy | Blocking questions, disclosed assumptions, and `not verified` handling |
| Workflow | Two unreferenced summary steps | Ordered steps linked to classification item IDs |
| Output | No output contract | Primary deliverable plus required result, verification, and quality-check sections |
| Quality | One compressed sentence in source data was not surfaced | Domain rules and failure-derived must-pass checks are separated and linked to item IDs |
| Permissions | Generic safety paragraph only | Workflow-specific permission item plus the generic fail-closed boundary |

The new generated-draft validator also rejects missing or ungrounded execution-contract sections and checks that the dependency graph includes the items rendered into `SKILL.md`.

## Claim boundary

This proves a deterministic compiler and validator change for one fixed fixture. It does not prove that the generated travel workflow is field-tested, that its content is optimal, or that workflow discovery is statistically accurate.
