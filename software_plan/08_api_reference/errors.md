# `nextneopi.errors`

稳定异常层次和可序列化 `ErrorRecord`。科学空结果不是异常。

## Exception hierarchy

```text
Exception
└── NextNeoPiError(record: ErrorRecord)
    ├── ConfigurationError
    │   ├── ConfigParseError
    │   ├── ConfigSchemaError
    │   ├── ConfigMigrationError
    │   ├── ForbiddenConfigOverrideError
    │   ├── ProfileMismatchError
    │   └── ImplementationConfigError
    ├── ValidationFailedError
    ├── CapabilityError
    │   ├── PluginNotFoundError
    │   ├── PluginConflictError
    │   ├── PluginIncompatibleError
    │   └── PluginResolutionError
    ├── PlanInvariantError
    ├── ArtifactError
    │   ├── ArtifactVerificationError
    │   ├── ArtifactCommitError
    │   └── PublishError
    ├── ExecutionError
    │   ├── BackendUnavailableError
    │   ├── ResourceExhaustedError
    │   ├── ToolExecutionError
    │   └── CancellationError
    └── ScientificInvariantError
```

## Models

```python
class ErrorRecord(BaseModel, frozen=True):
    code: str
    category: ErrorCategory
    message: str
    retryable: bool
    run_id: RunId | None
    case_id: CaseId | None
    task_id: TaskId | None
    context: Mapping[str, JsonValue]
    cause_ref: str | None

class NextNeoPiError(Exception):
    record: ErrorRecord
    def to_dict(self, *, redact: bool = True) -> dict[str, JsonValue]: ...

class ValidationFailedError(NextNeoPiError):
    report: ValidationReport
```

异常与序列化模型不再同名。`ValidationFailedError` 是 `NextNeoPiError` 直属子类，不同时继承 `ConfigurationError`。

## 阶段矩阵

| 阶段 | 对外表达 |
|---|---|
| Run/Site/Plugin config、调用前置条件 | `ValidationIssue`；显式 raise 时为配置/capability exception |
| Planning 插件选择/DAG 不变量 | `PluginResolutionError` / `PlanInvariantError` |
| 已提交工具或 collector 失败 | `ResultEnvelope(status=FAILED, value=None)` + `ErrorRecord` |
| Backend 提交/查询/取消失败 | `ExecutionError` |
| 科学/编程不变量失败 | `ScientificInvariantError` |

必需 reference/license 缺失属于 planning，不启动任务。

## Categories 与重试

`CONFIGURATION/INVALID_INPUT/CAPABILITY/LICENSE/SCHEMA/INTERNAL` 默认不可重试；`TOOL` 由 adapter；`RESOURCE_EXHAUSTED/TRANSIENT_INFRASTRUCTURE` 可重试；`DATA_INTEGRITY` 默认不可重试并可能重算父任务。

## Core codes

`INVALID_MANIFEST`、`PROFILE_MISMATCH`、`IMPLEMENTATION_CONFIG_INVALID`、`PLUGIN_NOT_FOUND/CONFLICT/INCOMPATIBLE`、`PLUGIN_RESOLUTION_FAILED`、`LICENSE_MISSING`、`REFERENCE_INCOMPATIBLE`、`SCHEMA_VIOLATION`、`CHECKSUM_MISMATCH`、`INCOMPLETE_SCATTER`、`PLAN_INVARIANT_VIOLATION`、`TOOL_EXIT_NONZERO`、`TIMEOUT`、`OUT_OF_MEMORY`、`BACKEND_UNAVAILABLE`、`PUBLISH_FAILED`。

不得 `except Exception: return EMPTY`。`ResultEnvelope.raise_for_failure()` 仅在 status=FAILED 时根据关联 ErrorRecord 抛 `ExecutionError`/`ScientificInvariantError`，其他状态不抛。