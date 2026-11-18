# MOD-10 RNA 比对与表达

## 目的、职责与非职责

把 tumor RNA reads 转换为规范 RNA alignment、表达量和 RNA read support，分别对应 E1–E3。RNA HLA 由 MOD-07 从准备好的 RNA reads 独立分型。表达工件区分未测量与测得 0。 [E 组算法单元](second-layer-algorithm-inventory.md#e-rna-表达融合与剪接事件) · [C2 RNA 分型](MOD-07-hla-typing.md#上下游与当前映射)

## 上下游与当前映射

上游 MOD-01/02/03/06；下游 MOD-11/12/14。NeoFuse 兼容实现可共用一次执行，产生 RNA BAM、TPM 和融合候选。E3 将表达和 RNA BAM 派生的等位基因读数接到 MOD-06 的体细胞注释 VCF。有 RNA 的病例使用补充后的 VCF，DNA-only 病例继续传递原注释 VCF。 [NeoFuse 产物](../../nextNEOpi.nf#L5364) · [RNA 注释](../../nextNEOpi.nf#L5507) · [DNA-only 合流](../../nextNEOpi.nf#L5585)

## 输入输出与不变量

输入 `CanonicalReadSet`、RNA library protocol、reference/GTF，E3 还使用目标变异；输出 `RnaAlignedBam`、`ExpressionMatrix`、`RnaVariantEvidence`。表达值包含单位/quantifier；gene/transcript ID 与 annotation 版本一致；`NOT_MEASURED`、测得 0、空 reads 和工具失败必须区分。

## 接口与实现差异

提供 `IF-RNA-001 AlignAndQuantifyRNA`。RNA 扩展可用 STAR/现有 NeoFuse 兼容 adapter；长期把 alignment、quantification 和 evidence annotation 拆成内部子任务。普通 RNA 与 3' tag RNA 的适用能力分别声明。

## 配置、容器与资源

配置 protocol、strandedness、aligner/quantifier 和 minimum coverage。STAR/quantifier 在固定镜像，reference 包含 STAR index 和 GTF。RNA alignment 高 CPU/内存/磁盘，资源由 descriptor 估算。

## 状态和 provenance

无 RNA 为 `NOT_REQUESTED`；3' tag 不支持能力为 `SKIPPED_UNSUPPORTED`；成功但无表达记录为 `EMPTY`；alignment 失败为 `FAILED`。记录 protocol、annotation、quantifier、单位、read support policy。

## 测试与验收

覆盖 DNA-only、普通 RNA、3' tag、stranded/unstranded、表达 0、缺 gene mapping、空 reads 和与 HLA 独立分流的情况。科学比较 alignment 摘要、TPM identity/value 容差和 read counts。验收 REQ-FUN-020、ACC-006。风险是现有 NeoFuse 巨型步骤隐藏多个产物和失败边界。
