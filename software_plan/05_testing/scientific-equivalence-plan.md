# 科学等价测试计划

## 原则

同方法等价验证比较旧流程和新 adapter，固定工具版本、镜像、参考、注释、模型和科学参数。替代算法评测冻结输入与其他方法，依据独立真值判断新方法的表现和适用范围。两类证据分别记录。

## 基线建立

当前尚无可回放的黄金基线。先选择能产生非空常规候选的配对 WES DNA 病例，以旧实现运行并保存输入、commit、实际生效的配置和调用器集合、工具/模型/参考和索引校验和、原始输出与状态记录。用合成或小型工件补足旧行为的边界条件。疑似旧缺陷同时记录实测旧行为和经评审的预期新语义。

将同一份旧上游工件送入新模块，比较结果，再接入旧下游验证交接。首轮比较到 pVACseq 的常规候选全量表和过滤表。配对 WES 原始输入到候选表的整链等价需要使用相同的调用器集合和实际纯度策略。若首期配方只保留 Mutect2 + VarScan2 并使用 configured purity，可从旧共识 VCF 注释边界开始回放，或直接注入旧 VEP 注释 VCF、定相、HLA 和实际纯度比较候选预测，另记录首期配方的连通性。在迁移旧最终发布表时，把 CCF、参考蛋白匹配和发布路径纳入对照。参见[首轮验收范围](../02_modules/first-layer-functional-design.md#首轮验收范围)。

## 分阶段比较

| ID | 工件 | 比较方法 |
|---|---|---|
| TST-SCI-READ-001 | FASTQ | read name/mate/count/quality 摘要，不比 gzip 字节 |
| TST-SCI-ALN-001 | BAM | read/RG/flag/coordinate/duplicate/BQSR/coverage 分布，不比 BAM 字节 |
| TST-SCI-VAR-001 | caller/consensus VCF | 按参考、CHROM/POS/REF/ALT 比较等位基因、FILTER、AD/DP/AF、样本角色和支持来源。刻画同位置不同 ALT 与多等位位点。 |
| TST-SCI-ANN-001 | VEP/phase | 比较转录本、后果、HGVS、蛋白序列及相位关系。覆盖顺式、反式、跨块和无法定相。若替换定相实现，验证 phased GT/PS 到旧消费者 HP 约定的转换及产出的肽。 |
| TST-SCI-HLA-001 | HLA | locus、resolution、zygosity、class/chain、DNA/RNA/source、最终组合 |
| TST-SCI-CNV-001 | CNV/purity | segment overlap/breakpoint 容差、major/minor/total CN、purity/ploidy |
| TST-SCI-CCF-001 | CCF | 先比肿瘤 REF/ALT 深度、区段和纯度来源，再比估计、区间及克隆分类。对新抗原表无精确匹配、同位置不同 ALT 的记录，刻画旧前向填充并检验新规则。 |
| TST-SCI-TMB-001 | TMB | numerator、callable denominator、口径、单位，再比较数值 |
| TST-SCI-RNA-001 | RNA | alignment summary、gene/transcript identity、TPM/read count 容差 |
| TST-SCI-NEO-001 | 新抗原 | 分别对全量表和过滤表按病例、变异或事件、转录本版本、WT/MT 肽、HLA 或配对、MHC 类别和候选来源比较记录及重复计数。比较模型分数、过滤判定和有业务含义的排名。 |
| TST-SCI-REP-001 | MiXCR | normalized clone identity、chain、count/frequency |
| TST-SCI-RPT-001 | 报告 | schema、单位、状态、provenance；HTML 只比结构关键字段 |

对可选分支至少用两个病例作对照，其中一例有普通 RNA，另一例无 RNA。检查各病例在 HLA、表达、事件和候选汇合时完整且相互隔离。另用 3′ tag、无读段定相、Class I only、空 VCF/零候选和工具失败样例检查状态与下游是否正确。对缺失 Class II 或模型不支持的 HLA，保留原因和影响的候选，分开记录真实空结果及运行失败。

## 容差管理

容差按实现/字段版本化，例如绝对/相对浮点误差、CNV breakpoint bp 窗口、segment reciprocal overlap。不得使用单一全局百分比。阈值附近样本必须单独测试，确保微小数值差异不被 rounding 掩盖。

## 首批可选算法评测

先把三个候选接到可回放的边界，默认配方继续使用旧实现。每项记录配方和参数锁、支持范围、冻结的数据划分、指标和允许的变化、性能、下游差异与回退方式。选取阈值和调整参数使用开发集，最终对照使用单独冻结的留出集。评测结果按同一方法的重复运行、两种方法共同可评分的集合、全量输入覆盖分别报告。记录不支持、缺少输入证据、失败和回退各自的分母与原因。

| 试验 | 固定输入与对照 | 实测报告 |
|---|---|---|
| A2 BWA-MEM2 | 相同配对 WES reads、参考序列和后处理，分别构建对应索引。纳入较难比对和分片边界区域。 | 比较 read 坐标、CIGAR、flags、MAPQ、RG、关键标签及覆盖，追踪 VCF 和候选表变化。科学输出满足约定后比较耗时、CPU 和峰值内存。 |
| C1 SpecHLA | 固定 BAM、assay 和目标 HLA 字典。使用有独立分型真值的样本，分开报告正常 DNA 和肿瘤 DNA 的覆盖与 LOH 情况。 | 按 locus 和分型分辨率报告 two-field 准确率、no-call、Class II 配对、可用于后续预测的 HLA 覆盖，以及候选新增/丢失。 |
| F3/F4 NetMHCpan 4.2 / NetMHCIIpan 4.3 | 冻结肽–HLA 输入、Class II α/β 配对、上下文和打分之外的策略。BA 使用独立定量结合数据，EL 使用独立免疫肽组数据。核对可执行版本、许可证与实际支持列表。 | BA 项比较排序相关、log IC50 误差和阈值判定。EL 项比较 AUPRC、Recall@K，写明已测/背景定义与缺标记。按 HLA、肽长、配对及覆盖报告，阈值变化和旧/新候选差异独立列出。 |

将留出集与方法公开的训练数据对照，核查病例、研究队列、肽–HLA 对和重叠肽核心。训练来源不透明或样本重叠未排除时，在报告里标明证据范围。EL 质谱未检出记录为未标注，BA、EL 和免疫原性各自使用对应的实验数据和指标。三个试验目前均为待执行方案。参见[算法盘点与来源](../02_modules/second-layer-algorithm-inventory.md#替换实验与验收)和[数据策略](test-data-strategy.md#候选方法留出集)。

## 差异分类

- `EQUIVALENT`：在已批准规则内。
- `EXPECTED_FORMAT_DIFFERENCE`：仅格式/排序/压缩差异。
- `APPROVED_SCIENTIFIC_CHANGE`：旧缺陷或新 policy，经 ADR/评审批准。
- `UNEXPLAINED_REGRESSION`：阻断发布。
- `NOT_COMPARABLE`：方法能力不同，只提供 benchmark。

## 报告

等价报告包含比较范围、输入/reference/tool lock、比较规则版本、总数/交并集、字段差异、阈值影响、抽样记录和批准人。替代算法报告包含真值来源与适用区间、数据划分、共同覆盖与全量覆盖、各分层的指标、资源、候选变化及是否满足启用条件。任何未解释差异不得通过 Nextflow 退役门禁。
