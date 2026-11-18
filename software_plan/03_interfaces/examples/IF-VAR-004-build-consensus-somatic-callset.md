# IF-VAR-004 `BuildConsensusSomaticCallset` 接口文档样例

> 本文是 nextNEOpi 子功能接口文档的完整样例，可作为其他 capability 文档的编写模板。它描述目标 Python 接口，不表示代码已经实现。

## 1. 接口元数据

| 字段 | 值 |
|---|---|
| Interface ID | `IF-VAR-004` |
| Python name | `BuildConsensusSomaticCallset` |
| Contract version | `1.0.0` |
| Status | `Proposed` |
| Owning module | [`MOD-05 Somatic Variants`](../../02_modules/MOD-05-somatic-variants.md) |
| Upstream interfaces | `IF-VAR-001 CallSomaticSmallVariants`、`IF-VAR-003 NormalizeSomaticCallset` |
| Downstream interfaces | `IF-ANN-001 AnnotateVariantConsequences`、`IF-CCF-001 EstimateCCF`、`IF-TMB-001 ComputeTMB` |
| First recipe | `wes_dna_canonical` |
| Requirement IDs | `REQ-FUN-008`、`REQ-FUN-009`、`REQ-FUN-010` |
| Risk IDs | `RISK-011`、`RISK-014`、`RISK-015` |
| Primary owner | Somatic Variant Domain Owner |
| Required reviewers | Bioinformatics、Python Architecture、Test Engineering |

相关约定：

- [接口约定](../interface-conventions.md)
- [Capability 模型](../capability-model.md)
- [错误与状态模型](../../04_specifications/error-and-status-model.md)
- [工件 Schema](../../04_specifications/schemas/artifact.schema.json)
- [科学等价测试计划](../../05_testing/scientific-equivalence-plan.md)

## 2. 目的

将两个或多个已经规范化的体细胞变异 callset 按版本化科学策略合并为高置信 callset。首个策略 `primary_confirmed` 保留 primary caller 的记录表达，只接受至少被一个 confirming caller 支持的同一规范 allele，并为每个 allele 保存 support provenance。

该接口解决的是**跨 caller 科学共识**，而不是第三方 caller 的执行、VCF 格式修复或 VEP 注释。

## 3. 科学语义

### 3.1 `primary_confirmed` 定义

设：

- `P` 为 primary caller 的规范 allele 集合；
- `C₁ … Cₙ` 为成功完成的 confirming caller 规范 allele 集合；
- `support(v)` 为包含 allele `v` 的 caller 集合，并始终包含 primary；
- `minimum_callers >= 2`。

则高置信集合为：

```text
HC = {v ∈ P | |support(v)| >= minimum_callers}
```

默认 `minimum_callers = 2`，即 primary 加至少一个 confirming caller。

### 3.2 必须保持的行为

1. 输出候选只来自 primary callset。
2. confirming-only allele 不进入高置信输出。
3. caller 支持必须基于规范 allele identity，而不是只比较 `CHROM:POS`。
4. primary 原生表达可以作为输出 VCF 表达基础，但必须附规范 identity 和 support metadata。
5. 每个输出 allele 必须记录支持它的 caller ID 与 implementation version。
6. 未确认的 primary allele 可输出到独立 supplemental artifact，不能混入 confirmed callset。
7. caller `FAILED` 不能当作“该 caller 不支持此 allele”。
8. caller `EMPTY` 表示成功但没有 allele，可以作为可用 caller 参与可用性判断，但不会提供 allele support。

### 3.3 明确非职责

本接口不负责：

- 调用 Mutect2、VarScan2、Strelka2 或 Mutect1；
- 将 caller 原生 FORMAT 转换为 `AD/DP/AF`；
- left normalization、多等位拆分或 contig alias 修复；
- 决定哪个 caller 应作为 primary；该值由配置 policy 指定；
- VEP 注释、phase、CCF 或 TMB；
- 判断不同 caller 方法在科学上等价。

上述前置转换属于 `IF-VAR-003 NormalizeSomaticCallset`。

## 4. 当前代码映射

现有实现位于 [`bin/make_hc_vcf.py`](../../../bin/make_hc_vcf.py)，由 [`nextNEOpi.nf`](../../../nextNEOpi.nf) 中高置信 VCF 流程调用。

现有脚本已经表达了以下核心意图：

- primary 记录仅在任一 confirming reader 同步到记录时进入 confirmed VCF；
- 输出 `VariantCalledBy`；
- 未确认 primary 记录写入另一个 VCF；
- 对 VarScan2/Strelka2 做部分 FORMAT 转换。

目标设计将其拆为：

1. caller-specific normalization：`IF-VAR-003`；
2. 纯领域共识：本文 `IF-VAR-004`；
3. VCF renderer：输出 adapter。

旧脚本使用 `walk_together` 同步位置，但没有在共识函数中显式校验 REF/ALT。重构必须用规范 allele identity 消除“同位置不同 ALT 被误认为支持”的风险，并通过 characterization test 记录行为差异。

## 5. 输入模型

### 5.1 Python 类型草案

```python
from __future__ import annotations

from typing import Annotated, Literal
from pydantic import BaseModel, Field, model_validator

ImplementationId = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_.-]*$")]
CaseId = Annotated[str, Field(pattern=r"^[A-Za-z0-9_.-]+$")]


class Sha256Digest(BaseModel, frozen=True):
    algorithm: Literal["sha256"] = "sha256"
    value: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]


class ReferenceIdentity(BaseModel, frozen=True):
    assembly: str
    dictionary_digest: Sha256Digest


class CanonicalCallsetRef(BaseModel, frozen=True):
    artifact_id: str
    uri: str
    checksum: Sha256Digest
    case_id: CaseId
    caller: ImplementationId
    implementation_version: str
    state: Literal["MATERIALIZED", "EMPTY"]
    reference: ReferenceIdentity
    normalization_contract: Literal["IF-VAR-003@1"]
    sample_order: tuple[str, ...]
    allele_count: int = Field(ge=0)


class ConsensusPolicy(BaseModel, frozen=True):
    strategy: Literal["primary_confirmed"]
    primary: ImplementationId
    minimum_callers: int = Field(default=2, ge=2)
    on_failed_confirming_caller: Literal["fail", "continue_if_minimum_available"] = "fail"
    preserve_primary_representation: bool = True


class BuildConsensusSomaticCallsetRequest(BaseModel, frozen=True):
    contract_version: Literal["1.0.0"] = "1.0.0"
    run_id: str
    case_id: CaseId
    callsets: tuple[CanonicalCallsetRef, ...]
    policy: ConsensusPolicy

    @model_validator(mode="after")
    def validate_callers(self) -> "BuildConsensusSomaticCallsetRequest":
        callers = [item.caller for item in self.callsets]
        if len(callers) != len(set(callers)):
            raise ValueError("caller IDs must be unique")
        if self.policy.primary not in callers:
            raise ValueError("primary caller must be present")
        if len(callers) < self.policy.minimum_callers:
            raise ValueError("not enough configured callers")
        return self
```

### 5.2 必需输入

| 字段 | 必需 | 说明 |
|---|---|---|
| `run_id` | 是 | 当前运行身份。 |
| `case_id` | 是 | 所有 callset 必须属于同一 case。 |
| `callsets` | 是 | 至少两个由 `IF-VAR-003@1` 产生的 callset。 |
| `policy.strategy` | 是 | 首版仅 `primary_confirmed`。 |
| `policy.primary` | 是 | 必须出现在 `callsets[].caller`。 |
| `policy.minimum_callers` | 是 | 包含 primary 在内，至少为 2。 |
| `on_failed_confirming_caller` | 是 | 失败 caller 的处理策略。 |

### 5.3 可选输入

首版没有隐式可选文件。未来增加 callable-region intersection 或 caller weight 时必须提升 contract minor/major，并明确科学语义，不能通过任意 `parameters: dict` 绕过类型。

## 6. 输出模型

```python
class AlleleIdentity(BaseModel, frozen=True):
    assembly: str
    sequence_id: str
    position: int = Field(ge=1)
    reference_bases: str
    alternate_bases: str
    normalization: Literal["left_aligned_biallelic_v1"]


class CallerSupport(BaseModel, frozen=True):
    caller: ImplementationId
    implementation_version: str
    callset_artifact_id: str
    is_primary: bool


class VariantSupportDecision(BaseModel, frozen=True):
    allele: AlleleIdentity
    accepted: bool
    supports: tuple[CallerSupport, ...]
    required_support_count: int
    reason: Literal["CONFIRMED", "PRIMARY_ONLY"]


class ConsensusSummary(BaseModel, frozen=True):
    primary_caller: ImplementationId
    available_callers: tuple[ImplementationId, ...]
    failed_callers: tuple[ImplementationId, ...]
    primary_allele_count: int = Field(ge=0)
    confirmed_allele_count: int = Field(ge=0)
    primary_only_allele_count: int = Field(ge=0)


class BuildConsensusSomaticCallsetResult(BaseModel, frozen=True):
    confirmed_callset: "ArtifactRef"
    primary_only_callset: "ArtifactRef"
    support_table: "ArtifactRef"
    decisions: tuple[VariantSupportDecision, ...]
    summary: ConsensusSummary
```

### 6.1 输出工件

| 工件 | Artifact kind | 内容 |
|---|---|---|
| `confirmed_callset` | `CONSENSUS_SOMATIC_VCF` | 被足够 caller 支持的 primary allele。即使为零也生成合法 empty VCF。 |
| `primary_only_callset` | `PRIMARY_ONLY_SOMATIC_VCF` | 未达到最小支持数的 primary allele。 |
| `support_table` | `VARIANT_SUPPORT_TABLE` | 每个 primary allele 的支持 caller、版本、accepted 和 reason。 |
| `summary` | 内联结构 | 数量、可用/失败 caller 和 policy 摘要。 |

### 6.2 `VariantCalledBy`

为兼容旧结果，confirmed/primary-only VCF 可以渲染：

```text
##INFO=<ID=VariantCalledBy,Number=.,Type=String,Description="Implementations supporting this normalized allele">
```

字段值按稳定 caller ID 排序，primary 始终排第一。权威 support 信息是 `support_table` 和 provenance，VCF INFO 是兼容投影。

## 7. 前置条件

planning/调用前必须满足：

1. 所有 callset 为 `MATERIALIZED` 或 `EMPTY`；`FAILED` 输入按 policy 在上游处理。
2. 所有 callset 具有相同 `case_id`。
3. reference assembly 和 dictionary digest 完全一致。
4. normalization contract 为接口支持版本。
5. caller ID 唯一。
6. primary 存在且成功完成。
7. 可用 caller 数不少于 `minimum_callers`。
8. sample order/schema 可被 renderer 兼容；差异不能静默重排。
9. 每个 callset 已拆为单 ALT、left-aligned 规范记录。

## 8. 数据不变量

### 8.1 Allele identity

两个记录仅在以下字段全部一致时表示同一 allele：

```text
assembly
sequence_id after approved alias normalization
1-based normalized position
normalized reference_bases
normalized alternate_bases
normalization algorithm/version
```

因此：

```text
chr1:100 A>C != chr1:100 A>G
chr1:100 AT>A == left-normalized equivalent representation only after IF-VAR-003
```

### 8.2 集合不变量

```text
confirmed ⊆ primary
primary_only ⊆ primary
confirmed ∩ primary_only = ∅
confirmed ∪ primary_only = primary
```

每个 primary allele 恰好产生一条 decision。每条 accepted decision 的 support 数量大于等于 `minimum_callers`。

### 8.3 状态不变量

- primary 为 `EMPTY`：confirmed 和 primary-only 均为空，接口返回 `EMPTY`。
- primary 非空但无 confirmed allele：接口返回 `EMPTY`，同时 primary-only 为非空 supplemental artifact。
- 有 confirmed allele：接口返回 `MATERIALIZED`。
- 任一不可忽略的 caller 失败：接口返回 `FAILED`，不能把它当作空 callset。

## 9. 算法契约

### 9.1 参考伪代码

```python
def build_primary_confirmed_consensus(request):
    validated = validate_request(request)
    primary = validated.primary_callset
    confirming = validated.confirming_callsets

    indexes = {
        callset.caller: stream_or_index_by_allele_identity(callset)
        for callset in confirming
    }

    confirmed = []
    primary_only = []
    decisions = []

    for primary_variant in stream_variants(primary):
        allele = primary_variant.allele_identity
        supports = [support_from_primary(primary, allele)]

        for caller, index in indexes.items():
            match = index.find_exact(allele)
            if match is not None:
                supports.append(support_from_match(caller, match))

        accepted = len(supports) >= request.policy.minimum_callers
        if accepted:
            confirmed.append(preserve_primary_record(primary_variant, supports))
        else:
            primary_only.append(preserve_primary_record(primary_variant, supports))

        decisions.append(make_decision(allele, supports, accepted))

    assert_partition_invariants(primary, confirmed, primary_only, decisions)
    return commit_typed_outputs(confirmed, primary_only, decisions)
```

### 9.2 确定性

输出不得依赖 callset 输入顺序、Python hash 随机化或文件系统 glob 顺序。support caller 顺序固定为 primary 第一，其余按 implementation ID 排序。VCF 记录按 reference dictionary/position/REF/ALT 排序。

### 9.3 内存策略

实现必须支持流式处理或按 contig/shard 索引，不能默认将全基因组 VCF 全部载入内存。索引方式是实现细节，但不能改变集合语义。

## 10. Capability 与实现

### 10.1 Capability 声明

| 维度 | 首版要求 |
|---|---|
| Assay | `WES`、`WGS` |
| Variant kinds | `SNV`、`INDEL` |
| Input state | `MATERIALIZED`、`EMPTY` |
| Input schema | `CanonicalSomaticCallset@1` |
| Reference | 同 assembly + dictionary digest |
| Scatter axis | `contig` 或 `none` |
| Partial gather | 不允许 |
| Empty input | typed empty |

### 10.2 实现列表

| Implementation | 状态 | 语义 |
|---|---|---|
| `primary_confirmed_v1` | 首期必需 | 本文定义的 primary+confirming 规则。 |
| `majority_vote_v1` | 未来候选 | 对所有 caller 对称投票，不与当前策略科学等价。 |
| `union_v1` | 未来候选 | caller 并集，不与当前策略科学等价。 |

后两种实现只能作为新 policy/recipe 明确选择，不能在 `primary_confirmed_v1` 不可用时自动降级。

## 11. 配置规范

```yaml
methods:
  somatic_callers:
    - mutect2
    - varscan2
    - strelka2

policies:
  somatic_consensus:
    implementation: primary_confirmed_v1
    strategy: primary_confirmed
    primary: mutect2
    minimum_callers: 2
    on_failed_confirming_caller: fail
    preserve_primary_representation: true
```

### 11.1 配置校验

- `primary` 必须包含在 `methods.somatic_callers`。
- `minimum_callers <= len(somatic_callers)`。
- `minimum_callers >= 2`。
- 选择的 consensus implementation 必须支持所有输入 variant kinds/reference。
- 若 `on_failed_confirming_caller=continue_if_minimum_available`，失败后剩余可用 caller 数仍必须达到 `minimum_callers`。

## 12. 错误模型

| Error code | Category | Retryable | 条件 |
|---|---|---:|---|
| `CONSENSUS_PRIMARY_MISSING` | `CONFIGURATION` | 否 | primary 未配置或无输入。 |
| `CONSENSUS_INSUFFICIENT_CALLERS` | `CAPABILITY` | 否 | 可用 caller 少于最小值。 |
| `CONSENSUS_CALLER_FAILED` | `TOOL` | 取决于上游 | policy 不允许忽略失败 caller。 |
| `CALLSET_CASE_MISMATCH` | `INVALID_INPUT` | 否 | callset 属不同 case。 |
| `CALLSET_REFERENCE_MISMATCH` | `INVALID_INPUT` | 否 | assembly/dictionary 不同。 |
| `CALLSET_SCHEMA_MISMATCH` | `SCHEMA` | 否 | normalization/sample schema 不兼容。 |
| `ALLELE_IDENTITY_INVALID` | `DATA_INTEGRITY` | 否 | allele 未规范化或非法。 |
| `CONSENSUS_INVARIANT_VIOLATION` | `INTERNAL` | 否 | confirmed/primary-only 分区不成立。 |
| `ARTIFACT_COMMIT_FAILED` | `TRANSIENT_INFRASTRUCTURE` | 是 | staging 校验通过但原子提交失败。 |

错误必须关联 `run_id`、`case_id`、task/attempt 和相关 artifact ID，不在日志输出完整 VCF 内容。

## 13. Scatter/Gather

### 13.1 Scatter

可按 reference dictionary 的 contig scatter。稳定 shard ID：

```text
<case_id>.consensus.<sequence_index>.<sequence_id>
```

每个 shard 必须同时接收 primary 和所有 confirming callset 的对应 contig 分片。不能因某 caller 在该 contig 无记录而省略其 typed empty shard。

### 13.2 Gather

- 必须等待全部预期 contig shard 成功或合法 `EMPTY`。
- 不允许 partial gather。
- 合并顺序遵循 reference dictionary。
- header、sample order、INFO/FORMAT schema 必须一致。
- gather 后重新验证集合不变量和总计数。

## 14. 资源模型

这是纯 Python/htslib-backed transform，不需要第三方算法容器或许可证。

建议默认资源：

```yaml
resources:
  cpus: 1
  memory_mb: 2048
  runtime_minutes: 60
  scratch_mb: 4096
  scaling_model: "memory=max(2048, total_vcf_gib*512); scatter_by_contig_when_total_vcf_gib>4"
```

站点可覆盖 CPU/内存/时间，但不能改变 scientific policy。实现应优先流式读取；大 callset 自动使用 contig scatter，而不是无限增加内存。

若纯 Python 任务也在 core OCI image 中执行，必须记录 core image digest；本接口不允许联网。

## 15. Cache key

除通用字段外，必须包含：

```text
IF-VAR-004 contract version
consensus implementation/version
primary caller ID
minimum_callers
failed-caller policy
preserve-primary-representation flag
ordered set of input caller IDs + implementation versions
all input artifact checksums
normalization contract/version
reference assembly + dictionary digest
renderer schema/version
```

输入 callset 列表顺序不应影响 key；应先按 caller ID 规范排序。CPU、partition、account 默认不进入 key。

## 16. Provenance

### 16.1 Task 级

记录：

- resolved policy；
- primary/confirming caller IDs 和版本；
- 输入 artifact IDs/checksums/states；
- reference/normalization identity；
- implementation/core image；
- cache hit/miss；
- task/attempt/resource；
- confirmed/primary-only 数量。

### 16.2 Allele 级 support

示例：

```json
{
  "allele": {
    "assembly": "GRCh38",
    "sequence_id": "chr7",
    "position": 140453136,
    "reference_bases": "A",
    "alternate_bases": "T",
    "normalization": "left_aligned_biallelic_v1"
  },
  "accepted": true,
  "required_support_count": 2,
  "supports": [
    {"caller": "mutect2", "implementation_version": "4.6.1.0", "is_primary": true},
    {"caller": "varscan2", "implementation_version": "2.4.3", "is_primary": false}
  ],
  "reason": "CONFIRMED"
}
```

不得只记录逗号字符串而丢失 caller 版本和输入 artifact。

## 17. 测试规范

### 17.1 Unit tests

| Test ID | Given | Expected |
|---|---|---|
| `TST-UNIT-VAR-004-001` | primary A>C，confirming A>C | allele confirmed。 |
| `TST-UNIT-VAR-004-002` | primary A>C，confirming A>G，同位置 | 不确认；进入 primary-only。 |
| `TST-UNIT-VAR-004-003` | primary-only allele | confirmed empty，support 仅 primary。 |
| `TST-UNIT-VAR-004-004` | confirming-only allele | 不出现在任一 primary 分区。 |
| `TST-UNIT-VAR-004-005` | 三 callers，最小支持 3 | 只有三者均支持时确认。 |
| `TST-UNIT-VAR-004-006` | confirming callset `EMPTY` | 成功处理但不提供支持。 |
| `TST-UNIT-VAR-004-007` | confirming `FAILED`，policy=fail | 接口失败。 |
| `TST-UNIT-VAR-004-008` | confirming `FAILED`，剩余仍满足 minimum | 按 continue policy 完成并记录 failed caller。 |
| `TST-UNIT-VAR-004-009` | primary `EMPTY` | typed empty outputs 和零计数。 |
| `TST-UNIT-VAR-004-010` | caller 输入顺序随机 | 输出与 cache key 不变。 |
| `TST-UNIT-VAR-004-011` | reference dictionary 不同 | validation fail。 |
| `TST-UNIT-VAR-004-012` | 多等位未拆分 | schema/identity validation fail。 |
| `TST-UNIT-VAR-004-013` | left-normalized 等价 indel | 在上游规范后精确匹配。 |
| `TST-UNIT-VAR-004-014` | duplicate caller ID | request validation fail。 |
| `TST-UNIT-VAR-004-015` | accepted/primary-only 集合 | 分区不变量成立。 |

Property tests：

- `confirmed` 永远是 primary 子集；
- caller 输入排列不改变结果；
- 增加一个不支持任何 primary allele 的 caller，在 minimum 不变时不改变 confirmed；
- 增加支持某 primary allele 的 caller不会使该 allele 从 accepted 变为 rejected；
- 每个 primary allele 恰有一条 decision。

### 17.2 Contract tests

`TST-CONTRACT-CONS-001` 必须验证：

- Request/Result Pydantic schema；
- deterministic plan/output ordering；
- typed empty；
- error mapping；
- cache key sensitivity/stability；
- artifact companion/index；
- provenance 完整；
- 无网络、无 `shell=True`、不修改输入。

### 17.3 Integration tests

`TST-INT-CONS-001` 使用 Mutect2、VarScan2、Strelka2 的保存 fixture：

1. 经各自 `IF-VAR-003` normalizer；
2. 运行共识；
3. 解析输出 VCF/support table；
4. 验证 primary 表达、support 和 empty；
5. 重复运行验证 cache hit。

### 17.4 Scientific-equivalence tests

`TST-SCI-VAR-001` 在相同输入、caller 版本和 reference 下比较旧/新结果：

- 规范 allele 集合；
- primary-only 集合；
- caller support 集合；
- primary 记录的 FILTER/AD/DP/AF；
- same-position-different-ALT 差异单独列为 characterization。

不比较 VCF 压缩字节、header 顺序或时间戳。若新实现修正旧 ALT 匹配问题，必须标记 `APPROVED_SCIENTIFIC_CHANGE`，不能简单放宽比较规则。

## 18. Demo 场景

输入：

```text
Mutect2 primary:
  chr1:100 A>C
  chr1:200 G>T
  chr1:300 AT>A

VarScan2 confirming:
  chr1:100 A>C
  chr1:200 G>A

Strelka2 confirming:
  chr1:300 AT>A
```

配置 `minimum_callers=2` 后期望：

```text
confirmed:
  chr1:100 A>C  [mutect2,varscan2]
  chr1:300 AT>A [mutect2,strelka2]

primary_only:
  chr1:200 G>T  [mutect2]

ignored confirming-only/same-position-different-ALT:
  chr1:200 G>A
```

运行接口的 SDK 形态：

```python
result = client.capabilities.build_consensus_somatic_callset(request)

assert result.status == ResultStatus.MATERIALIZED
assert result.value.summary.confirmed_allele_count == 2
assert result.value.summary.primary_only_allele_count == 1
```

## 19. 验收条件

- `ACC-IF-VAR-004-001`：所有输入/输出模型、状态和错误均实现并生成 Schema。
- `ACC-IF-VAR-004-002`：全部 unit/property/contract tests 通过，领域分支覆盖率不低于 90%。
- `ACC-IF-VAR-004-003`：same-position-different-ALT 不被确认。
- `ACC-IF-VAR-004-004`：失败 caller 不被当作无变异成功结果。
- `ACC-IF-VAR-004-005`：local/Slurm 和 scatter/non-scatter 产生相同规范结果。
- `ACC-IF-VAR-004-006`：每个 allele 可追踪到 caller/version/input artifact。
- `ACC-IF-VAR-004-007`：已接入 `wes_dna_canonical` recipe，并有可重复 Demo。
- `ACC-IF-VAR-004-008`：旧/新科学等价报告无未解释差异。

## 20. 已知风险与决策点

| 风险 | 处理 |
|---|---|
| 旧 `walk_together` 可能只同步位置 | characterization；目标实现使用 exact normalized allele identity。 |
| primary 切换改变输出表达 | 记录为 policy 变化，cache 和 provenance 必须变化。 |
| caller normalization 不完整 | 在 IF-VAR-003 阻止进入本接口，不在共识阶段猜 FORMAT。 |
| 大 WGS VCF 占用内存 | 流式或按 contig scatter；禁止默认全量 dict。 |
| confirming caller 失败影响结果 | 由显式 policy 决定，报告 failed callers。 |
| 多 caller 结果使用不同 reference | plan/validation fail，不自动 lift-over。 |

## 21. 版本演进规则

以下变化必须提升 contract major：

- 从 primary 子集改为 union/majority；
- 改变 allele identity 定义；
- 改变 `minimum_callers` 的计数是否包含 primary；
- 允许 partial gather；
- 将 caller 失败自动视为无支持。

新增可选 summary 字段、额外兼容 renderer 可以提升 minor。文档和错误信息修订提升 patch。

## 22. 实现完成检查清单

- [ ] Request/Result 与 JSON Schema 完成。
- [ ] 纯 Python domain implementation，无工具调用。
- [ ] exact allele identity 与分区不变量完成。
- [ ] streaming/contig scatter 完成。
- [ ] confirmed、primary-only、support artifacts 原子提交。
- [ ] 五类状态和错误分类完成。
- [ ] cache key 与 provenance 完成。
- [ ] unit/property/contract/integration/scientific tests 完成。
- [ ] YAML、SDK Demo 和 recipe wiring 完成。
- [ ] 生物信息学负责人批准语义。
- [ ] 需求—接口—测试—验收追踪更新。