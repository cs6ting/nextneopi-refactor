# ExecutionBackend 契约

## IF-PORT-001 ExecutionBackend v1.0

### 职责

将已验证的 `ExecutionPlan` 映射到本地或 Slurm，管理 task/attempt 状态、依赖、取消、重试和查询。它不解析科学配置、不选择插件、不修改 task argv。

### Python 契约

```python
class ExecutionBackend(Protocol):
    def validate(self, plan: ExecutionPlan) -> ValidationReport: ...
    def submit(self, plan: ExecutionPlan) -> RunHandle: ...
    def resume(self, run_id: RunId, policy: ResumePolicy) -> RunHandle: ...
    def status(self, run_id: RunId) -> RunStatus: ...
    def cancel(self, run_id: RunId, scope: CancelScope) -> CancelReport: ...
    def events(self, run_id: RunId) -> Iterable[RunEvent]: ...
```

### 输入输出

输入包含 DAG、`TaskSpec`、依赖、资源、retry policy、case failure domain。输出为稳定 run/task/attempt ID、状态事件和 committed artifacts 引用；引擎私有 ID 仅作为 provenance 附加字段。

### 不变量

依赖成功/允许状态前不得运行下游；同一 task scientific identity 的 attempt 串联；取消后不得提交未完成工件；resume 仅复用通过 ArtifactStore 校验的 cache hit；backend 不改变 scientific key。

### 状态与错误

状态包括 `PLANNED/QUEUED/RUNNING/SUCCEEDED/FAILED/CANCELLED/CACHED/SKIPPED`。错误分类按 infrastructure/resource/tool/input/schema/license；只对 retryable 分类重试。case 必需主链失败不影响其他独立 case。

### 资源和 scatter

支持 CPU、memory、runtime、scratch、GPU、partition/account/QoS/constraint。scatter shard 是普通稳定 task；gather 依赖完整 shard manifest。site profile 限制并发和状态查询频率。

### 实现差异

`pydra` 为首选候选、`snakemake` 为回退、`local` 用于开发；三者必须通过相同 conformance suite。实现不能泄露特有对象到 SDK Result。

### Contract tests

DAG 顺序、fan-out/fan-in、失败隔离、重试、资源提升、超时、取消、cache/resume、事件顺序、Slurm job 映射和千任务压力。科学等价要求不同 backend 的 committed artifacts 在同一实现下等价。

```yaml
execution:
  backend: slurm
  retry:
    max_attempts: 2
    resource_multiplier: 1.5
```