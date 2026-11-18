# MOD-03 Reads 预处理与 QC

## 目的、职责与非职责

将 FASTQ 或 BAM 输入物化为统一 `CanonicalReadSet`，支持 lane 合并、可选 trim 和 read-level QC。模块不进行 DNA/RNA alignment，也不根据 QC 自动改变科学方法，除非明确 policy。

## 上下游与当前映射

上游 MOD-01/02；下游 MOD-04、MOD-07、MOD-10、MOD-13。算法单元 A1 覆盖 BAM 检测和转 FASTQ、多 lane 合并以及 FastQC/fastp。`bin/check_pe.py` 负责 BAM layout 检查。准备后的 RNA reads 直接分流给 C2 RNA HLA，MiXCR 则独立消费准备后的 DNA/RNA reads。 [A 组算法单元](second-layer-algorithm-inventory.md#a-测序数据准备与-dna-比对) · [reads 分流](../../nextNEOpi.nf#L1030)

## 输入输出与不变量

输入 `RawFastqSet | RawBam`；输出 `CanonicalReadSet`、`TrimmedReadSet`（或 `NoTrim` passthrough）、`ReadQcMetrics`。PE 的 R1/R2 必须成对且 read 数量/名称一致；lane 顺序可追踪；BAM 输入首期明确为重新物化 reads，不伪装 analysis-ready BAM passthrough。

## 接口与实现差异

提供 `IF-READ-001 MaterializeReads`、`IF-READ-002 TrimReads`、`IF-QC-001 AssessReadQC`。实现包括 `fastq_passthrough`、`samtools_bam_to_fastq`、`no_trim`、`fastp`、`fastqc`。`no_trim` 是合法实现而不是缺步骤；FastQC 与 fastp metrics 是不同 capability，不互相冒充。

## 配置、容器与资源

`methods.read_materializer/trimmer/read_qc`，参数按 DNA/RNA 与 SE/PE schema 校验。samtools、fastp、FastQC 使用 digest 固定容器；输入只读、输出 staging 可写。资源通常低到中等，临时磁盘按输入大小估算。

## 状态、错误和 provenance

零 reads 若文件合法但无记录，默认 `INVALID_INPUT`；QC 无异常并非“无结果”。可选 trim 未请求为 `NOT_REQUESTED`，方法不支持为 `SKIPPED_UNSUPPORTED`。记录 lane、read counts、命令参数、工具和原始/trim 阶段。

## 测试

单元：lane、mate、命名；adapter contract：argv/mount/collector；集成：微型 FASTQ/BAM；系统：FASTQ/BAM、SE/PE、单/多 lane、cache。比较 read name/count、mate 和 QC 字段，不比较 gzip 字节。

## 验收与风险

验收 REQ-FUN-004～005、ACC-001。风险包括 BAM 类型误解、旧奇偶位置合并 lane 和 read header 转换；通过 typed lane manifest 与 identity fixture 控制。
