# `nextneopi.capabilities.annotation`

正常胚系上下文、VEP consequence 和 proximal phase API。所有接口 contract version `1.0.0`。

## API Summary

| Symbol | ID | Request → Result | Stability |
|---|---|---|---|
| `CallAndFilterNormalGermline` | IF-VAR-005 | `CallNormalGermlineRequest → GermlineContextCallset` | Beta |
| `AnnotateVariantConsequences` | IF-ANN-001 | `AnnotateConsequencesRequest → ConsequenceResult` | Beta |
| `BuildProximalPhaseContext` | IF-PHS-001 | `BuildPhaseContextRequest → PhaseContext` | Beta |

## `CallAndFilterNormalGermline`

```python
class CallAndFilterNormalGermline(CapabilityImplementation[CallNormalGermlineRequest, ArtifactRef[GermlineContextCallset]], Protocol): ...

class CallNormalGermlineRequest(BaseModel, frozen=True):
    normal_bam: ArtifactRef[RecalibratedBam]
    reference: ReferenceBundleRef
    intervals: CallableIntervalPlan
    filter_policy: GermlineFilterPolicy
```

实现 `gatk_nvscore`，用于 proximal context，不是临床 germline 报告。零变异返回带 empty VCF 的 `EMPTY`；模型/reference/shard 错误为 `FAILED`。按 interval scatter，禁止 partial gather。Tests：`TST-CONTRACT-VAR-005`、`TST-INT-ANN-001`。

## `AnnotateVariantConsequences`

```python
class AnnotateVariantConsequences(CapabilityImplementation[AnnotateConsequencesRequest, ConsequenceResult], Protocol): ...

class AnnotateConsequencesRequest(BaseModel, frozen=True):
    somatic_callset: ArtifactRef[ConsensusSomaticCallset]
    germline_context: ResultSlot[ArtifactRef[GermlineContextCallset]]
    reference: ReferenceBundleRef
    policy: ConsequencePolicy

class AnnotatedSomaticCallset(BaseModel, frozen=True):
    vcf: ArtifactRef[AnnotatedVcfFile]
    index: ArtifactRef[VcfIndex]
    reference: ReferenceIdentity
    annotation_version: str
    variant_count: int

class ConsequenceResult(BaseModel, frozen=True):
    annotated_callset: ResultSlot[ArtifactRef[AnnotatedSomaticCallset]]
    consequences: ResultSlot[ArtifactRef[ConsequenceTable]]
    protein_context: ResultSlot[ArtifactRef[ProteinContextSet]]
```

`AnnotatedSomaticCallset` 是下游 phase、CCF 和三类 neoantigen 的唯一 canonical 类型；不再使用模糊 `AnnotatedVcf` 别名。实现 `vep`，固定 cache/plugin/image。输入空时三个 slot 均 `EMPTY`；必需 annotated/consequence slot 失败使外层失败，按 contig scatter。

跨模块比较以参考版本和规范化 `CHROM/POS/REF/ALT` 对齐，核对 VCF/索引、坐标约定与注释版本。同一位置的两个 ALT 分别保留。 [变异接口](../../03_interfaces/variant-interfaces.md)

Errors：`ANNOTATION_SCHEMA_MISMATCH`、`VEP_CACHE_INCOMPATIBLE`、`PLUGIN_MISSING`。Cache 含 VEP/cache/plugin/policy；Tests：`TST-CONTRACT-ANN-001`、`TST-SCI-ANN-001`。

```yaml
methods: {consequence_annotator: vep}
```

## `BuildProximalPhaseContext`

```python
class BuildProximalPhaseContext(CapabilityImplementation[BuildPhaseContextRequest, ArtifactRef[PhaseContext]], Protocol): ...

class BuildPhaseContextRequest(BaseModel, frozen=True):
    somatic: ArtifactRef[AnnotatedSomaticCallset]
    germline: ResultSlot[ArtifactRef[GermlineContextCallset]]
    tumor_bam: ArtifactRef[RecalibratedBam]
    reference: ReferenceBundleRef
    requested_evidence: PhaseEvidenceLevel
```

`read_backed` 和 `annotation_only` 代表不同证据等级；fallback 写 `degraded_from`。未请求为 `NOT_REQUESTED`，无邻近上下文为 `EMPTY`。即使旧通道存在注释 VCF，仍须独立检查相位证据和实际 pVAC `-p` 参数。Errors：`PHASE_SAMPLE_MISMATCH`、`READ_BACKED_IMPLEMENTATION_MISSING`、`PHASE_CONFLICT`。按 contig scatter；Tests：`TST-CONTRACT-PHS-001`、`TST-SCI-PHS-001`。 [旧回退](../../../nextNEOpi.nf#L3759) · [实际参数](../../../nextNEOpi.nf#L5702)

```yaml
methods: {phase_context: read_backed}
policies: {phase_fallback: annotation_only}
```
