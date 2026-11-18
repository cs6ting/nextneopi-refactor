# MOD-11 融合与异常剪接

## 目的、职责与非职责

从 RNA alignment/reads 生成 fusion 和 splice event callsets，为 MOD-12 提供结构化事件。模块不直接仲裁 HLA、不聚合 canonical 候选，也不在不支持的 3' tag 数据上假装成功。

## 上下游与当前映射

上游 MOD-05（可选 Manta SV）、MOD-06（组合 VCF）、MOD-10（RNA BAM 或 reads）；NeoFuse 兼容路径还消费 MOD-07 已解析的 HLA。下游 MOD-12/14。E4 识别融合事件，E5 用 RSeQC、`tagXSstrandedData.awk` 和 RegTools 生成剪接证据。 [E 组算法单元](second-layer-algorithm-inventory.md#e-rna-表达融合与剪接事件) · [NeoFuse 输入与输出](../../nextNEOpi.nf#L5348) · [RegTools 输入](../../nextNEOpi.nf#L5913)

## 输入输出与不变量

输入 `RnaAlignedBam/RnaReadSet`、reference/GTF、可选 `SomaticSvCallset`、library protocol；输出 `FusionCallset`、`SpliceEventCallset`、strand evidence。事件 identity、breakpoints/junction、frame、gene/transcript、support 和坐标约定必须完整。

## 接口与实现差异

提供 `IF-FUS-001 CallGeneFusions`、`IF-SPL-001 CallSpliceEvents`。融合首个实现为 Arriba/NeoFuse 兼容 adapter，可选消费 Manta SV；剪接实现为 strand inference + regtools 子图。DNA SV evidence 是增强能力，不是必需接口伪字段。

NeoFuse 兼容实现与 MOD-10/12 共用一次执行。保留 RNA BAM/TPM、融合事件和融合候选各自的产物及来源，E4 的事件比较按断点、方向、支持读数和阅读框，F2 另行比较生成的肽。 [跨模块交接](first-layer-functional-design.md#跨模块数据依赖) · [F 组算法单元](second-layer-algorithm-inventory.md#f-新抗原候选构建与呈递预测)

## 配置、容器、参考与许可

配置 minimum support、DNA evidence policy、strandedness、允许 protocol。工具使用固定镜像；STAR index/GTF 属 ReferenceBundle。自研 AWK strand 标记迁移到 Python 或明确 adapter transform。

## 状态与错误

未启用为 `NOT_REQUESTED`；3' tag 等不支持场景为 `SKIPPED_UNSUPPORTED`；无事件为 `EMPTY`；工具/annotation/strand 冲突为 `FAILED`。可选 DNA evidence 缺失不得等价于 fusion caller 失败。

## Provenance、测试与验收

记录 caller、support、strand、DNA evidence、event normalization 和过滤。测试覆盖空事件、breakpoint、frame、重复 fusion、无 Manta、3' tag、XS tagging、空 junction 和 annotation mismatch。科学比较事件 identity/support，不比较行顺序。验收 REQ-FUN-020、ACC-006。风险：旧 3' tag 条件分支可能引用未定义 channel，应作为系统 characterization 场景。
