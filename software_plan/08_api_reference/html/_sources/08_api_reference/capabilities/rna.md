# `nextneopi.capabilities.rna`

RNA alignment、expression、variant evidence 和可选 HLA evidence API。

## API Summary

| Symbol | ID | Contract | Stability |
|---|---|---|---|
| `AlignAndQuantifyRNA` | IF-RNA-001 | 1.0.0 | Experimental |

## Signature

```python
class AlignAndQuantifyRNA(CapabilityImplementation[AlignAndQuantifyRnaRequest, RnaAnalysisResult], Protocol): ...

class AlignAndQuantifyRnaRequest(BaseModel, frozen=True):
    case_id: CaseId
    sample: SampleRef
    reads: ArtifactRef[CanonicalReadSet | TrimmedReadSet]
    protocol: RnaLibraryProtocol
    reference: ReferenceBundleRef
    requested_outputs: frozenset[RnaOutputFeature]
    policy: RnaAnalysisPolicy

class ExpressionMatrix(BaseModel, frozen=True):
    table: ArtifactRef[ExpressionTable]
    unit: Literal["TPM"]
    annotation_version: str
    gene_id_namespace: str

class RnaAnalysisResult(BaseModel, frozen=True):
    alignment: ResultSlot[ArtifactRef[RnaAlignedBam]]
    expression: ResultSlot[ArtifactRef[ExpressionMatrix]]
    variant_evidence: ResultSlot[ArtifactRef[RnaVariantEvidence]]
    hla_evidence: ResultSlot[ArtifactRef[HlaEvidence]]
    strandedness: ResultSlot[StrandednessEvidence]
```

每个子输出独立五态，不再用 `None` 混淆未请求、不支持和失败。Alignment/expression 是 recipe 请求时的必需 slot；3' tag 下 fusion/splice/HLA 能力可 `SKIPPED_UNSUPPORTED`。

## Contract

实现 `star_neofuse_compatible`；长期可拆内部 STAR/quantifier/bam-readcount tasks。Sample/reference/GTF/index 一致，ExpressionMatrix 含 gene/transcript、单位和 annotation version；测得 0 不等于 `NOT_REQUESTED`。

旧版兼容执行从已准备的 RNA reads、已选 HLA 和适用的 Manta SV 启动一次 NeoFuse，在同一运行记录下分别收集 RNA BAM/BAI、TPM、Arriba 事件和融合候选。`hla_evidence` 仅供可独立产出该证据的实现使用。旧 RNA 分型直接取 reads，旧 RNA 变异计数在 BAM 与注释 VCF 就绪后生成。 [交接约定](../../03_interfaces/rna-fusion-splicing-interfaces.md) · [旧输入输出](../../../nextNEOpi.nf#L5348)

外层汇总：任一必需 slot failed→`FAILED`；成功但主 expression 集为空→`EMPTY`；否则 `MATERIALIZED`。无 tumor RNA 由 recipe 返回 `NOT_REQUESTED`，不调用接口。

Errors：`RNA_PROTOCOL_UNSUPPORTED`、`RNA_REFERENCE_MISMATCH`、`RNA_ALIGNMENT_FAILED`、`EXPRESSION_SCHEMA_MISMATCH`、`STRANDEDNESS_CONFLICT`。按 sample；高 CPU/内存；固定 image/index。Cache/provenance 含 reads/protocol/annotation/parameters/image 和每 slot 决策。

```yaml
methods: {rna_alignment_quantification: star_neofuse_compatible}
policies:
  rna: {protocol: full_length, expression_unit: TPM, strandedness: auto}
```

Tests：`TST-CONTRACT-RNA-001`、`TST-INT-RNA-001`、`TST-SCI-RNA-001`，覆盖 DNA-only、普通/3' tag、stranded、TPM 0、空 reads、RNA HLA。
