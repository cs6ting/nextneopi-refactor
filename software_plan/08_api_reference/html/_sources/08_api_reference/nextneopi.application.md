# `nextneopi.application`

应用层负责配置解析、插件选择、recipe 构建和运行协调；不实现第三方算法。

## API Summary

| Symbol | 描述 |
|---|---|
| `NextNeoPiClient` | CLI/SDK 唯一 facade |
| `WorkflowPlanner` | `ResolvedConfiguration` → `ExecutionPlan` |
| `CapabilitySelector` | Request/capability → implementation |
| `CapabilityExecutor` | 受控执行单个 capability |
| `RecipeRegistry` | Recipe 注册与解析 |
| `PlanOptions` | 规划选项 |
| `RunHandle`, `CapabilityRunHandle` | 已提交运行句柄 |
| `RunResult`, `CaseRunResult`, `InspectionResult` | 稳定运行/查询结果 |

## `PlanOptions`

```python
class PlanOptions(BaseModel, frozen=True):
    predict_cache: bool = True
    include_optional_nodes: bool = True
    explain_selection: bool = False
```

## `NextNeoPiClient`

```python
class NextNeoPiClient:
    site_profile: ResolvedSiteProfile
    capabilities: CapabilityExecutor

    @classmethod
    def from_profile(
        cls,
        profile: SiteProfile | str | os.PathLike[str],
        *,
        plugin_policy: PluginPolicy | None = None,
    ) -> "NextNeoPiClient": ...

    def validate(self, config: RunConfig) -> ValidationReport: ...
    def plan(self, config: RunConfig, *, options: PlanOptions | None = None) -> ExecutionPlan: ...
    def run(self, plan: ExecutionPlan) -> RunHandle: ...
    def resume(self, run_id: RunId, policy: ResumePolicy) -> RunHandle: ...
    def status(self, run_id: RunId) -> RunStatus: ...
    def cancel(self, run_id: RunId, scope: CancelScope = CancelScope.RUN) -> CancelReport: ...
    def inspect(self, target: RunId | ArtifactId | TaskId) -> InspectionResult: ...
```

`from_profile` 恰好加载一次 SiteProfile；`validate` 要求 `config.execution.profile` 和 backend 与 Client profile 一致。SDK `run` 总是立即返回 handle；CLI 的 `--detach` 仅决定 CLI 是否随后调用 `wait()`。

## `RunHandle` 与结果

```python
class CaseRunResult(BaseModel, frozen=True):
    case_id: CaseId
    state: CaseState
    outputs: Mapping[str, ResultSlot[ArtifactRef]]
    scientific_report: ResultSlot[ArtifactRef[ScientificReportBundle]]
    error: ErrorRecord | None

class RunResult(BaseModel, frozen=True):
    run_id: RunId
    state: RunState
    cases: tuple[CaseRunResult, ...]
    execution_report: ResultSlot[ArtifactRef[ExecutionReport]]

    @property
    def failed_cases(self) -> tuple[CaseRunResult, ...]: ...

class RunHandle:
    run_id: RunId
    def status(self) -> RunStatus: ...
    def wait(self, timeout: float | None = None) -> RunResult: ...
    async def async_wait(self, timeout: float | None = None) -> RunResult: ...
    def cancel(self, scope: CancelScope = CancelScope.RUN) -> CancelReport: ...
    def events(self) -> Iterable[RunEvent]: ...
```

Timeout 只停止客户端等待，不自动取消 run；调用方显式 `cancel()`。

## `CapabilityExecutor`

```python
class CapabilityExecutor:
    def submit(
        self,
        capability_id: CapabilityId,
        request: RequestT,
        *,
        implementation_id: ImplementationId | None = None,
    ) -> CapabilityRunHandle[ResultT]: ...

    def execute(
        self,
        capability_id: CapabilityId,
        request: RequestT,
        *,
        implementation_id: ImplementationId | None = None,
        timeout: float | None = None,
    ) -> ResultEnvelope[ResultT]: ...

class CapabilityRunHandle(Generic[ResultT]):
    run_id: RunId
    def status(self) -> RunStatus: ...
    def wait(self, timeout: float | None = None) -> ResultEnvelope[ResultT]: ...
    async def async_wait(self, timeout: float | None = None) -> ResultEnvelope[ResultT]: ...
    def cancel(self) -> CancelReport: ...
```

`execute()` 等价于 `submit(...).wait()`，仍经过 selector、backend、ArtifactStore 和 provenance。

## `InspectionResult`

```python
class ProvenanceSummary(BaseModel, frozen=True):
    parents: tuple[ArtifactId, ...]
    container_digests: tuple[str, ...]
    implementation_ids: tuple[ImplementationId, ...]
    decisions: tuple[DecisionRecord, ...]

class InspectionResult(BaseModel, frozen=True):
    target: RunId | ArtifactId | TaskId
    artifact: ArtifactRef | None
    task: TaskInspection | None
    run: RunInspection | None
    provenance: ProvenanceSummary
```

## Planner 与 Selector

```python
class WorkflowPlanner(Protocol):
    def validate(self, config: RunConfig, site: ResolvedSiteProfile) -> ValidationReport: ...
    def build(self, config: RunConfig, site: ResolvedSiteProfile, *, run_id: RunId | None = None, options: PlanOptions | None = None) -> ExecutionPlan: ...

class CapabilitySelector(Protocol):
    def select(self, request: CapabilityRequest, candidates: Sequence[PluginDescriptor], *, policy: SelectionPolicy) -> ResolvedImplementation: ...
    def explain(self, request: CapabilityRequest, candidates: Sequence[PluginDescriptor]) -> SelectionReport: ...
```

## Neoantigen aggregation utility

```python
def aggregate_neoantigen_candidates(
    tables: Sequence[NeoantigenTable],
    *,
    policy: NeoantigenAggregationPolicy,
) -> NeoantigenTable: ...
```

使用 `NeoantigenIdentity` 去重并保留全部 predictor/evidence；不是新 IF，不执行第三方工具。

## Raises

`ValidationFailedError`、`PluginResolutionError`、`PlanInvariantError`、`ProfileMismatchError`、`BackendUnavailableError`。完整层次见 [errors.md](errors.md)。