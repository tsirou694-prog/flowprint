# FlowPrint Node 7 — Windows 单次验收

目标版本：`0.1.0+codex.20260720111640`

这次只验证新能力，不重复节点 6 的范围门测试。完整流程只需要一次安装、一次基础草案编译和两轮 Codex 对话。

## 1. 安装候选版本

在 PowerShell 中进入 ZIP 所在的 `Downloads`，把 `<ZIP-NAME>` 换成实际文件名：

```powershell
Get-FileHash ".\<ZIP-NAME>" -Algorithm SHA256

New-Item -ItemType Directory -Force ".\flowprint-node7-final" | Out-Null
Expand-Archive `
  -LiteralPath ".\<ZIP-NAME>" `
  -DestinationPath ".\flowprint-node7-final" `
  -Force

Set-Location ".\flowprint-node7-final\flowprint"

(Get-Content ".\plugins\flowprint\.codex-plugin\plugin.json" -Raw | ConvertFrom-Json).version

codex plugin marketplace remove flowprint-dev
codex plugin marketplace add "$HOME\Downloads\flowprint-node7-final\flowprint"
codex plugin add flowprint@flowprint-dev
codex plugin list | Select-String "flowprint" -Context 1,2
```

必须看到目标版本 `0.1.0+codex.20260720111640`。若不是该版本，停止，不继续测试。

## 2. 用当前候选版本生成基础草案

继续在项目根目录执行：

```powershell
$version = "0.1.0+codex.20260720111640"
$skillRoot = "$HOME\.codex\plugins\cache\flowprint-dev\flowprint\$version\skills\flowprint"
$runner = Join-Path $skillRoot "scripts\run_flowprint.ps1"
$base = ".flowprint\node7-demo\base-laosan"

& $runner validate ".\tests\fixtures\classification\sticker-ready-v0.3.json"
if ($LASTEXITCODE -ne 0) { throw "classification validation failed" }

& $runner compile `
  ".\tests\fixtures\classification\sticker-ready-v0.3.json" `
  $base `
  --skill-name "node7-laosan-workflow"
if ($LASTEXITCODE -ne 0) { throw "base compilation failed" }

$baseHashBefore = (Get-FileHash "$base\flowprint-manifest.json" -Algorithm SHA256).Hash
$baseHashBefore
```

若 `$base` 已存在，停止并使用一个新的空解压目录；不要删除或覆盖旧结果。

## 3. 启动 Codex，准备修订但不确认

仍在该项目根目录运行：

```powershell
codex
```

发送下面这一整段：

```text
$flowprint 我需要修正刚编译的基础草案：老三现在应明确为“没有可见尾巴”，不再保留“无尾或短尾”的二选一表述。

请把 tests/fixtures/classification/sticker-ready-v0.3.json 作为基础分类，只在新的 .flowprint/node7-demo/classification.next.json 中应用这次修正，并将本条用户修正作为该 Profile 项的新证据；不要修改原 fixture 或基础草案。

然后针对 .flowprint/node7-demo/base-laosan/flowprint-manifest.json 调用节点 7 revise，把修订事务写到 .flowprint/node7-demo/revision-1。返回 revision_id、changed_item_ids、stale_artifacts、stale_confirmation_ids、required_question_ids、full_revalidation_required，以及基础 manifest 的当前 SHA-256。

本轮只准备 revision：不要代替我确认，不要 finalize，不要编译修订版，不要安装、提交、上传或发布。
```

预期结果：

- `item-profile-tail` 被识别为变化；
- Profile、`SKILL.md` 等相关产物被标记 stale；
- 因为这是高影响 Profile 变化，`full_revalidation_required: true`；
- 旧确认被失效，状态停在 `needs_confirmation`；
- 没有 `classification.ready.json`、receipt 或修订草案。

## 4. 明确确认，并在同一轮完成拒绝与成功路径

看到 revision plan 后，发送：

```text
我确认这次修正，并接受刚才 revision plan 中全部推荐答案。请把我这句话作为实际用户确认记录，只绑定刚才显示的 revision_id 和它要求的全部 question/item IDs，不得补写其他授权。

先调用 confirm 生成 classification.ready.json 和 revision-receipt.json。随后先故意不带 --revision-receipt 编译到 .flowprint/node7-demo/should-not-exist，确认 revision_receipt gate 拒绝且目录不存在；再带正确 receipt 编译到新的 .flowprint/node7-demo/revised-laosan-r1，skill name 使用 node7-laosan-workflow。

最后返回：confirm/无 receipt 编译/有 receipt 编译三次退出码与 gate；基础 manifest 前后 SHA-256；新草案三个核心文件是否存在；旧/新 Profile version；revision_id 与 sequence；install_state、install_performed、external_action_performed。不要安装、提交、上传或发布。
```

## 5. 通过标准

只有以下条件全部满足才记为 Windows host pass：

- confirm 成功；
- 无 receipt 编译非零退出，gate 为 `revision_receipt`，目标目录不存在；
- 有 receipt 编译退出码为 0；
- 基础 manifest 前后哈希相同；
- 新草案与基础草案路径不同；
- Profile version 从 `1` 升至 `2`；
- revision sequence 为 `1`；
- `SKILL.md`、`flowprint-manifest.json`、`compile-record.json` 均存在；
- `install_state: not_authorized`；
- `install_performed: false`；
- `external_action_performed: false`；
- 没有执行安装、提交、上传或发布。

任何一项不满足都只记录实际结果，不手工修改 receipt、classification、manifest 或生成物来“补通过”。
