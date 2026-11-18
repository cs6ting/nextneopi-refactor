# MOD-04 DNA 比对

## 目的、职责与非职责

把 DNA `ReadSet` 转换为 caller/HLA 可用的规范 BAM，覆盖 alignment、uBAM 合并、duplicate marking、tag 修正、BQSR 和 alignment QC。模块不调用变异、不解释 HLA，也不隐藏分片失败。

## 上下游与当前映射

上游 MOD-02/03；下游 MOD-05/06/07/08/09/14。A2 使用 `FastqToSam`、BWA-MEM 和 `MergeBamAlignment`，A3 使用 `sambamba markdup`、SAMtools 排序及 GATK `SetNmMdAndUqTags`，A4 使用 GATK4 BQSR 并产生 Picard、SAMtools、mosdepth 等 QC 指标。 [A 组算法单元](second-layer-algorithm-inventory.md#a-测序数据准备与-dna-比对) · [比对](../../nextNEOpi.nf#L1054) · [重复标记](../../nextNEOpi.nf#L1255) · [BQSR](../../nextNEOpi.nf#L1405)

## 实体、输入输出与不变量

输入 `CanonicalReadSet + ReferenceBundle + CallableRegions`；输出 `AlignedBam`、`DuplicateMarkedBam`、`RecalibratedBam`、`AlignmentQcMetrics`。交给下游使用的 BAM 按坐标排序，具备有效索引，且 RG、样本身份和参考字典一致。HLA 的 DNA 取证使用肿瘤 `DuplicateMarkedBam`，CNVkit 使用配对 `DuplicateMarkedBam`，Mutect2 等调用器使用配对 `RecalibratedBam`。旧兼容路径的部分调用器、Sequenza 或近邻定相可消费 GATK3 重比对后的 BAM，应保留阶段与来源。 [重复标记产物分流](../../nextNEOpi.nf#L1281) · [BQSR 分流](../../nextNEOpi.nf#L1692) · [GATK3 分流](../../nextNEOpi.nf#L2384)

## 接口与实现

提供 `IF-ALN-001 AlignDNA`、`IF-ALN-002 PostprocessDNAAlignment`、`IF-ALN-003 RecalibrateBaseQuality`、`IF-QC-002 AssessAlignmentQC`。首期实现 BWA-MEM/GATK/Picard/sambamba/mosdepth；未来 BWA-MEM2 等通过 capability 新增。不同 aligner 参数与 supplementary/secondary 语义必须保留。

A2 优先以 BWA-MEM2 旁路回放。固定 reads、FASTA 与下游工具，重建比对索引，比较逐 reads 坐标、CIGAR、MAPQ、flags、RG、标签和下游候选，再记录耗时与内存。BWA-MEM 继续作为默认方法。 [试点验收](second-layer-algorithm-inventory.md#替换实验与验收)

## 配置、容器、资源与许可

配置 read group、线程、BQSR known-sites、scatter 和 QC policy；site profile 只覆盖资源。工具用固定镜像，参考只读。alignment/BQSR 为高 CPU/磁盘任务，scratch 估算和 gather I/O 单独声明。

## 状态和 provenance

必需主链失败为 `FAILED`；QC 可按 recipe 允许 section 失败，但不得使 BAM 假成功。错误包括 `READ_GROUP_MISMATCH`、`REFERENCE_MISMATCH`、`MISSING_INDEX`、`INCOMPLETE_SCATTER`。记录每个 shard、参数、工具、资源 attempt 和 parent artifacts。

## 测试

单元验证 RG/资源估算；契约验证各 adapter；集成比较 read/RG/flag/duplicate/coverage；系统验证分片失败重试、resume、local/Slurm。不得以 BAM 字节 hash 判断科学等价。

## 验收与风险

验收 REQ-FUN-006～007、ACC-001～003。风险是巨型 shell 管道中间结果不可见、gather 缺 shard、male/sex 传播错误；目标实现逐工件提交并严格检查集合。
