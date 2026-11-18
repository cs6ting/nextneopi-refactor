# MOD-06 注释与相位

## 目的、职责与非职责

为体细胞变异生成 consequence、transcript、蛋白上下文和 proximal variant phase evidence。模块不决定新抗原过滤，不把“未做 read-backed phasing”标记成相同质量的 phased 结果。

## 上下游与当前映射

上游 MOD-02/04/05；下游 MOD-09/10/11/12/14。B4 用正常样本的 HaplotypeCaller 生成胚系候选，由 NVScoreVariants 的 read tensor 模型评分，再用 `CNN_2D` tranche 过滤。B5 由 VEP 生成转录本与蛋白后果，B6 将组合 VCF 用于近邻变异定相。VEP 插件/补丁位于 `assets/Frameshift.pm`、`assets/Wildtype.pm` 等。 [B 组算法单元](second-layer-algorithm-inventory.md#b-dna-变异检测注释与定相) · [胚系模型](../../nextNEOpi.nf#L2126) · [VEP 与蛋白插件](../../nextNEOpi.nf#L3590)

## 输入输出与不变量

输入 `ConsensusCallset`、normal/tumor BAM、reference/VEP bundle；输出 `FilteredGermlineContext`、`AnnotatedVariantCallset`、`ProteinConsequenceSet`、`PhaseContext`。所有记录保留规范 variant identity；annotation 版本和 transcript policy 必须明确；空 callset 仍产生 typed empty。

## 接口与实现差异

提供 `IF-VAR-005 CallAndFilterNormalGermline`、`IF-ANN-001 AnnotateVariantConsequences`、`IF-PHS-001 BuildProximalPhaseContext`。首期实现 GATK germline、VEP 113 兼容 adapter、`read_backed` 与 `annotation_only` phase。后两者能力不同，descriptor 必须声明 evidence level。

旧流程缺 GATK3 时仍交付注释后的组合 VCF，pVACseq 此时省略定相参数。若试用 WhatsHap，需验证其 VCF phased GT/PS 与现用 pVACtools 5.3.0 的 FORMAT HP 消费规则能否正确适配，并比较近邻同相、异相及未定相对 WT/MT 肽的影响。 [旧参数分支](../../nextNEOpi.nf#L5702) · [pVACtools 5.3.0 近邻解析](https://github.com/griffithlab/pVACtools/blob/v5.3.0/pvactools/lib/proximal_variant.py#L28-L66)

## 配置、容器、参考与许可

配置 VEP pick/all transcript、SO terms、插件、germline filter 和 phase policy。VEP cache、GATK 模型及插件预先构建并锁定；vendored Perl 插件的 ownership/许可需在镜像清单核实。

## 状态和错误

零变异为 `EMPTY`；phase 未请求为 `NOT_REQUESTED`；没有 read-backed implementation 且 policy 允许时为明确的 annotation-only materialized result，而不是静默降级。错误包括 annotation schema、transcript/reference 不兼容和 phase sample mismatch。

## Provenance 与测试

记录 VEP/cache/annotation 版本、插件 hash、pick policy、germline filter、phase evidence 和父 callset。单元测试 consequence transform；adapter fixture 覆盖 SNV/indel/frameshift/多 transcript/空 VCF；科学比较 consequence、HGVS、peptide context 和 phase relation。

## 验收与风险

验收 REQ-FUN-012、ACC-001。风险为旧 GATK3 可用性决定分支、运行时插件差异和空 VCF channel 消失；目标契约必须在 planning 明示能力并保证 typed empty。
