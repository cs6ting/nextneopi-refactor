# `nextneopi.plugins`

插件 descriptor、实现协议、planning/collection context 和 factory API。

## API Summary

| Symbol | 描述 |
|---|---|
| `PluginDescriptor` | 唯一、可生成 Schema 的 implementation 元数据 |
| `CapabilityImplementation[RequestT, ResultT]` | 所有实现的 `validate/plan/collect` 生命周期 |
| `ToolAdapter[RequestT, ResultT]` | 必须具有 ContainerSpec 的第三方实现 |
| `PlanningContext`, `CollectionContext` | 只读执行上下文 |
| `CapabilityFactory`, `PluginPolicy` | Entry point 工厂与来源策略 |

## `PluginDescriptor`

```python
class PluginDescriptor(BaseModel, frozen=True, extra="forbid"):
    schema_version: Literal[1]
    capability_id: CapabilityId
    implementation_id: ImplementationId
    contract_version: SemVer
    implementation_version: SemVer
    core_compatibility: str | None = None
    supports: CapabilitySupport
    inputs: tuple[ArtifactContract, ...]
    outputs: tuple[ArtifactContract, ...]
    reference_requirements: tuple[ReferenceRequirement, ...]
    container: ContainerSpec | None
    resources: ResourceModel
    license: LicenseRequirement
    scatter: ScatterCapability
    empty_input: EmptyInputBehavior
    degradation: tuple[DegradationRule, ...]
    implementation_config_schema: Uri | None
```

字段名与 [`plugin-descriptor.schema.json`](../04_specifications/schemas/plugin-descriptor.schema.json) 完全一致。纯 Python实现 `container=None`；ToolAdapter 必须有 container。

```python
class ResourceModel(BaseModel, frozen=True):
    cpus: int
    memory_mb: int
    runtime_minutes: int
    scratch_mb: int
    gpus: int
    nodes: int
    tasks: int
    scaling_model: str | None
    scientific_resource_fields: tuple[str, ...]
```

Planner 将 `ResourceModel` 针对具体输入解析为 `ResourceRequest`，再由 SiteProfile 映射为执行请求。

## `CapabilityImplementation`

接口编号 `IF-PLG-001`，规范契约见 [插件契约](../03_interfaces/plugin-contract.md)。

```python
class CapabilityImplementation(Protocol[RequestT, ResultT]):
    descriptor: PluginDescriptor
    def validate(self, request: RequestT, context: PlanningContext) -> ValidationReport: ...
    def plan(self, request: RequestT, context: PlanningContext) -> ExecutionSubgraph: ...
    def collect(self, execution: ExecutionRecord, context: CollectionContext) -> ResultEnvelope[ResultT]: ...

class ToolAdapter(CapabilityImplementation[RequestT, ResultT], Protocol):
    descriptor: PluginDescriptor  # descriptor.container is required
```

## Contexts

```python
class PlanningContext(BaseModel, frozen=True, arbitrary_types_allowed=True):
    run_id: RunId
    reference: ReferenceBundle
    site: ResolvedSiteProfile
    resolved_config_digest: Digest
    resources: ResourceRequest
    expected_outputs: tuple[ArtifactSpec, ...]
    artifact_store: ArtifactStore
    container_runtime: ContainerRuntime

class CollectionContext(BaseModel, frozen=True, arbitrary_types_allowed=True):
    run_id: RunId
    task_id: TaskId
    attempt_id: AttemptId
    provenance_id: ProvenanceId
    expected_outputs: tuple[ArtifactSpec, ...]
    artifact_store: ArtifactStore
    provenance_store: ProvenanceStore
```

读取复合 metadata：

```python
reads = context.artifact_store.read_descriptor(
    request.reads,
    CanonicalReadSet,
)
```

不得使用不存在的 `request.reads.value`，也不得加载整个 BAM/VCF。

## Entry point

```toml
[project.entry-points."nextneopi.capabilities"]
fastp = "nextneopi_fastp.plugin:create_plugin"
```

```python
def create_plugin() -> CapabilityFactory: ...
```

Factory 加载无网络/安装/大型扫描。完整且与 Schema 一致的示例见 [实现插件](examples/implement-plugin.md)。