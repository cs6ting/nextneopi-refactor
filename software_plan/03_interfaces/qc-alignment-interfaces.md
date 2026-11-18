# Reads、QC 与 DNA 比对接口

## IF-READ-001 `MaterializeReads` v1.0

- **语义/Request/Result**：把 `RawFastqSet|RawBam` 转为 `CanonicalReadSet`；Request 含 sample/library、inputs、layout，Result 含 R1/R2、lane provenance、counts。
- **前置/不变量**：PE mates 完整且 identity 对齐；BAM 首期按兼容模式转 FASTQ 后重比对；不把 aligned BAM 静默 passthrough。
- **实现**：`fastq_passthrough`、`samtools_bam_to_fastq`；BAM implementation 需 samtools 容器，scatter 可按 library/lane。
- **错误/状态**：`MATE_MISMATCH`、`EMPTY_READS`、`UNSUPPORTED_BAM`；必需 reads 失败。
- **资源/cache/provenance**：I/O/临时盘按输入大小；key 含输入 checksum、layout、实现/镜像；记录 lane/read count。
- **测试/等价**：比较 read names、mate、count 和来源，不比较 gzip 字节。

```yaml
methods: {read_materializer: samtools_bam_to_fastq}
```

## IF-READ-002 `TrimReads` v1.0

- **语义/Request/Result**：对 `CanonicalReadSet` 应用明确 trim policy，输出 `TrimmedReadSet` 与 metrics。
- **实现差异**：`no_trim` 返回受控 passthrough；`fastp` 支持 SE/PE 与参数化过滤。二者结果不要求相等。
- **不变量**：sample/layout/reference-free identity 不变；不能交换 mates。
- **错误/状态**：未配置默认使用显式 recipe method；禁用不是缺失。工具成功但全部 reads 被过滤按 policy 为 `EMPTY` 或失败。
- **资源/cache/provenance**：可按 sample scatter；key 含参数/镜像；记录 before/after counts。
- **测试/等价**：contract 比 counts/metrics/schema；同 fastp 版本比较 read identity 和质量摘要。

```yaml
methods: {read_trimmer: fastp}
```

## IF-QC-001 `AssessReadQC` v1.0

- **语义/Request/Result**：评估 raw/trimmed reads，输出结构化 `ReadQcMetrics` 和 native report。
- **实现**：`fastqc`；未来实现需声明指标集合，不互相冒充。
- **前置/状态**：输入 read set 合法；合法报告无告警仍 `MATERIALIZED`；未请求为 `NOT_REQUESTED`。
- **资源/cache/provenance**：按 sample/stage scatter；记录 stage、工具、镜像和输入。
- **测试/等价**：解析 fixture、空/损坏 zip、模块名称漂移；比较指标而非 HTML。

```yaml
methods: {read_qc: fastqc}
```

## IF-ALN-001 `AlignDNA` v1.0

- **语义/Request/Result**：DNA reads+reference → sorted native aligned BAM；不做 duplicate/BQSR。
- **实现**：`bwa_mem` 首期，未来 `bwa_mem2`；descriptor 声明 SE/PE、secondary/supplementary 和 RG 行为。
- **不变量**：RG/sample 与 manifest 相等；reference dictionary 一致；BAM coordinate-sorted/index policy明确。
- **错误/状态**：`ALIGNER_FAILED`、`READ_GROUP_MISMATCH`、`REFERENCE_MISMATCH`；必需主链无 skip。
- **资源/cache/provenance**：按 sample，可在 interval 前不 scatter；CPU/内存/I/O 模型；key 含 reads/ref/参数/镜像。
- **测试/等价**：比较 mapped reads、flags、coordinates、RG 和摘要容差。

```yaml
methods: {dna_aligner: bwa_mem}
```

## IF-ALN-002 `PostprocessDNAAlignment` v1.0

- **语义/Request/Result**：合并 alignment/uBAM、mark duplicates、修正 NM/MD/UQ，输出 `DuplicateMarkedBam`。
- **实现**：GATK/Picard+sambamba 工具族子图；步骤产物可观测，不允许巨型不可分 shell。
- **不变量**：排序/index/RG/reference 有效；duplicate metric 与 BAM 同源。
- **阶段交接**：`AlignedBam`、`DuplicateMarkedBam`、`RecalibratedBam` 分别保留 BAM、适用索引和来源。HLA 的 DNA 取证使用重复标记并修正标签后的 BAM，Mutect2 等变异调用使用 BQSR BAM。旧 CNVkit 也使用重复标记后的肿瘤/正常 BAM；该输入需在 CNVkit 适配时单独验收。 [HLA 与 CNVkit 输入分流](../../nextNEOpi.nf#L1281) · [Mutect2 输入](../../nextNEOpi.nf#L1805)
- **错误/状态**：缺 companion/index、sample mismatch、collector schema 错误为失败。
- **资源/cache/provenance**：按 sample；记录每个子任务与父工件；所有镜像 digest 进入 key。
- **测试/等价**：read/flag/duplicate/NM/MD/UQ 和 metrics，不比较 BAM 字节。

```yaml
methods: {alignment_postprocessor: gatk_picard_sambamba}
```

## IF-ALN-003 `RecalibrateBaseQuality` v1.0

- **语义/Request/Result**：BAM+known-sites+interval plan → BQSR BAM/report。
- **实现/Scatter**：GATK4 BaseRecalibrator/ApplyBQSR，按 interval scatter、完整 gather。
- **不变量**：全部 shard 同 sample/ref/参数；关键链不允许 partial gather。
- **错误/状态**：`KNOWN_SITE_MISSING`、`SHARD_FAILED`、`INCOMPLETE_SCATTER`、`GATHER_INVALID`。
- **资源/cache/provenance**：每 shard 独立 key；gather key 引用完整 shard checksums；支持资源提升重试。
- **测试/等价**：分片集合、BQSR 摘要和重校准质量分布。

```yaml
methods: {base_recalibrator: gatk4}
execution: {scatter_count: 40}
```

## IF-QC-002 `AssessAlignmentQC` v1.0

- **语义/Request/Result**：BAM+assay intervals → `AlignmentQcMetrics`。
- **实现**：flagstat、alignment summary、mosdepth；WES 可有 HsMetrics，WGS 不伪造。
- **状态**：部分可选 metric 失败时按 recipe 标记 section `FAILED`，不能使 BAM 变成功/失败不明。
- **资源/cache/provenance**：按 sample/metric scatter；记录 assay、target checksum、工具。
- **测试/等价**：coverage 分布、mapped/duplicate counts 与容差；WES/WGS capability 负例。

```yaml
methods: {alignment_qc: gatk_mosdepth}
```
