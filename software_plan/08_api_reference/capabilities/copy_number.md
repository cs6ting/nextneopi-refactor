# `nextneopi.capabilities.copy_number`

Copy-number、purity 和 ploidy API。

## API Summary

| Symbol | ID | 描述 | Stability |
|---|---|---|---|
| `InferCopyNumber` | IF-CNV-001 | 生成带显式 feature set 的 CNV profile | Experimental |
| `ResolvePurityPloidy` | IF-PUR-001 | 按 policy 选择 purity/ploidy provider | Beta |

## `InferCopyNumber`

```python
class InferCopyNumber(
    CapabilityImplementation[InferCopyNumberRequest, ArtifactRef[CopyNumberProfile]], Protocol
): ...

class InferCopyNumberRequest(BaseModel, frozen=True):
    case_id: CaseId
    tumor_bam: ArtifactRef[RecalibratedBam]
    normal_bam: ArtifactRef[RecalibratedBam]
    assay: AssayDesign
    sex: BiologicalSex
    reference: ReferenceBundleRef
    requested_features: frozenset[CopyNumberFeature]

class CopyNumberProfile(BaseModel, frozen=True):
    segments: ArtifactRef[CopyNumberSegments]
    features: frozenset[CopyNumberFeature]
    purity: ResultSlot[float]
    ploidy: ResultSlot[float]
    quality: CopyNumberQuality
    native_outputs: tuple[ArtifactRef, ...]
```

`CopyNumberFeature` 分别定义 `TOTAL_CN`、`ALLELE_SPECIFIC_CN`、`BAF`、`PURITY`、`PLOIDY`；不能因都输出 TSV 就视为等价。

**Implementations:** ASCAT/Sequenza 可提供 allele-specific+purity/ploidy；CNVkit/FREEC 能力与当前用途不同。第三方 R 算法保留容器，自研 driver/collector 使用 Python。

此请求签名覆盖以 BQSR BAM 为输入的实现。兼容旧 CNVkit 时，需验收其重复标记后的 BAM 和所选纯度输入，不能将该实现视为已接通。 [旧 CNVkit 输入](../../../nextNEOpi.nf#L4344)

**Invariants:** segment coordinate/reference 一致；major/minor/total 关系合法；sex UNKNOWN 不自动设 male reference；purity 0～1、ploidy>0。

**Status:** 无可信 segment 可按 implementation contract `EMPTY` 或 `FAILED`；工具失败绝不能当 empty。按 case/contig/工具策略 scatter。Cache/provenance 含 BAM/assay/sex/reference/tool/image/feature set。

**Errors:** `CNV_FEATURE_UNSUPPORTED`、`CNV_REFERENCE_MISSING`、`SEX_REFERENCE_AMBIGUOUS`、`CNV_SEGMENT_INVALID`。

```yaml
methods: {copy_number: ascat}
```

## `ResolvePurityPloidy`

```python
class ResolvePurityPloidy(
    CapabilityImplementation[ResolvePurityRequest, ArtifactRef[PurityPloidyResult]], Protocol
): ...

class ResolvePurityRequest(BaseModel, frozen=True):
    case_id: CaseId
    candidates: tuple[PurityCandidate, ...]
    policy: PurityResolutionPolicy

class PurityEstimate(BaseModel, frozen=True):
    purity: float
    ploidy: float | None
    quality: QualityScore | None
    source_artifact: ArtifactId | None

class PurityCandidate(BaseModel, frozen=True):
    provider: ImplementationId
    estimate: ResultSlot[PurityEstimate]

class PurityPloidyResult(BaseModel, frozen=True):
    purity: float
    ploidy: ResultSlot[float]
    provider: ImplementationId
    quality: ResultSlot[QualityScore]
    decisions: tuple[ProviderDecision, ...]
```

实现/provider：`configured`、`ascat`、`sequenza`。Fallback 顺序属于 policy，不属于 tool adapter。首期允许显式 0.95，但不得在 CNV 失败后静默生成。

常规和剪接候选从这里消费已选纯度，CCF 是独立计算。回放旧病例时保存实际纯度及 ASCAT、Sequenza 或旧默认值的来源和选择原因。 [纯度选择](../../../nextNEOpi.nf#L4227) · [候选预测接口](neoantigens.md)

```yaml
policies:
  purity:
    providers: [configured]
    configured_value: 0.95
    on_failure: fail
```

**Errors:** `PURITY_PROVIDER_MISSING`、`PURITY_OUT_OF_RANGE`、`PURITY_ALL_PROVIDERS_FAILED`。纯 Python、低资源；cache/provenance 含候选、policy、配置值及每次 accepted/rejected 理由。

**Tests:** configured、ASCAT success、ASCAT→Sequenza、全部失败、XX/XY/UNKNOWN、feature selector 和 segment scientific concordance。
