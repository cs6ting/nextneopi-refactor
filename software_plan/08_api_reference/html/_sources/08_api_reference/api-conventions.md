# API 使用约定

## 公共 API 定义

只有本目录列出的非下划线 symbol 属于公共 API。实现内部模块使用 `_internal` 或前导下划线；用户和插件不得依赖。顶层 `nextneopi` 仅 re-export 高频稳定接口，其余从明确 namespace 导入。

## 稳定性标记

每个 symbol 标记 `Stable`、`Beta`、`Experimental` 或 `Internal`，规则见 [stability.md](stability.md)。设计阶段所有接口为 Proposed；首期实现默认 Beta，完成 ACC-001～005 后才可提升 Stable。

## 类型与不可变性

- 配置和跨边界数据使用 Pydantic `BaseModel`，默认 `extra="forbid"`。
- ID 使用 `NewType`/受限字符串；禁止互换 `CaseId` 与 `SampleId`。
- Request、Result、descriptor、plan、artifact 默认不可变。
- 大型 FASTQ/BAM/VCF 仅通过 `ArtifactRef[T]` 传递；`T` 是该持久工件的轻量 descriptor schema。Adapter 通过 `ArtifactStore.read_descriptor()` 读取 descriptor。
- 单输出且持久化的 capability 必须返回 `ResultEnvelope[ArtifactRef[DescriptorT]]`；复合输出返回包含多个 `ResultSlot[ArtifactRef[...]]` 的 Result model。
- 公共签名禁止无约束 `Any`；扩展 metadata 使用版本化 JSON value。
- 所有集合参数优先 `Sequence`/`Mapping`，返回不可变 tuple/mapping。

## Capability 与 Implementation

科学接口是泛型协议：

```python
RequestT = TypeVar("RequestT", bound=BaseModel)
ResultT = TypeVar("ResultT", bound=BaseModel)

class CapabilityImplementation(Protocol[RequestT, ResultT]):
    descriptor: PluginDescriptor

    def validate(
        self, request: RequestT, context: PlanningContext
    ) -> ValidationReport: ...

    def plan(
        self, request: RequestT, context: PlanningContext
    ) -> ExecutionSubgraph: ...

    def collect(
        self, execution: ExecutionRecord, context: CollectionContext
    ) -> ResultEnvelope[ResultT]: ...
```

每个 `IF-*` 页面定义专用 Request/Result 及其子协议，例如：

```python
class TypeHla(
    CapabilityImplementation[TypeHlaRequest, HlaCallset],
    Protocol,
):
    """IF-HLA-002."""
```

纯 Python 实现返回 `PythonTaskSpec`；第三方工具 adapter 返回 `ContainerTaskSpec`。两者都不能直接提交 Slurm。

## 状态与异常

`ArtifactRef` 仅表示已经提交的 `MATERIALIZED/EMPTY` 工件，并使用 `state: ArtifactState`。五类业务状态由 `ResultSlot[T]` 和最外层 `ResultEnvelope[T]` 表达：`MATERIALIZED`、`EMPTY`、`NOT_REQUESTED`、`SKIPPED_UNSUPPORTED`、`FAILED`。

`MATERIALIZED/EMPTY` 必须有 typed value；后三种状态 value 必须为 `None` 且有 `ResultReason`。复合 Result 中每个可独立成功/跳过/失败的输出必须使用 `ResultSlot[T]`，不得用裸 `None` 模拟状态。

配置/编程错误使用 [`NextNeoPiError`](errors.md)，其内部携带可序列化 `ErrorRecord`。不得通过缺文件、空字符串、0 或 `None` 模拟状态。

## 参数风格

- 必需科学输入放在 typed Request 中。
- 运行 context 使用 keyword-only 参数。
- 路径用 `ArtifactRef`/`Uri`，不接收未校验裸字符串。
- 单位写入字段名或独立 unit enum，例如 `memory_mb`、`runtime_minutes`。
- 未来扩展不能偷偷放入任意 `extra_options: str`；必须建模或明确 unsafe escape hatch（默认禁用）。

## 副作用

`validate()` 无副作用；`plan()` 只生成不可变任务图；只有 backend 可执行任务；`collect()` 只读取声明输出并经 ArtifactStore 原子提交。正式运行不联网、不安装、不 patch、不写输入/reference。

## 文档条目模板

每个 API symbol 必须记录：

1. 完整 Python signature；
2. stability、Interface ID/contract version；
3. 一句话用途与非职责；
4. Parameters/Returns/Raises；
5. 前置条件和数据不变量；
6. capability/实现差异；
7. status/scatter/resource/cache/provenance；
8. Example；
9. 对应测试与验收。

## 兼容

类型或科学语义破坏升 contract major；增加 optional field 升 minor；文档和非语义错误文本升 patch。序列化字段名和错误 code 属兼容面。