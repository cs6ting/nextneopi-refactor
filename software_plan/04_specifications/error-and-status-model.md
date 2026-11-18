# 错误与状态模型

## 分层状态

- Run：`PLANNED/QUEUED/RUNNING/SUCCEEDED/PARTIAL_FAILED/FAILED/CANCELLED`。
- Case：`PENDING/RUNNING/SUCCEEDED/FAILED/CANCELLED`。
- Task：`PLANNED/QUEUED/RUNNING/CACHED/SUCCEEDED/FAILED/SKIPPED/CANCELLED`。
- Result：`MATERIALIZED/EMPTY/NOT_REQUESTED/SKIPPED_UNSUPPORTED/FAILED`。
- Artifact：仅 `MATERIALIZED/EMPTY`。

Task 成功不保证科学结果非空。只有 `MATERIALIZED/EMPTY` 会产生 `ArtifactRef`；其余状态通过 `ResultSlot/ResultEnvelope` 表达。

## 可序列化错误与异常

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
```

`ErrorRecord` 用于 JSON/provenance/report；`NextNeoPiError` 用于 Python 控制流，二者不可同名异构。Context 必须脱敏。

## 阶段边界

| 阶段 | 表达方式 | 示例 |
|---|---|---|
| Schema/配置/调用者错误 | `ValidationIssue`，调用 `raise_for_errors()` 时抛特定异常 | primary 未在 callers 中 |
| Plugin/reference/license planning | `ValidationIssue` 或 `CapabilityError` | HLA-HD 必需但无 license |
| 已提交任务的科学空结果 | `ResultEnvelope(status=EMPTY)` | 无 confirmed variant |
| 已提交工具/collector 失败 | `ResultEnvelope(status=FAILED, value=None)`，reason 引用 `ErrorRecord` | VEP 非零退出 |
| Backend 控制面不可用 | `ExecutionError` | Slurm 无法提交/查询 |
| 编程/科学不变量错误 | `ScientificInvariantError` | consensus 分区不成立 |

必需 license 缺失必须在 planning 阶段失败，不得等到 collect 才返回运行失败。

## 类别与默认重试

| Category | 默认重试 | 示例 |
|---|---:|---|
| `CONFIGURATION`、`INVALID_INPUT`、`CAPABILITY`、`LICENSE`、`SCHEMA` | 否 | 配置、输入或契约错误 |
| `TOOL` | adapter 决定 | 工具非零退出 |
| `RESOURCE_EXHAUSTED` | 是，可提升资源 | OOM、timeout |
| `TRANSIENT_INFRASTRUCTURE` | 是 | node fail、Slurm 查询失败 |
| `DATA_INTEGRITY` | 默认否 | checksum/index/shard 错误 |
| `INTERNAL` | 否 | 不变量/程序错误 |

## 标准错误码

`INVALID_MANIFEST`、`REFERENCE_INCOMPATIBLE`、`PLUGIN_NOT_FOUND`、`PLUGIN_CONFLICT`、`PLUGIN_INCOMPATIBLE`、`LICENSE_MISSING`、`MISSING_COMPANION`、`INCOMPLETE_SCATTER`、`SCHEMA_VIOLATION`、`CHECKSUM_MISMATCH`、`TOOL_EXIT_NONZERO`、`TIMEOUT`、`OUT_OF_MEMORY`、`BACKEND_UNAVAILABLE`、`PLAN_INVARIANT_VIOLATION`、`PUBLISH_FAILED`。

## 复合结果汇总

每个 capability 文档必须定义子 `ResultSlot` 到外层 `ResultEnvelope` 的真值表。默认：必需 slot `FAILED`→外层 `FAILED`；全部成功但主科学集合为零→`EMPTY`；至少一个主结果非空且无必需失败→`MATERIALIZED`；可选 slot 失败由 recipe policy 决定，但必须出现在报告。

## 重试

每次 retry 新建 attempt。只有 retryable `ErrorRecord` 使用 backoff；资源提升受 site 上限。科学参数、镜像或输入变化必须产生新 plan/cache key，不是 retry。

禁止 `except Exception: return EMPTY`、空文件代替失败、或用 `None` 同时代表未请求/不支持/失败。