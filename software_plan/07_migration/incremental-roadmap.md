# 增量迁移路线

## 原则

按测试驱动的纵向增量实施；每阶段必须接入可运行 recipe、有 Demo 和验收记录，不创建孤立 adapter。旧 Nextflow 在 ACC-006 前保持可运行。

## 旧版基线

以旧代码 `9f34698` 和 README 指定的 DSL1 Nextflow `22.10.8` 建立参考运行。首个基线病例用能生成非空常规候选的配对 WES DNA，保存分阶段 BAM、体细胞共识与注释 VCF、定相状态、HLA、实际纯度，以及 pVACseq 全量与过滤表。记录实际调用器集合、配置、工具/镜像、参考、模型和执行状态。旧版测试包适用于冒烟测试，CNVkit 按 README 关闭，并另外用覆盖充分的样本验证。基线数据准备可与 Runtime walking skeleton 并行。 [旧运行入口与测试数据](../../README.md#14-testdata) · [基线计划](../05_testing/scientific-equivalence-plan.md)

## 实施阶段

| 阶段 | 目标与实现指导 | 测试与 Demo | 入口 / 出口条件 |
|---|---|---|---|
| 1 Runtime walking skeleton | 建立 `ExecutionBackend`；优先 Pydra，验证 local/Slurm/Apptainer、fan-out/in、retry/cache/cancel | 两 case 两容器任务；一个失败后 resume；backend conformance | 入：site 信息；出：ADR-002 门槛结论，失败则 Snakemake 回退 |
| 2 Domain/config/CLI/SDK | 建包分层、Pydantic 模型、JSON Schema、`validate/plan/run` 薄 CLI | 配置 unit/property；Demo 输出规范 plan | 入：阶段1端口；出：有效/无效配置全可诊断 |
| 3 Plugin/capability | entry points、descriptor、selector 和能力矩阵 | 冲突/不兼容 contract；Demo `plugins list/check` | 入：模型可用；出：无需改 core 注册实现 |
| 4 Artifact/cache/provenance | typed artifact、五状态、原子 store、cache key、事件 | 损坏缓存/并发/恢复；Demo 二次 run 命中 cache | 入：task 可执行；出：run/artifact 可反查 |
| 5 Manifest/reference/interval | 迁移输入校验、bundle、WES interval/scatter | FASTQ/BAM/SE/PE/sex/chr 边界；Demo plan shards | 入：Schema；出：无效输入不提交计算 |
| 6 Reads/QC | FASTQ passthrough、BAM-to-FASTQ、NoTrim/fastp、FastQC | native fixture+容器 smoke；Demo YAML 切 trim | 入：合法 case；出：规范 reads/QC |
| 7 DNA alignment | BWA、uBAM merge、markdup、tag/index 分工件 | BAM identity/QC；Demo tumor/normal markdup BAM | 入：reads/reference；出：HLA 取证与 BQSR 所需的 markdup BAM |
| 8 BQSR | GATK scatter/gather、mosdepth/HsMetrics | shard failure/resume；Demo 只重算失败 shard | 入：markdup/interval；出：调用器所需的完整 recal BAM |
| 9 Mutect2 | contamination/orientation/filter 子图和 normalizer | 合成 variants、empty VCF；Demo canonical callset | 入：matched BAM；出：首个 IF-VAR-001 实现 |
| 10 VarScan2+consensus | 第二 caller、Python 化 `make_hc_vcf`、primary-confirmed | same-pos ALT/multiallelic；Demo 切 primary | 入：Mutect2；出：高置信 VCF/support trace |
| 11 VEP | 固定 cache/plugins 镜像、consequence/protein contracts | SNV/indel/frameshift/empty；Demo annotated VCF | 入：consensus；出：稳定 annotation schema |
| 12 Germline/phase | GATK normal context；read-backed/annotation-only 分能力 | 近邻变异、无 GATK3、phase block 与旧 pVAC 读取约定；Demo evidence level | 入：BAM/VCF；出：带证据状态的 phase context |
| 13 HLA | evidence、OptiType/HLA-HD/custom、Python resolver | class/pairing/空/custom；Demo decision trace | 入：marked duplicate BAM；出：resolved genotype 与可用的分型来源 |
| 14 首个 WES canonical | 显式 purity、pVACseq 常规候选全量与过滤表、聚合、初版报告 | 先回放同病例旧 VEP 注释 VCF、HLA、phase 和实际纯度，再做 local+Slurm E2E、cache/partial/empty | 入：阶段1～13；出：首轮候选比较报告与 ACC-001～005 候选版本 |
| 15 扩展 callers | Manta/Strelka2/Mutect1 插件与 capability | PE/SE/WES/WGS 负例；Demo 配置增删 caller | 入：consensus 稳定；出：旧 caller 覆盖 |
| 16 WGS | `AssayDesign` 驱动 interval/QC/caller 差异 | contig/N/denominator；WGS 小数据 Demo | 入：WES稳定；出：WGS recipe |
| 17 ASCAT/Sequenza purity | 容器 adapter、allele CN、显式 fallback policy | XX/XY/unknown、双失败；Demo purity trace | 入：CNV refs；出：可信 purity/profile |
| 18 CNVkit/FREEC | 差异 feature flags、Python collector/可视化状态 | capability 拒绝、segment parser；切方法 Demo | 入：CNV contract；出：四方法并存 |
| 19 Python CCF/TMB | characterization `CCF.R`/TMB 后 Python 化 | 数值/坐标/denominator；新旧容差 Demo | 入：CN/purity；出：CCF/TMB 可追溯 |
| 20 RNA expression/HLA | 迁移初期复用一次 NeoFuse 执行，交付 STAR BAM、TPM 与融合产物；RNA HLA 从准备好的 reads 取证 | DNA-only/普通/3' tag、分支状态、共享执行来源；表达证据 Demo | 入：RNA reads/ref、HLA 与可用 Manta 证据；出：canonical 可加 expression |
| 21 Fusion | 迁移 NeoFuse 融合产物，再评估独立 Arriba 事件与建肽能力 | frame/breakpoint/empty、事件与候选分别比较；fusion report Demo | 入：RNA 证据或共享执行产物；出：fusion events/neo |
| 22 Splicing | strand、Python XS transform、regtools/pVACsplice | 3' skip/strand/empty；splice report Demo | 入：普通 RNA；出：splice events/neo |
| 23 补充呈递与候选证据 | MixMHC2pred 保留 Class II 呈递语义，BLAST/CCF 回填、CSiN 和 GBM 产出各自证据 | identity、HLA 配对、缺失、任务类型与适用性；评分 Demo | 入：candidate/HLA 证据；出：按来源和任务区分的结果 |
| 24 MiXCR/全功能 | MiXCR 支线、完整 recipes、文档/性能/等价 | local/Slurm/full scientific/perf；全功能 Demo | 入：全部模块；出：ACC-006 和退役评审 |

## 每阶段交付包

代码、Schema、接口/模块文档、unit/contract/integration tests、Demo 配置、run bundle、provenance、已知风险和追踪矩阵更新。阶段出口未通过不得把后续模块建立在临时文件名或私有实现上。

## 首批算法替代试点

使用独立配置和输出目录，与现有实现并行对照。每项试点在对应的旧方法回放可用后开始。核心迁移的验收条件按 [验收矩阵](../05_testing/acceptance-test-matrix.md) 执行，候选性能按 [二级算法清单](../02_modules/second-layer-algorithm-inventory.md#替换实验与验收) 评估。

| 试点 | 开始条件 | 对照和输出 |
|---|---|---|
| A2 BWA-MEM2 | 阶段 7 已有可复用的 reads、参考和旧版 BAM 对照 | 固定后处理，对照逐 reads 坐标、CIGAR、MAPQ、标签、覆盖及 VCF/候选，记录耗时与内存 |
| C1 SpecHLA | 阶段 13 已保存带来源的旧分型，具备独立分型真值 | 按位点、覆盖和分辨率比较准确率及无结果率，记录 MHC II 配对和下游可评分覆盖 |
| F3/F4 NetMHCpan 4.2 / NetMHCIIpan 4.3 | 阶段 14 已保存可回放的肽–HLA 输入，并锁定原模型和阈值 | 固定候选序列与 HLA，分别用结合实验和免疫肽组真值比较；记录任务、版本、覆盖、阈值影响及下游改变 |

每项输出包括输入锁、比较口径、适用范围、失败或缺失原因、结果差异和采纳结论。DeepSomatic、DeepVariant、WhatsHap 和免疫原性替代模型列为后续对照候选，随对应 assay 真值和接口验证准备推进。
