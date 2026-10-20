# 附录　资料阅读与证据对照 {#source-notes}

资料读取日期：2026-10-19；整理日期：2026-10-20。以下区分原文描述、原文的适用边界，以及本文据此提出的工程判断。本文不把产品介绍中的性能数字视为独立复现实验，也没有运行这些产品的在线调用或性能测试。

## S1．AWS AgentCore 长期记忆深度解读 {#source-s1}

- 原文：[Building smarter AI agents: AgentCore long-term memory deep dive](https://aws.amazon.com/blogs/machine-learning/building-smarter-ai-agents-agentcore-long-term-memory-deep-dive/)。
- 发布日期：HTML 元数据为 2025-10-15。
- 阅读范围：全文，重点为 `How AgentCore long-term memory works`、`Memory consolidation`、`Handling edge cases`、`Performance characteristics`、`Best practices for long-term memory`。

### 原文提供的具体信息

事件进入短期存储后，系统异步提取有价值的信息；这篇文章介绍 Semantic、User preferences、Summary 三种内置策略。不同策略独立处理，同一事件可以产生多条记忆。

合并时先在相同 namespace 和 strategy 内召回语义相近的旧记忆，再由 LLM 判断 ADD、UPDATE 或 NO-OP。旧版本通过 INVALID 标记保留轨迹，系统还处理迟到事件、冲突与部分失败。文章介绍了内置策略的提示词/模型 override 和自管理策略。

### 对方案的贡献

它为“事件 → 异步提取 → 相近候选 → 合并 → 检索”的完整生命周期提供具体产品例子，也提醒应用处理写入到可检索之间的延迟。它支持把当前任务状态与后台长期记忆分开。

### 不能照搬的部分

1. 三种产品策略不能直接映射成语义、情景、程序性三种认知用途。Summary 是摘要策略，不自动代表程序性能力。
2. 文章把 compression rate 定义为 `memory output tokens / full-context tokens`，却把较高数值解释成更强压缩，并将完整历史基线列为 0%。定义、方向和表格展示不一致。本文不据此换算“节省 89%～95% token”。
3. 文中的约 200 ms 检索、触发后 20～40 秒提取合并，属于该文报告的性能观察，不是所有负载的服务保证。
4. 同一评测表中，语义记忆在部分事实问答上的 correctness 低于完整历史 RAG 基线。不能只取压缩结果而省略准确率取舍。
5. 该博客介绍的是当时的服务与策略；当前区域、配额、SDK 和服务等级应在实施时查相应版本的正式文档。

## S2．MachineLearningMastery：三种长期记忆 {#source-s2}

- 原文：[Beyond Short-Term Memory: The 3 Types of Long-Term Memory AI Agents Need](https://machinelearningmastery.com/beyond-short-term-memory-the-3-types-of-long-term-memory-ai-agents-need/)。
- 作者：Vinod Chugani。
- 发布日期：原始页面元数据为 2025-12-30。
- 阅读范围：全文；直接获取遇到超时后使用 Jina 可读镜像，出版元数据与原页面核对。
- 关键章节：`Why Short-term Memory Hits a Wall`、`The Three Pillars of Long-term Agent Memory`、三个记忆类型的小节、`How the Three Memory Types Work Together`。

### 原文提供的具体信息

情景记忆保存过去的事件、动作、环境和结果；语义记忆保存事实、规则和关系；程序性记忆保存技能和多步流程。文章用研究助理说明三者如何协作，并指出不同应用可以赋予不同重点。

它列举向量数据库、关系库、知识图谱、RAG、强化学习、微调与显式工作流等实现方式，但没有规定统一数据库架构。

### 对方案的贡献与边界

适合作为文章的概念入口，帮助读者区分“发生过什么”“知道什么”“怎样做”。它是教育性文章，不是术语标准或生产验收合同。

原文把短期记忆比作应用退出即丢失的 RAM。本文采用更精确的工程定义：线程范围的状态可以持久化；扩大模型上下文也不会自动实现跨会话记忆管理。[\[S3\]](#source-s3)[\[S6\]](#source-s6)

它没有像 Handbook 一样充分展开多租户、权限、删除与血缘要求，因此这些设计内容不归因于该文。

## S3．LangChain：Long-term memory {#source-s3}

- 原文：[Long-term memory](https://docs.langchain.com/oss/python/langchain/long-term-memory)。
- 文档类型：动态更新的官方使用文档；未将访问日期当作发布日期。
- 阅读范围：全文，重点为 `Usage`、`Memory storage`、`Read long-term memory in tools`、`Write long-term memory from tools`。

### 原文提供的具体信息

长期记忆通过 LangGraph Store 保存 JSON 文档，以 namespace 与 key 组织。示例把 store 传入 `create_agent`，工具通过 `runtime.store` 读写，用户身份示例通过 runtime context 提供。

页面展示 InMemoryStore 和 PostgresStore、按 ID 读取、内容过滤，以及配置 embedding 后的语义搜索。它明确提醒生产环境使用数据库支持的 Store，而不是内存字典。

### 对方案的贡献与边界

它提供运行时接入和存储抽象，而非完整的业务记忆治理协议。下列能力仍需应用设计：身份认证、命名空间授权、来源、事实版本、合并规则、删除屏障、评估。

示例中的 embedding 函数返回占位向量，不能直接当成可用检索器。文档示例的模型名、包名与 API 会更新，本文没有把复制出的 SDK 片段声称为已运行代码。

namespace 是组织与查询边界，不能等同访问控制。InMemoryStore 也不因名字里有 Store 就具备进程重启后的持久性。

## S4．Mem0：长期记忆介绍 {#source-s4}

- 原文：[Long-Term Memory for AI Agents: The What, Why and How](https://mem0.ai/library/agent-memory/long-term-memory)。
- 作者：Deshraj Yadav。
- 页面标注更新：2026-09-10。
- 阅读范围：正文至 `Wrapping Up`，不把页面底部推荐文章当作本文内容。

### 原文提供的具体信息

文章使用语义、情景、程序性分类，讨论提取、合并、存储和推理时检索；比较向量与图，并展示 Mem0 的 `add`、`search` 接入思路。它将记忆层的用途与个性化、重复任务、长期交互联系起来。

### 对方案的贡献与边界

适合用来解释独立记忆层和检索流水线，但它同时是厂商的教育与产品介绍材料。正文中的准确率、p95 延迟、token 节省、召回提升和业务改善数字，缺少足以在本方案中独立复现的完整实验条件，因此不作为本文的通用事实或验收标准。

相似度 0.85/0.9、1,536 维、top-k 20、固定融合权重等，是该文的描述或示例，不是与模型和数据无关的最优参数。“记忆必须采用向量或图”“所有生产 Agent 都需要相同架构”也不作为本方案结论。

正文将 RAG 与静态文档联系起来，但 RAG 本身并不限制数据必须静态。本文把记忆视作可通过检索增强使用的一类动态、带主体和生命周期的数据，而不把 RAG 与记忆设为互斥选项。

## S5．阿里云 AI Agent Handbook {#source-s5}

- 主要资料仓库：[aliyun/ai-agent-handbook](https://github.com/aliyun/ai-agent-handbook)。
- 已读取的本地固定版本：`bd70686798d5896952dab9e21f7988a489d1e1b8`，提交日期为 2026-10-10。
- 读取范围：README 与目录结构；重点阅读第 5、8、23 章的记忆、上下文、治理和演进部分，并补读 MiniMax 长周期记忆案例。**未声称通读整个仓库。**
- 只读核对得到远端 HEAD `a5028af381306fd0f65c11f56a18fcbbb814d4f8`。随后获取该 commit 的 README 和第 5、8、23 章：三章内容与本地固定版本的 SHA-256 均一致，README 有变化。下列章节链接保留已读取的本地 commit，相关记忆内容已与该次远端 HEAD 核对；MiniMax 案例仅引用本地固定版本。

### 固定章节链接与采用的内容

| 章节 | 本文采用的主要内容 |
| --- | --- |
| [第 5 章：信息：上下文、状态与可复用能力资产](https://github.com/aliyun/ai-agent-handbook/blob/bd70686798d5896952dab9e21f7988a489d1e1b8/02-build/第%205%20章%20信息：上下文、状态与可复用能力资产.md) | §§5.1～5.6：上下文构造、State/Session/Workspace/Memory 边界、四类功能记忆、写入选择与作用域、证据和修订 |
| [第 8 章：Agent 状态存储与语义资产](https://github.com/aliyun/ai-agent-handbook/blob/bd70686798d5896952dab9e21f7988a489d1e1b8/03-run/第%208%20章%20Agent%20状态存储与语义资产.md) | §§8.1～8.7：持久数据对象、一致性、可恢复性、权威事实与索引、隔离、来源和生命周期 |
| [第 23 章：受控自进化](https://github.com/aliyun/ai-agent-handbook/blob/bd70686798d5896952dab9e21f7988a489d1e1b8/05-optimization/第%2023%20章%20受控自进化.md) | §§23.1～23.7：收集成功/失败经历、可重复实验、与无记忆基线对照，以及提升为 Skill/Workflow |
| [MiniMax 长周期记忆案例](https://github.com/aliyun/ai-agent-handbook/blob/bd70686798d5896952dab9e21f7988a489d1e1b8/06-case-study/第%2028%20章%20客户、销售与运营/MiniMax%20构建海量长周期记忆数据底座的实践.md) | 理解规模化冷热数据与检索需求；不据此要求 MVP 采用相同数据库 |

### 对方案的贡献与边界

这是本方案关于上下文/Harness、来源、权限、遗忘和经验提升的主要工程参考。它说明记忆是运行系统和数据平台的一部分，而不只是模型旁边的向量库。

它不意味着每个系统都应上图数据库、多级存储或独立微服务。本文的 Git/SQLite MVP、字段模式、接口路径、CAS 写入、删除 epoch 和具体验收值，是综合原则后的设计选择，并非 Handbook 逐字给出的实现。

## S6．补充：LangChain Memory conceptual guide {#source-s6}

- 链接：[Memory](https://docs.langchain.com/oss/python/concepts/memory)。
- 阅读原因：由S3 官方页面直接链接，用来补足概念与写入策略。
- 重点：`Short-term memory`、`Semantic memory`、`Episodic memory`、`Procedural memory`、`Writing memories`。

短期状态可以通过 checkpointer 持久化；长期记忆由跨线程的 Store 管理。语义记忆可以采用 profile 或 collection，两者分别把复杂度放在整体更新与检索/合并上。情景记忆可用于检索 few-shot 实例；程序性记忆涉及提示词、代码和权重。在线与后台写入各有实时性、复杂度和延迟取舍。

本文采用其抽象与取舍，不照搬概念页的伪代码作为生产实现。

## 跨来源对照

| 问题 | 来源支持 | 本文判断 |
| --- | --- | --- |
| 需要什么记忆？ | S2/S4/S6 的认知分类；S5 补充 Working Memory | 按用途建模，与表示方式分开 |
| 怎样形成长期记录？ | S1 的异步提取合并；S6 的在线/后台策略 | 显式写少量确定内容，大量推断先进入后台候选 |
| 怎样组织存储？ | S3 的 namespace/key/JSON；S5 的持久对象合同 | 权威内容、事务状态、派生索引分别负责 |
| 何时需要向量或图？ | S2/S4 讨论多种方式 | 先满足隔离与精确查询，再通过评测决定是否增加 |
| 怎样形成可复用方法？ | S5 的受控演进；S6 的程序性记忆 | 经验经过验证和评审后进入版本化能力资产 |
| 怎样证明收益？ | S1 的准确率与压缩取舍；S5 的基线实验 | 把准确、误用、成本、延迟、删除和隔离一起评估 |

## 阅读与验证说明

AWS、LangChain、Mem0 原始 HTML 和正文已在资料整理过程中获取并读取。MachineLearningMastery 通过可读镜像获取全文，原页面用于核对元数据。Handbook 使用固定版本的相关章节，其中第 5、8、23 章另与远端固定 commit 核对一致；不把仓库规模或案例中的收益当作通用结论。

电子书不依赖临时阅读目录，也未收入第三方全文。附录保留原创综合、来源链接、固定版本及阅读边界；所有外部资料的版权归各自作者所有。
