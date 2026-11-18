# 系统测试计划

## 测试对象

从 CLI/YAML 到发布报告的完整系统，包含配置、插件、backend、Slurm、Apptainer、ArtifactStore、状态和 provenance。

## 核心场景

| ID | 场景与步骤 | 预期结果 |
|---|---|---|
| TST-SYS-001 | `validate/plan` 处理有效及多处无效配置 | 汇总错误；无写入、无 Slurm job；有效计划实现/资源完整 |
| TST-SYS-002 | Local WES FASTQ/BAM canonical E2E | QC→alignment→BQSR→callers→VEP/phase→HLA→pVAC→报告全部可追踪 |
| TST-SYS-003 | 相同配置在 Slurm/Apptainer E2E | 完成且与 local 科学工件等价，job IDs/资源记录完整 |
| TST-SYS-004 | BQSR/caller scatter 一个 shard 首次失败 | 仅失败 shard 重试；gather 等待完整集合 |
| TST-SYS-005 | run 中断后 `resume` | 成功 task 命中 cache，不重复计算；新 attempt 可追踪 |
| TST-SYS-006 | OOM/timeout | 按 policy 提升资源，超过上限清晰失败 |
| TST-SYS-007 | 配置切换 caller/HLA/trim 实现 | recipe 无代码修改；计划和 provenance 反映实现 |
| TST-SYS-008 | Manta+SE、OptiType+required class-II、CCF+total-CN-only | planning fail-fast，无计算提交 |
| TST-SYS-009 | 两 case 中一例必需任务失败 | 另一例完成；run `PARTIAL_FAILED`，逐 case 报告正确 |
| TST-SYS-010 | 空 VCF/HLA/neoantigen、未请求 RNA、可选失败 | 五类 ResultStatus 准确，报告不缺失/伪成功 |
| TST-SYS-011 | DNA-only、普通 RNA、3' tag RNA recipe | capability 分支正确，3' splice 明确 skip |
| TST-SYS-012 | 无 GATK3/HLA-HD/license | phase/HLA/MiXCR 按必需/可选 policy 失败或 skip，有理由 |
| TST-SYS-013 | 完全断网运行 | 所有预备镜像/资源可用；无下载/patch 请求 |
| TST-SYS-014 | 输入/镜像/科学参数分别变化 | 正确 cache invalidation；仅 site 资源变化按规则复用 |
| TST-SYS-015 | 重复 publish、目标冲突、跨文件系统 | 幂等或安全失败；无半成品/覆盖 |
| TST-SYS-016 | 旧/新流程运行同一测试集 | 生成科学等价报告和已批准差异清单 |
| TST-SYS-017 | 数百 case/数千 shard 计划与执行样本 | 调度限流、状态查询、内存和事件完整 |

## 首期 E2E 入口条件

固定微型/合成数据、WES reference、Mutect2+VarScan2、VEP、HLA 至少满足配置所需 MHC class、configured purity=0.95、pVAC 镜像、local profile。Slurm E2E 还需真实 account/partition、共享存储和预拉取镜像。

## 出口条件

所有 P0 场景通过；无未解释 `FAILED` section；输出 schema、checksum 和 provenance 完整；运行日志无密钥；质量门禁通过。失败需保留 run bundle 供复现。