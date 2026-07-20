# FlowPrint 节点 5 Windows 回归验收

版本：`0.1.0+codex.20260717090647`

本轮只复测三个已发现问题：Windows Python 入口、会话范围污染 Permission Boundary、无成品时的 `result` 证据库存。

## 更新插件

```powershell
cd "$HOME\Downloads\flowprint-node5-regression-v0.1.0\flowprint"
codex plugin remove flowprint@flowprint-dev
codex plugin marketplace remove flowprint-dev
codex plugin marketplace add .
codex plugin add flowprint@flowprint-dev
codex plugin list | Select-String "flowprint@"
```

## 回归 1：PowerShell 启动器

在解压目录执行：

```powershell
& ".\plugins\flowprint\skills\flowprint\scripts\run_flowprint.ps1" validate ".\tests\fixtures\classification\sticker-ready-v0.3.json"
```

预期：即使 WindowsApps 的 `python3` 入口不可用，启动器也能找到本机 Python 3.13，返回 `PASS`，不安装任何软件。

## 回归 2：当前会话范围不进入持久层

全新 Codex 会话：

```text
$flowprint 请分类下面这段存在信息缺口的上下文，只返回完整分类预览：

摘要只保留了“背景使用红色”和“背景使用蓝色”两个方案；用户最终选择缺失，无法确定哪一个后来生效。

本轮只预览，不要生成或编译。
```

预期：颜色为 `ambiguous`/`conflicting`，状态 `needs_review`；“本轮只预览，不要生成或编译”被直接服从，但不进入六层分类，也不产生重复确认问题。

## 回归 3：无成品证据时 result=no

全新 Codex 会话：

```text
$flowprint 只根据以下约束生成完整分类预览：品牌通常使用圆角；这次尽量使用暖色；Logo 安全区必须保留。当前没有成品、验收结果或工作区产物。
```

预期：`result no`、`artifacts no`；通常/尽量/必须仍保持不同强度。

如果宿主仍额外调用无关 Skill，请保留输出；这属于节点 6 的技能路由隔离证据，不要隐藏。
