# CNV、纯度、CCF 与 TMB 接口

## IF-CNV-001 `InferCopyNumber` v1.0

- **语义/Request/Result**：matched BAM+assay+sex+reference → `CopyNumberProfile`，包含 segment 和实现实际支持的 features。
- **Result capability**：`TOTAL_CN`、`ALLELE_SPECIFIC_CN`、`BAF`、`PURITY`、`PLOIDY` 分别声明；segment 含坐标、major/minor/total、quality。
- **实现差异**：ASCAT/Sequenza 可供 allele-specific/purity；CNVkit/FREEC 能力和当前用途不同，不能自动用于 CCF。
- **旧流程交接**：旧 CNVkit 从重复标记后的肿瘤/正常 BAM 读取深度，另接收已选纯度。针对 CNVkit 的兼容验收使用这一阶段的输入。 [CNVkit 输入](../../nextNEOpi.nf#L4344)
- **前置/状态**：reference/sex/assay 兼容；无可信 segment 可 `EMPTY` 或按 policy 失败；工具失败为 `FAILED`。
- **Scatter/资源**：按 case/contig/工具策略；高内存/I/O；R 算法保留容器，自研 driver/collector Python 化。
- **缓存/provenance**：BAM、assay、sex、reference、工具/镜像/参数；记录 feature set 和 native outputs。
- **测试/等价**：segment overlap、breakpoint 容差、major/minor/total CN、purity/ploidy；不同方法做 concordance，不称等价。

```yaml
methods: {copy_number: ascat}
```

## IF-PUR-001 `ResolvePurityPloidy` v1.0

- **语义/Request/Result**：候选 provider 结果+policy → `PurityPloidyResult` 和完整 decision trace。
- **实现/策略**：`configured`、ASCAT、Sequenza；fallback 顺序属于 policy。首期 `configured: 0.95` 必须显式。
- **不变量**：purity 0～1、ploidy>0；source/quality/失败原因必填；工具失败不得静默转 0.95。
- **状态**：无可用必需 provider 为 `FAILED`；未请求 CNV 但 configured purity 可 `MATERIALIZED`。
- **资源/cache/provenance**：纯 Python低资源；key 含候选 results/policy/config value；记录每次选择/拒绝。
- **测试/等价**：ASCAT 成功、fallback Sequenza、两者失败、configured、范围错误；比较值、source 和 trace。旧流程两种估计均不可用时采用默认 0.95；迁移回放提供旧病例实际值和来源。所选纯度供常规/剪接预测，即使 CCF 不可计算也单独保留纯度结果。 [旧纯度选择](../../nextNEOpi.nf#L4227) · [pVACseq 输入](../../nextNEOpi.nf#L5674) · [pVACsplice 输入](../../nextNEOpi.nf#L5953)

```yaml
policies:
  purity: {providers: [configured], configured_value: 0.95, on_failure: fail}
```

## IF-CCF-001 `EstimateCCF` v1.0

- **语义/Request/Result**：annotated variants+allele-specific CN+purity → `CcfTable`，含 estimate、credible set 和 clonal probability。
- **实现**：Python 化 `CCF.R` 的 `binomial_grid_v1`；未来模型并存，必须版本化。
- **前置/不变量**：caller counts 可解释；segment/reference/坐标一致；只接受所需 CN capabilities。回填候选前按病例、参考及规范化等位基因身份匹配，显式转换 VCF 和候选表坐标。旧表缺少等位基因身份时，无法唯一对应的记录保留缺失原因。 [旧 CCF 回填](../../bin/add_CCF.py#L45)
- **状态/错误**：无 variant 为 `EMPTY`；缺 segment/count/purity 为 `FAILED`，不能 forward-fill 前一记录。
- **资源/cache/provenance**：可按 contig；低/中 CPU；key 含 counts、segments、purity、模型参数。
- **测试/等价**：数值 fixture、credible set、阈值、segment 边界、unmatched variant；先与旧 R 容差比较。

```yaml
methods: {ccf_estimator: binomial_grid_v1}
```

## IF-TMB-001 `ComputeTMB` v1.0

- **语义/Request/Result**：callset+tumor/normal callable bases+consequence/CCF policy → 多口径 `TmbMetricSet`。
- **口径**：all/coding/clonal 分别有 numerator、denominator、单位、policy version；不能只输出三位小数。
- **前置/不变量**：coverage/base-quality、contig 和 consequence set 明确；坐标一次性规范转换。
- **状态**：无 mutation 可为数值 0 且 `MATERIALIZED`；denominator 0/不可计算为 `FAILED`；未请求 clonal 为 `NOT_REQUESTED`。
- **资源/cache/provenance**：按 case/metric；key 含 callable/variants/policy；记录 numerator 和 denominator。
- **测试/等价**：chr/no-chr、0/1-based、低覆盖、长 contig、coding SO、clonal threshold；先比输入集合/denominator，再比数值。

```yaml
policies:
  tmb: {metrics: [all, coding, clonal], min_depth: 10, unit: mutations_per_mb}
```
