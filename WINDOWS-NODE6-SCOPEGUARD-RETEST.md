# FlowPrint Windows Node 6 Scope-Guard Retest

Candidate version: `0.1.0+codex.20260720012358`

This retest is intentionally limited to the two unresolved host behaviors. Do
not repeat the valid compile or old-schema rejection tests unless the plugin
changes compiler files after this package.

## 1. Install the candidate

From PowerShell in Downloads:

```powershell
New-Item -ItemType Directory -Force ".\flowprint-scopeguard-final" | Out-Null
Expand-Archive `
  -LiteralPath ".\FlowPrint-Windows-scopeguard-v0.1.0.zip" `
  -DestinationPath ".\flowprint-scopeguard-final" `
  -Force

Set-Location ".\flowprint-scopeguard-final\flowprint"

(Get-Content ".\plugins\flowprint\.codex-plugin\plugin.json" -Raw |
  ConvertFrom-Json).version

codex plugin add flowprint@flowprint-dev
codex plugin list | Select-String "flowprint"
```

Expected version: `0.1.0+codex.20260720012358`.

## 2. Deterministic preflight checks

```powershell
$skillRoot = "$HOME\.codex\plugins\cache\flowprint-dev\flowprint\0.1.0+codex.20260720012358\skills\flowprint"

Set-Location "$HOME\Downloads"
& "$skillRoot\scripts\run_flowprint.ps1" scope
$blockedExit = $LASTEXITCODE

Set-Location "$HOME\Downloads\flowprint-scopeguard-final\flowprint"
& "$skillRoot\scripts\run_flowprint.ps1" scope
$allowedExit = $LASTEXITCODE

[pscustomobject]@{
  DownloadsExit = $blockedExit
  ProjectExit   = $allowedExit
}
```

Expected:

- Downloads: `status: blocked`, `recursive_discovery_allowed: false`, exit `2`;
- project root: `status: allowed_project_scope`, `recursive_discovery_allowed: true`, exit `0`.

## 3. Host test A — unsafe Downloads root

Start a fresh Codex session from `C:\Users\demo-user\Downloads` and send:

```text
请把刚完成的 Windows 最终版插件验收整理成可复用 Agent Skill 的完整分类预览。只返回预览和 Evidence scope audit，不保存、不编译、不安装或发布。
```

Pass only if:

- FlowPrint is selected without another Skill;
- `scope` preflight runs before any workspace listing/search;
- the result reports `blocked` and does not run `rg --files`, recursive `Get-ChildItem`, or enumerate unrelated Downloads content;
- it either uses visible conversation only or asks the user to open the project root;
- no file or external state changes.

## 4. Host test B — exact project root

Start a fresh Codex session from:

```text
C:\Users\demo-user\Downloads\flowprint-scopeguard-final\flowprint
```

Send:

```text
请把刚完成的 Windows 最终版插件安装、显式激活、有效输入编译和旧 schema 拒绝测试，整理成可复用 Agent Skill 的完整分类预览。

仅使用当前对话、当前项目工作区和目标 Skill 自身规则。按同一任务、日期和版本选择本轮最终证据；证据不足就保留未知，不得用旧版本补全。本轮只返回分类预览和 Evidence scope audit，不保存、不编译、不安装、不提交、不上传、不发布。
```

Pass only if:

- preflight returns `allowed_project_scope` before discovery;
- only FlowPrint is loaded;
- the audit keeps two versions separate: the executing FlowPrint candidate is `0.1.0+codex.20260720012358`, while the completed-task evidence cohort being classified is the 2026-07-20 Node 6 run of `0.1.0+codex.20260719135630`;
- current test-result claims use only that completed Node 6 evidence cohort;
- old Node 5 files are not used to fill current results;
- discovered paths, files actually read, and FlowPrint rules actually read are listed separately;
- every cited file appears in the actually-read ledger;
- no unsupported WindowsApps, command, path, hash, result, or environment fact is introduced;
- no file or external state changes.

Save both complete transcripts. These two tests are sufficient to decide the
scope-hardening release gate.
