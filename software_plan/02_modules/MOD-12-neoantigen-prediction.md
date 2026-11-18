# MOD-12 新抗原预测

## 目的、职责与非职责

将规范变异/融合/剪接事件、HLA、purity、phase 和可选 expression 转换为可追踪的新抗原候选。模块负责 predictor 调用、过滤与聚合，不负责生成上游变异/HLA/CNV。

## 上下游与当前映射

上游 MOD-06/07/08/10/11；下游 MOD-13/14。当前 pVACseq、pVACsplice、NeoFuse 新抗原、按 HLA 分发、聚合和报告约位于 `nextNEOpi.nf:5590-6260`，辅助脚本包括 `concat_pvacseq.py` 等。

F1/F2 将事件转成候选肽，F3/F4 分别提供结合和呈递结果，F5 保存补充的免疫原性、加工与稳定性结果，F6 管理过滤与聚合。NeoFuse 兼容路径直接从共用任务接收融合候选。F4 的 MixMHC2pred 补充支线仍按旧实现归属 MOD-13。 [F 组算法单元](second-layer-algorithm-inventory.md#f-新抗原候选构建与呈递预测) · [共用 NeoFuse](MOD-11-fusion-and-splicing.md#接口与实现差异)

## 输入输出与不变量

输入 `AnnotatedVariantCallset/PhaseContext`、`ResolvedHlaGenotype`、`PurityPloidyResult`、可选 expression/read evidence，以及 fusion/splice events；输出 `CanonicalNeoantigenTable`、`FusionNeoantigenTable`、`SpliceNeoantigenTable`。候选 identity 至少为 variant/event、transcript、consequence、mutant peptide、HLA、MHC class；保留 predictor 与 filter evidence。

## 接口与实现差异

提供 `IF-NEO-001 PredictCanonicalNeoantigens`、`IF-NEO-002 PredictFusionNeoantigens`、`IF-NEO-003 PredictSpliceNeoantigens`。pVACseq、pVACsplice、NeoFuse/MixMHC2pred 不是无差别实现：输入事件、MHC class、phase/expression 和评分终点不同。聚合为领域 transform，不依赖文件 suffix 猜 schema。

## 配置、容器、参考与许可

methods 选择 predictor；policies 定义 peptide length、binding/coverage/VAF、standard/relaxed/custom filter。IEDB/MHCflurry 等模型在镜像/预备资源中，许可由 descriptor 声明。首期 purity 必须显式 provider。

分别存储 BA（结合亲和力）、EL（呈递）和 IM（免疫原性）的任务、模型版本、分数单位或百分位定义、方向及适用范围。F3/F4 优先以 NetMHCpan 4.2、NetMHCIIpan 4.3 旁路评分，同一批肽–HLA 对分别用结合和呈递对照数据验收。默认预测器、过滤策略及首期 canonical 范围继续沿用既定方案。 [试点验收](second-layer-algorithm-inventory.md#替换实验与验收)

## 状态、错误与 provenance

零候选返回 `EMPTY`；未请求 fusion/splice 返回 `NOT_REQUESTED`；上游 protocol 不支持返回 `SKIPPED_UNSUPPORTED`。缺必需 HLA/purity、predictor schema 漂移或 aggregation identity 冲突为 `FAILED`。记录每个候选的来源证据和所有过滤理由。

## 测试与验收

测试按 HLA scatter/gather、class-I/II、空 VCF、空 HLA、phase/expression 缺失、聚合去重、schema drift。科学比较规范候选 identity、filter status 和分数容差。验收 REQ-FUN-015～017、ACC-001/006。风险是旧逐 allele 文件名聚合和失败被 optional 输出掩盖。
