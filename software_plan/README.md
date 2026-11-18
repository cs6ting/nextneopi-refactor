# nextNEOpi Python 重构设计文档

## 目的

本目录是 nextNEOpi 重构研发的设计基线。目标不是逐行翻译 `nextNEOpi.nf`，而是把现有肿瘤新抗原流水线拆分为具有稳定科学语义、版本化输入输出和可替换实现的 Python 能力接口。第三方算法由 Python adapter 调用，并在固定 OCI digest 的 Apptainer 容器中运行。

本文档集描述目标设计、测试和迁移策略。旧版行为以提交 `9f34698` 的 [`nextNEOpi.nf`](../nextNEOpi.nf)、[`conf/`](../conf/) 和 [`bin/`](../bin/) 为参考。通过旧版运行记录确认静态分析发现的边界问题，再决定兼容还是修正。

## 从哪里开始

1. [第一层功能拆分](02_modules/first-layer-functional-design.md)给出 7 个计算功能组、跨组产物和首轮常规候选验证范围。
2. [第二层算法清单](02_modules/second-layer-algorithm-inventory.md)逐项说明 32 个算法单元和规则的目标、当前实现、替代候选和验证方法。
3. [模块地图](02_modules/module-map.md)把两层分析对应到现有 `MOD-01～14`。接口和实施工作继续使用原有 `MOD-*`、`IF-*` 编号。
4. [增量迁移路线](07_migration/incremental-roadmap.md)列出旧版基线、首轮交付和候选试点。[科学等价测试计划](05_testing/scientific-equivalence-plan.md)说明如何区分同方法回放与新方法性能对照。

## 已确认的设计基线

- 所有自研控制逻辑和业务逻辑最终使用 Python。
- BWA、GATK、VEP、ASCAT、Sequenza、pVACtools 等第三方算法不重写。
- 同一科学 capability 可有多个 implementation；能力差异必须显式声明。
- 配置分离 `workflow`、`methods`、`policies`、`reference`、`execution` 和 site profile。
- 提供 CLI、Python SDK、本地及 Slurm 执行。
- 支持 DAG、scatter/gather、缓存、resume、重试、部分 case 失败继续和 provenance。
- 首期纵向切片是配对 WES DNA 到 canonical 新抗原报告。
- 首个科学检查点是 pVACseq 常规候选全量表和过滤表。首期交付还包含聚合、初版报告和现有运行验收项。
- 同方法迁移按规范化实体、过滤判定和约定容差验证。替代算法按独立真值、覆盖率和对下游的影响评估。

## 文档导航

| 主题 | 入口 |
|---|---|
| 范围、需求与术语 | [`00_requirements/`](00_requirements/scope-and-goals.md) |
| 总体架构与 ADR | [`01_architecture/architecture-overview.md`](01_architecture/architecture-overview.md) |
| 模块边界 | [`02_modules/module-map.md`](02_modules/module-map.md) |
| 接口与插件契约 | [`03_interfaces/interface-conventions.md`](03_interfaces/interface-conventions.md) |
| Python Reference API（实现入口） | [`08_api_reference/README.md`](08_api_reference/README.md) |
| 配置、CLI、状态和 Schema | [`04_specifications/configuration-specification.md`](04_specifications/configuration-specification.md) |
| 测试与科学等价 | [`05_testing/test-strategy.md`](05_testing/test-strategy.md) |
| 质量门禁 | [`06_quality/quality-gates.md`](06_quality/quality-gates.md) |
| 增量迁移路线 | [`07_migration/incremental-roadmap.md`](07_migration/incremental-roadmap.md) |
| 需求追踪 | [`00_requirements/traceability-matrix.md`](00_requirements/traceability-matrix.md) |
| 离线阅读 | [Reference API 打包说明](08_api_reference/README.md#离线文档) |

## 约束性语言

- **必须**：研发和验收不可省略。
- **应该**：默认遵守，偏离时必须记录 ADR。
- **可以**：可选扩展，不构成当前验收条件。

## 编号规则

`REQ-FUN-*` 表示功能需求，`NFR-*` 表示非功能需求，`ADR-*` 表示架构决策，`MOD-*` 表示模块，`IF-*` 表示接口，`ART-*` 表示工件，`CFG-*` 表示配置，`TST-*` 表示测试，`ACC-*` 表示验收条件，`RISK-*` 表示风险。

## 文档维护规则

1. 设计变更先更新需求或 ADR，再修改模块、接口和测试。
2. 每个接口必须能追踪到模块、配置、测试及验收条件。
3. 每个插件必须接入至少一个 recipe，不接受孤立实现。
4. 代码与文档不一致时，发布门禁失败；不得用“实现为准”绕过评审。
5. 科学语义变更必须由生物信息学负责人批准并补充等价或差异报告。

## 当前状态

状态：**设计基线草案**。完成 [`05_testing/acceptance-test-matrix.md`](05_testing/acceptance-test-matrix.md) 中相应门禁并获得评审后，单个模块才可进入正式实现。

BWA-MEM2、SpecHLA 和新版 NetMHCpan / NetMHCIIpan 是优先对照候选。当前资料为设计与源码核对，候选尚无本项目基准结果。
