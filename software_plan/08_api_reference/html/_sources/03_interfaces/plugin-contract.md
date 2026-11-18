# 插件契约

## IF-PLG-001 `PluginLifecycle` v1.0.0

插件将 implementation 注册为科学 capability 的实现。它负责无副作用校验、任务子图规划和原生结果收集；不选择自身、不提交 Slurm、不修改全局配置/reference。

## Python 契约

```python
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

纯 Python implementation 规划 `PythonTaskSpec`；第三方 `ToolAdapter` 规划 `ContainerTaskSpec`。二者均由 ExecutionBackend 执行。

## `PluginDescriptor` 唯一字段

`schema_version`、`capability_id`、`implementation_id`、contract/implementation version、完整 supports、inputs/outputs、reference requirements、可空 container、资源、license、scatter、empty behavior、degradation 和 `implementation_config_schema`。Schema 见 [`../04_specifications/schemas/plugin-descriptor.schema.json`](../04_specifications/schemas/plugin-descriptor.schema.json)。

纯 Python实现 `container=None`；ToolAdapter 必须指定固定 OCI digest、entrypoint 和环境 allow-list。

## Context

```python
class PlanningContext(BaseModel, frozen=True):
    run_id: RunId
    reference: ReferenceBundle
    site: ResolvedSiteProfile
    resources: ResourceRequest
    expected_outputs: tuple[ArtifactSpec, ...]
    artifact_store: ArtifactStore
    container_runtime: ContainerRuntime

class CollectionContext(BaseModel, frozen=True):
    run_id: RunId
    task_id: TaskId
    attempt_id: AttemptId
    provenance_id: ProvenanceId
    expected_outputs: tuple[ArtifactSpec, ...]
    artifact_store: ArtifactStore
    provenance_store: ProvenanceStore
```

Adapter 使用 `artifact_store.read_descriptor(ref, ModelType)` 读取轻量复合 metadata；不得假定 `ArtifactRef` 存在 `.value`。

## 生命周期与错误

Registry 经 `nextneopi.capabilities` entry points 发现 factory，验证 descriptor/版本/allow-list，selector 再绑定。License/reference/config 在 planning 阶段失败。Collector 合法零记录返回 `EMPTY`；缺文件/schema/工具失败返回 `FAILED` envelope；控制面异常由 backend exception 表达。

## 配置扩展

Descriptor 的 `implementation_config_schema` 注册严格 Pydantic Schema。RunConfig 使用：

```yaml
implementation_configs:
  mutect2:
    minimum_allele_depth: 5
```

未知插件、字段或缺必需字段失败。

## Contract tests

Descriptor Schema、无副作用 validate、deterministic plan、argv 安全、mount 权限、typed empty/failed、native schema drift、cache key、provenance、实现配置和不兼容 request 必须通过。

```toml
[project.entry-points."nextneopi.capabilities"]
mutect2 = "nextneopi_mutect2.plugin:create_plugin"
```