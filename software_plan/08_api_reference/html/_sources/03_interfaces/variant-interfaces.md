# 变异、注释与相位接口

## IF-VAR-001 `CallSomaticSmallVariants` v1.0

- **语义/Request/Result**：matched tumor/normal `RecalibratedBam`、reference、intervals → `NativeSomaticCallset`；不含跨 caller consensus。
- **实现能力**：Mutect2（PON/germline/contamination/orientation）、VarScan2（mpileup/fpfilter）、Strelka2（Manta candidate、PE）、Mutect1（legacy）。descriptor 声明 SNV/INDEL、assay/layout、FORMAT/FILTER。
- **不变量/状态**：sample/ref/interval 一致；合法零记录为 `EMPTY`；工具失败不可作为空 caller。
- **Scatter/资源**：可按 interval；implementation 定义 gather/filter 子图和高资源模型。
- **缓存/provenance**：输入 BAM/ref/interval/科学参数/镜像；记录 native FILTER 与全部子模型。
- **测试/等价**：每实现只与同版本自身比较 PASS allele、FILTER、AD/DP/AF。

```yaml
methods: {somatic_callers: [mutect2, varscan2]}
```

## IF-VAR-002 `CallSomaticSvCandidates` v1.0

- **语义/Request/Result**：matched BAM → `SomaticSvCallset` 和可选 small-indel candidates。
- **实现**：Manta；PE 必需，WES 使用 call regions/exome，WGS 策略不同。
- **错误/状态**：SE 为 plan incompatibility；无 SV 为 `EMPTY`；candidate 与 SV 输出分别校验。
- **资源/cache/provenance**：按 case，通常内部并行；记录 assay、layout、镜像。
- **测试/等价**：breakpoint/allele/support 和 candidate linkage。

```yaml
methods: {somatic_sv_caller: manta}
```

## IF-VAR-003 `NormalizeSomaticCallset` v1.0

- **语义/Request/Result**：caller native VCF → `CanonicalSomaticCallset`；纯 Python/受控 htslib transform。
- **必需输出**：normalized allele identity、PASS/FILTER、tumor/normal AD/DP/AF、caller provenance；保留 native ref。
- **实现差异**：每 caller 有 parser，但共同输出 schema；VarScan 百分比、Strelka nucleotide/tier counts、Mutect FORMAT 规则独立。
- **错误/状态**：未知 FORMAT、sample mismatch、REF/ALT 不合法失败；空输入返回 `EMPTY`。
- **资源/cache/provenance**：按 callset/contig scatter；normalizer/schema version 进入 key。
- **测试/等价**：同位点不同 ALT、多等位拆分、left normalization、indel、chr alias。

```yaml
policies: {variant_normalization: {left_align: true, decompose: true}}
```

## IF-VAR-004 `BuildConsensusSomaticCallset` v1.0

- **语义/Request/Result**：多个 canonical callset → primary 表达的 `ConsensusCallset`；至少一个 confirming 支持同 allele。
- **Request**：callsets、`primary`, `minimum_callers`, missing-caller policy；Result 含 support IDs/versions。
- **不变量**：比较 normalized allele，不只比较 position；primary 必须成功启用；失败 caller 不计支持。
- **状态**：无 confirmed allele 为 `EMPTY`；可用 caller 数不足为 `FAILED`；不 silent union。
- **资源/cache/provenance**：纯 Python，可按 contig；key 含所有 callset/policy；记录每 allele decision。
- **测试/等价**：同位置不同 ALT、多等位、primary 切换、caller 空/失败、排序；与旧逻辑先 characterization。

```yaml
policies:
  somatic_consensus: {strategy: primary_confirmed, primary: mutect2, minimum_callers: 2}
```

## IF-VAR-005 `CallAndFilterNormalGermline` v1.0

- **语义/Request/Result**：normal BAM → 用于 proximal context 的过滤 germline VCF，不是临床 germline 报告。
- **实现**：GATK HaplotypeCaller+NVScore+FilterVariantTranches；要求模型/known resources。
- **Scatter/状态**：interval scatter/full gather；零 germline 为 `EMPTY`；模型缺失失败。
- **缓存/provenance**：normal BAM、interval、模型/known-sites digest、参数/镜像。
- **测试/等价**：PASS allele、genotype/AD/DP、FILTER 和 shard 完整性。

```yaml
methods: {normal_germline_context: gatk_nvscore}
```

## IF-ANN-001 `AnnotateVariantConsequences` v1.0

- **语义/Request/Result**：somatic/combined VCF → consequence、annotated VCF、protein context。
- **实现**：VEP；pick 与 all-transcript 是配置输出视图；插件/cache 固定。
- **不变量/状态**：注释保留参考版本和规范化 `CHROM/POS/REF/ALT` 身份，区分同位点不同 ALT。记录 VCF 坐标约定、索引与注释版本；空 VCF 返回 typed `EMPTY`。
- **资源/cache/provenance**：可按 contig；VEP/cache/plugin hash/parameters 全入 key。
- **测试/等价**：SNV、indel、frameshift、多 transcript、HGVS、空输入；比较 consequence identity。

```yaml
methods: {consequence_annotator: vep}
```

## IF-PHS-001 `BuildProximalPhaseContext` v1.0

- **语义/Request/Result**：somatic+germline+tumor BAM → `PhaseContext`。
- **实现差异**：`read_backed` 含 reads evidence；`annotation_only` 不含，evidence level 不等价。
- **前置/状态**：sample/ref 一致；未请求为 `NOT_REQUESTED`；无邻近上下文为 `EMPTY`；允许降级时记录实际 evidence level 和原因。旧流程在 GATK3 缺失时把注释 VCF 送入旧相位输出通道，pVACseq 省略 `-p`。有 VCF 文件和具备 read-backed phase 是两项独立的就绪条件。 [相位回退](../../nextNEOpi.nf#L3759) · [pVACseq 参数](../../nextNEOpi.nf#L5702)
- **资源/cache/provenance**：按 contig；phase method、evidence、工具/镜像进入 key。
- **测试/等价**：相邻变异、cis/trans、冲突、无 GATK3、空 germline；比较 phase relation/evidence。

```yaml
methods: {phase_context: read_backed}
policies: {phase_fallback: annotation_only}
```
