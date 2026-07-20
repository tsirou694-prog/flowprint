# FlowPrint Node 8 — Windows Runtime Acceptance

Run from the extracted `flowprint` project root after installing the updated local plugin. Use the installed cache path shown by `codex plugin list` for `$skillRoot`.

## 1. Resolve the installed runner

```powershell
$version = (
  Get-Content ".\plugins\flowprint\.codex-plugin\plugin.json" -Raw |
  ConvertFrom-Json
).version

$skillRoot = "$HOME\.codex\plugins\cache\flowprint-dev\flowprint\$version\skills\flowprint"
$runner = Join-Path $skillRoot "scripts\run_flowprint.ps1"

[pscustomobject]@{
  Version = $version
  RunnerExists = Test-Path -LiteralPath $runner
}
```

Expected: `RunnerExists = True`.

## 2. Validate and render unresolved multi-workflow input

```powershell
& $runner validate ".\tests\fixtures\classification\yueyang-needs-selection-v0.4.json"
$routingValidateExit = $LASTEXITCODE

& $runner render ".\tests\fixtures\classification\yueyang-needs-selection-v0.4.json"
$routingRenderExit = $LASTEXITCODE
```

Expected:

- both exits are `0`;
- rendering shows two workflow candidates;
- status is `needs_workflow_selection`;
- no six-layer items are rendered.

## 3. Confirm compiler rejection before selection

```powershell
$blockedTarget = ".flowprint\node8\must-not-exist"

& $runner compile `
  ".\tests\fixtures\classification\yueyang-needs-selection-v0.4.json" `
  $blockedTarget `
  --skill-name "must-not-exist"

$blockedCompileExit = $LASTEXITCODE

[pscustomobject]@{
  CompilerExit = $blockedCompileExit
  TargetExists = Test-Path -LiteralPath $blockedTarget
}
```

Expected:

- compiler exit is `1`;
- rejection gate is `workflow_selection`;
- target does not exist.

## 4. Compile the user-selected trip workflow

```powershell
$tripTarget = ".flowprint\node8\yueyang-trip-planning"

& $runner validate ".\tests\fixtures\classification\yueyang-trip-selected-v0.4.json"
$tripValidatorExit = $LASTEXITCODE

& $runner compile `
  ".\tests\fixtures\classification\yueyang-trip-selected-v0.4.json" `
  $tripTarget `
  --skill-name "plan-multigenerational-road-trip"

$tripCompilerExit = $LASTEXITCODE
$tripManifest = Get-Content (Join-Path $tripTarget "flowprint-manifest.json") -Raw | ConvertFrom-Json
$tripRecord = Get-Content (Join-Path $tripTarget "compile-record.json") -Raw | ConvertFrom-Json

[pscustomobject]@{
  ValidatorExit = $tripValidatorExit
  CompilerExit = $tripCompilerExit
  ScopeStatus = $tripManifest.workflow_scope.status
  SelectedCandidate = $tripManifest.workflow_scope.selected_candidate_id
  SelectionBound = $tripManifest.workflow_scope.selection_confirmation_bound
  CandidateCount = $tripRecord.workflow_selection.candidate_count
  InstallState = $tripManifest.skill.install_state
  InstallPerformed = $tripRecord.install_performed
  ExternalActionPerformed = $tripRecord.external_action_performed
}
```

Expected:

- validator/compiler exits are `0`;
- selected candidate is `trip-planning`;
- selection is bound;
- candidate count is `2`;
- install state is `not_authorized`;
- no installation or external action occurred.

## 5. Compile the independently selected poster workflow

```powershell
$posterTarget = ".flowprint\node8\yueyang-trip-poster"

& $runner validate ".\tests\fixtures\classification\yueyang-poster-selected-v0.4.json"
$posterValidatorExit = $LASTEXITCODE

& $runner compile `
  ".\tests\fixtures\classification\yueyang-poster-selected-v0.4.json" `
  $posterTarget `
  --skill-name "create-family-trip-invitation"

$posterCompilerExit = $LASTEXITCODE
$posterManifest = Get-Content (Join-Path $posterTarget "flowprint-manifest.json") -Raw | ConvertFrom-Json

[pscustomobject]@{
  ValidatorExit = $posterValidatorExit
  CompilerExit = $posterCompilerExit
  SelectedCandidate = $posterManifest.workflow_scope.selected_candidate_id
  InstallState = $posterManifest.skill.install_state
}
```

Expected selected candidate: `trip-poster`.

## 6. Legacy regression and complete suite

```powershell
& $runner validate ".\tests\fixtures\classification\sticker-ready-v0.3.json"
$legacyValidatorExit = $LASTEXITCODE

python -m unittest discover -s tests -p "test_*.py" -v
$suiteExit = $LASTEXITCODE

[pscustomobject]@{
  LegacyValidatorExit = $legacyValidatorExit
  SuiteExit = $suiteExit
}
```

Expected both exits: `0`.

Do not install either generated draft and do not send, publish, book, pay, cancel, or perform another external action during this acceptance run.
