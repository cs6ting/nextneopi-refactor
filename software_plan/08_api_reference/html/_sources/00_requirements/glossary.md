# 术语表

| 术语 | 定义 |
|---|---|
| Adapter | 将第三方工具原生命令、文件和错误转换为项目统一契约的 Python 实现。 |
| Allele identity | 规范化后的变异身份，至少由 reference build、序列位置、REF、ALT 和 normalization 规则确定；可参考 GA4GH VRS。 |
| Artifact | 可寻址、可校验、携带 provenance 的文件或结构化结果。 |
| AssayDesign | 描述 WES/WGS、capture targets、callable policy 和 coverage denominator 的领域对象。 |
| Capability | 稳定的科学职责及其输入输出语义，例如 `TypeHla`。 |
| CapabilitySelector | 根据配置、输入和 descriptor 选择兼容 implementation 的应用服务。 |
| Case | 同一患者/分析单元下可关联 tumor、normal 和 RNA 样本的领域实体。 |
| Characterization test | 在重构前固定旧实现实际行为的测试；不代表该行为一定科学正确。 |
| Collector | adapter 生命周期中解析原生输出并生成 typed result 的阶段。 |
| ContainerRuntime | 执行固定镜像的端口；目标实现为 Apptainer。 |
| Contract test | 验证实现遵守接口输入、输出、状态、命令计划和错误语义的测试。 |
| CCF | Cancer Cell Fraction，携带某变异的肿瘤细胞比例估计。 |
| DAG | Directed Acyclic Graph，任务依赖有向无环图。 |
| Descriptor | 插件的版本、能力、资源、容器、许可和 schema 元数据。 |
| ExecutionBackend | 将通用任务图映射到 local 或 Slurm 的端口。 |
| Implementation | 某 capability 的具体实现，例如 `mutect2` 实现 `CallSomaticSmallVariants`。 |
| Native artifact | 第三方工具直接生成、尚未规范化的工件。 |
| Normalized artifact | 经 collector/domain transform 转成稳定 schema 的工件。 |
| Plan | 完成校验和插件选择后生成的不可变任务图及资源/容器请求。 |
| Policy | 与工具实现分离的科学决策，例如 primary-confirmed consensus 或 purity fallback。 |
| Provenance | 工件与任务的输入、参数、版本、容器、参考、父子关系和状态记录。 |
| Recipe | 由 capability 组成的应用级流程，例如 `wes_dna_canonical`。 |
| ReferenceBundle | 同一 build/annotation 语义下的 FASTA、索引、字典、数据库和模型集合。 |
| Scientific equivalence | 在规范 identity、字段和预定义容差下，新旧流程结论相等或可解释一致。 |
| Site profile | 与机构集群有关的 partition、account、scratch、并发和挂载配置。 |
| Typed empty | 成功执行但无科学记录的结果，状态为 `EMPTY`，并仍具有合法 schema/provenance。 |

## 状态术语

- `MATERIALIZED`：成功生成非空或允许为空的可用工件。
- `EMPTY`：任务成功，合法结果集合为零。
- `NOT_REQUESTED`：recipe/config 未要求该能力。
- `SKIPPED_UNSUPPORTED`：输入或 implementation 明确不支持，且 policy 允许跳过。
- `FAILED`：请求过该能力，但执行或结果验证失败。

## 样本角色

`TUMOR_DNA`、`NORMAL_DNA`、`TUMOR_RNA` 是规范角色；旧 manifest 中的 `tumor_DNA`、`normal_DNA`、`tumor_RNA` 在输入边界归一化。`sample_id` 与 `case_id` 必须分离，禁止用删除 map 字段的方式隐式构造 join key。