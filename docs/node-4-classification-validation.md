# FlowPrint 节点 4：去情境化分类引擎验收记录

日期：2026-07-17  
版本：`0.1.0+codex.20260717075254`

## 结论

节点 4 按预定的机制与集成验收范围通过。证据范围是两个预设夹具和一次用户真实 Windows Codex CLI 前向测试（任务样本 N=3），足以证明分类契约、确定性风险门、预览渲染与安装后的调用链能够工作，但不代表六层分类已经在大量真实任务上达到统计意义上的准确率。实机样本中的六层分类符合预期，并在两项用户确认后由 `needs_review` 转为 `ready`。

## 已实现的机制

- 六层分类：Core Workflow、Domain Knowledge、Profile、Run Parameters、Failure Lessons、Permission Boundaries。
- 不使用模型自报数字置信度，改用可枚举的 `rule_hits`、证据状态和影响等级。
- 高影响、含糊、冲突、仅靠视觉推断的 Profile，以及权限项不得静默通过。
- 确认卡最多三个问题，且必须覆盖所有需要复核的项目。
- 原始对话不得写入分类产物。
- 节点 4 只分类，不生成、安装或发布最终 Skill。

## 确定性校验

校验器：`skills/flowprint/scripts/validate_classification.py`

主要硬门包括：

- 禁止 `confidence`、`probability`、`certainty` 类字段；
- `ambiguous` / `conflicting` 或 `high` impact 必须进入复核；
- Core Workflow 不得由“只出现一次的偏好”规则直接支撑；
- 仅视觉或模型推断的 Profile 必须复核；
- Permission Boundary 必须是高影响且进入复核；
- Failure Lesson 必须包含抽象后的防错规则；
- `review_item_ids` 与确认问题必须严格一致；
- 确认问题不得超过三个；
- `raw_transcript_stored` 必须为 `false`。

## 测试证据

执行：

```text
python3 -m unittest -v tests/test_classification.py
```

结果：10 项通过。

测试样本：

1. 微信表情包任务：验证角色个体尾巴特征进入 Profile、数量进入 Run Parameters、发布进入 Permission Boundaries。
2. 文档迁移任务：验证模板结构、DOCX 规则、个人写作偏好和本次文件参数能正确分层。

此外，Skill 结构快速校验、插件 manifest 校验和隔离 `CODEX_HOME` 安装均通过。

## 真实 Codex CLI 前向测试

测试环境：用户已登录的 Windows Codex CLI。  
测试场景：老三柯基微信表情包制作与投稿物料准备。  
原始证据：`tests/evidence/windows-cli-node4-classification.txt`。

结果：

- 角色身份检查进入 Core Workflow；
- 微信导出约束进入 Domain Knowledge，且没有虚构缺失的具体规格数值；
- “老三无尾或短尾”只进入 Profile，没有泛化为所有柯基；
- “8 张”和“当前只准备物料”进入 Run Parameters；
- 动画过快、透明边缘白边和个体特征误泛化进入 Failure Lessons；
- 实际提交、上传或发布被识别并归入需要复核的 Permission Boundaries；本节点没有执行能力，因此不把该结果表述为“成功拦截”；
- 初始状态为 `needs_review`，仅提出两个会改变复用边界的问题；
- 用户确认后状态转为 `ready`；
- 输出没有数字置信度。节点 4 未生成最终 Skill，但这是当前能力边界形成的结构性结果，不是对“系统已有生成能力但主动停止”的行为验证。

一个高风险 Failure Lesson 与对应 Profile 共享同一确认问题。这符合机器契约允许一个问题关联多个 `item_ids` 的设计；节点 5 保存机器结果时必须显式记录该关联，不能只依赖用户界面的语义推断。

## 已知局限

- 规则命中仍依赖模型理解自然语言，确定性脚本只能检查分类结果是否遵守契约，不能保证模型第一次理解必然正确。
- 图片中的角色特征属于高风险证据，当前必须通过可见文本或用户确认才能稳定进入 Profile。
- 当前测试证明的是结构与风险门行为，不代表分类器已经在大量真实任务上达到统计意义上的准确率。
- “Tested”状态、跨任务复用计数和依赖图属于后续节点，不在本节点中宣称已经完成。

## 本节点没有证明的事项

- 未证明分类器在大样本或跨领域分布上的普遍准确率；当前任务样本数为 3。
- 未证明执行权限门能在系统已经具备外部操作能力时真正阻止未授权动作；这里只证明了权限动作被正确识别和归类。
- 未证明编译器在已经具备 Skill 生成能力时会因分类校验失败或用户未确认而主动停止；节点 5 必须重新进行行为验证。
- 未覆盖否定/反讽、后续修正覆盖早期要求、上下文缺口、单图误升格为 Profile，以及“通常/尽量/必须”强度混淆等高风险边缘场景。

## 实机验收结果

用户已在真实 Codex CLI 中运行 `CLI-TEST.md` 的老三表情包样本：

- 六层均出现且没有明显错层；
- 老三尾巴特征只进入 Profile，不污染 Core 或 Domain；
- 本次数量进入 Run Parameters；
- 发布/提交进入 Permission Boundaries；
- 状态为 `needs_review`，确认问题不超过三个；
- 不出现数字置信度；
- 按节点 4 当前能力边界未生成最终 Skill；该项不计作“已有生成能力但主动停止”的行为验证。

以上属于节点 4 既定范围的标准均已满足。节点 4 正式关闭；未验证事项已转入 `docs/node-5-acceptance-criteria.md`，不能因节点 4 通过而视为自动满足。
