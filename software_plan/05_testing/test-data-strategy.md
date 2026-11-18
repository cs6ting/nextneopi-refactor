# 测试数据策略

## 四层数据

| 层级 | 内容 | 用途 | 仓库策略 |
|---|---|---|---|
| L0 | Python 内存对象/小文本 fixture | 领域单元/property | 可提交，人工可读 |
| L1 | 第三方工具 native output fixture | collector/contract | 最小化、注明来源/版本/许可 |
| L2 | 微型 reference+合成 reads | 容器 integration/local E2E | 可再分发且体积受控；大文件外部缓存 |
| L3 | 公开 tumor/normal benchmark | 科学/性能/Slurm | 不入 Git，checksum manifest 下载/预置 |

## L0/L1 设计

必须覆盖 FASTQ/BAM、SE/PE、多 lane、XX/XY/UNKNOWN、空 VCF/HLA、同位置不同 ALT、多等位 indel、chr/no-chr、0/1-based、各 caller FORMAT、HLA class-II pairing、ASCAT/Sequenza outputs、RNA protocol 和五类状态。每个 fixture 附 `fixture.yaml`：来源、生成命令、工具/镜像、reference、checksum、许可、预期语义。

首轮回放保留注释 VCF/定相工件、HLA、实际纯度及两个 pVACseq 候选表。为旧行为刻画另备同位置不同 ALT 的确认调用、CCF 缺失或无精确匹配、顺式/反式和跨块定相、旧 pVACtools 消费的 HP 格式样例。为可选分支准备仅 Class I、RNA 缺失/普通/3′ tag、空结果与真实失败样例。

## L2 合成数据

构建少量 contig 的 FASTA/FAI/dict、capture BED/GTF/known-sites 和 matched tumor/normal reads；注入 SNV/indel、近端 germline、不同 VAF、覆盖边界与可选 RNA event。随机生成固定 seed。无法在微型 reference 上运行的工具使用真实 reference 小区间 nightly test，不能用假成功替代。

## L3 公开候选

NIST Cancer Genome in a Bottle HG008 提供公开 tumor/normal 方向和 draft somatic small/SV/CNV benchmark，是长期候选；其版本成熟度、数据规模和下载成本必须在采用时锁定并记录，draft 版本不得作为唯一发布真值。还应评估可公开再分发的挑战/工具示例数据。

## 候选方法留出集

给首批可选试验记录数据来源、纳入标准、真值范围、可能的训练重叠和冻结批次。BWA-MEM2 使用同一份配对 reads，保留逐 read 对照和候选比较所需病例。SpecHLA 使用可核验的独立分型真值，按样本或队列留出并分层报告覆盖、位点及罕见等位基因。BA 与 EL 分开保存配对输入、标签来源、队列或研究批次，并检查肽、重叠序列核心和 HLA 的重复；缺标记单独编码。冻结可比范围和支持列表后，在共同可评分集合比较指标，同时汇报全量输入的覆盖率。相关判定见[首批可选算法评测](scientific-equivalence-plan.md#首批可选算法评测)。

## 隐私与许可

真实内部数据不得进入 Git/普通 CI；使用受控存储、去标识 ID 和访问审计。公开数据仍核验条款。fixture 不包含 license、token 或可识别信息。

## 版本与更新

测试数据 manifest 有版本与 checksum；变更需说明科学目的，并同时保留旧版用于回归窗口。reference/tool 升级时新增 baseline，不覆盖历史。

## 数据验收

数据可重建、来源完整、预期结果有领域解释、体积/运行时间适合所属测试层，并覆盖追踪矩阵要求。
