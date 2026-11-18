# `nextneopi.capabilities.events`

Fusion 和异常 splice event calling API；peptide 预测由 neoantigen namespace 完成。

## API Summary

| Symbol | ID | 描述 | Stability |
|---|---|---|---|
| `CallGeneFusions` | IF-FUS-001 | RNA evidence → 规范 fusion callset | Experimental |
| `CallSpliceEvents` | IF-SPL-001 | RNA/strand/phase → 规范 splice events | Experimental |

## `CallGeneFusions`

```python
class CallGeneFusions(
    CapabilityImplementation[CallGeneFusionsRequest, ArtifactRef[FusionCallset]], Protocol
): ...

class CallGeneFusionsRequest(BaseModel, frozen=True):
    case_id: CaseId
    rna_alignment: ArtifactRef[RnaAlignedBam]
    rna_reads: ResultSlot[ArtifactRef[ReadSet]]
    reference: ReferenceBundleRef
    dna_sv_evidence: ResultSlot[ArtifactRef[SomaticSvCallset]]
    policy: FusionCallingPolicy

class FusionEvent(BaseModel, frozen=True):
    event_id: FusionEventId
    left_breakpoint: GenomicBreakpoint
    right_breakpoint: GenomicBreakpoint
    genes: tuple[GeneId, GeneId]
    transcripts: tuple[TranscriptId | None, TranscriptId | None]
    frame: ReadingFrame
    rna_support: ReadSupport
    dna_support: ReadSupport | None
    filters: tuple[FilterReason, ...]
```

首个实现 `arriba`/`neofuse_compatible`；Manta DNA evidence 是可选增强，不是伪造的必需字段。

旧 NeoFuse 已同时计算 RNA 比对、表达、Arriba 事件和融合候选，兼容配方在一次任务中收集对应结果。可单独消费 RNA BAM 的调用器按上述 API 执行。 [旧任务输入输出](../../../nextNEOpi.nf#L5348)

**Status:** 无 fusion 为 `EMPTY`；无 RNA 为 `NOT_REQUESTED`；3' tag 不支持时按 policy `SKIPPED_UNSUPPORTED`；caller/annotation 失败为 `FAILED`。

**Errors:** `FUSION_PROTOCOL_UNSUPPORTED`、`FUSION_REFERENCE_MISMATCH`、`FUSION_CALLER_FAILED`、`FUSION_EVENT_INVALID`。按 sample 执行；cache 含 RNA/reference/annotation/tool/image/可选 DNA parent。科学等价比较规范 breakpoints、gene/transcript、frame 和 support。

```yaml
methods: {fusion_caller: arriba}
policies: {fusion_dna_evidence: optional}
```

## `CallSpliceEvents`

```python
class CallSpliceEvents(
    CapabilityImplementation[CallSpliceEventsRequest, ArtifactRef[SpliceEventCallset]], Protocol
): ...

class CallSpliceEventsRequest(BaseModel, frozen=True):
    case_id: CaseId
    rna_alignment: ArtifactRef[RnaAlignedBam]
    strandedness: StrandednessEvidence
    reference: ReferenceBundleRef
    phase_context: ResultSlot[ArtifactRef[PhaseContext]]
    protocol: RnaLibraryProtocol
    policy: SpliceCallingPolicy

class SpliceEvent(BaseModel, frozen=True):
    event_id: SpliceEventId
    junction: GenomicInterval
    strand: Strand
    gene_id: GeneId | None
    transcript_id: TranscriptId | None
    event_type: SpliceEventType
    support: ReadSupport
    phase: PhaseRelation | None
```

实现 `regtools` 子图可包含 RSeQC strandedness 和 Python XS transform。3' tag 默认不支持；strand unknown 是否允许由 policy 决定。

兼容适配器显式解析 RegTools 所需 VCF。有 read-backed phase 时使用相位 VCF，允许 annotation-only 时使用注释 VCF；两种来源与就绪状态均进入运行记录。 [RegTools 输入](../../../nextNEOpi.nf#L5913) · [旧相位分支](../../../nextNEOpi.nf#L3759)

**Errors:** `SPLICE_PROTOCOL_UNSUPPORTED`、`STRAND_REQUIRED`、`GTF_MISSING`、`SPLICE_CALLER_FAILED`。无 junction 为 `EMPTY`；按 sample/contig scatter。Cache/provenance 含 protocol、strand/phase、GTF、transform/tool/image。

```yaml
methods: {splice_event_caller: regtools}
policies: {unsupported_protocol: skip_with_reason}
```

**Tests:** fusion 空/重复/breakpoint/frame/无 Manta；splice strand/unknown/3' tag/空 junction/phase/reference。
