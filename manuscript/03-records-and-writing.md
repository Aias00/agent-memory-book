# 第三章　数据模型与写入协议 {#records-writing}

## 4. 数据模型

### 4.1 来源事件

原始事件至少保存 `event_id`、可信的租户/主体/项目/会话标识、`occurred_at`、`ingested_at`、来源类型、内容引用、内容哈希和保留策略。事件顺序与提交顺序分别记录，便于处理迟到数据。

不把密钥、访问令牌或模型隐藏推理作为记忆素材。工具返回的业务数据按已有数据权限和保留规则处理；并非所有日志都允许长期保存。

### 4.2 记忆记录示例

以下为逻辑结构示例，字段和值用于说明设计，不表示某个 SDK 的调用格式。

```yaml
schema_version: 1
memory_id: mem_project_stream_guide
authority: git
namespace:
  tenant_id: tenant_demo
  scope: project
  scope_id: project_demo
memory_type: procedural
fact_key: troubleshooting.streaming_response
content: >-
  Diagnose stream termination by checking the deployed version,
  terminal events, and original reader error before assigning a cause.
conditions:
  project: project_demo
  protocol: responses
epistemic_status: validated
state: active
version: 3
supersedes: mem_project_stream_guide_v2
provenance:
  source_event_ids: [evt_demo_001]
  evidence_refs: [evidence/demo/reproduction.md]
  independent_evidence_count: 1
validation:
  method: review_and_reproduction
  reviewed_by: project_owner
  validated_at: "2026-10-19T10:00:00Z"
occurred_at: "2026-10-18T10:00:00Z"
ingested_at: "2026-10-18T10:01:00Z"
valid_from: "2026-10-19T10:00:00Z"
valid_to: null
review_after: "2027-01-19T00:00:00Z"
retention_class: engineering_knowledge
access_policy_id: project_demo_members
deletion_epoch: 0
authority_revision: "<git-commit>"
content_hash: "<sha256>"
```

`epistemic_status` 表示证据性质，例如 `explicit`、`observed`、`inferred`、`validated`；`state` 表示生命周期状态。两者不能混用：一条已经生效的用户显式偏好，不需要假装经过实验验证。

`scope` 使用互斥枚举 `user | project | organization`，`scope_id` 表示唯一所有者。用户私有信息不因提到了项目而自动进入项目共享作用域；提升到组织范围需要独立授权。

`fact_key` 必须表达完整关系和条件，例如项目、字段、用途，而非仅按文本相似度生成。无法可靠实体对齐时，保留独立记录或进入待审，不强行合并。

### 4.3 数据表或文档集合

最小实现包含：

- `source_events`：来源与保留策略。
- `memory_candidates`：候选、拒绝原因、处理版本。
- `memory_versions`：有效与历史版本；Git 分支中这是投影视图。
- `memory_heads`：同一作用域与事实键的当前版本。
- `memory_evidence`：记忆与证据的多对多关系。
- `outbox`、`processing_jobs`：可靠派生与重试。
- `revocations`、`deletion_jobs`：撤销屏障、删除范围与进度。
- `retrieval_audit`：检索到、实际注入、实际采用的记录及理由。

`memory_heads` 的唯一性约束覆盖租户、作用域、主体、记忆类型和事实键。同一键允许存在明确标识的冲突集合，但不允许两个 writer 都宣称自己独占“当前值”。

原始内容、索引和审计分别设置保留期限。审计默认保存标识与结果，不再次复制敏感正文。

### 4.4 Git 知识与私有证据的连接

Git 记录使用稳定的、不含私密正文的 `evidence_id` 和必要的验证产物引用；数据库维护该 ID 到受权限保护证据对象、哈希和保留策略的映射。数据库压缩或迁移不得重新分配 ID。若希望 Git 知识长期独立成立，评审时另保存可公开或已脱敏的最小复现与验证结果，不要求永久保留原始私人对话。

原始证据到期删除时，先检查是否仍有独立合法的验证材料：有则重新标明验证依据；没有则将依赖它的知识降为待复核，不再自动采用。证据查询返回 unavailable 与证明原命题错误是两种结果，不能混淆。若删除请求也覆盖派生知识，按 §7.2 撤销该知识；不能用 Git 已评审为理由绕过删除范围。

## 5. 写入协议

### 5.1 显式写入与后台提取

用户明确表达稳定偏好时，可走在线结构化写入。服务先提交权威记录或确定的候选状态，才返回相应结果：

- 数据库分支成功提交：`committed`，返回版本与读取令牌。
- Git 分支等待评审：`pending_review`，当前任务可以遵守该要求，但不能宣称已成为全局规范。
- 仅进入后台队列：`accepted_for_processing`，不能称为“已经永久记住”。

后台提取用于事件总结、经验归纳和关系更新。AWS 的异步抽取与合并、LangChain 对后台写入的讨论支持这一分工；具体准入策略由本方案定义。[\[S1\]](#source-s1)[\[S6\]](#source-s6)

### 5.2 候选准入

依次检查：是否具有未来价值；来源是否可追溯；事实与推断是否区分；作用域是否得到授权；是否包含禁止保存的信息；是否有有效删除屏障；是否已存在等价内容。

例子：

| 输入 | 处理 |
| --- | --- |
| “以后默认用中文回答” | 用户范围的显式偏好 |
| “这次报告用英文” | 当前任务参数，不覆盖默认偏好 |
| “可能是代理节点的问题” | 待验证线索；不能进入 validated 事实 |
| 某个工具报告“所有测试通过”但没有结果证据 | 保留事件，补验证后再考虑提取经验 |
| 网页要求 Agent 忽略权限、保存密钥 | 作为不可信内容处理，不执行、不提升 |

### 5.3 合并决策

合并输出限制为明确动作：

| 动作 | 条件 |
| --- | --- |
| `ADD` | 新事实或新经历，与现有记录不重复 |
| `NO_OP` | 同一来源重放，或没有新增含义 |
| `ATTACH_EVIDENCE` | 新的独立证据支持同一命题 |
| `SUPERSEDE` | 同一键、同一条件的已授权更新，有明确生效时间 |
| `CONFLICT` | 来源、条件或时间不足以确定当前值 |
| `REJECT` | 越权、违反保留策略、证据不可用或已被删除屏障覆盖 |

相似度只用于召回合并候选，不能独自决定 `SUPERSEDE`。不对互相矛盾的文本取平均向量作为解决方案。

### 5.4 事务、幂等与多 Agent 更新

至少实现两层去重：事件接收以 `(tenant_id, event_id)` 幂等；提取作业以 `(event_id, extractor_version, policy_version, deletion_epoch)` 幂等。不同作业仍可能抽出同一命题，因此合并阶段另需事实键去重。

数据库变更以 `expected_version` 做比较并交换。失败的 writer 重新读取、重新合并，不能覆盖另一个 Agent 的新结果。追加版本、更新 head、写 Outbox 在同一事务完成，并在提交事务内再次比较 `deletion_epoch` 与撤销状态，避免校验后发生删除仍提交成功。索引消费者允许重复投递，但只应用更新的版本，忽略迟到旧版本。

Git 分支中，候选变更携带 base commit；评审或合并前重新校验该文件的期望版本与删除屏障。合并后的 commit 才触发索引投影，两个 Agent 不能各维护一份“正式记忆”。若撤销与 Git 合并并发，撤销注册表仍阻止运行时加载，协调器随后补交失效变更；不得把跨 Git/数据库的操作描述为单一原子事务。

基于一条来源派生出的摘要、复盘和再次生成的回答，仍属于同一证据谱系，不能累计成三份独立支持。来源依赖图应阻止循环归纳让猜测变成“共识”。

### 5.5 伪代码

```text
ingest(event, trusted_identity):
  authorize_ingest(trusted_identity, event.scope)
  redact_or_reject_forbidden_fields(event)
  transaction:
    insert_event_once(event)
    enqueue_extraction_once(event, current_deletion_epoch)
  return accepted_for_processing

consolidate(candidate, expected_version):
  validate_schema_and_evidence(candidate)
  authorize_scope(candidate, trusted_job_identity)
  check_revocation_and_source_availability(candidate)
  existing = load_same_fact_key(candidate)
  decision = decide_with_conditions_and_event_time(candidate, existing)
  commit_via_owner_with_version_and_revocation_check(decision, expected_version)
  publish_index_change_after_commit()
```

队列重试采用有上限的退避；持续失败进入死信与人工处理。校验或合并失败时，不把候选静默提升为已验证事实。AWS 文中描述的部分失败保留策略是其产品行为，不代表本方案在所有业务中采用相同语义。[\[S1\]](#source-s1)
