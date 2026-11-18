# `nextneopi.capabilities.ccf_tmb`

Cancer Cell Fraction 与 Tumor Mutational Burden API；contract `1.0.0`。

## API Summary

| Symbol | ID | Request → Result | Stability |
|---|---|---|---|
| `EstimateCCF` | IF-CCF-001 | `EstimateCcfRequest → CcfResult` | Experimental |
| `ComputeTMB` | IF-TMB-001 | `ComputeTmbRequest → TmbMetricSet` | Experimental |

## `EstimateCCF`

```python
class EstimateCCF(CapabilityImplementation[EstimateCcfRequest, CcfResult], Protocol): ...

class EstimateCcfRequest(BaseModel, frozen=True):
    case_id: CaseId
    variants: ArtifactRef[AnnotatedSomaticCallset]
    copy_number: ArtifactRef[CopyNumberProfile]
    purity: ArtifactRef[PurityPloidyResult]
    policy: CcfPolicy

class CcfResult(BaseModel, frozen=True):
    records: ArtifactRef[CcfTable]
    summary: CcfSummary
```

`binomial_grid_v1` 由 CCF.R characterization 后 Python 化。要求 allele-specific CN+purity；精确 variant/segment join，不允许 forward-fill。无合格变异 `EMPTY`；缺 segment/count/purity `FAILED`。按 contig scatter。Errors：`CCF_REQUIRED_FEATURE_MISSING`、`CCF_SEGMENT_NOT_FOUND`、`CCF_COUNT_INVALID`、`CCF_NUMERIC_FAILURE`。Tests：`TST-CONTRACT-CCF-001`、`TST-SCI-CCF-001`。

候选表回填在 CCF 计算后进行。核对病例、参考及规范化 `CHROM/POS/REF/ALT`，显式转换坐标约定；位置相同但 ALT 不同或无法唯一对应时保留缺失原因。旧版按位置前向填充的输出仅用于刻画旧行为。 [旧 CCF 回填](../../../bin/add_CCF.py#L45) · [科学等价计划](../../05_testing/scientific-equivalence-plan.md)

## `ComputeTMB`

```python
class ComputeTMB(CapabilityImplementation[ComputeTmbRequest, TmbMetricSet], Protocol): ...

class ComputeTmbRequest(BaseModel, frozen=True):
    case_id: CaseId
    variants: ArtifactRef[CanonicalSomaticCallset]
    tumor_coverage: ArtifactRef[CoverageMap]
    normal_coverage: ArtifactRef[CoverageMap]
    callable_regions: ArtifactRef[IntervalSet]
    consequences: ResultSlot[ArtifactRef[ConsequenceTable]]
    ccf: ResultSlot[ArtifactRef[CcfTable]]
    policy: TmbPolicy

class TmbMetric(BaseModel, frozen=True):
    metric_id: Literal["all", "coding", "clonal"]
    numerator: int = Field(ge=0)
    denominator_bases: int = Field(gt=0)
    value_mutations_per_mb: float = Field(ge=0)
    policy_version: SemVer

class TmbMetricSet(BaseModel, frozen=True):
    metrics: Mapping[Literal["all", "coding", "clonal"], ResultSlot[TmbMetric]]
```

每个 metric 独立五态。未请求 clonal 为 slot `NOT_REQUESTED`；无 mutation 是数值0且 `MATERIALIZED`；denominator 0 为该 slot `FAILED`。必需 metric 失败使外层 FAILED。

Errors：`TMB_DENOMINATOR_EMPTY`、`TMB_COORDINATE_MISMATCH`、`TMB_CONSEQUENCE_REQUIRED`、`TMB_CCF_REQUIRED`。按 case/metric；cache 含 callable、variants、policy。Tests：`TST-CONTRACT-TMB-001`、`TST-SCI-TMB-001`。

```yaml
methods: {ccf_estimator: binomial_grid_v1}
policies:
  tmb: {metrics: [all, coding, clonal], min_depth: 10, unit: mutations_per_mb}
```
