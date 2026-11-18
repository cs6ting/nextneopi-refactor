# 当前代码到目标架构映射

源码映射以旧版提交 `9f34698` 为准。功能交接见 [第一层设计](../02_modules/first-layer-functional-design.md)，算法级问题、替代候选及证据见 [第二层清单](../02_modules/second-layer-algorithm-inventory.md)。

## 主流程与配置

| 功能组 | 旧版入口与行为 | 目标模块或能力 |
|---|---|---|
| 输入与运行 | [manifest 和参数](../../nextNEOpi.nf#L121)、[检测区间](../../nextNEOpi.nf#L548) | MOD-01～02、配置 resolver、工具与许可预检 |
| A 测序数据准备与 DNA 比对 | [BAM 接入](../../nextNEOpi.nf#L420)、[BWA](../../nextNEOpi.nf#L1094)、[重复标记](../../nextNEOpi.nf#L1212)、[BQSR](../../nextNEOpi.nf#L1405) | MOD-03～04，IF-READ/QC/ALN。保留 reads、不同阶段 BAM 及覆盖 |
| B DNA 变异与注释 | [Mutect2](../../nextNEOpi.nf#L1779)、[胚系过滤](../../nextNEOpi.nf#L2126)、[共识](../../nextNEOpi.nf#L3204)、[VEP](../../nextNEOpi.nf#L3520)、[定相](../../nextNEOpi.nf#L3664) | MOD-05～06，IF-VAR/ANN/PHS。输出调用器证据、共识与注释、定相状态和适用的 Manta 证据 |
| C HLA 分型 | [DNA 取证](../../nextNEOpi.nf#L4732)、[RNA reads 分流](../../nextNEOpi.nf#L1038)、[HLA-HD](../../nextNEOpi.nf#L5067)、[分型合并](../../nextNEOpi.nf#L5224) | MOD-07，IF-HLA。标准分型与各预测器的可用性独立记录，保留 MixMHC2pred 所需分型证据 |
| D 肿瘤特征 | [ASCAT](../../nextNEOpi.nf#L3785)、[纯度回退](../../nextNEOpi.nf#L4227)、[CCF](../../nextNEOpi.nf#L4523)、[TMB](../../nextNEOpi.nf#L4612) | MOD-08～09，IF-CNV/PUR/CCF/TMB。预测所用纯度与 CCF 的可用性独立记录 |
| E RNA 表达与事件 | [NeoFuse 的 RNA/融合输出](../../nextNEOpi.nf#L5348)、[表达及 RNA 读数](../../nextNEOpi.nf#L5507)、[RegTools](../../nextNEOpi.nf#L5904) | MOD-10～11，IF-RNA/FUS/SPL。与 F 复用旧版 NeoFuse 执行并投影各产物 |
| F 新抗原候选与呈递预测 | [pVACseq](../../nextNEOpi.nf#L5668)、[pVACsplice](../../nextNEOpi.nf#L5947)、[MixMHC2pred](../../nextNEOpi.nf#L6265) | MOD-12 协调三类候选与呈递，保留 MOD-13 既有补充呈递入口的迁移映射。按任务与 MHC 类别输出 |
| G 免疫证据分析 | [CCF 回填](../../nextNEOpi.nf#L6446)、[BLAST](../../nextNEOpi.nf#L6577)、[CSiN](../../nextNEOpi.nf#L6684)、[GBM](../../nextNEOpi.nf#L6771)、[MiXCR](../../nextNEOpi.nf#L6863) | MOD-13，IF-IMM/REP。候选分析与 reads 直连的受体库并行 |
| 报告与发布 | [样本汇总](../../nextNEOpi.nf#L6925)、[MultiQC](../../nextNEOpi.nf#L7001)、[运行收尾](../../nextNEOpi.nf#L7410) | MOD-14、ArtifactStore、ProvenanceStore |

[参数](../../conf/params.config)、[资源与容器配置](../../conf/process.config)、[部署 profile](../../conf/profiles.config) 和 [参考资源](../../conf/resources.config) 对应目标中的 methods/policies、执行与镜像配置、以及版本化 `ReferenceBundle`。参见 [配置规范](../04_specifications/configuration-specification.md)。

## `bin/` 脚本

| 脚本 | 目标模块/接口 | 迁移方式 |
|---|---|---|
| `CCF.R` | MOD-09 / IF-CCF-001 | characterization 后纯 Python 数值实现 |
| `CSiN.py` | MOD-13 / IF-IMM-002 | 重构为可导入纯 Python domain/scorer |
| `HLAHD2mixMHC2pred2.py` | C → F，MOD-07/13 | 将 HLA-HD 证据转换为预测器支持的候选配对，记录推断来源与不支持项 |
| `HLA_parser.py` | MOD-07 / IF-HLA-003 | 纯 Python resolver+decision trace，修正 mutable/default 风险 |
| `NameToID.py` | MOD-10 | annotation-aware Python transform |
| `NeoAg_immunogenicity_predicition_GBM.R` | MOD-13 | 第三方模型 adapter，保留固定容器 |
| `SequenzaScript.R` | MOD-08 | Sequenza tool adapter 容器 driver/collector |
| `add_CCF.py` | MOD-09/13 | typed join；禁止未匹配 forward-fill |
| `ascat3.R` | MOD-08 | ASCAT adapter 容器 driver/collector |
| `assess_significance.R` | MOD-08 | FREEC optional visualization adapter |
| `check_pe.py` | MOD-01/03 | 合并为 BAM metadata/materializer Python 服务 |
| `concat_pvacseq.py` | MOD-12 | schema-aware candidate aggregator |
| `convertAlleleCounts.r` | MOD-08 | 先确认是否在主链；需要则 Python 化，否则经 ADR 删除 |
| `freec2bed.pl` | MOD-08 | Python FREEC collector/coordinate transform |
| `freec2circos.pl` | MOD-08 | Python optional renderer transform |
| `get_epitopes.py` | MOD-13 | typed scorer feature builder |
| `immuno_score.py` | MOD-13 | 纯 Python score collector/domain logic |
| `makeGraph.R` | MOD-08 | FREEC optional visualization 容器 |
| `make_hc_vcf.py` | MOD-05 / IF-VAR-003/004 | 拆 caller normalizer+primary-confirmed policy |
| `make_merged_exon_bed.sh` | MOD-02 | Python resource-build utility，运行前执行 |
| `make_peptide_fasta.py` | MOD-13 | typed peptide transform |
| `make_release.sh` | release tooling | Python packaging/release pipeline；旧脚本已漂移需退役 |
| `mkCCF_input.py` | MOD-09 | typed count/CN join 与坐标校验 |
| `mkSampleInfo.py` | MOD-14 | ScientificReport renderer |
| `mutationalLoad.py` | MOD-09 / IF-TMB-001 | 口径版本化的 Python TMB service |
| `parse_blast_result.py` | MOD-13 / IF-IMM-001 | BLAST collector |
| `parse_infer_experiment.py` | MOD-10/11 | strandedness typed parser |
| `parse_mixMHC2pred.py` | F，MOD-13 兼容入口 | Class II 呈递结果 collector |
| `parse_mixMHC2pred_pVACsplice.py` | F，MOD-13 兼容入口 | 剪接候选的 Class II 呈递结果 collector |
| `pepChopper.py` | F，MOD-12/13 | peptide transform，测试 WT/MT 长度变化、滑窗与候选身份 |
| `tagXSstrandedData.awk` | MOD-11 | Python stream transform，flag/mate property tests |

## `assets/`

`*.def/*.yml` 迁移为受控镜像构建输入和 image lock；`Final_gbm_model.rds`/allele lists 进入 versioned model/resource bundle；`Frameshift.pm/Wildtype.pm` 及 patches 在确认 ownership/许可后进入固定 VEP/工具镜像构建期，禁止运行期 patch；邮件模板归 MOD-14 外围通知 adapter。

## 判定规则

自研科学转换迁入 domain；第三方命令和原生格式进入 adapter；DAG/资源/retry/publish 进入 infrastructure；未知 ownership 先登记风险，未经许可审查不复制到新发行包。
