# 范围与目标

## 背景

现有 nextNEOpi 是 Nextflow DSL1 单体流程，覆盖 FASTQ/BAM 输入、QC、DNA/RNA 比对、多 caller 体细胞变异、VEP、相位、HLA、CNV/纯度、CCF/TMB、融合/剪接、新抗原、免疫原性和 MiXCR。编排、科学策略、工具安装、状态判断和文件转换混合在 [`nextNEOpi.nf`](../../nextNEOpi.nf) 及多语言脚本中，增加了维护和替换算法的成本。

## 总体目标

- **GOAL-001 可维护性**：按科学职责建立稳定模块与端口，依赖只指向内层。
- **GOAL-002 可替换性**：增加同 capability 的实现时不修改核心 workflow recipe。
- **GOAL-003 可复现性**：输入、配置、参考、实现、容器和产物形成可验证 provenance。
- **GOAL-004 可执行性**：同一科学配置可在本地或 Slurm 运行。
- **GOAL-005 科学连续性**：同方法迁移按明确口径验证科学等价。替代算法以独立真值和同病例下游影响支撑变更。
- **GOAL-006 渐进交付**：每个迭代都有测试和可运行 Demo，不等待“大爆炸”重写完成。

## 首期范围

首期 recipe `wes_dna_canonical` 包含：

1. 配对 WES tumor/normal DNA，FASTQ 或 BAM 输入。
2. manifest、参考和 capture interval 预检。
3. reads materialization、可选 fastp、FastQC。
4. BWA 比对、比对后处理、BQSR 和 alignment QC。
5. Mutect2 primary caller 和至少一个 confirming caller。
6. caller-specific normalization 与 primary-confirmed consensus。
7. VEP 注释、正常胚系上下文及显式 phase capability。
8. DNA HLA：OptiType、HLA-HD 或 custom。
9. 显式 `PurityProvider`；允许配置 `0.95`，禁止静默 fallback。
10. pVACseq canonical 新抗原、聚合和初版科学报告。
11. 本地与 Slurm、缓存/resume、重试、部分 case 隔离和 provenance。

首个科学检查点是常规候选全量表和过滤表。完整首期交付还包含聚合、初版科学报告和运行能力，按 [验收测试矩阵](../05_testing/acceptance-test-matrix.md) 执行。与完整旧流程对照时使用同一套调用器与纯度策略。首期简化 recipe 可通过回放旧共识 VCF 与实际纯度，对候选预测这一段建立等价结论。

## 后续范围

- Manta、Strelka2、Mutect1 等更多 caller。
- WGS assay。
- ASCAT、Sequenza、CNVkit、Control-FREEC。
- Python CCF/TMB。
- RNA expression/HLA、fusion、splicing。
- MixMHC2pred、BLAST、CSiN、GBM。
- MiXCR 和完整报告。

算法替代的试点范围由 [二级算法清单](../02_modules/second-layer-algorithm-inventory.md) 和 [增量迁移路线](../07_migration/incremental-roadmap.md) 维护。候选实现可在相应能力和旧版对照工件就绪后独立评估。

## 范围外

- 重写第三方成熟算法。
- 首期建设 REST API、Web UI、LIMS 或临床决策支持。
- 声称达到临床诊断或监管认证要求。
- 保证旧、新文件字节或目录逐项完全一致。
- 在运行时联网下载、安装或 patch 工具。

## 关键约束

- Python 是自研代码唯一实现语言；第三方容器内部语言不受此限制。
- VCF/BAM/FASTQ 等行业格式继续作为交换工件。
- 领域层不得导入 Pydra、Snakemake、Slurm 或 Apptainer API。
- 方法选择与科学策略必须分开配置。
- `EMPTY`、`NOT_REQUESTED`、`SKIPPED_UNSUPPORTED` 和 `FAILED` 不可互换。
- 插件能力不足必须在 plan 阶段 fail-fast。

## 成功指标

| ID | 指标 |
|---|---|
| ACC-001 | `wes_dna_canonical` 在合成数据上本地端到端通过 |
| ACC-002 | 相同 recipe 在真实 Slurm/Apptainer 环境通过，科学工件等价 |
| ACC-003 | 失败 shard 可重试，resume 不重复成功任务，单 case 失败不阻断其他 case |
| ACC-004 | 新实现可通过 entry point 安装，核心 recipe 无代码修改即可选择 |
| ACC-005 | 每个模块满足质量门禁和需求—测试追踪 |
| ACC-006 | 全功能迁移完成并达到 Nextflow 退役条件 |

## 评审职责

生物信息学负责人评审 caller consensus、HLA、CNV/purity、CCF/TMB 和新抗原语义；平台负责人评审 Slurm、共享存储、Apptainer 和资源 profile；软件负责人评审边界、依赖、API 和质量门禁。
