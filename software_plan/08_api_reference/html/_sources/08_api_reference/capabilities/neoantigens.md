# `nextneopi.capabilities.neoantigens`

Canonical、fusion 和 splice neoantigen prediction API。Contract version 均为 `1.0.0`。

## API Summary

| Symbol | ID | Request → Result | Stability |
|---|---|---|---|
| `PredictCanonicalNeoantigens` | IF-NEO-001 | `PredictCanonicalRequest → CanonicalNeoantigenTable` | Beta |
| `PredictFusionNeoantigens` | IF-NEO-002 | `PredictFusionNeoantigensRequest → FusionNeoantigenTable` | Experimental |
| `PredictSpliceNeoantigens` | IF-NEO-003 | `PredictSpliceNeoantigensRequest → SpliceNeoantigenTable` | Experimental |

## 公共模型

```python
class NeoantigenIdentity(BaseModel, frozen=True):
    source_event: VariantIdentity | FusionEventId | SpliceEventId
    transcript_id: TranscriptId
    consequence: str
    mutant_peptide: AminoAcidSequence
    hla: HlaAllele
    mhc_class: MhcClass

class NeoantigenTable(BaseModel, frozen=True):
    source_type: Literal["CANONICAL", "FUSION", "SPLICE", "AGGREGATED"]
    candidates: ArtifactRef[NeoantigenCandidateTable]
    candidate_count: int

class CanonicalNeoantigenTable(NeoantigenTable): ...
class FusionNeoantigenTable(NeoantigenTable): ...
class SpliceNeoantigenTable(NeoantigenTable): ...
```

三类结果共享 `NeoantigenTable` 基类，因而可直接消费于 similarity/scoring/reporting。聚合函数见 `nextneopi.application.aggregate_neoantigen_candidates`。

## `PredictCanonicalNeoantigens`

```python
class PredictCanonicalNeoantigens(CapabilityImplementation[PredictCanonicalRequest, ArtifactRef[CanonicalNeoantigenTable]], Protocol): ...

class PredictCanonicalRequest(BaseModel, frozen=True):
    case_id: CaseId
    variants: ArtifactRef[AnnotatedSomaticCallset]
    phase: ResultSlot[ArtifactRef[PhaseContext]]
    hla: ArtifactRef[ResolvedHlaGenotype]
    purity: ArtifactRef[PurityPloidyResult]
    expression: ResultSlot[ArtifactRef[ExpressionMatrix]]
    policy: NeoantigenPredictionPolicy
```

首期 `pvacseq`；注释变异、适用 HLA、所选纯度必需。按 policy 独立检查相位 slot；缺少 read-backed 证据且允许降级时，按实际等级记录，旧 pVACseq 省略 `-p`。无 RNA 时 expression slot 为 `NOT_REQUESTED`，保留已测量值 `0` 的科学含义。按 case/HLA scatter 并完整 gather；成功零候选 `EMPTY`。Errors：`NEO_HLA_REQUIRED`、`NEO_PURITY_REQUIRED`、`PREDICTOR_UNSUPPORTED_ALLELE`、`PREDICTION_SCHEMA_MISMATCH`。Tests：`TST-CONTRACT-NEO-001`、`TST-SCI-NEO-001`。 [旧输入和相位参数](../../../nextNEOpi.nf#L5674)

## `PredictFusionNeoantigens`

```python
class PredictFusionNeoantigens(CapabilityImplementation[PredictFusionNeoantigensRequest, ArtifactRef[FusionNeoantigenTable]], Protocol): ...

class PredictFusionNeoantigensRequest(BaseModel, frozen=True):
    fusions: ArtifactRef[FusionCallset]
    hla: ArtifactRef[ResolvedHlaGenotype]
    expression: ResultSlot[ArtifactRef[ExpressionMatrix]]
    policy: NeoantigenPredictionPolicy
```

实现 `neofuse_compatible`；无 fusion `EMPTY`、无 RNA `NOT_REQUESTED`、protocol 不支持 `SKIPPED_UNSUPPORTED`。Tests：`TST-CONTRACT-NEO-002`。

旧版候选由编排层从 IF-RNA-001/IF-FUS-001 共用的 NeoFuse 执行中收集。结果记录同一执行引用和来源事件。 [旧 NeoFuse 输出](../../../nextNEOpi.nf#L5364)

## `PredictSpliceNeoantigens`

```python
class PredictSpliceNeoantigens(CapabilityImplementation[PredictSpliceNeoantigensRequest, ArtifactRef[SpliceNeoantigenTable]], Protocol): ...

class PredictSpliceNeoantigensRequest(BaseModel, frozen=True):
    events: ArtifactRef[SpliceEventCallset]
    annotated_variants: ArtifactRef[AnnotatedSomaticCallset]
    hla: ArtifactRef[ResolvedHlaGenotype]
    purity: ArtifactRef[PurityPloidyResult]
    policy: NeoantigenPredictionPolicy
```

实现 `pvacsplice`；3' tag 可 skip，无 event `EMPTY`。Tests：`TST-CONTRACT-NEO-003`。

## Shared execution

三者 cache/provenance 均含 source identity、HLA、purity/expression/phase、predictor/model/image/filter policy。科学等价比较 event/variant、transcript、consequence、peptide、HLA/MHC、filter 和 predictor-specific 容差。

分别保留全量、过滤、聚合视图及重复计数，并为每条预测记录模型及版本、端点（BA/EL/加工/稳定性/IM）、分数、单位或百分位、排序方向与适用性。pVACtools 5.3.0 的旧合并百分位按原算法保存用于回归。新增算法独立旁路运行，比较相同可评分肽–HLA 对，另报告完整候选集的覆盖率和缺失原因。 [旧版汇总](https://raw.githubusercontent.com/griffithlab/pVACtools/v5.3.0/pvactools/lib/output_parser.py) · [替换实验](../../02_modules/second-layer-algorithm-inventory.md#替换实验与验收) · [验收矩阵](../../05_testing/acceptance-test-matrix.md)

MixMHC2pred 兼容适配器作为独立的 Class II 呈递补充路径，使用 pVAC 长肽、相应事件证据和原始 DNA HLA-HD（或经验证的规范化配对证据）。这个输入集合超出现有 IF-NEO-001/003 的最终分型字段，待补充路径验收时再明确公共请求。 [旧补充预测路径](../../../nextNEOpi.nf#L6265) · [接口说明](../../03_interfaces/neoantigen-interfaces.md)

```yaml
methods:
  canonical_neoantigen: pvacseq
  fusion_neoantigen: neofuse_compatible
  splice_neoantigen: pvacsplice
```
