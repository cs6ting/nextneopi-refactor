# MOD-05 体细胞变异

## 目的、职责与非职责

执行 matched tumor/normal 体细胞 small-variant/SV candidate 调用，规范化 caller 原生格式，并按独立 policy 生成高置信共识。模块不做 VEP consequence、不将所有 caller 假定等价，也不把 Manta SV 当作普通 SNV caller。

## 上下游与当前映射

上游 MOD-02/04；下游 MOD-06/09/11/14。B1 为体细胞小变异调用，B2 为高置信共识，B3 为结构变异及候选 indel。当前方法包括 Mutect2、VarScan2、Manta/Strelka2 和可选 MuTect1。共识与 caller FORMAT 转换主要在 `bin/make_hc_vcf.py`。胚系调用见 MOD-06。 [B 组算法单元](second-layer-algorithm-inventory.md#b-dna-变异检测注释与定相) · [Mutect2 污染输入](../../nextNEOpi.nf#L1632) · [主调用器共识](../../nextNEOpi.nf#L3204)

## 输入输出与不变量

输入 matched `RecalibratedBam`、reference/callable intervals、caller resources；输出 `NativeSomaticCallset`、`CanonicalSomaticCallset`、`ConsensusCallset`、可选 `SomaticSvCallset`。规范 identity 由 build/contig/normalized REF/ALT 决定；sample order、FILTER、AD/DP/AF 和 caller provenance 必须明确。

## 接口与实现差异

提供 `IF-VAR-001 CallSomaticSmallVariants`、`IF-VAR-002 CallSomaticSvCandidates`、`IF-VAR-003 NormalizeSomaticCallset`、`IF-VAR-004 BuildConsensusSomaticCallset`。

- Mutect2：PON、germline resource、contamination、orientation bias。
- VarScan2：mpileup、阈值和 fpfilter。
- Strelka2：可消费 Manta small-indel 候选，SE 路径转交空 Manta 证据。SNV/indel FORMAT 语义不同。
- Mutect1：legacy Java/GATK3，能力与维护等级较低。
- Manta：仅在 PE 路径运行，分别输出给 Strelka2 的 small-indel 候选和给 NeoFuse 的 somatic SV，WES/WGS 区间策略另行记录。

DeepSomatic 是配对 WES 的候选旁路实现。接入时适配样本列、FILTER 和各等位基因的读数，并随结果记录模型版本。 [B 组算法单元](second-layer-algorithm-inventory.md#b-dna-变异检测注释与定相) · [Manta 到 Strelka 的可选交接](../../nextNEOpi.nf#L3039)

## 共识语义

`primary_confirmed` 保留 primary caller 记录，并要求至少一个 confirming caller 支持同一规范 allele；输出记录 support implementations。它不是 union 或多数投票，切换 primary 可能改变 FORMAT 和记录表达。

上述为目标规则。旧版 PyVCF `walk_together` 默认按 `CHROM/POS` 对齐。先用同位点不同 ALT 的样例锁定旧行为，再把等位基因级确认作为独立科学改动验证。 [旧实现](../../bin/make_hc_vcf.py#L73) · [科学等价验证](first-layer-functional-design.md#验证步骤)

## 配置、容器、参考和资源

`methods.somatic_callers` 与 `policies.somatic_consensus` 分离。每个 caller descriptor 声明 interval、layout、variant kind、PON/known resource 和资源模型；固定镜像离线运行。

## 状态与 provenance

合法零变异返回 `EMPTY`；caller 失败为 `FAILED`，不得作为“无支持”参与 consensus。primary 未启用、confirming 数不足、REF/ALT 不一致或 sample schema 错误在 plan/collect 阶段失败。

## 测试与验收

单元覆盖 allele key、同位置不同 ALT、多等位、left normalization；contract 覆盖每 caller 原生输出；科学测试比较 PASS allele、FILTER、AD/DP/AF 和 support。验收 REQ-FUN-008～011、ACC-001/004。风险：旧输出 glob 拼写、`walk_together` 未显式比 ALT；先 characterization，再采用规范科学语义。
