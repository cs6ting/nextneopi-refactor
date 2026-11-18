# `nextneopi.ports`

六边形架构的外部端口。领域和 application 只依赖这些 Protocol；Pydra、Snakemake、Slurm、Apptainer 和文件系统位于实现层。

## API Summary

| Symbol | Interface | 描述 |
|---|---|---|
| `ExecutionBackend` | IF-PORT-001 | 执行、恢复、查询和取消 DAG |
| `ArtifactStore` | IF-PORT-002 | Staging、commit、cache、publish、retain |
| `ContainerRuntime` | Supporting port | 执行已固定 digest 的容器任务 |
| `PluginRegistry` | Supporting port | 枚举和加载 entry point 插件 |
| `ProvenanceStore` | Supporting port | 追加事件并查询 run/task/artifact 血缘 |

## `ExecutionBackend`

```python
class ExecutionBackend(Protocol):
    def validate(self, plan: ExecutionPlan) -> ValidationReport: ...
    def submit(self, plan: ExecutionPlan) -> RunHandle: ...
    def resume(self, run_id: RunId, policy: ResumePolicy) -> RunHandle: ...
    def status(self, run_id: RunId) -> RunStatus: ...
    def cancel(self, run_id: RunId, scope: CancelScope) -> CancelReport: ...
    def events(self, run_id: RunId) -> Iterable[RunEvent]: ...
```

实现：local、Pydra candidate、Snakemake fallback。不得改变 scientific cache key 或 task argv。

## `ArtifactStore`

```python
class ArtifactStore(Protocol):
    def stage(self, spec: ArtifactSpec) -> StagingHandle: ...
    def commit(
        self, handle: StagingHandle, metadata: ArtifactMetadata
    ) -> ArtifactRef: ...
    def lookup(self, cache_key: CacheKey) -> ArtifactRef | None: ...
    def verify(self, artifact: ArtifactRef) -> VerificationReport: ...
    def read_descriptor(
        self, artifact: ArtifactRef[DescriptorT], model: type[DescriptorT]
    ) -> DescriptorT: ...
    def publish(
        self, artifact: ArtifactRef, target: PublishTarget
    ) -> PublishedArtifact: ...
    def retain(self, run_id: RunId, artifacts: Collection[ArtifactId]) -> None: ...
```

Commit 只生成 `MATERIALIZED/EMPTY` ArtifactRef，必须验证 schema/checksum/伴随索引/shards 并原子完成；损坏 cache hit 不得返回。`read_descriptor` 只解析轻量 typed metadata，不加载整个 BAM/VCF。

## `ContainerRuntime`

```python
class ContainerRuntime(Protocol):
    def validate(self, spec: ContainerSpec) -> ValidationReport: ...
    def prepare(self, spec: ContainerSpec, *, offline: bool = True) -> PreparedImage: ...
    def execute(
        self,
        task: ContainerTaskSpec,
        *,
        cancellation: CancellationToken,
    ) -> ExecutionRecord: ...
```

生产实现是 Apptainer；`prepare(offline=True)` 只验证预备镜像，不下载。输入/reference mount 只读，环境 allow-list。

## `PluginRegistry`

```python
class PluginRegistry(Protocol):
    def discover(self) -> tuple[PluginDescriptor, ...]: ...
    def get(self, implementation_id: ImplementationId) -> CapabilityFactory: ...
    def check(self, policy: PluginPolicy) -> ValidationReport: ...
```

通过 PyPA entry points；重复 ID、版本冲突和未允许来源失败。

## `ProvenanceStore`

```python
class ProvenanceStore(Protocol):
    def append(self, event: RunEvent) -> EventId: ...
    def record_artifact(self, artifact: ArtifactRef) -> None: ...
    def get_run(self, run_id: RunId) -> RunProvenance: ...
    def trace(self, artifact_id: ArtifactId) -> ProvenanceGraph: ...
    def export_ro_crate(self, run_id: RunId, target: Uri) -> ArtifactRef: ...
```

事件追加写；cache reuse 也要记录新 run 的使用关系。敏感 argv/env/license 必须脱敏。

## Conformance

每个端口实现必须通过相同 contract suite：幂等、并发、失败恢复、事件顺序、取消和 schema。端口具体异常见 [errors.md](errors.md)。