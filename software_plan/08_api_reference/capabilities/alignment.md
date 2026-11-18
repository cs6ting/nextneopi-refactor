# `nextneopi.capabilities.alignment`

DNA alignment、postprocess、BQSR 和 alignment QC API。

## API Summary

| Symbol | ID | 描述 | Stability |
|---|---|---|---|
| `AlignDNA` | IF-ALN-001 | DNA reads → sorted aligned BAM | Beta |
| `PostprocessDNAAlignment` | IF-ALN-002 | uBAM merge、markdup、tag/index | Beta |
| `RecalibrateBaseQuality` | IF-ALN-003 | GATK BQSR scatter/gather | Beta |
| `AssessAlignmentQC` | IF-QC-002 | Coverage、flag、WES/WGS QC | Beta |

## `AlignDNA`

```python
class AlignDNA(
    CapabilityImplementation[AlignDnaRequest, ArtifactRef[AlignedBam]], Protocol
): ...

class AlignDnaRequest(BaseModel, frozen=True):
    reads: ArtifactRef[CanonicalReadSet | TrimmedReadSet]
    reference: ReferenceBundleRef
    read_group: ReadGroup
    policy: AlignmentPolicy
```

**Returns:** coordinate-sorted `AlignedBam`（index 是否同阶段产生由 artifact contract 明确）；不做 markdup/BQSR。

**Implementations:** `bwa_mem` 首期，未来 `bwa_mem2`；descriptor 声明 SE/PE、secondary/supplementary 和 RG 语义。

**Invariants:** RG/sample 与 manifest 一致；reference dictionary 一致；output 可由 htslib 校验。

**Errors:** `ALIGNER_FAILED`、`READ_GROUP_MISMATCH`、`REFERENCE_MISMATCH`、`BAM_VALIDATION_FAILED`。高 CPU/I/O、按 sample 执行。科学比较 mapped reads/flags/coordinates/RG 与摘要容差。

```yaml
methods: {dna_aligner: bwa_mem}
```

## `PostprocessDNAAlignment`

```python
class PostprocessDNAAlignment(
    CapabilityImplementation[PostprocessAlignmentRequest, ArtifactRef[DuplicateMarkedBam]],
    Protocol,
): ...

class PostprocessAlignmentRequest(BaseModel, frozen=True):
    alignment: ArtifactRef[AlignedBam]
    unaligned_bam: ArtifactRef[UnalignedBam]
    reference: ReferenceBundleRef
    policy: PostprocessAlignmentPolicy
```

实现 `gatk_picard_sambamba` 可规划 MergeBamAlignment、MarkDuplicates、SetNmMdAndUqTags 等子任务；每个中间边界可观察，不允许一个不可诊断的巨型 shell。

**Output:** `DuplicateMarkedBam` + index + duplicate/alignment metrics。

每个阶段独立交付 BAM 及适用索引。HLA DNA 取证使用 `DuplicateMarkedBam`，Mutect2 等调用器使用 `RecalibratedBam`。旧 CNVkit 也使用 `DuplicateMarkedBam`，其输入需在兼容验收中单列。 [阶段输入映射](../typed-edge-matrix.md) · [旧通道分流](../../../nextNEOpi.nf#L1281)

**Errors:** `MISSING_COMPANION`、`SAMPLE_MISMATCH`、`BAM_SORT_INVALID`、`TAG_VALIDATION_FAILED`。Cache/provenance 包含全部子工具/镜像和父工件。等价比较 read/flag/duplicate/NM/MD/UQ。

## `RecalibrateBaseQuality`

```python
class RecalibrateBaseQuality(
    CapabilityImplementation[BaseRecalibrationRequest, ArtifactRef[RecalibratedBam]], Protocol
): ...

class BaseRecalibrationRequest(BaseModel, frozen=True):
    bam: ArtifactRef[DuplicateMarkedBam]
    reference: ReferenceBundleRef
    known_sites: tuple[ArtifactRef[KnownSitesVcf], ...]
    intervals: CallableIntervalPlan
    scatter: ScatterPolicy
```

首期实现 `gatk4`，子图为 BaseRecalibrator → report gather → ApplyBQSR → BAM gather。

**Scatter:** interval；每 shard stable ID；不允许 partial gather。`EMPTY` 不适用于有 reads 的必需 BAM。

**Errors:** `KNOWN_SITE_MISSING`、`SHARD_FAILED`、`INCOMPLETE_SCATTER`、`GATHER_INVALID`。每 shard 独立 cache；gather key 引用完整 shard checksums。资源耗尽可提升 attempt 资源，不改变科学 key。

```python
request = BaseRecalibrationRequest(
    bam=marked_bam,
    reference=reference,
    known_sites=reference.gatk_known_sites,
    intervals=interval_plan,
    scatter=ScatterPolicy(axis="interval", count=40),
)
```

## `AssessAlignmentQC`

```python
class AssessAlignmentQC(
    CapabilityImplementation[AssessAlignmentQcRequest, AlignmentQcResult], Protocol
): ...

class AssessAlignmentQcRequest(BaseModel, frozen=True):
    bam: ArtifactRef[DuplicateMarkedBam | RecalibratedBam]
    assay: AssayDesign
    intervals: CallableIntervalPlan | None
    requested_metrics: frozenset[AlignmentQcMetric]
```

实现 `gatk_mosdepth` 组合 flagstat、alignment summary、mosdepth；WES 可有 HsMetrics，WGS 不伪造。部分可选 metric 失败按 recipe 记录 section `FAILED`，不能污染 BAM 状态。

**Tests:** WES/WGS capability、coverage、mapped/duplicate counts、missing metric、local/Slurm、BQSR shard retry/resume。
