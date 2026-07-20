param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet('scope', 'validate', 'render', 'compile', 'impact', 'revise', 'confirm', 'preflight')]
    [string]$Command,

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$FlowPrintArguments
)

$ErrorActionPreference = 'Stop'
$scriptMap = @{
    scope     = 'check_evidence_scope.py'
    validate  = 'validate_classification.py'
    render    = 'render_classification.py'
    compile   = 'compile_skill.py'
    impact    = 'analyze_impact.py'
    revise    = 'prepare_revision.py'
    confirm   = 'finalize_revision.py'
    preflight = 'validate_generated_skill.py'
}

$candidates = @()
foreach ($name in @('python3', 'python', 'py')) {
    $resolved = Get-Command $name -ErrorAction SilentlyContinue
    if ($null -ne $resolved) {
        $prefix = if ($name -eq 'py') { @('-3') } else { @() }
        $candidates += [pscustomobject]@{ Path = $resolved.Source; Prefix = $prefix }
    }
}

$searchPatterns = @()
if ($env:LOCALAPPDATA) {
    $searchPatterns += (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python*\python.exe')
}
if ($env:ProgramFiles) {
    $searchPatterns += (Join-Path $env:ProgramFiles 'Python*\python.exe')
}
foreach ($pattern in $searchPatterns) {
    Get-ChildItem -Path $pattern -File -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending |
        ForEach-Object {
            $candidates += [pscustomobject]@{ Path = $_.FullName; Prefix = @() }
        }
}

$selected = $null
foreach ($candidate in $candidates) {
    try {
        & $candidate.Path @($candidate.Prefix) --version *> $null
        if ($LASTEXITCODE -eq 0) {
            $selected = $candidate
            break
        }
    }
    catch {
        continue
    }
}

if ($null -eq $selected) {
    Write-Error 'FlowPrint could not find a working Python 3 interpreter. No software was installed and no compiler output was created.'
    exit 127
}

$scriptPath = Join-Path $PSScriptRoot $scriptMap[$Command]
& $selected.Path @($selected.Prefix) $scriptPath @FlowPrintArguments
exit $LASTEXITCODE
