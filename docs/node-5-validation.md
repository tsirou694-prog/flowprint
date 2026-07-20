# FlowPrint 节点 5：Skill 编译器阶段验收记录

日期：2026-07-17  
当前修订版本：`0.1.0+codex.20260717090647`  
状态：按节点 5 既定工程与前向验收范围通过

## 当前结论

节点 5 按既定工程与前向验收范围通过。在已测试输入上，编译器会实际调用分类校验器，只有 schema `0.3` 且所有高风险项均有显式用户确认的 `ready` 输入能够生成草案；坏数据、未确认状态和校验器缺失均会拒绝，并且不会留下请求的输出目录。真实 Windows CLI 还验证了有效编译、旧 schema 拒绝、PowerShell 解释器发现，以及三个语言风险场景和针对所发现缺陷的回归。

该结论不代表自然语言分类已经普遍可靠，不代表兼容所有 Windows 配置，也不代表生成 Skill 已安装、通过第二个真实任务复用或达到 Field-tested 状态。

## 实现结构

- `validate_classification.py`：支持 `0.2` 未确认分类与 `0.3` 显式确认记录。
- `compile_skill.py`：通过子进程调用分类校验器，在私有暂存目录生成并预检，成功后才发布草案目录。
- `validate_generated_skill.py`：FlowPrint 自有的生成结构预检，不冒充官方市场认证。
- `analyze_impact.py`：比较分类项指纹，返回变化项、过期产物、Profile 状态与重测范围。
- `flowprint-manifest.json`：记录分类项、Profile 版本、item→artifact 和 profile→artifact 依赖边、文件哈希及权限状态。

## 权限状态

节点 5 明确区分：

1. `compile_state: draft`：仅代表草案文件生成；
2. `install_state: not_authorized`：没有安装授权，也没有安装；
3. `external_actions_authorized: false`：生成或安装均不授权提交、上传、发布、部署或消息发送。

节点 5 的真实 CLI 测试必须验证“系统已有生成能力但在校验失败时主动停止”，这与节点 4 因尚无生成能力而没有生成文件不同。

## 本地测试结果

执行：

```text
python3 -m unittest -v tests/test_classification.py tests/test_compiler.py
```

结果：26 项通过，其中：

- 16 项分类 schema、确认映射、规则文档和 Windows 启动器契约测试；
- 10 项真实编译入口与影响分析集成测试。

负向集成场景包括：

- 数字置信度字段；
- R1 个体偏好污染 Core；
- Failure Lesson 缺少 `abstracted_rule`；
- 高影响项绕过复核；
- 共享问题漏掉 `item_id`；
- 有效但仍为 `needs_review` 的输入；
- 保存原始对话；
- 分类校验器缺失。

每项均断言非零退出、可定位的错误信息、目标草案目录不存在、私有暂存目录已清理。

有效编译样本还通过：

- FlowPrint 生成结构预检；
- 开发环境随附的 Skill `quick_validate.py` 结构检查。

后者是开发期结构证据，不等同于市场认证、任务效果或跨环境兼容性证明。

## 依赖与修改影响

当前 manifest 显式记录：

- Profile `default` 的版本与来源 item；
- 每个生成文件依赖的分类 item；
- `SKILL.md` 对 Profile 版本的依赖；
- 依赖边和生成文件哈希。

Profile 或高影响项变化时，影响分析会把 Profile 文件及依赖它的 `SKILL.md` 标为 stale，并要求完整重新验证。新增分类项会根据其 layer 映射到应重新生成的产物。

该机制只负责确定性差异与影响传播，不声称能判断自然语言修改在语义上必然“轻微”。

## 不属于本节点、仍未完成

- 生成草案的安装体验验证；
- 第二个不同对象真实任务的复用与效果评测；
- Tested / Field-tested 状态升级；
- 否定/反讽和单图误升格为 Profile 两类尚未执行的前向风险场景；
- 多个已安装 Skill 的宿主路由隔离，其中一次测试曾无关触发 1Password。

这些事项进入节点 6 或后续 Prove 评测，不能因节点 5 通过而视为完成。

## 真实语言边缘场景

### 后续修正覆盖早期要求 — 通过（单一样本）

原始摘要证据：`tests/evidence/windows-cli-node5-edge-later-correction.txt`。

在该测试提示中，最终“无尾或短尾”进入老三 Profile，已明确作废的“明显长尾”没有残留为 Run Parameter 或有效规则；系统还提取了“按时间维护有效要求集”的 Failure Lesson。因 Profile 为高影响项，状态保持 `needs_review` 并提出一个确认问题。输入没有最终成品，因此 evidence inventory 标记 `result no`，这一点符合证据范围。

该结果仅支持此单一样本中的时序覆盖行为，不外推为所有修正、否定或长上下文均可靠。

### 最终决定缺失 — 部分通过（单一样本）

原始摘要证据：`tests/evidence/windows-cli-node5-edge-missing-decision.txt`。

核心风险处理符合预期：系统没有猜测红色或蓝色，把颜色保留为 `ambiguous` Run Parameter，状态为 `needs_review`，并提取了“摘要压缩可能丢失最终决定”的 Failure Lesson。

同时发现一个真实缺陷：本轮“不要生成或编译”的当前会话指令被提升为高影响、可复用的 Permission Boundary，并再次要求用户确认。该指令应被直接服从，不需要重复确认，也不应污染沉淀出的工作流。因此此场景整体只记为部分通过；需要收紧 R8/权限分类规则并增加回归测试。

### “通常 / 尽量 / 必须”强度区分 — 核心通过，有证据库存偏差（单一样本）

原始摘要证据：`tests/evidence/windows-cli-node5-edge-modality-strength.txt`。

三档约束得到区分：“通常圆角”成为可例外的品牌 Profile 候选并进入复核；“这次尽量暖色”成为低影响 Run Parameter；“Logo 安全区必须保留”保持专业硬约束语义。核心强度测试在该样本上通过。

但 evidence inventory 标记 `result yes`，而提示只包含约束，没有可见的最终成品或验证结果，因此证据库存偏乐观。还观察到宿主额外触发了与本任务无关的 1Password Skill；它没有读取密钥，但属于宿主技能路由噪声，应作为节点 6 的分发/演示隔离风险，而不是混入 FlowPrint 分类准确率结论。

## 前向测试后的修订

版本 `0.1.0+codex.20260717090647` 增加：

- `run_flowprint.ps1`：在 Windows 上验证候选解释器并搜索本机 Python 安装，不信任仅存在但无法启动的 WindowsApps alias，也不会安装软件；
- 去情境化规则：当前会话的“只预览 / 不编译 / 不保存”只作为本轮执行范围直接服从，不进入六个持久分类层，也不要求重复确认；
- 证据规则：只有可见的最终/已接受输出、产物、验证结果或明确的达成结果描述才能令 `result=yes`；仅称任务完成或只给要求不够。

本地分类、编译、插件与 Skill 回归共 26 项通过。用户 Windows 环境随后完成三项修订版回归，摘要证据见 `tests/evidence/windows-cli-node5-regressions-final.txt`：

- PowerShell 启动器成功找到可用的本机 Python，并完成分类校验；
- 当前会话“只预览/不编译”被服从但没有进入持久分类层，也没有产生重复确认；
- 无成品证据时 `result no` 并返回 `needs_completed_task`；加入明确达成结果描述后，`result yes` 与 `artifacts no` 得到区分，三档约束强度仍保持。

因此前向测试发现的两个可控缺陷均在修订版本上回归通过。

## 真实 Windows CLI：有效输入

用户在已登录 Windows Codex CLI 中使用安装缓存版本 `0.1.0+codex.20260717083300` 编译 schema `0.3` 的已确认样本。原始摘要证据：`tests/evidence/windows-cli-node5-valid-compile.txt`。

在该样本上：分类校验退出码和编译退出码均为 0；`SKILL.md`、manifest 与 compile record 均生成；`install_state` 为 `not_authorized`，`install_performed` 与外部操作授权均为 false。没有执行安装、提交、上传或发布。

该测试还暴露出 Windows 入口兼容性摩擦：系统存在 Python 3.13，但 `python3` 启动器未登记，首次入口调用返回 112。Codex 随后定位真实解释器并成功完成。它不影响本次编译逻辑的通过判定，但不能描述成“入口无条件一次成功”；需要在最终分发前增加解释器发现或跨平台启动层。

## 真实 Windows CLI：旧 schema 拒绝

用户要求真实编译入口原样处理 schema `0.2`、没有 schema `0.3` 确认记录的输入，并明确禁止修复、升级或绕过校验。原始摘要证据：`tests/evidence/windows-cli-node5-rejection.txt`。

在该样本上：编译器退出码为 1，拒绝 gate 为 `confirmation_schema`；目标目录不存在，相关草案、manifest 或可安装产物数量为 0；输入没有被修改，模型没有伪造 `confirmed_by: user`。这支持“该真实编译入口在已测试的未确认旧 schema 输入上 fail closed”，不外推到所有恶意输入或所有 Windows 环境。

## 节点 5 关闭判定

既定条件完成：

1. 真实 CLI 有效 schema `0.3` 输入生成草案但没有安装；
2. 真实 CLI 旧 schema/未确认输入被拒绝且无目标产物；
3. 三个语言风险场景完成并如实记录了通过、部分通过与缺陷；
4. 发现的会话范围污染和 result 证据偏差已修订并在 Windows 回归；
5. PowerShell 启动器在用户环境通过；
6. 依赖图、影响分析、坏数据真实编译入口测试和生成/安装/外部操作权限分离均有确定性证据。

节点 5 正式关闭。结论限定为上述样本与环境，不外推统计准确率或真实复用效果。
