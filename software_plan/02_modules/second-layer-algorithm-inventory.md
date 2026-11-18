# nextNEOpi 第二层算法清单与替换评估

本文沿用[第一层的 A～G 功能组](first-layer-functional-design.md)，把每组拆到能独立验证的算法或规则。现状以本地提交 `9f34698` 的代码和配置为准。替代方法根据原始论文或官方文档核对，检索日期为 2026 年 11 月 17 日。首轮按项目现有的**配对 Illumina WES DNA → 常规变异候选**来排序，RNA、WGS 和其他测序条件另行评估。替代项均是待验证方案，本文没有运行旧流程或新工具。

**建议先做三个对照：** BWA-MEM2 测比对的输出一致性和性能，SpecHLA 测有独立分型真值时的 HLA 位点准确率，NetMHCpan / NetMHCIIpan 新版在同一批已生成的肽–HLA 对上分别测结合和呈递。DeepSomatic、DeepVariant 和候选免疫原性模型适合并行试跑，依据独立真值和下游候选变化决定是否启用。

现有机器学习功能主要在 **B4 的胚系变异过滤、F3/F4 的结合与呈递预测、F5/G4 的免疫原性评分**。它们分别需要变异真值、结合或呈递实验数据、以及 T 细胞应答标签。HLA 分型、候选肽枚举、TMB 和 CSiN 可按各自的分型、序列或统计问题验证，也有改进空间。

## A. 测序数据准备与 DNA 比对

| 算法单元与问题 | 当前做法 | 可选替代与验收 |
|---|---|---|
| **A1. reads 整理和质控。** 合并测序批次，识别低质量碱基和接头 | BAM 先转 FASTQ，合并同样本 reads。FastQC 提供质控报告，fastp 按 DNA/RNA 独立开关裁剪，默认关闭。属于格式处理、规则和统计。 [BAM 转换](../../nextNEOpi.nf#L420) · [FastQC](../../nextNEOpi.nf#L826) · [fastp](../../nextNEOpi.nf#L910) · [默认开关](../../conf/params.config#L25) | 首轮保留。若接头识别或可重复性是实际问题，可对比 [Cutadapt](https://cutadapt.readthedocs.io/en/stable/guide.html)。将接头去除和质量过滤拆开测，核对配对、reads 保留率、截短位置、有效覆盖和变异影响。 |
| **A2. DNA 比对。** 确定 reads 的基因组位置与比对质量 | `bwa mem` 采用种子比对与延伸，后接排序和 GATK MergeBamAlignment，恢复下游使用的 read group 和其他信息。 [比对与排序](../../nextNEOpi.nf#L1130) · [合并 BAM](../../nextNEOpi.nf#L1186) | **优先试 BWA-MEM2。** 为同一参考重建对应索引，保留其他参数和后处理。逐 reads 比较坐标、CIGAR、MAPQ、flags、RG 与关键标签，进一步核对覆盖和候选，并记录耗时、峰值内存。上游声称对齐输出一致，仍需在本项目参数下确认。 [BWA-MEM2 官方仓库](https://github.com/bwa-mem2/bwa-mem2) |
| **A3. 重复标记。** 识别由同一原始片段产生的重复 reads | Sambamba 标记重复，随后整理比对标签。 [重复标记](../../nextNEOpi.nf#L1255) | 首轮保留。若需要替换，可单独评估 [samtools markdup](https://www.htslib.org/doc/samtools-markdup.html)，按其输入约定处理 mate 标签和排序，核对重复标记、保留代表和光学重复。 |
| **A4. 碱基重校准与覆盖统计。** 控制碱基质量偏差，量化各区域覆盖 | GATK4 BQSR 利用已知位点统计系统误差。部分分支另用 GATK3 局部重比对，Mosdepth 统计覆盖。 [BQSR](../../nextNEOpi.nf#L1405) · [局部重比对](../../nextNEOpi.nf#L2248) · [覆盖](../../nextNEOpi.nf#L1732) | 首轮冻结 BQSR 和覆盖口径。按消费者区分重复标记、重校准与局部重比对产物。后续调整时分别检查碱基质量、分片边界、可调用区域，以及对低 VAF 变异的影响。 |

## B. DNA 变异检测、注释与定相

| 算法单元与问题 | 当前做法 | 可选替代与验收 |
|---|---|---|
| **B1. 体细胞 SNV/小 indel 检测。** 从肿瘤–正常配对中区分真实突变、胚系变异和技术噪声 | Mutect2 是默认主调用器，包含局部组装、似然估计，以及污染、方向偏差等过滤。VarScan2 基于 pileup、频率和统计检验，Strelka2 用统计与单倍型证据，MuTect1 有条件运行。 [主调用器配置](../../conf/params.config#L58) · [Mutect2](../../nextNEOpi.nf#L1779) · [Mutect2 过滤](../../nextNEOpi.nf#L1938) · [VarScan2](../../nextNEOpi.nf#L2432) · [MuTect1](../../nextNEOpi.nf#L2788) · [Strelka2](../../nextNEOpi.nf#L3057) | **DeepSomatic 的配对 WES 模型可作为旁路调用器。** 它用 CNN 对 pileup 表示分类并输出 VCF。先核对样本角色、参考、`FILTER`、`AD/DP/VAF`，用独立肿瘤样本分层测 SNV、indel 和低 VAF。保留 Mutect2 主链，待验证哪些变化能改善候选事件与肽的召回，再考虑修改共识。 [DeepSomatic 论文](https://doi.org/10.1038/s41587-025-02839-x) · [官方模型与适用测序类型](https://github.com/google/deepsomatic) |
| **B2. 多调用器共识。** 从主调用器保留有确认支持的记录 | `make_hc_vcf.py` 使用主调用器与确认调用器的规则，额外记录支持来源。同位置不同 ALT 是旧实现的重点回归样例。 [共识任务](../../nextNEOpi.nf#L3204) · [现有匹配实现](../../bin/make_hc_vcf.py#L73) | 可先让 [bcftools norm](https://samtools.github.io/bcftools/bcftools#norm) 规范化对照文件，再试按参考与 `CHROM/POS/REF/ALT` 确认支持。将规则变化单独版本化。用同位点不同 ALT、等价 indel、多等位基因、主调用器独有、零记录和确认器缺席验证。 |
| **B3. DNA 结构变异与候选 indel。** 找断点并给下游提供证据 | Manta 在配对 reads 分支产生两路产物，候选小 indel 供 Strelka2，SV VCF 供 NeoFuse。属于传统结构变异检测。 [Manta 输出](../../nextNEOpi.nf#L2998) · [Strelka 的输入分支](../../nextNEOpi.nf#L3040) | WGS 扩展可并行评估 [GRIDSS2](https://doi.org/10.1186/s13059-021-02423-x) 的断点和单断端证据。需要单独处理 SV 表示与 NeoFuse 接口。Strelka2 所需的 Manta 小 indel 输入继续用原实现验证。 |
| **B4. 正常样本胚系 SNV/indel 与过滤。** 提供近邻变异和定相背景 | GATK HaplotypeCaller 用局部组装得到候选。**NVScoreVariants 对已有候选用 `read_tensor` 深度模型打分**，FilterVariantTranches 再按 `CNN_2D` 过滤。 [HaplotypeCaller](../../nextNEOpi.nf#L2063) · [NVScoreVariants](../../nextNEOpi.nf#L2126) · [tranche 过滤](../../nextNEOpi.nf#L2226) · [模型官方说明](https://gatk.broadinstitute.org/hc/en-us/articles/10064202674971-Introducing-NVIDIA-s-NVScoreVariants-a-new-deep-learning-tool-for-filtering-variants) | **DeepVariant WES 可替换整条正常样本调用与过滤链。** 先产出规范化正常 VCF，再沿用下游的注释和定相契约，其 VCF 使用自身的质量语义。用独立 GIAB 样本的高置信区比较基因型、SNV/indel 和近邻候选保留，最后核对突变肽。 [DeepVariant 官方仓库](https://github.com/google/deepvariant) · [NIST GIAB](https://www.nist.gov/programs-projects/genome-bottle) |
| **B5. 功能注释。** 把基因组变异映射到指定转录本、蛋白后果和野生型序列 | VEP 按转录本规则与参考数据库注释。pVACseq 路径依赖 `--pick`、Frameshift/Wildtype 插件和 VEP `CSQ` 字段。 [VEP 调用](../../nextNEOpi.nf#L3590) · [pVACtools 5.3.0 字段契约](https://github.com/griffithlab/pVACtools/blob/v5.3.0/pvactools/lib/input_file_converter.py#L96-L109) | 优先保留 VEP，独立评估注释与转录本版本升级。SnpEff 等仅在显式转换字段、复现转录本选择和一致生成蛋白序列后才具备替换条件。逐条核对 transcript/version、移码、蛋白变化和最终 WT/MT 肽。 |
| **B6. 近邻变异定相。** 判断多个变异是否在同一条单倍型上 | 有 GATK3 时做 read-backed phasing。无该能力时沿用注释上下文，pVACseq 不传 `-p`。 [定相任务](../../nextNEOpi.nf#L3664) · [回退](../../nextNEOpi.nf#L3759) · [pVACseq 定相参数](../../nextNEOpi.nf#L5706) | 可试 [WhatsHap](https://whatshap.readthedocs.io/en/latest/guide.html)，先处理 phased GT/`PS` 与旧版消费者读取的 `HP` 约定，同时保留单样本、索引和注释要求。验证顺式、反式、跨块、纯合、无法定相，以及最终蛋白序列。在肿瘤 CNV/LOH 区域单列适用性。 [pVACtools 5.3.0 近邻变异读取逻辑](https://github.com/griffithlab/pVACtools/blob/v5.3.0/pvactools/lib/proximal_variant.py#L28-L66) |

## C. HLA 分型

| 算法单元与问题 | 当前做法 | 可选替代与验收 |
|---|---|---|
| **C1. DNA HLA Class I/II 分型。** 按位点确定等位基因并提供候选呈递分子 | 肿瘤 DNA 取证后，OptiType 用整数线性规划推断 Class I。可用时 HLA-HD 通过 reads 对参考等位基因的比对与分型规则提供 Class I/II 证据。 [DNA 取证](../../nextNEOpi.nf#L4732) · [OptiType](../../nextNEOpi.nf#L4903) · [HLA-HD](../../nextNEOpi.nf#L5067) · [OptiType 官方实现](https://github.com/FRED-2/OptiType) · [HLA-HD 官方说明](https://www.genome.med.kyoto-u.ac.jp/HLA-HD/) | **优先旁路试 SpecHLA** 的 reads 分箱和局部组装。图比对方法 HLA*LA 可作独立对照。WES 优先测各位点的 two-field 准确率、无结果比例、低覆盖和少见等位基因，另核对新模型支持的 HLA 清单。使用有独立真值的正常 DNA 样本，肿瘤 DNA 的 LOH 与低覆盖分层。 [SpecHLA](https://pmc.ncbi.nlm.nih.gov/articles/PMC10545945/) · [HLA*LA](https://doi.org/10.1093/bioinformatics/btz235) |
| **C2. RNA 分型。** 补充 RNA 中可观察到的 HLA | RNA reads 可进入 OptiType，HLA-HD RNA 另有启用开关，3′ tag 路径受限制。 [RNA OptiType 路由](../../nextNEOpi.nf#L4937) · [RNA HLA-HD 路由](../../nextNEOpi.nf#L5121) | 全长 bulk RNA 可试 [arcasHLA](https://pmc.ncbi.nlm.nih.gov/articles/PMC6956775/) 或用加权 EM 的 [T1K](https://pmc.ncbi.nlm.nih.gov/articles/PMC10519407/)。对同病例的独立 DNA 分型核对位点与等位基因，保留表达不足和无法判定状态。3′ tag 单列验证。 |
| **C3. 分型合并、配对与工具可用性。** 把多来源分型整理成预测器可用的 HLA | `HLA_parser.py` 按自定义、强制 DNA/RNA 和普通合并路径解析，并用旧 pVAC 等位基因列表筛查。MixMHC2pred 还有直接消费 HLA-HD DNA 证据的路径。 [合并规则](../../bin/HLA_parser.py#L386) · [旧可用 HLA 清单](../../nextNEOpi.nf#L5274) · [MixMHC2pred 依赖](../../nextNEOpi.nf#L6284) | 继续用显式规则。分开保存原始分型和各模型支持的表示，统一 IPD-IMGT/HLA 版本，测试 Class II α/β 配对、低置信、用户覆盖、未知等位基因和模型拒绝原因。替掉 HLA-HD 前补齐 MixMHC2pred 所需证据，或将该支路单独标为不适用。 |

## D. 拷贝数、纯度、克隆性与突变负荷

| 算法单元与问题 | 当前做法 | 可选替代与验收 |
|---|---|---|
| **D1. CNV、纯度和倍性。** 从深度和等位基因平衡推断肿瘤基因组组成 | ASCAT3 根据 LogR/BAF 拟合；Sequenza 根据深度比和等位基因频率估计。主路径选择 ASCAT 或 Sequenza，失败时预测支路可收到默认纯度 0.95。CNVkit 和 Control-FREEC 是分支结果。 [ASCAT](../../bin/ascat3.R#L107) · [Sequenza](../../nextNEOpi.nf#L4080) · [纯度选择](../../nextNEOpi.nf#L4227) · [CNVkit](../../nextNEOpi.nf#L4335) | 可对照 [FACETS](https://doi.org/10.1093/nar/gkw520) 的等位基因特异 CN，或在目标 panel/WES 上对照 [PureCN](https://doi.org/10.1186/s13029-016-0060-z)。验收断点与区段重叠、major/minor CN、LOH、纯度、倍性和回退来源，并记录不同解的置信信息。未经验证先保留 ASCAT/Sequenza 路径。 |
| **D2. 单变异 CCF。** 结合等位基因读数、区段 CN 和纯度估算携带该变异的癌细胞比例 | `mkCCF_input.py` 组装输入，`CCF.R` 用二项似然和离散网格估计 CCF 与区间，并输出克隆性判定。实际 CCF 依赖可用的 CN 和纯度，两个估计分支都失败时单独保留缺失状态。 [流水线入口](../../nextNEOpi.nf#L4523) · [CCF 计算](../../bin/CCF.R#L69) | 先保留公式并回放小粒度真值。用已知纯度、CN 和读数的样例核对极端深度、阈值两侧和无匹配。若需要对变异做亚克隆聚类，可加 [PyClone-VI](https://pmc.ncbi.nlm.nih.gov/articles/PMC7730797/) 支线，以簇及其细胞比例另行验证。 |
| **D3. TMB。** 计算可评估区域内每 Mb 的合格突变数 | 脚本从两个 BAM 计算深度、碱基质量达标的交集，输出全范围和编码区结果。旧代码还有 contig 长度等隐式规则。 [TMB 入口](../../nextNEOpi.nf#L4612) · [区间和分母实现](../../bin/mutationalLoad.py#L390) | 先显式输出突变计数、可评估区域大小和规则版本。按 assay 固定统计对象、捕获区、可调用区和过滤条件，用重叠 BED、零分母、同位点多 ALT 测试。任何新口径单独发布并对照。 [TMB Harmonization Project](https://pmc.ncbi.nlm.nih.gov/articles/PMC7174078/) |

## E. RNA 表达、融合与剪接事件

| 算法单元与问题 | 当前做法 | 可选替代与验收 |
|---|---|---|
| **E1. RNA 比对。** 将 RNA reads 放回基因组坐标，保存剪接与覆盖证据 | NeoFuse 复合任务产出 STAR RNA BAM/BAI。旧 SIF 的 STAR 实际版本和参数需从运行镜像确认。 [NeoFuse 输出](../../nextNEOpi.nf#L5379) · [NeoFuse 官方实现](https://github.com/icbi-lab/NeoFuse) | 首轮单独交付 STAR BAM/BAI，继续供融合、剪接和 RNA 变异读数使用。拆出独立 STAR 任务时比较坐标、CIGAR、junction、嵌合比对和输入的参考与注释。 |
| **E2. 表达定量。** 估计基因或转录本的表达水平 | 旧复合任务输出 TPM。上游 NeoFuse 实现用 featureCounts 进行基因层面计数，再生成 TPM。SIF 内部实际版本和参数待核对。 [TPM 产物](../../nextNEOpi.nf#L5375) · [上游脚本](https://github.com/icbi-lab/NeoFuse/blob/master/Docker/source/NeoFuse_single.sh) | 可并行试 [Salmon](https://www.nature.com/articles/nmeth.4197) 做转录本定量，再按明确规则汇总到基因。比较基因 ID、计数、TPM、跨过表达阈值的候选和低表达样本。 |
| **E3. 变异级 RNA 支持。** 估计突变位点的深度和等位基因读数 | 现有流程对 RNA BAM 计算 readcount，并分别为 SNV、indel 向 VCF 增加支持信息。 [RNA 变异注释](../../nextNEOpi.nf#L5557) | 首轮保留读数工具并把计数输出独立。验收固定 RNA BAM 下的 AD/DP/VAF、多等位基因匹配、坐标与转换语义，区分没有 RNA、覆盖不足与确实零 ALT。 |
| **E4. 融合事件。** 从跨断点 reads 与跨越断点的配对证据识别融合基因和断点 | NeoFuse 集成 Arriba，适用时接收 Manta DNA SV 证据，同时在同一任务生成融合候选肽。 [输入与输出](../../nextNEOpi.nf#L5348) · [NeoFuse 论文](https://doi.org/10.1093/bioinformatics/btz879) | 先导出 Arriba 事件表和证据，再用 [STAR-Fusion](https://pubmed.ncbi.nlm.nih.gov/31639029/) 作并行事件检测。按断点、方向、读段支持、阅读框和真值事件对比。事件转肽的变化在 F 单独验收。 |
| **E5. 异常剪接证据。** 提取 junction 并关联可能影响剪接的 DNA 变异 | RSeQC 判断链特异性，现有脚本补 XS，RegTools 从 RNA BAM 与变异拿到 junction 和顺式剪接证据。3′ tag 有条件跳过。 [链特异性和剪接](../../nextNEOpi.nf#L5816) · [RegTools 任务](../../nextNEOpi.nf#L5904) · [RegTools 论文](https://www.nature.com/articles/s41467-023-37266-6) | 保留 RegTools 作为真实 RNA 证据来源。可用 [SpliceAI](https://pubmed.ncbi.nlm.nih.gov/30661751/) 的深度序列模型另加“DNA 变异可能影响剪接”的分数，再与观测 junction 对照。验收供体/受体坐标、链方向、支持读数、RNA 类型和缺失状态。 |

## F. 新抗原候选构建与呈递预测

这里有三个不同的训练和评估终点。**BA（binding affinity）**估计肽与 HLA 结合强度，通常涉及 IC50 或结合百分位。**EL（eluted ligand）或呈递评分**用质谱检出的配体等数据学习肽被呈递的可能性。**IM（immunogenicity）**评价肽–HLA 触发特定 T 细胞应答的可能性。每个模型独立存储任务类型、模型版本、原始分数、单位或百分位定义、分数方向和适用范围。

| 算法单元与问题 | 当前做法 | 可选替代与验收 |
|---|---|---|
| **F1. 常规变异到肽。** 由突变和转录本得到 WT/MT 序列 | pVACseq 消费 VEP VCF、可选定相、HLA 和纯度。有 RNA 时 VCF 还带表达与 RNA 支持。默认 Class I 长度 8–11，Class II 15–25。候选枚举是规则和序列转换。 [入口](../../nextNEOpi.nf#L5674) · [长度配置](../../conf/params.config#L197) | 先保持枚举和组装规则。比较评分模型时冻结肽–HLA 输入和事件键。若升级 pVACseq，再单独比较转录本版本、突变位置、WT/MT 肽、移码、近邻变异、候选重复数和缺失原因。 |
| **F2. 融合和剪接事件到肽。** 依据断点或 junction 恢复阅读框并生成候选 | NeoFuse 在同一任务输出融合候选，pVACsplice 消费 RegTools junction、注释 VCF、HLA 和纯度。 [NeoFuse 候选](../../nextNEOpi.nf#L5364) · [pVACsplice](../../nextNEOpi.nf#L5953) | 可用同一份 Arriba 注释事件对比 [pVACfuse](https://pvactools.readthedocs.io/en/stable/pvacfuse.html)。剪接可用 [splice2neo](https://pubmed.ncbi.nlm.nih.gov/38863673/) 作旁路对照。先比事件能否恢复正确转录本、阅读框和肽，再独立评估呈递。现有 pVACsplice 有对错误做降级的路径，验收需区分真正零事件和执行失败。 [旧错误处理](../../nextNEOpi.nf#L6018) |
| **F3. BA，Class I/II 结合亲和力。** 判断给定肽和 HLA 的结合强度 | 当前配置包含 Class I 的 NetMHCpan、MHCflurry、MHCnuggetsI，Class II 的 NetMHCIIpan、MHCnuggetsII。NetMHCpan 系列、MHCflurry 和 MHCnuggets 均涉及训练模型。 [配置](../../conf/params.config#L197) · [各模型的任务类型](https://pvactools.readthedocs.io/en/stable/pvacseq/features.html) | **优先对比 [NetMHCpan 4.2](https://services.healthtech.dtu.dk/services/NetMHCpan-4.2/) 和 [NetMHCIIpan 4.3](https://services.healthtech.dtu.dk/services/NetMHCIIpan-4.3/) 的 BA 输出。** 用独立定量结合实验比较 Spearman、对数 IC50 误差和阈值判定，分层报告 HLA、肽长和数据缺口。DTU 新版上线也需要单独核对本地适配、许可证和所用小版本。 |
| **F4. EL，Class I/II 呈递。** 判断肽被所给 HLA 呈递的可能性 | 配置包含 Class I 的 NetMHCpanEL、MHCflurryEL，Class II 的 NetMHCIIpanEL。另有 MixMHC2pred 2.0.2.2 支线，它使用 HLA-HD 证据和单独的候选肽构建。 [配置](../../conf/params.config#L123) · [呈递算法清单](../../conf/params.config#L200) · [补充呈递路径](../../nextNEOpi.nf#L6265) | 对照新版 NetMHCpan/IIpan 的 EL 输出。Class I 可加 [MixMHCpred 3.0（2025）](https://doi.org/10.1186/s13073-025-01450-8)，Class II 可加 [ImmuScope-EL（2025）](https://www.nature.com/articles/s42256-025-01073-z)。用独立免疫肽组质谱的已观测配体评估 AUPRC、Recall@K 和 HLA 覆盖，说明背景或负例构建方式。质谱未检出作为未标注证据处理。 |
| **F5. 免疫原性补充分数与加工/稳定性。** 提供与结合不同的证据 | pVAC 配置已包含 Class I 的 BigMHC_IM 和 DeepImmuno。NetChop 默认关闭，NetMHCstab 默认开启，并依赖对应类别和适用条件。 [配置](../../conf/params.config#L197) · [实际参数](../../nextNEOpi.nf#L5703) | 已有的 IM 结果按 G 的免疫原性基准一起比较。若新增稳定性或切割模型，分别用对应实验指标验收。旧版 NetMHCstab 适配器会将肽与 HLA 信息发往外部服务，即便结合预测使用本地 IEDB。复现时优先用公开对照数据或已保存的稳定性结果，将联网依赖纳入运行记录。 [pVACtools 5.3.0 NetMHCstab 实现](https://raw.githubusercontent.com/griffithlab/pVACtools/v5.3.0/pvactools/lib/netmhc_stab.py) |
| **F6. 过滤、聚合与报告字段。** 把预测结果按阈值、表达、覆盖和转录本规则整理成候选 | pVACseq/pVACsplice 有 standard、relaxed、custom 配置，RNA 文库类型可改变生效的 RNA 筛选条件。旧版 IC50 汇总只使用亲和力估计，综合百分位可能混入多个预测终点的 rank。 [过滤配置](../../conf/params.config#L204) · [RNA tag 路径](../../nextNEOpi.nf#L5728) · [旧版聚合实现](https://raw.githubusercontent.com/griffithlab/pVACtools/v5.3.0/pvactools/lib/output_parser.py) | 先核对实际预测包和模型，再考虑整体升级。[pVACtools 7.0.0](https://github.com/griffithlab/pVACtools/releases/tag/v7.0.0) 提供按结合、呈递、免疫原性划分的输出和规则。按模型保留原始分数，分别验证字段映射、临界值、过滤去留，以及 CSiN 等消费者用到的旧字段。 |

pVACtools 镜像配置指向 `5.3.0`。构建文件声明 MHCflurry `2.0.6`，BigMHC 和 DeepImmuno 从 Git 安装且未在相应行写明提交号；还应记录实际镜像、IEDB 版本、模型文件哈希和预测器返回的支持清单。现行 pVACtools 文档的 Class I `NetMHCpan` 执行入口仍列 4.1，因此 4.2 先走直接的本地旁路适配器。Class II 文档有 4.3 参数，也应核对该运行路径实际调用到的版本。 [旧镜像配置](../../conf/process.config#L234) · [构建与补丁](../../assets/pVACtools_icbi.def#L85) · [pVACseq 本地版本说明](https://pvactools.readthedocs.io/en/stable/pvacseq/features.html)

## G. 候选证据、免疫原性与免疫受体库

| 算法单元与问题 | 当前做法 | 可选替代与验收 |
|---|---|---|
| **G1. 参考蛋白匹配。** 判断突变肽是否完整出现在参考蛋白中 | BLASTP-short 最多返回 5 个比对，解析器保留全长且所有残基一致的命中，并将匹配信息附回候选。 [BLAST 参数](../../nextNEOpi.nf#L6608) · [命中判定](../../bin/parse_blast_result.py#L98) | 若功能只需精确存在性和匹配蛋白 ID，可用 [Aho–Corasick 多模式匹配](https://doi.org/10.1145/360825.360855) 在同一蛋白库检索。测试全长、近似、重复命中、边界和旧 BLAST 限制引起的差异。将全库精确索引和旧版截断口径分开报告。 |
| **G2. 候选 CCF 回填。** 把单变异估计关联到对应候选肽 | 当前只给 pVACseq 候选追加 CCF。脚本转换坐标后按染色体和位置合并，并启用前向填充。 [追加 CCF](../../nextNEOpi.nf#L6466) · [旧合并规则](../../bin/add_CCF.py#L45) | 优先验证精确的病例和等位基因关联，将无匹配保留为缺失。先用相邻变异、同位置不同 ALT、同变异多个肽和输入缺失记录旧输出。变更回填规则需单独比较。 |
| **G3. 病例级免疫证据汇总。** 聚合常规候选在表达、结合与变异频率上的证据 | CSiN 读 pVACseq 全量表，使用百分位、IC50、表达阈值、肿瘤 DNA VAF 和候选负荷计算 Class I/II 和合并分数。属于公式与规则，输入中所用的 VAF 与 D 组 CCF 有不同含义。 [输入路由](../../nextNEOpi.nf#L6099) · [分数公式](../../bin/CSiN.py#L57) · [CSiN 论文](https://pmc.ncbi.nlm.nih.gov/articles/PMC7239327/) | 先保留公式、旧输入字段和结果语义，验证仅一类 HLA、空候选、缺表达及相同坐标等边界。如果研究目标需要显式克隆结构，再将 NeoPrecis 的病例级景观分析作为独立指标，以相同病例终点比较。 [NeoPrecis 论文（2026）](https://doi.org/10.1038/s41467-026-68651-6) |
| **G4. 候选级免疫原性。** 对给定候选评估 T 细胞反应的可能性 | 独立 IGS 分支使用 **GBM 梯度提升模型**，读取经过滤的常规 Class I 候选，从 WT/MT 肽和突变位置提取特征。业务文档将该模型描述为适用于 8–11 aa 的 SNV 候选，旧 wrapper 实际按 Class I 表和 WT/MT 是否存在选行，模型适用范围应在新接口明确。pVAC 内还有 BigMHC_IM、DeepImmuno。 [适用范围](../../README.md#L39) · [IGS 输入](../../nextNEOpi.nf#L6091) · [特征与模型](../../bin/NeoAg_immunogenicity_predicition_GBM.R#L27) · [GBM 原论文](https://pubmed.ncbi.nlm.nih.gov/31515258/) | 用现有 GBM、BigMHC_IM 和 DeepImmuno 作基线。Class I 可比较 [PRIME 2.0](https://doi.org/10.1016/j.cels.2022.12.002)，较新的 [NeoPrecis-Immuno（2026）](https://doi.org/10.1038/s41467-026-68651-6) 可按 Class I/II 分层试验，Class II 还可用 [ImmuScope-IM](https://www.nature.com/articles/s42256-025-01073-z)。按有实验标注的 T 细胞应答比较 AUPRC、患者内 Precision@K/Recall@K 与覆盖。区分不适用、成功但结果为空和运行失败，测同序列多来源是否重复回填。 |
| **G5. BCR/TCR 受体库重建。** 从测序 reads 恢复受体链、克隆型与丰度 | MiXCR 从 DNA 和 RNA reads 独立运行，按样本角色选 preset，配置的下载版本为 `4.7.0`。这里做 V(D)J 比对和克隆组装。 [版本配置](../../conf/params.config#L115) · [MiXCR 输入和 preset](../../nextNEOpi.nf#L6880) | bulk RNA 可旁路评估 [TRUST4](https://www.nature.com/articles/s41592-021-01142-2)。以链别、CDR3、V/J、克隆集合和丰度为验收项，优先设计与同病例专用受体库测序的对照。保留 DNA 分支单独评估。交接字段参考 [AIRR Rearrangement](https://docs.airr-community.org/en/stable/datarep/rearrangements.html)。 |

## 替换实验与验收

**先做同方法回放，再做新旧方法的性能对照。** 回放使用同一份边界输入、参考、模型、过滤规则和版本，验证换编排前后关键实体、过滤去留及状态一致。换模型后允许数值、排序和候选集合变化，是否启用看独立真值、预先约定的指标和下游影响。每次只改一个算法单元，并保存旧结果、新结果和差异。 [第一层验证步骤](first-layer-functional-design.md#验证步骤) · [科学等价测试计划](../05_testing/scientific-equivalence-plan.md#分阶段比较)

| 对照实验 | 固定输入和对照数据 | 判断依据 |
|---|---|---|
| **1. BWA-MEM2 比对** | 同一 WES reads、同一参考、相同后处理。至少纳入配对、分片边界和较难比对区域。 | 核对逐条比对与关键标签变化，向下核对 VCF 与候选。结果满足等价要求后，比较耗时和内存。 |
| **2. SpecHLA 分型** | 冻结 BAM、文库类型与 HLA 字典。有独立高分辨率分型真值的样本按覆盖、位点和等位基因分层。 | 同时报 two-field 准确率、无结果比例、Class II 配对和实际可评分的 HLA 覆盖。只有覆盖的新等位基因另列，追踪其新增或丢失的候选。 |
| **3. BA 与 EL 预测** | 固定同一批候选肽、序列上下文、HLA 配对和 RNA/纯度。BA 用量化结合实验，EL 用独立质谱配体，现行模型和新版各分数头分别跑。 | 同时报告共同覆盖集合的表现和全量覆盖率。按 HLA 位点、肽长、少见等位基因及 II 类 α/β 配对分层。实际使用时单独记录不支持、缺上下文和回退。 |
| **4. 新变异调用器** | 固定配对 BAM、WES assay 和参考，以可信区与捕获及可调用区交集评估。SEQC2 HCC1395 可用于兼容性和复核；DeepSomatic 使用过该病例的数据，独立性能验收另留病例。正常胚系用独立 GIAB 数据。 [SEQC2 真值](https://pmc.ncbi.nlm.nih.gov/articles/PMC8532138/) · [DeepSomatic 数据与训练](https://doi.org/10.1038/s41587-025-02839-x) | 分 SNV/indel、VAF、覆盖和样本类型比较精确率、召回率和 F1。记录新增/丢失的变异、其支持证据、是否经过共识以及影响的候选表行。 |
| **5. IM 模型与病例内优先级** | 采用有独立实验标签的肿瘤新抗原数据，如 TESLA 或另一个未进入所评模型训练的队列。以患者和队列分组，同时检查完全重复肽、相近序列及重叠肽核心。DTU 4.2 部分任务用过 CEDAR 数据，其他模型也要核对训练来源。 [TESLA 实验数据](https://pmc.ncbi.nlm.nih.gov/articles/PMC7652061/) · [DTU 训练说明](https://services.healthtech.dtu.dk/services/NetMHCpan-4.2/) | 用病例内 Precision@K/Recall@K、AUPRC 和覆盖率评价，并按患者重采样估计不确定性。实验未测的候选标为未标注。病例级汇总使用病例级终点单独评估。 |

候选差异报告沿用第一层的身份字段，至少保留病例、事件或规范化等位基因、转录本版本、WT/MT 肽、HLA 或配对、MHC 类别和候选来源。另记录模型与版本、任务类型、输入支持情况、失败原因，以及入选变化来自事件变化、肽变化、HLA 变化还是评分规则变化。评估阈值和可接受的变化在对照前约定，并保留各单位的旧实现作为回退。

各算法条目的归属见 [模块地图](module-map.md)。首批试点的开始条件和交付见 [增量迁移路线](../07_migration/incremental-roadmap.md#首批算法替代试点)，采纳与回退见 [迁移兼容策略](../07_migration/compatibility-strategy.md#候选算法的采纳)。
