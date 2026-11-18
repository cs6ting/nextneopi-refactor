# `nextneopi.models`

跨模块公共领域、工件、结果和执行模型。模型不可变、`extra="forbid"`、可 JSON 序列化；Schema 由同一 Pydantic 定义生成。

## API Summary

| 类别 | Public symbols |
|---|---|
| Identity | `RunId`, `CaseId`, `SampleId`, `LibraryId`, `ArtifactId`, `TaskId`, `AttemptId`, `ProvenanceId`, `Uri`, `SemVer` |
| Enums | `SampleRole`, `BiologicalSex`, `MoleculeType`, `LibraryLayout`, `AssayKind`, `ArtifactState`, `ResultStatus`, `RunState`, `CaseState`, `TaskState` |
| Artifact/Result | `Digest`, `ReferenceIdentity`, `ProducerIdentity`, `ArtifactRef[T]`, `ResultReason`, `ResultSlot[T]`, `ResultEnvelope[T]` |
| Domain | `CaseManifest`, `Case`, `Sample`, `Library`, `AssayDesign`, `ReferenceBundle` |
| Execution | `ResourceRequest`, `MountSpec`, `ContainerSpec`, `ArtifactSpec`, `TaskSpec`, `PythonTaskSpec`, `ContainerTaskSpec`, `ExecutionSubgraph`, `ExecutionPlan`, `ExecutionRecord` |
| Validation/Run | `ValidationIssue`, `ValidationReport`, `RunHandle`, `RunResult`, `CaseRunResult`, `RunStatus`, `InspectionResult` |

## Artifact 与结果

```python
class ArtifactState(StrEnum):
    MATERIALIZED = "MATERIALIZED"
    EMPTY = "EMPTY"

class ResultStatus(StrEnum):
    MATERIALIZED = "MATERIALIZED"
    EMPTY = "EMPTY"
    NOT_REQUESTED = "NOT_REQUESTED"
    SKIPPED_UNSUPPORTED = "SKIPPED_UNSUPPORTED"
    FAILED = "FAILED"

class Digest(BaseModel, frozen=True):
    algorithm: Literal["sha256"] = "sha256"
    value: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]

class ProducerIdentity(BaseModel, frozen=True):
    capability_id: CapabilityId
    implementation_id: ImplementationId
    implementation_version: SemVer
    container_digest: str | None

class ArtifactRef(BaseModel, Generic[T], frozen=True):
    metadata_schema_version: Literal[1] = 1
    data_schema_version: SemVer
    artifact_id: ArtifactId
    kind: ArtifactKind
    uri: Uri
    media_type: str
    checksum: Digest
    state: ArtifactState
    case_id: CaseId | None = None
    sample_id: SampleId | None = None
    role: SampleRole | None = None
    assay: AssayKind | None = None
    reference: ReferenceIdentity | None = None
    producer: ProducerIdentity
    parameter_digest: Digest
    parents: tuple[ArtifactId, ...]
    companion_artifacts: tuple[ArtifactId, ...] = ()
    reason: str | None = None
    created_at: AwareDatetime
    published_uri: Uri | None = None

class ResultReason(BaseModel, frozen=True):
    code: str
    message: str
    details: Mapping[str, JsonValue] = Field(default_factory=dict)

class ResultSlot(BaseModel, Generic[T], frozen=True):
    metadata_schema_version: Literal[1] = 1
    status: ResultStatus
    value: T | None
    reason: ResultReason | None
    provenance_id: ProvenanceId

    def raise_for_failure(self) -> None: ...

class ResultEnvelope(ResultSlot[T], Generic[T]):
    """一个 capability 调用的最外层结果。"""
```

Validators：`MATERIALIZED/EMPTY` 必须有 value；其他状态 value 必须为 `None` 且有 reason。ArtifactRef 只允许 MATERIALIZED/EMPTY；EMPTY artifact 必须有 reason。

## Case 模型

```python
class Library(BaseModel, frozen=True):
    library_id: LibraryId
    molecule: MoleculeType
    layout: LibraryLayout
    protocol: str | None
    inputs: tuple[ArtifactRef, ...]

class Sample(BaseModel, frozen=True):
    sample_id: SampleId
    role: SampleRole
    sex: BiologicalSex
    assay: AssayDesign
    libraries: tuple[Library, ...]

class Case(BaseModel, frozen=True):
    case_id: CaseId
    samples: tuple[Sample, ...]

    def tumor_dna(self) -> Sample: ...
    def normal_dna(self) -> Sample: ...
    def tumor_rna(self) -> Sample | None: ...
    def validate_matched_pair(self) -> None: ...
```

## 公共引用类型

```python
class SampleRef(BaseModel, frozen=True):
    case_id: CaseId
    sample_id: SampleId
    role: SampleRole

class LibraryRef(BaseModel, frozen=True):
    case_id: CaseId
    sample_id: SampleId
    library_id: LibraryId

ReferenceBundleRef = ArtifactRef[ReferenceBundle]
RunProvenanceRef = ArtifactRef[RunProvenance]
ResolvedConfigRef = ArtifactRef[ResolvedConfigurationSnapshot]
```

这些类型是 typed DAG 边的唯一公共引用；不得以裸 ID/path 替代。

## 任务模型

```python
class ContainerSpec(BaseModel, frozen=True):
    oci: str
    digest: Annotated[str, Field(pattern=r"^sha256:[a-f0-9]{64}$")]
    runtime: Literal["apptainer"]
    entrypoint: tuple[str, ...]
    environment_allowlist: tuple[str, ...]

class MountSpec(BaseModel, frozen=True):
    host_uri: Uri
    container_path: str
    mode: Literal["ro", "rw"]

class ResourceRequest(BaseModel, frozen=True):
    cpus: int = Field(ge=1)
    memory_mb: int = Field(ge=128)
    runtime_minutes: int = Field(ge=1)
    scratch_mb: int = Field(default=0, ge=0)
    gpus: int = Field(default=0, ge=0)
    nodes: int = Field(default=1, ge=1)
    tasks: int = Field(default=1, ge=1)
    partition: str | None = None
    account: str | None = None
    qos: str | None = None
    constraints: tuple[str, ...] = ()

class TaskSpec(BaseModel, frozen=True):
    task_id: TaskId
    case_id: CaseId | None
    capability_id: CapabilityId
    implementation_id: ImplementationId
    dependencies: tuple[TaskId, ...]
    resources: ResourceRequest
    expected_outputs: tuple[ArtifactSpec, ...]
    retry_policy: RetryPolicy
    scientific_cache_key: Digest

class PythonTaskSpec(TaskSpec, frozen=True):
    callable_ref: str
    arguments: Mapping[str, JsonValue]

class ContainerTaskSpec(TaskSpec, frozen=True):
    argv: tuple[str, ...]
    container: ContainerSpec
    mounts: tuple[MountSpec, ...]
    shell: Literal[False] = False

class ExecutionSubgraph(BaseModel, frozen=True):
    tasks: tuple[PythonTaskSpec | ContainerTaskSpec, ...]
    outputs: Mapping[str, TaskOutputRef]

class ExecutionPlan(BaseModel, frozen=True):
    run_id: RunId
    recipe_id: RecipeId
    tasks: tuple[PythonTaskSpec | ContainerTaskSpec, ...]
    resolved_config_digest: Digest
    reference_digest: Digest
    plugin_lock_digest: Digest
    site_fingerprint: Digest

class ExecutionRecord(BaseModel, frozen=True):
    task_id: TaskId
    attempt_id: AttemptId
    state: TaskState
    exit_code: int | None
    outputs: Mapping[str, Uri]
    error: ErrorRecord | None

    def require_success(self) -> None: ...
    def output(self, name: str) -> Uri: ...
```

## Validation

```python
class ValidationIssue(BaseModel, frozen=True):
    severity: Literal["ERROR", "WARNING", "INFO"]
    code: str
    path: str | None
    message: str
    context: Mapping[str, JsonValue]

class ValidationReport(BaseModel, frozen=True):
    issues: tuple[ValidationIssue, ...]

    @property
    def is_valid(self) -> bool: ...
    def errors(self) -> tuple[ValidationIssue, ...]: ...
    def raise_for_errors(self) -> None: ...
```

Run/inspection 的完整模型见 [`nextneopi.application`](nextneopi.application.md)。反向索引见 [type-index.md](type-index.md)。