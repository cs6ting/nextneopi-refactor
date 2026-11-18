# Typed DAG Edge Matrix

本表是 producer Result → consumer Request 的唯一连接规范。类型名必须与 [类型索引](type-index.md) 一致；不允许用文件后缀或别名隐式连接。

| Producer | Output type | Consumers / input field |
|---|---|---|
| IF-IN-001 | `CaseManifest` | Planner/case expansion |
| IF-REF-001 | `ReferenceBundleRef` | 所有 reference-aware capabilities |
| IF-REF-002 | `CallableIntervalPlan` | IF-ALN-003、IF-QC-002、IF-VAR-001/002/005 |
| IF-READ-001 | `ArtifactRef[CanonicalReadSet]` | IF-READ-002、IF-QC-001、IF-ALN-001、IF-HLA-001（RNA reads，按预处理策略）、IF-RNA-001、IF-REP-001 |
| IF-READ-002 | `ArtifactRef[TrimmedReadSet]` | IF-QC-001、IF-ALN-001、IF-HLA-001（RNA reads，按预处理策略）、IF-RNA-001、IF-REP-001 |
| IF-ALN-001 | `ArtifactRef[AlignedBam]` | IF-ALN-002 |
| IF-ALN-002 | `ArtifactRef[DuplicateMarkedBam]` | IF-ALN-003、IF-QC-002、IF-HLA-001 |
| IF-ALN-003 | `ArtifactRef[RecalibratedBam]` | IF-QC-002、IF-VAR-001/002/005、IF-CNV-001、IF-PHS-001 |
| IF-VAR-001 | `ArtifactRef[NativeSomaticCallset]` | IF-VAR-003 |
| IF-VAR-002 | `SomaticSvResult` slots | Strelka implementation、IF-FUS-001 optional evidence |
| IF-VAR-003 | `ArtifactRef[CanonicalSomaticCallset]` | IF-VAR-004、IF-TMB-001 |
| IF-VAR-004 | `ArtifactRef[ConsensusSomaticCallset]` | IF-ANN-001 |
| IF-VAR-005 | `ResultSlot[ArtifactRef[GermlineContextCallset]]` | IF-ANN-001、IF-PHS-001 |
| IF-ANN-001 | `ResultSlot[ArtifactRef[AnnotatedSomaticCallset]]` | IF-PHS-001、IF-CCF-001、IF-NEO-001/003（必需，检查 slot 就绪） |
| IF-ANN-001 | `ResultSlot[ArtifactRef[ConsequenceTable]]` | IF-TMB-001（按口径） |
| IF-PHS-001 | `ResultSlot[ArtifactRef[PhaseContext]]` | IF-NEO-001、IF-SPL-001 optional |
| IF-HLA-001 | `ArtifactRef[HlaEvidence]` | IF-HLA-002 |
| IF-HLA-002 | `ArtifactRef[HlaCallset]` | IF-HLA-003 |
| IF-HLA-003 | `ArtifactRef[ResolvedHlaGenotype]` | IF-NEO-001/002/003 |
| IF-CNV-001 | `ArtifactRef[CopyNumberProfile]` | IF-PUR-001、IF-CCF-001 |
| IF-PUR-001 | `ArtifactRef[PurityPloidyResult]` | IF-CCF-001、IF-NEO-001/003（独立于 CCF 就绪状态） |
| IF-CCF-001 | `ResultSlot[ArtifactRef[CcfTable]]` | IF-TMB-001（按口径）、IF-IMM-002（实现声明需要时）、reporting |
| IF-TMB-001 | `ArtifactRef[TmbMetricSet]` | IF-IMM-002（实现声明需要时）、reporting |
| IF-RNA-001 | `ResultSlot[ArtifactRef[RnaAlignedBam]]` | IF-FUS-001、IF-SPL-001 |
| IF-RNA-001 | `ResultSlot[ArtifactRef[ExpressionMatrix]]` | IF-NEO-001/002 |
| IF-RNA-001 | `ResultSlot[ArtifactRef[HlaEvidence]]` | IF-HLA-002，仅在 RNA 实现可独立产出证据时使用；旧 NeoFuse 路径从 IF-HLA-001 接入 |
| IF-FUS-001 | `ArtifactRef[FusionCallset]` | IF-NEO-002 |
| IF-SPL-001 | `ArtifactRef[SpliceEventCallset]` | IF-NEO-003 |
| IF-NEO-001/002/003 | `ArtifactRef[NeoantigenTable]` | `aggregate_neoantigen_candidates`、IF-IMM-001/002、reporting |
| IF-IMM-001 | `ArtifactRef[SelfSimilarityResult]` | reporting |
| IF-IMM-002 | `ImmunogenicityScoreSet` slots | reporting |
| IF-REP-001 | `ArtifactRef[RepertoireProfile]` | reporting |
| IF-RPT-001/002 | `ArtifactRef[QcReportBundle/ScientificReportBundle]` | publish、RunResult |

## Edge invariants

1. Artifact reference、case/sample、reference dictionary、data schema 和 ResultStatus 必须兼容。
2. Consumer 接收 optional edge 时必须接收 `ResultSlot[T]`，不得把 `None` 当状态。
3. Producer 的 `FAILED` slot 不进入需要真实 artifact 的 consumer；由 recipe failure policy 决定阻断/跳过。
4. 所有 edge 在 planning 阶段进行静态类型/Schema 校验，并有 `TST-CONTRACT-EDGE-*` 测试。
5. `AnnotatedVcf`、`ExpressionEvidence` 等未声明 alias 禁止用于边；需要投影时必须增加显式 transform/API。
6. 注释变异的可用性和相位证据等级分别验证。必需工件由 recipe 检查 slot 状态、文件与索引；候选/CCF 交接以病例、参考和规范化等位基因为键，坐标约定明确后再比较或连接。

## 旧流程兼容映射

- `DuplicateMarkedBam` 用于 HLA DNA 取证，`RecalibratedBam` 用于 Mutect2 等调用器。旧 CNVkit 使用重复标记阶段并另接收所选纯度；现有 IF-CNV-001 的 BQSR 请求签名尚不能表达该旧输入，CNVkit 纳入前需单独校验。 [旧 CNVkit 输入](../../nextNEOpi.nf#L4344)
- 旧 NeoFuse 由编排层接收准备后的 RNA reads、适用 Manta SV 与已选 HLA，一次执行并分别收集 IF-RNA-001、IF-FUS-001、IF-NEO-002 结果，绑定同一运行记录。旧 RNA HLA 独立走 reads→IF-HLA-001→IF-HLA-002/003，避免 RNA BAM 与已选 HLA 形成依赖环。RNA 变异读数与 RegTools 还需使用相应注释或相位 VCF。 [reads 分流](../../nextNEOpi.nf#L1030) · [NeoFuse](../../nextNEOpi.nf#L5348) · [RNA 变异证据](../../nextNEOpi.nf#L5513) · [RegTools](../../nextNEOpi.nf#L5913)
- 补充 Class II 呈递由兼容适配器读取 IF-HLA-002 的原生 DNA HLA-HD 结果引用，或经等价验证的规范化配对证据，另接收相应长肽与 VCF/事件证据。现有 IF-NEO-001/003 的最终 HLA 字段尚未覆盖这条支路的完整输入。MiXCR 从 IF-READ-001/002 独立启动。 [MixMHC2pred](../../nextNEOpi.nf#L6265) · [MiXCR](../../nextNEOpi.nf#L6880)

[第一层功能设计](../02_modules/first-layer-functional-design.md) · [第二层算法清单](../02_modules/second-layer-algorithm-inventory.md) · [验收测试矩阵](../05_testing/acceptance-test-matrix.md)
