# 功能需求

## 输入与参考

| ID | 需求 | 验收摘要 |
|---|---|---|
| REQ-FUN-001 | 系统必须读取版本化 case manifest，支持 FASTQ/BAM、SE/PE、多 lane、tumor/normal DNA 和可选 RNA。 | 无效配对、角色或 layout 在 plan 前被拒绝。 |
| REQ-FUN-002 | 系统必须解析版本化 `ReferenceBundle`，校验 FASTA、索引、dictionary、annotation 和 assay 资源兼容性。 | 不兼容 build/contig hash fail-fast。 |
| REQ-FUN-003 | 系统必须按 WES/WGS assay 规划 callable intervals 和 scatter shards。 | shard 无缺失、重叠策略明确、可重建。 |

## Reads、QC 与比对

| ID | 需求 | 验收摘要 |
|---|---|---|
| REQ-FUN-004 | 系统必须将 FASTQ 或 BAM 物化为规范 `ReadSet`，并支持 lane 合并。 | read identity、mate 和来源可追踪。 |
| REQ-FUN-005 | 系统必须支持可配置 trim 和 read QC 实现。 | `NoTrim` 与 fastp 可配置切换，FastQC 状态明确。 |
| REQ-FUN-006 | 系统必须完成 DNA alignment、merge、duplicate marking、tag 修正和索引。 | BAM 排序、RG、sample、index 和 provenance 合格。 |
| REQ-FUN-007 | 系统必须支持 BQSR scatter/gather 和 alignment QC。 | 失败 shard 可恢复，gather 完整性受检。 |

## 变异与注释

| ID | 需求 | 验收摘要 |
|---|---|---|
| REQ-FUN-008 | 系统必须支持多个体细胞 small-variant caller 实现。 | Mutect2 首期可用，VarScan2 为 confirming 实现。 |
| REQ-FUN-009 | 系统必须将 caller 原生结果规范化为统一 allele identity，同时保留原生 provenance。 | 同位点不同 ALT、多等位和 indel 正确处理。 |
| REQ-FUN-010 | 系统必须实现 primary-confirmed consensus：保留 primary 记录，至少一个 confirming caller 支持。 | support caller 明确写入结果。 |
| REQ-FUN-011 | 系统必须支持 Manta SV/candidate，并不得把它无差别当作 SNV caller。 | capability selector 阻止错误替换。 |
| REQ-FUN-012 | 系统必须支持正常胚系上下文、VEP consequence 和 phase capability。 | read-backed 与 annotation-only 显式区分。 |

## HLA 与新抗原

| ID | 需求 | 验收摘要 |
|---|---|---|
| REQ-FUN-013 | 系统必须抽取 HLA evidence，并支持 OptiType、HLA-HD 和 custom HLA。 | class、来源、分辨率和证据完整。 |
| REQ-FUN-014 | 系统必须按可审计策略仲裁 DNA/RNA/custom HLA。 | 保留入选、丢弃及原因和 class-II pairing。 |
| REQ-FUN-015 | 系统必须支持 canonical、fusion 和 splice neoantigen capability。 | 首期交付 canonical，后续 recipe 增量接入。 |
| REQ-FUN-016 | 首期 purity 必须由显式 provider 提供；配置值 0.95 必须记录来源。 | 未配置 provider 时 plan 失败。 |
| REQ-FUN-017 | 系统必须聚合 pVAC 结果并保留 variant/transcript/peptide/HLA identity。 | 空候选输出 `EMPTY`，不令下游消失。 |

## 扩展分析

| ID | 需求 | 验收摘要 |
|---|---|---|
| REQ-FUN-018 | 系统必须支持 ASCAT、Sequenza、CNVkit 和 FREEC 的差异化 CNV capability。 | total/allele-specific/purity 能力不可混淆。 |
| REQ-FUN-019 | 系统必须支持显式 purity/ploidy policy、Python CCF 和多口径 TMB。 | denominator、segment assignment 和 fallback 可审计。 |
| REQ-FUN-020 | 系统必须支持 RNA alignment/quantification、RNA HLA、fusion 和 splicing。 | DNA-only、普通 RNA、3' tag 状态不同。 |
| REQ-FUN-021 | 系统必须支持 BLAST、CSiN、GBM、MixMHC2pred 和 MiXCR 的独立可选能力。 | 方法适用范围及 license 预检。 |
| REQ-FUN-022 | 系统必须生成 QC、科学结果和执行/provenance 报告。 | section 可为未请求、不可用、空或失败。 |

## 配置、插件和执行

| ID | 需求 | 验收摘要 |
|---|---|---|
| REQ-FUN-023 | 配置必须分离 recipe、methods、policies、reference、execution 和 site profile。 | Schema 验证且最终生效配置被固化。 |
| REQ-FUN-024 | 插件必须通过 PyPA entry points 发现，并具有版本化 `PluginDescriptor`。 | 新插件无需改核心 registry。 |
| REQ-FUN-025 | 系统必须提供 CLI 与等价 Python SDK。 | CLI 是 SDK 薄封装，错误码一致。 |
| REQ-FUN-026 | 执行必须经 `ExecutionBackend`，支持 local 和 Slurm。 | 领域和 plugin contract 不依赖引擎。 |
| REQ-FUN-027 | 系统必须支持 DAG、并行、scatter/gather、缓存、resume、重试和资源调度。 | 由系统测试覆盖完整状态转换。 |
| REQ-FUN-028 | 系统必须隔离 case 失败并允许其余 case 完成。 | 批次报告包含逐 case 状态。 |
| REQ-FUN-029 | 系统必须提供 `validate`、`plan`、`run`、`resume`、`status`、`plugins`、`schema`、`inspect`。 | 所有命令具备稳定退出码和结构化输出选项。 |
| REQ-FUN-030 | 所有运行必须产生输入、参数、参考、实现、容器、父工件和状态 provenance。 | 任一发布工件可反向追踪。 |