# MOD-07 HLA 分型

## 目的、职责与非职责

从 tumor DNA/RNA 或用户输入获得 HLA calls，并按可审计 policy 解析最终 genotype。模块不把 class-I 与 class-II、DNA 与 RNA、预测与 custom 证据无差别合并。

## 上下游与当前映射

上游 MOD-01/03/04；下游 MOD-11（NeoFuse 兼容路径）、MOD-12/13/14。C1 从肿瘤标记重复 BAM 取证后运行 DNA 分型，C2 直接消费 MOD-03 准备的 RNA reads，C3 合并分型、用户证据与预测器支持信息。NeoFuse 依赖解析后的 HLA 执行，RNA 分型在 NeoFuse 前即可完成。 [C 组算法单元](second-layer-algorithm-inventory.md#c-hla-分型) · [RNA reads 分流](../../nextNEOpi.nf#L1030) · [DNA 取证](../../nextNEOpi.nf#L4750) · [分型合并](../../nextNEOpi.nf#L5224)

## 实体、输入输出与不变量

输入 `DuplicateMarkedBam | ReadSet | UserHlaCallset`；输出 `HlaEvidence`、`HlaCallset`、`ResolvedHlaGenotype` 和 `HlaDecisionTrace`。每条 call 包含 locus、allele fields、resolution、zygosity、class、chain、DNA/RNA evidence、source、quality；class-II alpha/beta pairing 显式建模。

最终分型提供给 pVAC 和 NeoFuse，原始 HLA-HD DNA 分型按可选产物交给旧 MixMHC2pred 兼容支线。后者独立记录原生格式、来源和适用状态。 [HLA-HD 输出分流](../../nextNEOpi.nf#L5114) · [MixMHC2pred 输入](../../nextNEOpi.nf#L6280)

## 接口与实现差异

提供 `IF-HLA-001 ExtractHlaEvidence`、`IF-HLA-002 TypeHla`、`IF-HLA-003 ResolveHlaGenotype`。

- OptiType：主要 class-I A/B/C。
- HLA-HD：class-I/II，独立安装/许可和参考要求。
- custom：用户证据，不是预测软件。
- DNA/RNA：证据偏差不同；RNA 仅可按 policy 补充或强制。

最终对 pVAC 支持列表过滤时，必须保留被丢弃 call 及原因，不能静默消失。

C1 优先旁路试 SpecHLA。使用有独立真值的样本，比较位点和 two-field 准确率、低覆盖、无结果比例、Class II 配对及可评分等位基因覆盖。原分型和合并策略继续用于默认流程。 [试点验收](second-layer-algorithm-inventory.md#替换实验与验收)

## 配置、容器、参考和许可

配置 typer 列表、force DNA/RNA、custom precedence、minimum resolution、允许的 MHC class。HLA-HD、OptiType/Yara 使用独立 digest 镜像与 reference；license/可再分发性由 descriptor 预检。

## 状态、错误与 provenance

没有 HLA evidence 但工具成功可为 `EMPTY`；必需 MHC class 无任何可用实现时 plan 失败；可选 class-II 不支持可为 `SKIPPED_UNSUPPORTED`。记录所有原始 calls、入选/丢弃、policy 版本和理由。

## 测试与验收

覆盖 homozygous DNA+RNA 补充、custom-only、无 HLA-HD、低分辨率、重复 allele、alpha/beta pairing、空 evidence、mutable default regression。科学等价按 locus/resolution/组合和证据比较。验收 REQ-FUN-013～014、ACC-001/004。风险包括旧空 custom 判断和 RNA HLA parser 参数缺失。
