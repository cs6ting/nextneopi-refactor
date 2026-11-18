# `nextneopi.capabilities.variants`

体细胞 small variant、SV candidate、caller normalization 和高置信 consensus API。

## API Summary

| Symbol | ID | 描述 | Stability |
|---|---|---|---|
| `CallSomaticSmallVariants` | IF-VAR-001 | Matched tumor/normal small-variant calling | Beta |
| `CallSomaticSvCandidates` | IF-VAR-002 | SV 与 small-indel candidate | Experimental |
| `NormalizeSomaticCallset` | IF-VAR-003 | Caller-native VCF → canonical callset | Beta |
| `BuildConsensusSomaticCallset` | IF-VAR-004 | Primary-confirmed consensus | Beta |

## `CallSomaticSmallVariants`

```python
class CallSomaticSmallVariants(
    CapabilityImplementation[CallSomaticVariantsRequest, ArtifactRef[NativeSomaticCallset]],
    Protocol,
): ...

class CallSomaticVariantsRequest(BaseModel, frozen=True):
    case_id: CaseId
    tumor_bam: ArtifactRef[RecalibratedBam]
    normal_bam: ArtifactRef[RecalibratedBam]
    reference: ReferenceBundleRef
    intervals: CallableIntervalPlan
    variant_kinds: frozenset[Literal["SNV", "INDEL"]]
    implementation_config: BaseModel
```

实现：`mutect2`（PON/germline/contamination/orientation）、`varscan2`（mpileup/fpfilter）、`strelka2`（Manta candidate/PE）、`mutect1`（legacy）。它们只共享 contract，不科学等价。

**Returns:** native VCF+index、caller metadata；合法零变异为 `EMPTY`。工具失败不可作为空 caller。

**Scatter:** interval，具体 gather/filter 子图由 implementation 定义。**Errors:** `MATCHED_PAIR_INVALID`、`CALLER_FAILED`、`PON_INCOMPATIBLE`、`INCOMPLETE_SCATTER`。

同实现等价比较 PASS allele、FILTER、AD/DP/AF；cache 含 BAM/ref/interval/参数/镜像。

## `CallSomaticSvCandidates`

```python
class CallSomaticSvCandidates(
    CapabilityImplementation[CallSomaticSvRequest, SomaticSvResult], Protocol
): ...

class CallSomaticSvRequest(BaseModel, frozen=True):
    tumor_bam: ArtifactRef[RecalibratedBam]
    normal_bam: ArtifactRef[RecalibratedBam]
    assay: AssayDesign
    intervals: ResultSlot[CallableIntervalPlan]
```

首期实现 `manta`；PE 必需。Result 含 `sv_callset` 与可选 `small_indel_candidates`，两者分别校验。SE 在 planning 阶段不兼容；无 SV 为 `EMPTY`。

## `NormalizeSomaticCallset`

```python
class NormalizeSomaticCallset(
    CapabilityImplementation[NormalizeCallsetRequest, ArtifactRef[CanonicalSomaticCallset]],
    Protocol,
): ...

class NormalizeCallsetRequest(BaseModel, frozen=True):
    callset: ArtifactRef[NativeSomaticCallset]
    caller: ImplementationId
    reference: ReferenceBundleRef
    policy: VariantNormalizationPolicy
```

**Output 必需字段:** normalized allele identity、PASS/FILTER、tumor/normal AD/DP/AF、caller/version/native record ref。

Caller-specific parser 分别处理 VarScan 百分比、Strelka nucleotide/tier counts、Mutect FORMAT。未知 FORMAT、sample mismatch、非法 REF/ALT 为 `FAILED`；空输入返回 typed `EMPTY`。

**Invariants:** 单 ALT、left-aligned、reference dictionary 一致。可按 contig scatter；normalizer/schema version 进入 cache。测试必须覆盖同位置不同 ALT、多等位、indel 和 chr alias。

## `BuildConsensusSomaticCallset`

```python
class BuildConsensusSomaticCallset(
    CapabilityImplementation[BuildConsensusRequest, ArtifactRef[ConsensusSomaticCallset]],
    Protocol,
): ...

class BuildConsensusRequest(BaseModel, frozen=True):
    case_id: CaseId
    callsets: tuple[ArtifactRef[CanonicalSomaticCallset], ...]
    policy: ConsensusPolicy
```

`primary_confirmed_v1`：输出只来自 primary；至少一个 confirming caller 支持同一规范 allele；失败 caller 不计支持。Result 含 confirmed VCF、primary-only VCF、support table 和 decision trace。

```yaml
policies:
  somatic_consensus:
    implementation: primary_confirmed_v1
    primary: mutect2
    minimum_callers: 2
    on_failed_confirming_caller: fail
```

**Errors:** `CONSENSUS_PRIMARY_MISSING`、`CONSENSUS_INSUFFICIENT_CALLERS`、`CALLSET_REFERENCE_MISMATCH`、`ALLELE_IDENTITY_INVALID`。无 confirmed allele 为 `EMPTY`；不允许 silent union/partial gather。

完整实现样例：[IF-VAR-004 文档](../../03_interfaces/examples/IF-VAR-004-build-consensus-somatic-callset.md)。