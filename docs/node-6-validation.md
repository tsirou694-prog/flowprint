# FlowPrint 节点 6：Mac 跨平台与产品体验验收

状态：完成（Codex CLI MVP 范围）  
日期：2026-07-19

当前实机验证版：`0.1.0+codex.20260719135630`  
已通过 Windows 作用域宿主短测的 scope-hardening 候选：`0.1.0+codex.20260720012358`

## 本节点目标

验证 FlowPrint 在用户真实、可写、已登录的 macOS Codex CLI 中能够完成 Marketplace 注册、插件安装、显式触发、有效编译与拒绝门回归；随后再验证宿主路由与最小产品体验。节点 6 不负责把编译草案描述成已安装或已实战验证的 Skill。

## 已完成证据

| 检查 | 当前结果 | 环境 | 证据边界 |
|---|---|---|---|
| 归档完整性 | 通过 | 用户 Mac | SHA-256 为 `65938362c0d896f1ef43cc8a8fdf1468c89da20a076b75eea5a141acbabb2ea0` |
| Codex CLI 安装与登录 | 通过 | 用户 Mac | `codex-cli 0.144.6`；`Logged in using ChatGPT` |
| Python 运行时 | 通过 | 用户 Mac | `Python 3.14.3`；尚未据此外推所有脚本兼容性 |
| Marketplace 注册 | 通过 | 用户 Mac | `flowprint-dev` 指向本地解压项目 |
| 插件安装与启用 | 通过 | 用户 Mac | `flowprint@flowprint-dev` 为 `installed, enabled`，版本 `0.1.0+codex.20260717090647` |
| 显式 `$flowprint` 激活 | 通过 | 用户 Mac | 返回 `ACTIVE`、正确版本与 `macOS · Codex CLI`，并报告 `Changes None` |
| 有效输入编译 | 通过 | 用户 Mac | schema 0.3 输入的校验器与编译器退出码均为 0；三个草案产物存在，`install_state` 为 `not_authorized`，未执行外部操作 |
| 未确认输入拒绝 | 通过 | 用户 Mac | 结构校验退出码 0 后，真实编译器以退出码 1 命中 `confirmation_schema`；目标不存在、无残留、输入哈希未改变 |
| 宿主路由与自动触发 | 修正后通过 | 用户 Mac | 最终版未写 `$flowprint` 仍自动选中 FlowPrint；仅加载 `flowprint:flowprint`，未读取 Memory、Shell 历史、全局配置、用户目录或其他插件；证据不足时保守标记且不编造 |
| 最终分发包用户侧哈希 | 通过 | 用户 Mac | `FlowPrint-Mac-routingfix-v0.1.0.zip` 的 SHA-256 与发布值 `fafdedd93484d9ae3e46021564786ca27f304c4c572f6f6d75fb0327a5ab590a` 一致 |

## 当前结论

FlowPrint 的 Marketplace、安装、显式触发、一个 schema 0.3 有效输入的编译，以及一个 schema 0.2 未确认输入的拒绝链路，已在一台真实 Intel Mac 上通过。有效编译后保持 `not_authorized`；拒绝样本没有残留或输入篡改。这个结论只覆盖当前用户环境与已测试样本；在宿主路由完成前，不把节点 6 判定为完成。

首次隐式触发成功选中 FlowPrint，但暴露出证据作用域缺口：Agent 为重建已完成任务读取了 `MEMORY.md`、Shell 历史、全局 Codex 配置、用户目录和插件库存。修正版必须把证据根固定为当前可见会话、当前工作区和 FlowPrint 自身引用；证据不足时保守降级，不得扩大读取范围。宿主同时预载 `superpowers:using-superpowers` 的现象单独记为宿主路由污染，不能用 FlowPrint 的分类正确性掩盖。

修正版 `0.1.0+codex.20260719133822` 已加入显式 Evidence scope gate、当前会话控制排除规则和对应静态契约回归。Skill 结构校验与插件 manifest 校验通过，28 个单元/集成测试全部通过。这证明修正规则已打包且现有确定性测试未回归；是否能约束真实宿主行为仍需在 Mac 更新插件后的全新会话中复测。

第一次修正版复测显示正文 gate 对加载后的行为有效：Shell 历史、全局配置、用户目录扫描和当前会话权限污染均消失；但宿主在加载 FlowPrint 正文前仍搜索 `MEMORY.md`，并加载 `skill-creator` 与四个 `superpowers` Skills。因此把同一边界前移到 frontmatter，并声明 FlowPrint 独占自身的分类/编译流程。正常环境再复测一次；若 `superpowers` 仍强制加载，将其列为环境级冲突并转向隔离 Demo 验证。

frontmatter 修正版 `0.1.0+codex.20260719135630` 已通过 Skill 与插件校验，29 个单元/集成测试全部通过，其中新增测试确保路由元数据同时携带证据作用域与独占路由约束。

最终 Mac 全新会话复测通过：宿主仅加载 `flowprint:flowprint`，分类证据仅来自当前可见请求，规则仅来自 FlowPrint 自身 bundle；没有 Memory、Shell 历史、全局配置、用户目录或无关 Skill/Plugin 读取。当前会话控制没有被持久化，缺失的目标、版本、命令和产物证据没有被补造。节点 6 因此在 Codex CLI MVP 范围内完成。

范围限定：本节点不证明 ChatGPT Work 图形界面的安装/分发，也不证明普通 ChatGPT 网页版可用；这些能力不得写入当前功能清单。节点 7 应以本节点的 macOS 完整闭环作为主 Demo 证据。Windows 已补齐最终版本 `0.1.0+codex.20260719135630` 的安装、显式激活、schema `0.3` 正向编译和 schema `0.2` fail-closed 拒绝；但首次最终版隐式触发虽然通过路由隔离与读取作用域检查，却错误绑定了工作区内旧节点 5 证据和旧版本参数。因此仍不能声称最终版本已完成双平台同范围端到端验证。GUI 分发列为 Future Work。

## Windows 最终版本补充验收（2026-07-20）

| 检查 | 当前结果 | 证据强度 |
|---|---|---|
| 最终分发包哈希 | 通过 | 用户 Windows 的 SHA-256 与 Mac 发布值一致 |
| 最终版本安装与显式激活 | 通过 | `0.1.0+codex.20260719135630` 在 Windows Codex CLI 中 installed/enabled，并返回 ACTIVE |
| schema `0.3` 有效编译 | 通过 | 校验器 0、编译器 0、三个产物存在，且未安装、未执行外部动作 |
| schema `0.2` 拒绝 | 通过 | 校验器 0、编译器 1、命中 `confirmation_schema`；无目标目录、无产物、输入哈希不变 |
| 隐式路由隔离 | 单样本通过 | 仅加载 FlowPrint；未读 Memory、历史、全局配置、Home 或其他插件 |
| 隐式分类的证据新鲜度 | 第二次复测通过 | 第二次预览采用四份 2026-07-20 Node 6 最终证据，并绑定 `0.1.0+codex.20260719135630`；旧节点 5 结果未用于补全最终四项结论 |
| 隐式分类的工作区根安全 | 未通过 | 会话从 `C:\Users\demo-user\Downloads` 启动，`rg --files` 枚举了无关下载内容；系统没有把过宽的个人目录识别为不安全证据根 |
| Evidence scope audit 一致性 | 未通过 | 输出引用了未在读取轨迹/审计中出现的 compiler contract，并包含最终证据与已列规则不能直接支撑的 WindowsApps 旧知识 |

因此 Windows 当前状态为：**显式执行闭环通过；隐式路由与最终版本证据绑定获得单样本通过；过宽工作区根防护及证据审计一致性待修正与复测。**

scope-hardening 候选已实现确定性的工作区根预检、exact-source-only 模式、证据 cohort 契约和实际读取审计契约，并通过 41 项单元/集成测试、Node 3 冒烟测试、Skill 结构校验和插件 manifest 校验。随后按 `WINDOWS-NODE6-SCOPEGUARD-RETEST.md` 完成两次短宿主测试，没有重跑已闭合的编译与拒绝链。

Windows 宿主短测 A 已通过：候选版本在 Downloads 根目录中隐式触发后，先运行 preflight 并以 `blocked` 停止，未执行文件枚举、未读取 Downloads 内容、未加载其他 Skill、未写入或执行外部动作。

Windows 宿主短测 B 已通过：候选版本从精确项目根隐式触发后，preflight 返回 `allowed_project_scope`；只读取四份 Windows Node 6 最终证据；旧 Windows Node 4/5 与 Mac Node 6 仅发现文件名、未读取内容、未用于补全结论；执行中的候选版本与被分类的已完成测试版本保持分离；Evidence scope audit 与工具轨迹一致，且零写入、零外部动作。

scope-hardening 发布门至此关闭。限定结论为：候选版本已在一台真实 Windows Codex CLI 上分别证明过宽根目录 fail-closed 与项目根 scoped discovery。当前候选的编译器代码未改动并通过集成测试，但没有把旧运行时的用户侧编译证据改写成候选版本的同版本 CLI 证据；节点 7 的正式 Demo 可在录制过程中自然补上该项，而无需在节点 6 再重复整套验收。

原始证据：

- `tests/evidence/mac-cli-node6-activation.txt`
- `tests/evidence/mac-cli-node6-valid-compile.txt`
- `tests/evidence/mac-cli-node6-rejection.txt`
- `tests/evidence/mac-cli-node6-implicit-trigger-scope-failure.txt`
- `tests/evidence/mac-cli-node6-implicit-trigger-scope-retest-1.txt`
- `tests/evidence/mac-cli-node6-implicit-trigger-final.txt`
- `tests/evidence/mac-cli-node6-final-archive-hash.txt`
- `tests/evidence/windows-cli-node6-final-install.txt`
- `tests/evidence/windows-cli-node6-final-activation.txt`
- `tests/evidence/windows-cli-node6-final-valid-compile.txt`
- `tests/evidence/windows-cli-node6-final-rejection.txt`
- `tests/evidence/windows-cli-node6-final-implicit-trigger-freshness-failure.txt`
- `tests/evidence/windows-cli-node6-final-implicit-trigger-scope-root-failure.txt`
- `tests/evidence/windows-cli-node6-scopeguard-unsafe-root-pass.txt`
- `tests/evidence/windows-cli-node6-scopeguard-project-root-pass.txt`
