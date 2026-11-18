# 集成测试计划

## 目标

验证 Python adapter、固定容器、微型 reference、原生工具及 ArtifactStore 的真实边界。测试规模小但不 mock 工具进程；默认断网。

## 测试链

| ID | 链路 | 主要断言 |
|---|---|---|
| TST-INT-READ-001 | BAM→FASTQ→fastp→FastQC | mate/count、metrics、容器离线 |
| TST-INT-ALN-001 | reads→BWA→postprocess | sorted/index、RG、duplicate、reference |
| TST-INT-BQSR-001 | BAM→scatter BQSR→gather | shard 完整、重校准报告、resume |
| TST-INT-M2-001 | matched BAM→Mutect2 | native/filtered/normalized VCF、empty |
| TST-INT-VS-001 | matched BAM→VarScan2 | mpileup/FORMAT/fpfilter normalization |
| TST-INT-CONS-001 | 两 caller→consensus | 核对 allele identity、support provenance 和同位置不同 ALT |
| TST-INT-ANN-001 | VCF→VEP→phase | consequence/protein、顺式/反式/跨块，annotation-only/read-backed 和相位格式 |
| TST-INT-HLA-001 | evidence→OptiType/HLA-HD→resolve | locus/class/resolution/decision trace，Class II 缺失与不支持 |
| TST-INT-NEO-001 | annotated VCF+HLA+purity→pVAC | scatter/gather、全量表和过滤表的候选身份、合法空结果与可选输入状态 |
| TST-INT-CNV-001 | matched BAM→ASCAT/Sequenza | feature flags、segment、purity/fallback |
| TST-INT-RNA-001 | RNA reads→alignment/expression | BAM、TPM、not-measured/0 |
| TST-INT-FUS-SPL-001 | RNA→fusion/splice | event identity、protocol/strand |
| TST-INT-IMM-001 | peptide→BLAST/score | hit、模型版本、失败状态 |
| TST-INT-RPT-001 | typed results→reports | JSON schema、status、parent links |

## 微型 reference

包含少量 contig/interval、FASTA/FAI/dict、最小 known-sites、GTF 和预期变异。无法缩小的工具（如完整 VEP/HLA 模型）采用保存的 native fixture 或单独 nightly image smoke，不能伪造工具成功。

## 环境要求

镜像必须使用 lock 中 digest；网络关闭；HOME clean；reference/input 只读；work/staging 独立。测试结束验证无源代码/reference 写入和无未声明文件。

## 失败注入

缺 index、损坏 shard、超时、模拟 OOM、collector 缺列、只读 work、license 缺失、共享 FS 延迟。断言错误分类、重试决策、原子提交和下游阻断。

## 通过标准

每条链保存 run manifest 和 provenance；结果经 schema/科学不变量校验；重复运行命中缓存；镜像 digest 或参数变化触发重算。
