# FlowPrint 节点 6 工程验收与评审记录

状态：完成，限定为 Codex CLI MVP 范围  
验收日期：2026-07-19  
最终受测版本：`0.1.0+codex.20260719135630`  
scope-hardening 候选：`0.1.0+codex.20260720012358`（确定性测试、Windows unsafe-root 与 project-root 宿主短测均通过）  
文档用途：供产品、工程、安全与评测同事独立审阅
文档修订：v2，已纳入第一轮专业评审意见

## 1. 结论摘要

节点 6 在一台用户实际控制、可写且已登录的 Intel Mac 上完成了以下闭环：

1. 本地 Marketplace 注册与 FlowPrint 插件安装；
2. 显式 `$flowprint` 激活；
3. schema `0.3` 已确认输入的真实编译；
4. schema `0.2` 未确认输入的真实拒绝；
5. 不写 `$flowprint` 的隐式触发；
6. 证据作用域、无关 Skill 路由和当前会话控制的两轮缺陷修复与实机回归。

最终实机回归中，Codex 自动选择 `flowprint:flowprint`，没有加载其他 Skill/Plugin，没有读取 Memory、Shell 历史、全局 Codex 配置、用户目录或插件库存；证据不足时保留缺口，没有补造插件名、schema 版本、命令、路径、退出码或错误文案；“本轮不要编译/安装/发布”被执行，但没有被沉淀为长期 Permission Boundary。

因此节点 6 可判定为：**在已测试的 macOS Codex CLI 环境和样本上通过**。

该判定不代表：

- 隐式触发已达到统计意义上的普遍准确率；
- Apple Silicon、Linux 或所有 Codex CLI 版本均兼容；
- ChatGPT Work 图形界面或普通 ChatGPT 网页版可以安装；
- 编译出的 Skill 已安装或经过真实业务复用；
- 自然语言作用域规则等同于确定性的文件访问控制。

## 2. 验收环境

| 项目 | 实测值 | 证据性质 |
|---|---|---|
| 设备 | Intel Mac | 用户终端输出 |
| 操作系统 | macOS | Codex 运行时识别与用户终端输出 |
| Codex CLI | `0.144.6` | `codex --version` |
| 认证 | `Logged in using ChatGPT` | `codex login status` |
| Python | `3.14.3` | `python3 --version` 与编译回报 |
| Python 路径 | `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3` | 编译回报 |
| Marketplace | `flowprint-dev` | `codex plugin list` |
| 最终插件 | `flowprint@flowprint-dev` | `codex plugin list` 与运行时 Skill 路径 |
| 最终版本 | `0.1.0+codex.20260719135630` | 最终隐式触发审计 |

隐私说明：评审文档不保留用户姓名、邮箱、认证内容或完整 Home 路径；仓库内的原始验收摘录仅保存任务所需的最小技术证据。

## 3. 节点目标与非目标

### 3.1 目标

- 证明 FlowPrint 能在真实 macOS Codex CLI 中被发现、安装和调用；
- 证明节点 5 编译器能在 Mac/Python 3.14.3 上执行；
- 证明有效输入生成未安装草案；
- 证明旧 schema 不能绕过确认门；
- 证明隐式触发不会为了重建上下文越界读取；
- 证明当前会话控制不会被误写进可复用 Skill；
- 记录失败、修复和回归，而不是只保留最终成功结果。

### 3.2 非目标

- 安装编译产物为个人 Skill；
- 执行提交、上传、发布或部署；
- 证明生成 Skill 的业务价值或 Field-tested 状态；
- 实现 ChatGPT Work GUI 或普通网页端分发；
- 完成大样本分类准确率、触发准确率或安全红队统计。

## 4. 版本演进

| 版本 | 用途 | 结果 |
|---|---|---|
| `0.1.0+codex.20260717090647` | 初始 Mac 安装、显式激活、正向编译、旧 schema 拒绝 | 核心链路通过；隐式触发暴露作用域与路由缺陷 |
| `0.1.0+codex.20260719133822` | 将 Evidence scope gate 加入 Skill 正文 | Shell 历史、全局配置、Home 扫描和权限污染消失；但宿主在正文加载前仍搜索 Memory 并加载无关 Skills |
| `0.1.0+codex.20260719135630` | 将作用域与独占路由约束前移至 frontmatter | 最终全新会话回归通过；仅加载 FlowPrint，未越界读取 |

最终分发归档：`FlowPrint-Mac-routingfix-v0.1.0.zip`  
归档 SHA-256：`fafdedd93484d9ae3e46021564786ca27f304c4c572f6f6d75fb0327a5ab590a`

用户 Mac 已对最终归档独立执行 `shasum -a 256`，结果与打包环境发布值完全一致；运行时路径同时确认加载版本 `0.1.0+codex.20260719135630`。文件完整性与运行时版本证据分别保存，不互相替代。

## 5. 验收矩阵

| 验收项 | 结果 | 关键证据 | 证据强度与边界 |
|---|---|---|---|
| 初始归档完整性 | 通过 | 初始 Mac 包 SHA-256 与发布值一致 | 强；仅覆盖该下载文件 |
| CLI 安装与登录 | 通过 | `codex-cli 0.144.6`；ChatGPT 登录成功 | 强；单机单账号 |
| Marketplace 注册 | 通过 | `flowprint-dev` 注册到本地项目 | 强；本地 Marketplace 路径 |
| 插件安装与启用 | 通过 | `installed, enabled` | 强；不等于 Skill 行为已验证 |
| 显式激活 | 通过 | `Status ACTIVE`、正确版本、`Changes None` | 中强；一次显式请求 |
| 有效输入编译 | 通过 | 分类校验与编译退出码均为 0；三个产物存在 | 强；一个 schema 0.3 fixture |
| 编译不安装 | 通过 | `install_state: not_authorized`、`install_performed: false` | 强；一个编译路径 |
| 外部操作隔离 | 通过 | `external_action_performed: false` | 中强；本次执行轨迹 |
| 旧 schema 拒绝 | 通过 | 编译退出码 1；`confirmation_schema` | 强；一个 schema 0.2 fixture |
| 拒绝无残留 | 通过 | 目标目录和三个产物均不存在 | 强；一个拒绝路径 |
| 输入不被篡改 | 通过 | 输入 SHA-256 前后相同 | 强；一个 fixture |
| 隐式触发 | 修正后通过 | 不写 `$flowprint` 仍自动选择 FlowPrint | 中；一个最终提示，不是准确率统计 |
| 独占路由 | 修正后通过 | 最终仅加载 `flowprint:flowprint` | 中；一次全新会话 |
| Evidence scope | 修正后通过 | 最终未读 Memory、历史、全局配置、Home 或其他插件 | 中；工具轨迹和审计一致，但规则仍是自然语言约束 |
| 会话控制排除 | 修正后通过 | 禁止动作被执行但未持久化为权限规则 | 中；一个分类样本 |
| 静态与集成测试 | 通过 | Skill 校验、插件校验、29 个测试通过 | 强于代码契约；不等同于宿主端到端行为统计 |
| 最终分发包用户侧哈希 | 通过 | 用户 Mac 的 `shasum -a 256` 与发布 SHA-256 完全一致 | 强；覆盖该下载归档的文件完整性，不代替运行时行为验证 |

## 6. 核心正向编译证据

输入：`tests/fixtures/classification/sticker-ready-v0.3.json`  
目标：`.flowprint/drafts/mac-laosan-sticker-workflow`

结果：

```text
classification_validator_exit: 0
compiler_exit: 0
SKILL.md: exists
flowprint-manifest.json: exists
compile-record.json: exists
install_state: not_authorized
install_performed: false
external_action_performed: false
```

支持的结论：

- 一个满足 schema `0.3` 且已记录用户确认的输入能在 Mac 上生成草案；
- 编译成功不会自动安装草案；
- 编译授权、安装授权和外部操作授权相互独立。

不支持的结论：

- 所有合法输入都能编译；
- 草案符合所有第三方 Agent Skills 实现；
- 草案已经可用、优质或经过真实任务验证。

## 7. 核心拒绝证据

输入：`tests/fixtures/classification/sticker-valid.json`，schema `0.2`  
目标：`.flowprint/drafts/mac-should-not-exist`

结果：

```text
classification_validator_exit: 0
compiler_exit: 1
rejection_gate: confirmation_schema
target_directory_exists: false
SKILL.md: not generated
flowprint-manifest.json: not generated
compile-record.json: not generated
input_modified: false
```

输入 SHA-256 前后均为：

```text
6777dc9569467aa9313d4f0971029caf092daac10b06bddf8cd3b805f97a4674
```

### 为什么结构校验为 0，但编译仍拒绝

这不是测试矛盾，而是两层契约：

1. 分类校验器确认 schema `0.2` 文档在其所属分类阶段结构合法；
2. 编译器的 `confirmation_schema` gate 进一步要求节点 5 输入为 schema `0.3`，并包含覆盖所有复核项的真实用户确认。

因此“结构合法”不等于“已获编译授权”。这次测试验证的是编译器内部硬门确实在真实入口生效，而不是依赖前置脚本偶然报错。

## 8. 隐式触发缺陷与修复过程

### 8.1 首次隐式触发：失败

已通过部分：

- 不写 `$flowprint` 时自动选中了 FlowPrint；
- 返回六层分类预览；
- 没有编译、安装或发布。

失败部分：

- 同时加载 `superpowers:using-superpowers`；
- 搜索 `MEMORY.md`；
- 搜索全局 Codex 配置和插件状态；
- 搜索用户 Home/Library 与 Shell 历史；
- 当前会话限制参与生成持久 Permission Boundary 候选。

判定：**不通过**。分类内容看似合理，不能抵消取证越界。

### 8.2 第一轮修正：部分通过

修正：在 Skill 正文加入 Evidence scope gate，允许根固定为：

1. 当前可见对话；
2. 当前工作区；
3. FlowPrint 自身引用与脚本。

并禁止用 Memory、Shell 历史、全局配置、Home 扫描和其他插件补证据；当前会话控制只执行、不持久化。

复测改善：

- Shell 历史、全局配置、Home 扫描消失；
- 缺失的命令、路径和退出码没有被编造；
- 当前会话限制未被持久化。

仍失败：

- 宿主在 FlowPrint 正文加载前已搜索 Memory；
- 加载 `skill-creator` 与四个 `superpowers` Skills。

根因判断：正文 gate 生效时间晚于宿主路由与预读取。

### 8.3 第二轮修正：最终通过

修正：把以下约束前移至始终可见的 Skill frontmatter：

- FlowPrint 独占自身的分类和编译请求；
- 除非用户明确要求元评审，不与 `skill-creator`、`writing-skills` 或其他 Skill 联用；
- 路由和执行阶段只使用当前对话、当前工作区和 FlowPrint 自身 bundle；
- 禁止用 Memory、Shell 历史、Home、全局配置或其他插件库存重建证据。

最终新会话结果：

- 自动选择 `flowprint:flowprint`；
- 其他 Skills/Plugins：无；
- 未读取 Memory、Shell 历史、全局配置、环境变量、Home 或其他插件；
- 仅以当前请求为成果证据；
- 证据不足时返回 `goal no`、`artifacts no` 和 `ambiguous`，没有补造细节；
- 当前会话禁止动作没有进入持久 Permission Boundaries；
- 没有生成文件或执行外部动作。

## 9. 代码与契约修正

主要修正位置：

- `plugins/flowprint/skills/flowprint/SKILL.md`
  - frontmatter 的独占路由与证据作用域；
  - Evidence scope gate；
  - 当前会话控制排除规则。
- `plugins/flowprint/skills/flowprint/agents/openai.yaml`
  - 默认提示同步证据边界。
- `plugins/flowprint/.codex-plugin/plugin.json`
  - 产品描述同步“只使用可见对话与工作区证据”。
- `tests/trigger-cases.md`
  - 新增 Evidence-scope regression 契约。
- `tests/test_evidence_scope_contract.py`
  - 验证 scope gate、frontmatter 路由元数据和当前会话控制规则已打包。

最终验证：

```text
Skill is valid!
Plugin validation passed
29 tests passed
```

## 10. 安全与隐私判断

### 已验证行为

- 编译不等于安装；
- 安装不等于发布；
- 未确认旧输入不能被模型自行升级或伪造用户确认；
- 拒绝路径不留下可误用的半成品；
- 当前会话的禁止操作不会被写成长期用户规则；
- 最终隐式触发在已测试的一个中文提示和一次新会话中没有越界取证；不得脱离下方“残余风险 3”单独外推。

### 残余风险

1. **作用域目前主要由自然语言契约约束。** 当前插件没有确定性的 pre-tool hook 或文件访问 allowlist；模型或宿主行为变化仍可能造成回归。
2. **当前工作目录可能就是 Home。** 规则明确禁止 Home-wide 搜索，并在最终测试中保守停止，但该冲突尚未由代码强制解决。
3. **隐式触发样本量小。** 最终通过只覆盖一个中文自然语言提示和一次新会话。
4. **审计提示会影响行为。** 最终测试明确要求 Evidence scope audit，属于定向验收，不等同于无提示条件下的长期观测。
5. **同一模型参与分类与自述。** 工具轨迹与审计相互印证，但没有独立安全监控器证明所有未读行为。

工程建议：MVP 保留当前 skills-only 设计并诚实披露上述限制；后续如需更强安全保证，应考虑确定性的读路径 hook、scope manifest 或宿主策略，而不是继续堆叠提示词。

## 11. 未覆盖范围

- Apple Silicon Mac；
- Linux；
- 其他 Python 主版本；
- 其他 Codex CLI 版本；
- ChatGPT Work GUI 安装与分发；
- 普通 ChatGPT 网页版；
- 自动触发的正负样本统计；
- 恶意提示、反讽、否定句与 prompt injection；
- 生成 Skill 的安装、卸载、升级和跨设备同步；
- 用户在拒绝后以自然语言修正分类、影响分析标记旧状态、重新确认、重新验证并再次编译的完整 CLI 链路；
- dependency graph 已在节点 5 的 manifest、校验器、影响分析器和单元测试中实现，但尚未完成上述“自然语言修正 → 级联 stale → 重新提交”的真实 CLI 端到端验证；
- 第二个真实业务任务中的 Field-tested 复用；
- Prove 模式的独立评分与用户验收。

## 12. 节点判定

建议判定：**节点 6 通过，但必须带限定语。**

推荐对外措辞：

> FlowPrint has been validated end-to-end on one writable, logged-in Intel macOS Codex CLI environment for plugin activation, conservative classification, schema-gated draft compilation, fail-closed rejection, and scoped implicit triggering. The evidence covers the tested environment and fixtures; ChatGPT GUI distribution, broader platform coverage, and field reuse remain future work.

Windows 证据必须单独陈述：用户随后在真实 Windows CLI 上补齐了最终版本 `0.1.0+codex.20260719135630` 的安装、显式激活、有效 schema `0.3` 编译与 schema `0.2` fail-closed 拒绝。首次最终版隐式触发只加载 FlowPrint，但错误绑定旧节点 5 证据；第二次复测已正确绑定四份最终 Node 6 证据，却因会话从整个 `Downloads` 目录启动而枚举到无关文件名，且审计引用了未实际读取的 compiler contract 和未被最终证据支撑的 WindowsApps 旧知识。故 Windows 的显式链路和最终证据新鲜度已分别获得实机证据，但工作区根安全与审计一致性尚未闭合，仍不能与 macOS 证据合并成“最终版本双平台同范围端到端验证”。

不推荐措辞：

- “FlowPrint 已在所有平台验证”；
- “自动触发准确”；
- “生成 Skill 已被证明有效”；
- “作用域绝不会越界”；
- “支持普通 ChatGPT 网页版”。

## 13. 建议评审重点

请评审同事重点挑战以下问题：

1. frontmatter 中的独占路由规则是否过强，会不会降低合法组合能力？
2. Evidence scope 是否必须在 MVP 中升级为确定性 hook，而不是只靠 Skill 契约？
3. `classification_validator_exit: 0`、`compiler_exit: 1` 的两层门设计是否足够清晰，是否需要拆分命名？
4. 最终隐式触发测试是否应补一个“不要求 audit”的自然任务样本？
5. 是否需要在提交前至少补一个 Apple Silicon 或第二台 Mac 环境？
6. 节点 7 的 Prove 评测应如何避免同模型生成、同模型评分的同源偏差？
7. 哪些限制应进入 README 的 Known Limitations，哪些只保留在工程验收文档？
8. 最终分发 ZIP 的用户侧哈希已闭环；后续若重新打包，是否建立了强制重新校验规则？
9. Windows 隐式触发在新证据缺失时选择了旧节点 5 文件；是否需要增加确定性的证据版本/时间边界，而不能只依赖自然语言 scope gate？
10. Evidence scope gate 是否必须拒绝 Home、Downloads、Desktop、Documents 等过宽根目录，并在递归发现前要求用户切换到项目根？
11. Evidence scope audit 是否需要由工具调用日志确定性生成，避免输出引用未实际读取的规则文件？

## 14. 证据索引

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
- `docs/node-6-validation.md`

## 15. 评审后的状态更新规则

- 发现措辞证据强度不足：先收紧结论，不自动扩大测试结论；
- 发现确定性缺陷：回到节点 6 修复并补对应反例；
- 发现非阻塞残余风险：进入 Known Limitations 与节点 7 风险说明；
- 发现 GUI/普通网页端缺口：列为 Future Work，不描述为当前能力；
- 只有评审意见影响核心安全门、隐式触发或编译正确性时，才重新打开节点 6。

## 16. 第一轮专业评审意见响应

1. **双平台对外措辞：接受核心批评并修正。** Windows 不是完全没有节点 5 证据，但节点 6 文档没有建立同版本、同范围的 Windows 证据链；推荐措辞已改为仅声明一台 Intel Mac 的完整闭环。
2. **最终 ZIP 用户侧哈希：接受并已补证。** 用户 Mac 的独立 SHA-256 与发布值完全一致；运行时版本证据和文件完整性证据仍分别表述。
3. **拒绝后修正重新提交：接受，进入节点 7 待办。** 当前只验证一次性拒绝和确定性影响分析，没有真实 CLI 的完整恢复链。
4. **dependency graph：事实校正。** 依赖图并非缺失；节点 5 已在 manifest 中记录 item、Profile、artifact 与边，`analyze_impact.py` 和集成测试能标记 stale 与完整重验。未完成的是自然语言修改到重新提交的端到端链路，已补入未覆盖范围。
5. **隐式触发措辞：接受。** “没有越界取证”已在同一句中限定为一个中文提示和一次新会话，并指向残余风险 3。
