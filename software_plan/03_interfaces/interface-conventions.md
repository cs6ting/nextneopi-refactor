# 接口约定

## 两层契约

1. **Scientific capability contract**：规定稳定科学语义、Request/Result、前置条件、不变量和等价标准。
2. **Tool adapter contract**：规定某实现如何校验、规划第三方任务、收集原生输出并转换成 capability Result。

workflow 只依赖 capability，不依赖工具命令。不得用一个无科学语义的 `run_tool()` 替代接口。

## ID 与版本

接口 ID 形如 `IF-VAR-001`；Python 名称使用 PascalCase。每个 contract 有 `contract_version`：破坏 Request/Result 或科学语义时升 major；增加可选字段升 minor；文档修订升 patch。implementation 有独立版本。

## 共享类型

```python
@dataclass(frozen=True)
class CapabilityRequest:
    run_id: RunId
    case_id: CaseId
    inputs: tuple[ArtifactRef, ...]
    reference: ReferenceBundleRef
    parameters: Mapping[str, JsonValue]

@dataclass(frozen=True)
class ResultEnvelope(Generic[T]):
    status: ResultStatus
    value: T | None
    reason: ResultReason | None
    provenance_id: ProvenanceId
```

大文件只通过 `ArtifactRef` 传递。`ResultStatus` 必须为 `MATERIALIZED`、`EMPTY`、`NOT_REQUESTED`、`SKIPPED_UNSUPPORTED` 或 `FAILED`。

## 每个接口的必填文档项

- ID、名称、版本与所属模块；
- 科学语义和明确非职责；
- Request/Result 模型、必需/可选输入；
- 前置条件、数据不变量和合法空结果；
- capability 维度及实现差异；
- 错误码、状态和 retry 分类；
- scatter/gather 和资源模型；
- 容器、reference、license；
- cache key 增量字段和 provenance；
- contract test 与科学等价标准；
- YAML method/policy 示例。

## 错误与重试

错误以结构化 `NextNeoPiError` 返回：`code`、`category`、`message`、`context`、`retryable`、`cause_ref`。adapter 不吞异常、不通过空文件表示失败。基础类别见 [`../04_specifications/error-and-status-model.md`](../04_specifications/error-and-status-model.md)。

## Scatter/gather

接口必须声明 `scatter_axis`、稳定 shard ID、最小/最大 shard、是否允许部分 gather 和 gather identity。默认关键科学工件不允许部分 gather。scatter 仅改变执行，不改变 contract Result。

## 资源与容器

资源请求使用 `ResourceRequest`；站点 override 不得改变科学参数。第三方实现必须声明 OCI digest、mount、entrypoint、reference 和 license；命令为 argv，禁止 `shell=True`。

## 缓存与 provenance

通用 cache key 见 ADR-004。接口文档只列额外字段。每个 Result 记录 implementation、工具/镜像、参数、parents、reference、decision trace 和 attempt。

## 测试规则

- contract test 对所有 implementation 参数化执行；
- collector 使用保存的原生输出 fixture；
- scientific equivalence 在相同 implementation/version/reference 下比较规范实体；
- 不适用的 capability 必须在 planning 被拒绝或显式跳过；
- 每个接口至少关联一个 recipe Demo。