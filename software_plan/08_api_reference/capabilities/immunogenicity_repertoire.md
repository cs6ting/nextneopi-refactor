# `nextneopi.capabilities.immunity`

Self-similarity、免疫原性评分和 TCR/BCR repertoire API；contract `1.0.0`。

## API Summary

| Symbol | ID | Result | Stability |
|---|---|---|---|
| `CheckSelfSimilarity` | IF-IMM-001 | `SelfSimilarityResult` | Experimental |
| `ScoreImmunogenicity` | IF-IMM-002 | `ImmunogenicityScoreSet` | Experimental |
| `ProfileImmuneRepertoire` | IF-REP-001 | `RepertoireProfile` | Experimental |

## `CheckSelfSimilarity`

```python
class CheckSelfSimilarity(CapabilityImplementation[CheckSelfSimilarityRequest, ArtifactRef[SelfSimilarityResult]], Protocol): ...
class CheckSelfSimilarityRequest(BaseModel, frozen=True):
    candidates: ArtifactRef[NeoantigenTable]
    protein_database: ArtifactRef[ProteinDatabase]
    policy: SimilarityPolicy
```

实现 `blastp_short`。无命中是 materialized evidence；无候选才 `EMPTY`。Errors：`PROTEIN_DATABASE_MISSING`、`BLAST_FAILED`、`SIMILARITY_SCHEMA_MISMATCH`。按 peptide scatter；Tests：`TST-CONTRACT-IMM-001`。

## `ScoreImmunogenicity`

```python
class ModelRef(BaseModel, frozen=True):
    model_id: str
    version: SemVer
    artifact: ArtifactRef[ModelFile]
    applicable_mhc: frozenset[MhcClass]

class ScoreImmunogenicityRequest(BaseModel, frozen=True):
    candidates: ArtifactRef[NeoantigenTable]
    ccf: ResultSlot[ArtifactRef[CcfTable]]
    tmb: ResultSlot[ArtifactRef[TmbMetricSet]]
    models: tuple[ModelRef, ...]
    policy: ImmunogenicityPolicy

class ImmunogenicityScoreSet(BaseModel, frozen=True):
    scores: Mapping[str, ResultSlot[ArtifactRef[ImmunogenicityScoreTable]]]

class ScoreImmunogenicity(CapabilityImplementation[ScoreImmunogenicityRequest, ImmunogenicityScoreSet], Protocol): ...
```

CSiN 和 GBM 每模型一个 ResultSlot。CSiN 用未过滤的常规候选计算样本级分数，GBM 用过滤后的常规 Class I 表计算候选分数。两者在旧流程均不以 CCF/TMB 作为直接输入；现有 slot 按模型需求取用。记录模型版本、候选视图和结果粒度；不适用 `SKIPPED_UNSUPPORTED`、无候选 `EMPTY`、模型失败 `FAILED`。Cache/provenance 含模型/feature/database digest。Tests：`TST-CONTRACT-IMM-002`、数值科学回归。 [旧输入分流](../../../nextNEOpi.nf#L6084)

MixMHC2pred 的旧登记保留在机器可读清单中，实际算法是 [补充 Class II 呈递](neoantigens.md#shared-execution)。免疫原性验收按有实验标注的 T 细胞反应评估候选级模型；样本级指标单独评估。 [第二层算法清单](../../02_modules/second-layer-algorithm-inventory.md)

## `ProfileImmuneRepertoire`

```python
class ProfileImmuneRepertoire(CapabilityImplementation[ProfileRepertoireRequest, ArtifactRef[RepertoireProfile]], Protocol): ...
class ProfileRepertoireRequest(BaseModel, frozen=True):
    case_id: CaseId
    sample: SampleRef
    reads: ArtifactRef[ReadSet]
    material: MoleculeType
    assay: AssayKind
    species: str = "hsa"
    policy: RepertoirePolicy
```

实现 `mixcr`。无 license 在 planning 阶段：必需 capability 失败；可选按 policy `SKIPPED_UNSUPPORTED`。无 clone `EMPTY`。Errors：`REPERTOIRE_PRESET_UNSUPPORTED`、`LICENSE_MISSING`、`MIXCR_FAILED`、`REPERTOIRE_SCHEMA_MISMATCH`。Tests：`TST-CONTRACT-REP-001`、`TST-SCI-REP-001`。

MiXCR 直接消费准备后的 DNA/RNA `ReadSet` 并按样本角色选 preset。可以与候选预测并行执行，结果独立进入报告。 [旧 MiXCR 输入](../../../nextNEOpi.nf#L6880)

```yaml
methods:
  self_similarity: blastp_short
  immunogenicity_scorers: [csin, gbm]
  immune_repertoire: mixcr
```
