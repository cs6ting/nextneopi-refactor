# Nextflow 退役条件

旧 `nextNEOpi.nf` 仅在以下条件全部满足并签署后停止作为受支持路径。

## 功能覆盖

- [ ] WES/WGS、FASTQ/BAM、SE/PE、多 lane。
- [ ] DNA QC/alignment/BQSR、多 caller/consensus、VEP/phase、HLA、canonical neoantigen。
- [ ] ASCAT/Sequenza/CNVkit/FREEC、purity、CCF/TMB。
- [ ] DNA-only、普通 RNA、3' tag；expression、fusion、splicing。
- [ ] BLAST、CSiN、GBM、MixMHC2pred、MiXCR 和完整报告。
- [ ] 旧有效配置有迁移工具或清晰替代说明。

## 科学验收

- [ ] 同版本工具/reference 的旧/新等价报告覆盖代表性合成、公开和受控数据。
- [ ] VCF/HLA/neoantigen/CNV/CCF/TMB/RNA 等关键层无未解释 regression。
- [ ] 所有批准变更有 ADR、风险、用户影响和领域负责人签署。
- [ ] 空结果、边界和旧疑似缺陷已明确决策。
- [ ] 已采纳的算法替代有独立真值对照、适用范围、候选影响记录和可回退配置。单段回放的比较范围已标明，首轮候选表通过与最终发布表通过分别记录。

## 运行与质量

- [ ] local/真实 Slurm/离线 Apptainer E2E 稳定。
- [ ] cache/resume/retry/资源提升/部分 case 隔离和发布通过。
- [ ] 性能、磁盘、资源和调度压力达到已批准基线。
- [ ] core/plugin/image/reference lock、SBOM、许可和 provenance 完整。
- [ ] 质量门禁、发布清单和安全检查全部通过。

## 运维与采用

- [ ] CLI/SDK/配置/错误/runbook/迁移文档完成。
- [ ] 生产 site profile 与容量由平台负责人签署。
- [ ] 至少两个发布周期双轨运行，无 P0/P1 未解决回归。
- [ ] 用户培训和支持窗口完成，新流程成为默认。
- [ ] 回滚到最后稳定 Nextflow/新版本路径均演练。

## 退役步骤

1. 宣布冻结旧流程，只修严重安全/科学缺陷。
2. 新流程成为默认，旧入口输出明确弃用警告。
3. 保留只读代码、容器/reference lock、基线结果和文档归档。
4. 停止生产支持但保留可审计重现环境。
5. 任何未达条件由风险豁免委员会批准，不能由单个开发者决定。

## 签署

软件架构负责人、生物信息学负责人、Slurm/容器平台负责人和产品/研究负责人共同签署 ACC-006。
