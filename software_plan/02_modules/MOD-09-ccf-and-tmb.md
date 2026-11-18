# MOD-09 CCF 与 TMB

## 目的、职责与非职责

基于规范变异、allele-specific CN、purity 和 callable bases 计算 CCF 与 TMB。模块负责项目科学口径，不负责运行 CNV caller，也不以最终单一数值掩盖输入/denominator 差异。

## 上下游与当前映射

上游 MOD-02/04/05/06/08；下游 MOD-13/14。当前逻辑位于 `bin/mkCCF_input.py`、`bin/CCF.R`、`bin/add_CCF.py`、`bin/mutationalLoad.py` 和 `nextNEOpi.nf` 对应流程。

D2 估计单变异 CCF，D3 输出全范围和编码区等口径的 TMB。G2 消费 D2 的 CCF 表，为同一病例的常规候选关联变异 CCF。仅有配置纯度时可支持候选预测，CCF 状态仍受 allele-specific CN 的可用性约束。 [D 组算法单元](second-layer-algorithm-inventory.md#d-拷贝数纯度克隆性与突变负荷) · [G2 回填](second-layer-algorithm-inventory.md#g-候选证据免疫原性与免疫受体库) · [旧关联规则](../../bin/add_CCF.py#L45)

## 输入输出与不变量

输入 `AnnotatedVariantCallset`、`CopyNumberProfile`、`PurityPloidyResult`、tumor/normal coverage/callable regions；输出 `CcfTable`、`TmbMetricSet` 和可选候选回填表。CCF segment assignment 必须坐标一致；TMB denominator 明确 all/coding/clonal 和 coverage/base-quality policy；`NOT_MEASURED` 不写 0。

## 接口与实现

提供 `IF-CCF-001 EstimateCCF`、`IF-TMB-001 ComputeTMB`。现有 `CCF.R` 的 binomial 网格、credible set、clonal/subclonal 概率属于自研科学逻辑，先 characterization 后 Python 化；ASCAT/Sequenza driver 仍在 MOD-08 容器。TMB 可通过 policy 实现多个口径，但每个口径有独立 ID/version。

## 配置、资源与能力

配置 minimum depth/base quality、consequence set、contig policy、CCF threshold。CCF 要求 allele-specific CN+purity；selector 必须拒绝只提供 total CN 的 profile。Python 实现运行在 core image，无额外第三方许可。

## 状态、错误与 provenance

无合格变异可合法 `EMPTY`，无法计算 denominator 为 `FAILED`。记录 raw counts、segment assignment、purity source、denominator、公式/policy version 和数值精度。

## 测试

单元和 property tests 覆盖 binomial 数值、credible set、边界、chr/no-chr、0/1-based、segment 外变异和低覆盖；科学测试先比较输入 counts/denominator，再比较 CCF/TMB 容差与阈值分类。

## 验收与风险

验收 REQ-FUN-019、ACC-006。风险：旧 `add_CCF.py` 的 ordered merge/forward-fill 可能传播前一 CCF，TMB 有 contig 长度与坐标隐含规则，chrM 处理存在 TODO；必须用 fixture 决策，不能无声继承或修正。
