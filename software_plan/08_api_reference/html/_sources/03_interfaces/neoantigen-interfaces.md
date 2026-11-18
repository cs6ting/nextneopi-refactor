# 新抗原、免疫原性与免疫组库接口

接口沿用现有 `IF-*` 边界。[第一层功能设计](../02_modules/first-layer-functional-design.md) 与 [第二层算法清单](../02_modules/second-layer-algorithm-inventory.md) 分别说明模块交接和算法旁路对照，验收使用 [现有测试矩阵](../05_testing/acceptance-test-matrix.md)。

## IF-NEO-001 `PredictCanonicalNeoantigens` v1.0

- **语义/Request/Result**：annotated/phase variants+HLA+explicit purity+可选 expression → `CanonicalNeoantigenTable`。
- **实现**：pVACseq 首期；predictor 集合、MHC class、peptide length 和 filters 属 methods/policies 分区。
- **不变量**：候选按病例、variant/transcript/consequence/peptide/HLA/MHC 标识，保留来源与重复计数。前置为已就绪的注释变异、适用 HLA、所选纯度及显式相位状态。CCF 在后处理阶段回填。
- **Scatter/状态**：按 HLA/case scatter，完整 gather；缺必需输入为 `FAILED`，成功零候选为 `EMPTY`。无 RNA 时表达 slot 为 `NOT_REQUESTED`，不能以数值 0 表示缺失。
- **资源/cache/provenance**：pVAC/IEDB/MHCflurry 镜像/模型/参数及所有 evidence；license 预检。
- **测试/等价**：class-I/II、空 VCF/HLA、phase/expression、有/无候选；比较 identity、filter 和分数容差。

```yaml
methods: {canonical_neoantigen: pvacseq}
```

## IF-NEO-002 `PredictFusionNeoantigens` v1.0

- **语义/Request/Result**：fusion events+HLA+expression/policy → `FusionNeoantigenTable`。
- **实现差异**：NeoFuse-compatible 或未来 predictor；不能替换 canonical 接口。
- **旧流程交接**：融合候选和 IF-RNA-001/IF-FUS-001 的 RNA BAM、TPM、Arriba 事件共享同一次 NeoFuse 执行和 provenance。 [旧输出](../../nextNEOpi.nf#L5364)
- **不变量/状态**：保留 fusion/frame/support；无 fusion `EMPTY`，无 RNA `NOT_REQUESTED`，protocol 不支持为 skip。
- **资源/cache/provenance**：按 case/HLA；记录 event/HLA/predictor/镜像和 filters。
- **测试/等价**：in-frame/out-of-frame、重复 peptide、空 event、HLA class；比较 event/peptide/HLA identity。

```yaml
methods: {fusion_neoantigen: neofuse_compatible}
```

## IF-NEO-003 `PredictSpliceNeoantigens` v1.0

- **语义/Request/Result**：splice events+annotated variants+HLA+purity → `SpliceNeoantigenTable`。
- **实现**：pVACsplice；要求 protocol/strand/event capability。
- **状态**：3' tag 可 `SKIPPED_UNSUPPORTED`；无 event `EMPTY`；缺必需 evidence `FAILED`。
- **资源/cache/provenance**：按 case/HLA scatter；记录 pVACsplice、annotation、event 和 filter policy。
- **测试/等价**：空 junction、strand、phase、class-I/II、聚合；比较 event/transcript/peptide/HLA。

```yaml
methods: {splice_neoantigen: pvacsplice}
```

### 呈递、结合与评分输出

保持全量、过滤和聚合视图的候选身份可追溯。每个评分记录算法、版本、端点、原始分数、单位或百分位、排序方向和适用范围。亲和力（BA/IC50）、呈递（EL）、加工、稳定性和免疫原性（IM）分别保留。pVACtools 5.3.0 曾跨方法汇总可用百分位，兼容输出保留旧字段并标明汇总定义。替换候选用相同输入旁路运行，按端点单独验收。 [旧版汇总实现](https://raw.githubusercontent.com/griffithlab/pVACtools/v5.3.0/pvactools/lib/output_parser.py) · [算法替换实验](../02_modules/second-layer-algorithm-inventory.md#替换实验与验收)

MixMHC2pred 属于补充 Class II 呈递，现有常规/剪接支路消费 pVAC 长肽、相应事件证据及原始 DNA HLA-HD。解析后使用等位基因配对证据和独立评分结果。只提供最终 HLA 列表的签名尚不足以验收这一路径，先由兼容适配器保留该输入和输出。 [旧补充预测路径](../../nextNEOpi.nf#L6265)

## IF-IMM-001 `CheckSelfSimilarity` v1.0

- **语义/Request/Result**：候选 peptide+protein DB → `SelfSimilarityEvidence`，不直接删除候选。
- **实现**：`blastp_short`；Result 含 query identity、hit、coverage/identity/e-value 和 policy interpretation。
- **状态**：无候选 `EMPTY`；无命中是成功 materialized evidence；DB/BLAST 失败为 `FAILED`。
- **资源/cache/provenance**：可按 peptide shard；DB checksum、BLAST/镜像/参数进入 key。
- **测试/等价**：无/多命中、短 peptide、重复 query；比较命中集合与阈值。

```yaml
methods: {self_similarity: blastp_short}
```

## IF-IMM-002 `ScoreImmunogenicity` v1.0

- **语义/Request/Result**：候选、模型及实现声明的可选证据 → `ImmunogenicityScoreSet`；每个模型独立命名。可选 CCF/TMB slot 随实现使用，旧 CSiN/GBM 的命令均不消费这两项。
- **实现差异**：CSiN 消费未过滤的常规候选并产生样本汇总，GBM 消费过滤后的常规 Class I 候选并产生候选分数。保持各自适用范围、粒度和缺失状态。CSiN 自研 Python 化，GBM 保留第三方 R/model 容器。 [旧输入分流](../../nextNEOpi.nf#L6084)
- **状态**：不适用为 `SKIPPED_UNSUPPORTED`，无候选 `EMPTY`，模型失败 `FAILED`；可选失败由 recipe 决定 case 影响。
- **资源/cache/provenance**：模型/数据库 checksum、实现/镜像、features/参数；记录 score direction/version。
- **测试/等价**：适用范围、缺 feature、数值 fixture、模型版本；同实现比较容差。

```yaml
methods: {immunogenicity_scorers: [csin, gbm]}
```

## IF-REP-001 `ProfileImmuneRepertoire` v1.0

- **语义/Request/Result**：独立消费 DNA/RNA 已准备的 `ReadSet`、material 和 assay，生成 `RepertoireProfile`。DNA 和 RNA preset 按样本角色选择，结果可直接汇总到报告。 [旧 MiXCR 输入](../../nextNEOpi.nf#L6880)
- **实现**：MiXCR；descriptor 声明 exome DNA/RNA preset、species 和 license。
- **状态**：未启用 `NOT_REQUESTED`；无 license 对必需能力失败、可选能力按 policy skip；无 clone 可 `EMPTY`。
- **资源/cache/provenance**：按 sample；reads、preset、镜像、license fingerprint 进入记录，license 内容不记录。
- **测试/等价**：DNA/RNA preset、无 license、空 repertoire、clone identity/count；同 MiXCR 版本比较规范 clone 表。

```yaml
methods: {immune_repertoire: mixcr}
```
