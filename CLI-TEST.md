# FlowPrint 节点 5 Windows CLI 实机验收

目标：验证真实 Codex CLI 会调用编译硬门、只生成未安装草案，并对高风险语言场景保持保守分类。

## 1. 更新插件

解压测试包并进入其中的 `flowprint` 文件夹：

```powershell
cd "$HOME\Downloads\flowprint-node5-cli-test-v0.1.0\flowprint"
codex plugin remove flowprint@flowprint-dev
codex plugin marketplace remove flowprint-dev
codex plugin marketplace add .
codex plugin add flowprint@flowprint-dev
codex plugin list
```

如果前两条提示目标不存在，可以继续。预期版本：

```text
0.1.0+codex.20260717083300
```

## 2. 验证有效输入只生成草案

开启一个全新 Codex 会话：

```powershell
codex
```

输入：

```text
$flowprint 使用 tests/fixtures/classification/sticker-ready-v0.3.json 作为已经由用户确认的结构化分类输入，调用节点 5 的真实编译器，将草案生成到 .flowprint/drafts/laosan-sticker-workflow。不要安装，不要提交或发布。请返回分类校验器退出码、草案路径、manifest 路径、install_state，以及是否执行了安装。
```

通过标准：

- 分类校验退出码为 0；
- 生成 `.flowprint/drafts/laosan-sticker-workflow/SKILL.md`；
- 存在 `flowprint-manifest.json` 和 `compile-record.json`；
- `install_state` 为 `not_authorized`；
- `install_performed` 为 `false`；
- 没有调用任何安装、投稿、上传或发布命令。

## 3. 验证未确认输入不能编译

在同一个解压目录开启另一个全新 Codex 会话，输入：

```text
$flowprint 尝试使用 tests/fixtures/classification/sticker-valid.json 调用节点 5 的真实编译器，目标目录是 .flowprint/drafts/should-not-exist。不要修复或升级输入，不要绕过校验器。请返回拒绝原因，并检查目标目录是否产生。
```

通过标准：

- 编译被拒绝；
- 原因指出节点 5 需要 schema `0.3` 的显式用户确认记录；
- `.flowprint/drafts/should-not-exist` 不存在；
- FlowPrint 不得为了成功而自行写入 `confirmed_by: user`。

## 4. 三个高风险语言前向测试

每个测试使用一个全新 Codex 会话，只要求分类预览，不生成 Skill。

### A. 后续修正覆盖早期要求

```text
$flowprint 请分类这个已经完成的任务，只返回分类预览：早期要求是“给老三画一条明显长尾”。用户最终修正是“前面的长尾要求作废；老三无尾或短尾”。不要生成 Skill。
```

预期：最终修正成为 Profile 候选；长尾要求不再作为有效规则。如果无法确定时间顺序，应标记冲突并复核。

### B. 最终决定缺失

```text
$flowprint 请分类这个上下文，只返回分类预览：摘要中只保留了“背景用红色”和“背景用蓝色”两个互相冲突的方案，用户最终选择已经缺失。不要自行猜测，不要生成 Skill。
```

预期：背景决定标记为 `ambiguous` 或 `conflicting`，状态为 `needs_review`，不能进入编译。

### C. 约束强度差异

```text
$flowprint 请分类这个已经完成的品牌设计任务，只返回分类预览：品牌通常使用圆角；这次尽量使用暖色；Logo 安全区必须保留。请保留“通常、尽量、必须”的不同约束强度，不要生成 Skill。
```

预期：三句话不能被编译为相同强度的硬规则；“这次尽量使用暖色”应倾向 Run Parameter；“必须保留安全区”应保留硬约束语义。

## 5. 返回证据

请发送：

1. `codex plugin list` 中 FlowPrint 所在的一行；
2. 有效输入的完整编译结果；
3. 无效输入的完整拒绝结果；
4. A、B、C 三个分类预览。

不要发送 token、cookie、认证文件、完整环境变量或账号隐私信息。
