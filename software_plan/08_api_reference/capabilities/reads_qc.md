# `nextneopi.capabilities.reads_qc`

Reads materialization、trim 和 read-level QC API。

## API Summary

| Symbol | ID | 描述 | Stability |
|---|---|---|---|
| `MaterializeReads` | IF-READ-001 | FASTQ/BAM → 规范 `ReadSet` | Beta |
| `TrimReads` | IF-READ-002 | 显式 trim/passthrough | Beta |
| `AssessReadQC` | IF-QC-001 | 结构化 raw/trimmed QC | Beta |

## `MaterializeReads`

```python
class MaterializeReads(
    CapabilityImplementation[MaterializeReadsRequest, ArtifactRef[CanonicalReadSet]], Protocol
): ...

class MaterializeReadsRequest(BaseModel, frozen=True):
    sample: SampleRef
    library: LibraryRef
    inputs: tuple[ArtifactRef[RawFastq | RawBam], ...]
    expected_layout: LibraryLayout
    bam_policy: Literal["rematerialize_and_realign"] = "rematerialize_and_realign"
```

**Returns:** `CanonicalReadSet`，含 R1/R2 artifact、lane provenance、read counts、layout。BAM 首期保持“转 FASTQ 后重比对”，不能静默 passthrough aligned BAM。

**Implementations:** `fastq_passthrough`、`samtools_bam_to_fastq`。可按 library/lane scatter；后者使用 samtools 容器。

**Invariants:** PE mate 数量/identity 对齐；lane 顺序稳定；sample/library 不变。

**Errors:** `MATE_MISMATCH`、`EMPTY_READS`、`UNSUPPORTED_BAM`、`INPUT_CHECKSUM_MISMATCH`。

Cache key 含输入 checksum、layout、lane manifest、实现/镜像；科学比较 read names/mates/count，不比较 gzip 字节。

```python
result = capability.collect(execution, context)
assert result.value.layout is LibraryLayout.PAIRED_END
```

## `TrimReads`

```python
class TrimReads(
    CapabilityImplementation[TrimReadsRequest, TrimReadsResult], Protocol
): ...

class TrimReadsRequest(BaseModel, frozen=True):
    reads: ArtifactRef[CanonicalReadSet]
    policy: TrimPolicy

class TrimReadsResult(BaseModel, frozen=True):
    reads: ArtifactRef[TrimmedReadSet]
    metrics: ResultSlot[ArtifactRef[TrimMetrics]]
```

**Implementations:** `no_trim` 是合法 passthrough；`fastp` 支持 SE/PE、adapter/quality policy。两者结果不要求等价，但都必须保持 sample/layout/mate 语义。

**Status:** 未启用时 recipe 仍显式选择 `no_trim`；全部 reads 被过滤由 policy 决定 `EMPTY` 或 `FAILED`，不得伪装成功非空。

**Resource/Cache:** 按 sample scatter；fastp 中等 CPU/I/O。Key 含 reads checksum、policy、tool/image。Provenance 记录 before/after counts。

```yaml
methods: {read_trimmer: fastp}
```

## `AssessReadQC`

```python
class AssessReadQC(
    CapabilityImplementation[AssessReadQCRequest, ReadQcResult], Protocol
): ...

class AssessReadQCRequest(BaseModel, frozen=True):
    reads: ArtifactRef[CanonicalReadSet | TrimmedReadSet]
    stage: Literal["RAW", "TRIMMED"]
    metrics: frozenset[ReadQcMetric]

class ReadQcResult(BaseModel, frozen=True):
    metrics: ArtifactRef[ReadQcMetrics]
    native_report: ResultSlot[ArtifactRef[NativeReport]]
```

首期实现 `fastqc`。合法报告无告警仍是 `MATERIALIZED`；未请求 stage 为 `NOT_REQUESTED`。

**Errors:** `QC_TOOL_FAILED`、`QC_REPORT_MISSING`、`QC_SCHEMA_MISMATCH`。按 sample/stage scatter；cache/provenance 含 stage、tool/image、input。科学等价比较结构化指标，不比较 HTML/ZIP 字节。

```python
request = AssessReadQCRequest(
    reads=trimmed,
    stage="TRIMMED",
    metrics=frozenset(ReadQcMetric),
)
```

**Required tests:** FASTQ/BAM、SE/PE、单/多 lane、no-trim/fastp、空/损坏 FastQC 输出、cache/resume。