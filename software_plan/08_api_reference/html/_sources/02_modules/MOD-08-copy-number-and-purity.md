# MOD-08 拷贝数、纯度与倍性

## 目的、职责与非职责

提供具有显式能力的 CNV profile 和 purity/ploidy result。模块不把 total CN、allele-specific CN、BAF、purity 视为同一能力，也不静默使用 0.95。

## 上下游与当前映射

上游 MOD-01/02/04；下游 MOD-09/12/14。当前 ASCAT、Sequenza、Control-FREEC、CNVkit 和 purity fallback 位于 `nextNEOpi.nf:3740-4725`；驱动/转换脚本包括 `bin/ascat3.R`、`SequenzaScript.R`、`freec2bed.pl`、`freec2circos.pl`、`assess_significance.R`、`makeGraph.R`。

D1 按实现区分所用 BAM 阶段和输出能力。旧版优先使用 ASCAT，按条件转用 Sequenza，两者都无法给出纯度时预测支路可收到 0.95。CCF 仍须有合格区段和纯度。 [D 组算法单元](second-layer-algorithm-inventory.md#d-拷贝数纯度克隆性与突变负荷) · [旧纯度选择](../../nextNEOpi.nf#L4227) · [旧 CCF 判定](../../nextNEOpi.nf#L4564)

## 输入输出与不变量

输入 matched BAM、sex、assay、reference、可选 configured purity；输出 `CopyNumberProfile`、`PurityPloidyResult`。segment 明确坐标、major/minor/total CN 和质量；purity 范围 0～1，ploidy 为正；sex `UNKNOWN` 不可隐式设 male reference。

## 接口与实现差异

提供 `IF-CNV-001 InferCopyNumber`、`IF-PUR-001 ResolvePurityPloidy`。

- ASCAT/Sequenza：可产生 allele-specific CN、purity、ploidy，满足 CCF 前提。
- CNVkit/FREEC：按现有用法主要提供其他 CNV/BAF/可视化能力，不能直接冒充 allele-specific provider。
- `configured`：首期显式 purity provider，无 CNV capability。

fallback 顺序属于 policy，失败不是空 profile。

## 配置、容器、参考与许可

配置方法列表、fallback policy、assay/sex 参数、质量阈值。第三方 R 工具保留在容器；自研 driver/转换迁移到 Python adapter。资源包括 loci、GC、annotation 和 targets，均属 ReferenceBundle。

## 状态与 provenance

CNV 未请求为 `NOT_REQUESTED`；工具成功但无可信 segment 可为 `EMPTY` 或按 policy 失败；fallback 记录每次失败和选择理由。首期目标支持显式 `configured` provider，任何配置纯度均记录来源。与旧运行做等价回放时使用实际生效的纯度及其来源，分别核对 CNV 与 CCF 状态。

## 测试与验收

contract 覆盖四种原生输出；系统覆盖 ASCAT→Sequenza、两者失败、XX/XY/unknown、WES/WGS。科学比较 segment overlap、major/minor/total CN、purity/ploidy。验收 REQ-FUN-016/018、ACC-001/006。风险包括旧 Boolean 与字符串 `maleRef` 比较和被忽略的可视化失败。
