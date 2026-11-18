# nextNEOpi Reference API 总览与开发指引

> 设计版本：`0.1` · Python API 基线：`v1` · 状态：Proposed（设计基线，尚无可导入实现）

本文件是 [Reference API](README.md) 的导读：说明这套接口按什么规则设计、分为哪些主要接口，以及后续如何依据接口开展实现。它定义的是重构后 `nextneopi` Python package 的公共契约，是写代码、写测试、写插件时直接对照的规范，而非当前已存在的实现。

## 1. 定位

- 目标不是逐行翻译现有的 `nextNEOpi.nf`，而是把肿瘤新抗原流水线拆分为具有稳定科学语义、版本化输入输出、可替换实现的 Python 能力接口。
- 自研控制与业务逻辑用 Python；BWA、GATK、VEP、ASCAT、Sequenza、pVACtools 等第三方算法不重写，由 Python adapter 在固定 OCI digest 的容器中调用。
- 同一科学 capability 可以有多个 implementation，能力差异必须显式声明。
- 组织方式参考 PyTorch Reference API：顶层按 namespace 建索引，每个 namespace 页先给 API Summary 表，再逐个符号展开签名、参数、返回、异常与示例。

## 2. 设计规则

规则集中在 [API 使用约定](api-conventions.md)，核心如下。

### 2.1 契约优先、类型优先

- 跨边界数据一律用 Pydantic `BaseModel`，默认 `extra="forbid"`。
- ID 使用 `NewType`/受限字符串，禁止 `CaseId` 与 `SampleId` 之类互换。
- 公共签名禁止无约束 `Any`，禁止 `dict[str, Any]`、裸路径、通用 `run_tool()` 等绕过类型的逃逸口。
- 集合参数优先 `Sequence`/`Mapping`，返回不可变 `tuple`/`mapping`。

### 2.2 大文件不进内存、不进签名

- FASTQ/BAM/VCF 等大型工件只通过 `ArtifactRef[T]` 传递，`T` 是该持久工件的轻量 descriptor schema。
- adapter 通过 `ArtifactStore.read_descriptor()` 按需读取 descriptor，不在接口间传递字节。

### 2.3 明确的五态结果模型

- `ArtifactRef` 只表示已提交的工件，状态限 `MATERIALIZED` / `EMPTY`。
- 业务五态由 `ResultSlot[T]` 和最外层 `ResultEnvelope[T]` 承载：`MATERIALIZED`、`EMPTY`、`NOT_REQUESTED`、`SKIPPED_UNSUPPORTED`、`FAILED`。
- `MATERIALIZED/EMPTY` 必须有 typed value；后三种 value 必须为 `None` 且带 `ResultReason`。
- 禁止用缺文件、空字符串、`0`、`None` 模拟状态；配置/编程错误走 [`NextNeoPiError`](errors.md) 并携带可序列化 `ErrorRecord`。

### 2.4 统一生命周期与副作用纪律

科学接口是泛型协议 `CapabilityImplementation[RequestT, ResultT]`，统一三段式：

```python
class CapabilityImplementation(Protocol[RequestT, ResultT]):
    descriptor: PluginDescriptor
    def validate(self, request: RequestT, context: PlanningContext) -> ValidationReport: ...
    def plan(self, request: RequestT, context: PlanningContext) -> ExecutionSubgraph: ...
    def collect(self, execution: ExecutionRecord, context: CollectionContext) -> ResultEnvelope[ResultT]: ...
```

- `validate()` 无副作用；`plan()` 只生成不可变任务图；只有执行 backend 能真正跑任务；`collect()` 只读取声明输出并经 ArtifactStore 原子提交。
- 正式运行不联网、不安装、不 patch、不写输入或 reference。

### 2.5 自研与第三方分层

- 纯 Python 实现产出 `PythonTaskSpec`；第三方工具 adapter 产出 `ContainerTaskSpec`（固定 digest 的容器）。
- 两者都不能直接提交 Slurm，统一由执行 backend 调度。

### 2.6 版本化兼容

- 类型或科学语义破坏升 contract major；新增 optional 字段升 minor；仅文案/非语义修正升 patch。
- 序列化字段名与错误码属于兼容面，变更需同步升版。

### 2.7 稳定性与文档模板

- 每个符号标记 `Stable` / `Beta` / `Experimental` / `Internal`，规则见 [stability.md](stability.md)；当前处于设计阶段，实现状态均为 `NOT_IMPLEMENTED`。
- 每个 API 符号必须记录：完整签名、stability 与 Interface ID/contract version、一句话用途与非职责、Parameters/Returns/Raises、前置条件与数据不变量、capability/实现差异、status/scatter/resource/cache/provenance、Example、对应测试与验收。

## 3. 接口分层与清单

分两层，共 38 个 `IF-*` 接口。机器可读全量清单见 [interface-inventory.json](interface-inventory.json)。

### 3.1 平台 API（8 个 Python namespace）

提供运行时骨架，其中端口/插件协议对应 3 个接口。

| Namespace | 用途 | 关键接口 |
|---|---|---|
| [`nextneopi`](nextneopi.md) | 顶层便捷函数与稳定 re-export | — |
| [`nextneopi.config`](nextneopi.config.md) | 版本化配置、加载、合并、Schema | — |
| [`nextneopi.models`](nextneopi.models.md) | 领域实体、工件、状态、任务、结果模型 | — |
| [`nextneopi.application`](nextneopi.application.md) | Client、planner、selector、recipe registry | — |
| [`nextneopi.ports`](nextneopi.ports.md) | Execution/Artifact/Container/Plugin/Provenance 端口 | IF-PORT-001、IF-PORT-002 |
| [`nextneopi.plugins`](nextneopi.plugins.md) | 插件 descriptor、实现协议、entry point | IF-PLG-001 |
| [`nextneopi.workflows`](nextneopi.workflows.md) | Workflow recipe 与 DAG 构建 | — |
| [`nextneopi.errors`](errors.md) | 异常、错误类别、错误码 | — |

### 3.2 科学能力 API（13 个 capability namespace，35 个接口）

覆盖从输入/参考到新抗原报告的完整链路。

| 能力域 | 接口数 | 代表接口 |
|---|---|---|
| [input_reference](capabilities/input_reference.md) | 3 | IF-IN-001、IF-REF-001~002 |
| [reads_qc](capabilities/reads_qc.md) | 3 | IF-READ-001~002、IF-QC-001 |
| [alignment](capabilities/alignment.md) | 4 | IF-ALN-001~003、IF-QC-002 |
| [variants](capabilities/variants.md) | 4 | IF-VAR-001~004（含 primary-confirmed consensus） |
| [annotation / phasing](capabilities/annotation_phasing.md) | 3 | IF-VAR-005、IF-ANN-001、IF-PHS-001 |
| [hla](capabilities/hla.md) | 3 | IF-HLA-001~003 |
| [copy_number](capabilities/copy_number.md) | 2 | IF-CNV-001、IF-PUR-001 |
| [ccf_tmb](capabilities/ccf_tmb.md) | 2 | IF-CCF-001、IF-TMB-001 |
| [rna](capabilities/rna.md) | 1 | IF-RNA-001 |
| [events（fusion/splicing）](capabilities/fusion_splicing.md) | 2 | IF-FUS-001、IF-SPL-001 |
| [neoantigens](capabilities/neoantigens.md) | 3 | IF-NEO-001~003 |
| [immunity / repertoire](capabilities/immunogenicity_repertoire.md) | 3 | IF-IMM-001~002、IF-REP-001 |
| [reporting](capabilities/reporting.md) | 2 | IF-RPT-001~002 |

### 3.3 统计口径

- 运行形态：纯 Python 12 个、混合 8 个、容器化第三方工具 18 个。
- 目标稳定性标记：Beta 26 个、Experimental 12 个。
- 实现状态：全部 `NOT_IMPLEMENTED`（这正是"设计基线"的含义）。

## 4. 依据接口开发的流程

每个 capability 可以有多个 implementation，通过实现 `CapabilityImplementation[RequestT, ResultT]` 协议接入。以 [实现一个插件](examples/implement-plugin.md)（给 `IF-READ-002 TrimReads` 实现 fastp adapter）为模板，标准 6 步：

1. 定义 implementation config（Pydantic，`frozen`/`extra="forbid"`），只暴露该实现真正需要的可调参数。
2. 写 `PluginDescriptor`：把 `capability_id` 绑定到某个 `IF-*`，声明 contract/实现版本、支持矩阵（assay/molecule/layout 等）、输入输出 `ArtifactContract`、资源 `ResourceModel`、容器 `ContainerSpec`（固定 digest）、scatter、许可等。
3. 实现 adapter 的 `validate/plan/collect`：`validate` 只查前置条件；`plan` 生成 `ContainerTaskSpec`（工具用 argv、禁 shell、不写 reference）或 `PythonTaskSpec`；`collect` 解析输出并按五态返回 `ResultEnvelope`。
4. 注册 entry point：`CapabilityFactory.create()` + `create_plugin()`，挂到 `nextneopi.capabilities` entry point 组。
5. 在 RunConfig 中选用：`methods.<角色>: <implementation_id>` 选实现，`implementation_configs.<id>` 传参（先过 RunConfig 扩展点校验，再由该实现的 config model 严格校验）。
6. 过测试与门禁：`@pytest.mark.contract("IF-READ-002@1.0.0")` 契约测试，并覆盖正常/边界/工具失败/schema drift/离线镜像/recipe wiring/cache key/provenance；全部通过才算实现完成。

配套两张矩阵用于把控推进：

- [实现与完整性矩阵](implementation-matrix.md)：逐个 IF 跟踪"有哪些实现、门禁是否通过"。
- [Typed DAG Edge Matrix](typed-edge-matrix.md)：规定 DAG 上下游工件类型如何衔接，保证接口拼接时类型对齐。

开发遵循项目既定的纵向切片顺序：首期先打通配对 WES DNA 到 canonical 新抗原报告这条链路，再横向扩展能力与实现。

## 5. 建议阅读顺序

1. [README.md](README.md)：Reference API 索引。
2. 本文件：设计规则、接口分层、开发流程。
3. [api-conventions.md](api-conventions.md)：完整约定。
4. 目标能力的 [capabilities/](capabilities/) 页面，及其上下游接口。
5. [examples/quickstart.md](examples/quickstart.md) 与 [examples/implement-plugin.md](examples/implement-plugin.md)：照着写。
6. 对照 [implementation-matrix.md](implementation-matrix.md) 认领接口，用 [typed-edge-matrix.md](typed-edge-matrix.md) 校验衔接。

## 相关文档

- 设计基线总览：[`../README.md`](../README.md)
- 类型索引：[type-index.md](type-index.md)
- 目标 package 布局：[package-layout.md](package-layout.md)
- 错误与状态模型：[errors.md](errors.md)
