# `nextneopi.capabilities.hla`

HLA evidence、typing 和跨来源 genotype resolution API。

## API Summary

| Symbol | ID | 描述 | Stability |
|---|---|---|---|
| `ExtractHlaEvidence` | IF-HLA-001 | 从 DNA/RNA 工件抽取 typer evidence | Beta |
| `TypeHla` | IF-HLA-002 | 单一实现生成原始 HLA callset | Beta |
| `ResolveHlaGenotype` | IF-HLA-003 | 仲裁 DNA/RNA/custom calls | Beta |

## `ExtractHlaEvidence`

```python
class ExtractHlaEvidence(
    CapabilityImplementation[ExtractHlaEvidenceRequest, ArtifactRef[HlaEvidence]], Protocol
): ...

class ExtractHlaEvidenceRequest(BaseModel, frozen=True):
    sample: SampleRef
    source: ArtifactRef[DuplicateMarkedBam | ReadSet]
    molecule: MoleculeType
    layout: LibraryLayout
    regions: ArtifactRef[IntervalSet] | None
    policy: HlaEvidencePolicy
```

首期 DNA 实现 `samtools_mhc_unmapped` 使用 `DuplicateMarkedBam`，合并 MHC 区域和 unmapped reads。RNA 兼容路径使用准备后分流的 `ReadSet`，在 NeoFuse 之前建立证据。header transform 必须保持 read/mate identity。 [旧 reads 分流](../../../nextNEOpi.nf#L1030)

**Returns:** `HlaEvidence`（reads/BAM、molecule、layout、counts、source）。合法零 evidence 为 `EMPTY`。

**Errors:** `HLA_EVIDENCE_REFERENCE_MISMATCH`、`HLA_READ_HEADER_INVALID`、`MATE_MISMATCH`。按 sample scatter；cache 含 source/region/policy/tool。科学比较 read identity/count，不比较压缩字节。

## `TypeHla`

```python
class TypeHla(
    CapabilityImplementation[TypeHlaRequest, ArtifactRef[HlaCallset]], Protocol
): ...

class TypeHlaRequest(BaseModel, frozen=True):
    case_id: CaseId
    sample_id: SampleId
    evidence: ResultSlot[ArtifactRef[HlaEvidence]]
    custom_callset: ResultSlot[ArtifactRef[UserHlaCallset]]
    reference: ReferenceBundleRef
    requested_mhc_classes: frozenset[MhcClass]

class HlaAlleleCall(BaseModel, frozen=True):
    locus: HlaLocus
    allele_fields: tuple[str, ...]
    resolution: HlaResolution
    zygosity: Zygosity | None
    mhc_class: MhcClass
    chain: HlaChain | None
    evidence_type: Literal["DNA", "RNA", "CUSTOM"]
    source: ImplementationId
    quality: HlaQuality
```

**Implementations:**

- `optitype`：主要 HLA-A/B/C class-I；
- `hlahd`：class-I/II，独立 reference/license；
- `custom_hla`：用户证据，不是预测算法。

必需 class 无兼容实现时 planning 失败；成功无 call 为 `EMPTY`。License 缺失对必需 capability 为 `FAILED`，可选 capability 可显式 skip。

按 sample/typer scatter；cache/provenance 含 evidence、HLA reference、typer/image、参数和 license fingerprint。科学等价按 locus、resolution、zygosity、class/chain 和 call 比较。

保留原生 DNA HLA-HD 结果引用。补充 MixMHC2pred 兼容路径按专用支持列表从这份结果生成 DR 和 DP/DQ 配对；迁移至规范化证据前比较逐 locus、链、分辨率和配对。 [HLA-HD 原生产物](../../../nextNEOpi.nf#L5091) · [配对规则](../../../bin/HLAHD2mixMHC2pred2.py#L97)

```yaml
methods:
  hla_typers: [optitype, hlahd]
```

## `ResolveHlaGenotype`

```python
class ResolveHlaGenotype(
    CapabilityImplementation[ResolveHlaRequest, ArtifactRef[ResolvedHlaGenotype]], Protocol
): ...

class ResolveHlaRequest(BaseModel, frozen=True):
    case_id: CaseId
    callsets: tuple[ArtifactRef[HlaCallset], ...]
    supported_alleles: ArtifactRef[HlaSupportCatalog]
    policy: HlaResolutionPolicy

class ResolvedHlaGenotype(BaseModel, frozen=True):
    accepted: tuple[ResolvedHlaAllele, ...]
    rejected: tuple[RejectedHlaAllele, ...]
    class_ii_pairs: tuple[HlaClassIiPair, ...]
    decision_trace: tuple[HlaDecision, ...]
```

`legacy_compatible_v1` 首期：以 DNA 为主，可按 policy 用 RNA 补充；custom precedence/force DNA/RNA 明确。所有输入 call 必须出现在 accepted 或 rejected trace 中；pVAC 不支持的 allele 不能静默消失；class-II alpha/beta pairing 保留。

**Errors:** `HLA_REQUIRED_CLASS_MISSING`、`HLA_CALLSET_CASE_MISMATCH`、`HLA_RESOLUTION_CONFLICT`、`HLA_PAIR_INVALID`。纯 Python、按 case、低资源。Cache 含全部 callsets/catalog/policy；测试覆盖 homozygous DNA+RNA、custom-only、低分辨率、重复与空 HLA。

```yaml
policies:
  hla_resolution:
    strategy: legacy_compatible_v1
    required_mhc_classes: [I, II]
    allow_rna_completion: true
```
