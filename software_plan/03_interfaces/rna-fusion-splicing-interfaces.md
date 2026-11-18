# RNA、融合与剪接接口

## IF-RNA-001 `AlignAndQuantifyRNA` v1.0

- **语义/Request/Result**：tumor RNA `ReadSet`+protocol+reference/GTF → `RnaAlignedBam`、`ExpressionMatrix`、可选 `RnaVariantEvidence/HlaEvidence`。
- **前置/不变量**：sample/ref/annotation 一致；表达单位和 gene/transcript ID 明确；未测量不等于 0。
- **实现差异**：STAR/现有 NeoFuse 兼容实现；普通 RNA 与 3' tag capability 不同；alignment/quantification 可内部拆任务但共享接口结果。
- **旧流程交接**：NeoFuse 用已准备的 RNA reads、已选定的 HLA 和适用的 Manta DNA SV 一次执行。编排层将 RNA BAM/BAI、TPM、Arriba 事件与融合候选分别交给 IF-RNA-001、IF-FUS-001、IF-NEO-002 的结果收集；三者共享执行记录。可选 RNA HLA evidence 经独立 reads 支路就绪。旧 RNA 变异读数需在 RNA BAM 和注释 VCF 均就绪后生成。 [NeoFuse 输入输出](../../nextNEOpi.nf#L5348) · [RNA 变异注释](../../nextNEOpi.nf#L5507)
- **错误/状态**：无 RNA 为 `NOT_REQUESTED`；protocol 不支持某输出为 `SKIPPED_UNSUPPORTED`；成功无表达记录为 `EMPTY`；alignment 失败为 `FAILED`。
- **Scatter/资源**：按 sample；高 CPU/内存/I/O；固定 STAR/quantifier 镜像和 index。
- **缓存/provenance**：reads、protocol、annotation/index、参数/镜像；记录单位、read support 和 strandedness。
- **测试/等价**：DNA-only、普通/3' tag、stranded、TPM 0、gene map、空 reads；比较 alignment 摘要和 expression identity/value 容差。

```yaml
methods: {rna_alignment_quantification: star_neofuse_compatible}
```

## IF-FUS-001 `CallGeneFusions` v1.0

- **语义/Request/Result**：RNA alignment/reads+annotation+可选 DNA SV → `FusionCallset`；不直接预测 peptide。
- **Result**：fusion identity、breakpoints、genes/transcripts、frame、RNA support、可选 DNA evidence。
- **实现差异**：Arriba/NeoFuse adapter；DNA Manta evidence 是增强 capability，不是必需的假字段。
- **状态**：无事件 `EMPTY`；无 RNA `NOT_REQUESTED`；3' tag 不支持时 `SKIPPED_UNSUPPORTED`；caller/annotation 失败为 `FAILED`。
- **资源/cache/provenance**：按 sample；reference/annotation/实现/镜像及可选 DNA parent 进入 key。
- **测试/等价**：空/重复 fusion、breakpoint/frame、支持数、无 Manta；比较规范 event identity。

```yaml
methods: {fusion_caller: arriba}
policies: {fusion_dna_evidence: optional}
```

## IF-SPL-001 `CallSpliceEvents` v1.0

- **语义/Request/Result**：RNA BAM+strand evidence+reference/GTF+可选 phase → `SpliceEventCallset`。
- **实现**：RSeQC/strand transform/regtools 子图；自研 XS tagging 迁移 Python。
- **前置/不变量**：protocol 支持、strand 明确或 policy 可处理 unknown；junction 坐标/reference 一致。旧 RegTools 还需要变异 VCF：read-backed 路径使用相位 VCF，允许的 annotation-only 路径使用注释 VCF。适配器显式核对 case、参考与 VCF/索引就绪状态。 [RegTools 输入](../../nextNEOpi.nf#L5913) · [相位回退](../../nextNEOpi.nf#L3759)
- **状态/错误**：3' tag 默认 `SKIPPED_UNSUPPORTED`；无 junction `EMPTY`；strand 冲突、缺 GTF、tool failure 为 `FAILED`。
- **Scatter/资源**：按 sample/contig；中等资源；工具容器固定。
- **缓存/provenance**：RNA BAM、protocol、strand/phase、annotation、参数/镜像；记录 XS transform。
- **测试/等价**：strand 类型、unknown、3' tag、空 junction、坐标、phase 缺失；比较 event identity/support。

```yaml
methods: {splice_event_caller: regtools}
policies: {unsupported_protocol: skip_with_reason}
```
