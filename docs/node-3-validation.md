# FlowPrint 节点 3 验证记录

日期：2026-07-17  
范围：插件骨架、Repo Marketplace、最小触发契约与安装链路预验证  
状态：节点 3 核心门禁通过；扩展触发用例待后续执行

## 交付结构

```text
flowprint/
├── .agents/plugins/marketplace.json
├── plugins/flowprint/
│   ├── .codex-plugin/plugin.json
│   └── skills/flowprint/
│       ├── SKILL.md
│       └── agents/openai.yaml
├── tests/node3_smoke_test.py
├── tests/trigger-cases.md
├── tests/logs/node3-runtime-errors.txt
├── tests/evidence/windows-cli-activation-card.txt
└── docs/node-3-validation.md
```

## 节点 3 行为边界

`$flowprint` 在本节点只确认插件已激活、检查当前任务证据是否可见、生成候选工作流名称并返回 `scaffold_ready`。它不执行去情境化分类，不生成 Skill 文件包，也不声称流程已经可复用；这些能力从节点 4 开始实现。

## 验证结果

| 检查 | 结果 | 测试环境 | 证据与边界 |
|---|---|---|---|
| Skill frontmatter 与命名 | 静态预检通过 | 当前工作区 | OpenAI/Codex 随附的 `skill-creator/scripts/quick_validate.py` 返回 `Skill is valid!`；不等同于真实触发通过 |
| 插件 manifest | 静态预检通过 | 当前工作区 | OpenAI/Codex 系统 `plugin-creator/scripts/validate_plugin.py` 返回 `Plugin validation passed`；属于 manifest preflight，不是端到端认证 |
| Marketplace 发现 | 隔离验证通过 | 临时可写 `CODEX_HOME`，未登录 | Codex 能列出 `flowprint@flowprint-dev`；尚未在真实已登录配置中复现 |
| 插件安装与启用 | 隔离验证通过 | 临时可写 `CODEX_HOME`，未登录 | 状态为 `installed, enabled`，版本 `0.1.0` |
| 安装缓存副本 | 隔离静态预检通过 | 临时可写 `CODEX_HOME`，未登录 | 缓存后的 Skill 再次通过 `quick_validate.py` |
| 触发用例集 | 已定义，部分执行 | 测试定义文件 | `tests/trigger-cases.md` 已定义正向、反向和模糊请求；其中一个显式正向请求已执行，其余不得写成“通过” |
| 已登录新会话触发 | 未完成 | 当前已登录托管环境 | 状态数据库和插件目录被只读挂载，新会话在模型调用前退出 |
| 显式 `$flowprint` 正向触发 | 端到端通过 | 用户自有、可写、已登录的 Windows Codex CLI | FlowPrint 返回完整 activation card，候选流程、四类证据、`scaffold_ready` 和 Node 4 提示均符合预期 |
| 反向与模糊触发 | 未执行 | — | 不因一个正向用例通过而推定其他触发边界正确，保留到后续触发评测 |

## 环境限制范围判断

只读诊断结果为：

```text
/root/.codex tmpfs tmpfs ro,nosuid,nodev,noexec,relatime,...
CODEX_HOME_NOT_WRITABLE
```

这表明 `/root/.codex` 是在本次托管容器中被单独以只读 `tmpfs` 挂载，并非仅由普通 Unix 文件权限导致。OpenAI 官方 Codex 文档说明，插件正常安装会写入 `~/.codex/plugins/cache/...`，启用状态写入 `~/.codex/config.toml`；因此“全局状态目录可写”是正常本地插件安装的前提，本次只读挂载不是官方文档描述的常规 CLI 默认行为。

据此可以判断：**当前错误更可能是本次调试沙箱特有的宿主限制，而不是 FlowPrint 自身要求或 Codex CLI 的正常默认行为。**这一判断随后获得实机验证支持：相同测试包在用户自有、可写且已登录的 Windows Codex CLI 中成功返回 activation card。该结果排除了“FlowPrint 在普通本地 CLI 中必然因只读状态目录无法运行”的高风险假设，但仍不能保证所有托管评审环境都可写。

用户已明确授权全局安装，但当前环境无法创建 Marketplace 缓存或更新状态数据库。因此安装测试使用项目外层的隔离 `CODEX_HOME`，不会改变现有 Codex 配置。隔离环境成功完成 Marketplace 登记、插件安装、启用和缓存验证，但因不复制用户凭据，无法完成真实模型响应。

考虑到用户现有 Windows Codex 已使用 `my-skills@personal`，项目 Marketplace 已从通用名称 `personal` 改为唯一名称 `flowprint-dev`。改名后重新执行隔离安装，Codex 返回 `flowprint@flowprint-dev · installed, enabled · 0.1.0`，避免实机测试时与既有个人 Marketplace 冲突。

另一次测试在当前已登录 Codex 中临时暴露同一份 repo Skill，尝试用 `--ephemeral` 启动新会话；运行时仍因只读状态数据库在模型调用前退出。结合两个独立静态校验和隔离安装结果，现有证据支持“阻塞发生在宿主状态初始化阶段”的判断，但尚不足以证明 FlowPrint 在真实宿主中一定能正确触发。

## 校验器来源与可信度边界

- `quick_validate.py` 来自当前 Codex 随附的 OpenAI `skill-creator`，不是 FlowPrint 团队自写；它检查 YAML frontmatter、必需字段和命名规则。
- `validate_plugin.py` 来自当前 Codex 系统 `plugin-creator`，不是 FlowPrint 团队自写；它检查插件 manifest schema、路径和占位符等 preflight 项。
- `tests/node3_smoke_test.py` 是 FlowPrint 自写，只检查本项目的 wiring、固定字段和触发描述是否存在，不具备独立认证效力。
- 两个随附校验器都不能替代 Agent Skills 规范复核、实际安装、真实模型触发和输出行为测试。最终仍需对照 https://agentskills.io/specification 及 OpenAI 插件文档验证。

## 原始错误证据

完整的脱敏 stderr 摘录保存在 `tests/logs/node3-runtime-errors.txt`。关键错误包括：

```text
Error: failed to create marketplace install directory /root/.codex/.tmp/marketplaces:
Read-only file system (os error 30)

failed to open state db at /root/.codex/state_5.sqlite:
attempt to write a readonly database

Error: failed to initialize in-process app-server client:
Read-only file system (os error 30)
```

## Windows CLI 实机证据

用户在自己完全掌控的 Windows Codex CLI 中安装测试包，并执行显式 `$flowprint` 请求，返回：

```text
FlowPrint is active.
Candidate workflow: 插件安装与验证
Evidence: goal yes · result yes · corrections yes · artifacts yes
Status: scaffold_ready
Next capability: decontextualization classifier (Node 4)
```

原始响应保存在 `tests/evidence/windows-cli-activation-card.txt`。由于测试包中不存在 repo 级 `.agents/skills/flowprint/SKILL.md`，运行时使用的是插件内的 FlowPrint Skill，而不是临时测试入口。

本证据只覆盖一个显式正向触发。它没有验证隐式触发、不应触发请求或模糊请求的澄清行为。

## 实机验收标准

本项目开发 Marketplace 使用唯一名称 `flowprint-dev`，避免与你现有的 `my-skills@personal` 冲突。在已登录 Codex 环境中添加本项目 Marketplace、安装 `flowprint@flowprint-dev` 并开启新任务。输入：

```powershell
cd <FlowPrint项目根目录>
codex plugin marketplace add .
codex plugin add flowprint@flowprint-dev
codex plugin list
codex
```

在新任务中输入：

```text
$flowprint 把我们刚完成的任务准备成可复用 Skill。
```

预期返回包含：

```text
FlowPrint is active.
Status: scaffold_ready
Next capability: decontextualization classifier (Node 4)
```

## 节点结论

结构、静态校验、隔离安装链路和用户自有 Windows Codex CLI 的显式端到端触发均已验证。当前托管容器的只读 `/root/.codex` 限制没有在用户本地环境重现，因此不再构成节点 4 的前置阻塞。

节点 3 核心门禁判定通过，可以进入节点 4。证据边界保持不变：目前只完成一个显式正向触发，反向、模糊和隐式触发仍为待测项；这些项目不会被错误写成“已通过”，并应在节点 6 的完整 Demo/触发评测中补齐。

## 官方依据

- Codex 插件 Marketplace、安装与缓存路径： https://learn.chatgpt.com/docs/build-plugins
- Agent Skills 开放规范： https://agentskills.io/specification
