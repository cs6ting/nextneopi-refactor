# 验收测试矩阵

## 首轮科学对照

首轮对照终点是**配对 WES DNA 到 pVACseq 常规候选全量表和过滤表**。用现有 TST-SCI-NEO-001 比较两张表的候选身份、重复计数、过滤去留及相关分数。与 TST-SYS-016 的旧/新对照共用证据，报告里标明实际比较从配对 reads/BAM 还是共识 VCF、实际纯度等已冻结的边界开始。旧最终发布表的 CCF、参考蛋白匹配、汇总和路径随相关阶段验证。

第一份验收记录包含旧版边界工件、版本锁、比较范围与结果。设计阶段记录待执行项。ACC-001～005 仍用于首期发布，A2、C1、F3/F4 的候选算法评测分别见[科学等价测试计划](scientific-equivalence-plan.md#首批可选算法评测)。

## 首期 `wes_dna_canonical`

| 验收 | 需求/模块/接口 | 必须通过 | 通过条件 |
|---|---|---|---|
| ACC-001 Local E2E | REQ-FUN-001～017、022～030；MOD-01～08/12/14 | TST-SYS-001/002/007/008/010/013～015 | FASTQ/BAM WES 闭环完成；所有必需工件、状态和 provenance 合法 |
| ACC-002 Slurm E2E | REQ-FUN-026～027；NFR-014～017 | TST-SYS-003、TST-SLURM-001～008、TST-CONT-001～004 | 真实 Slurm/Apptainer 通过，与 local 科学等价 |
| ACC-003 恢复/隔离 | REQ-FUN-027～028；NFR-010～012 | TST-SYS-004～006/009/014 | shard 重试、resume、资源提升、case 隔离符合策略 |
| ACC-004 插件替换 | REQ-FUN-008/013/024 | TST-CONTRACT-PLG-001、TST-SYS-007/008 | 插件无核心修改注册；不兼容 fail-fast |
| ACC-005 质量/审计 | REQ-FUN-022/025/029/030；NFR-018～026 | 全部 P0 unit/contract、TST-SYS-010/013/015 | 覆盖/类型/Schema/安全/许可/追踪门禁通过 |

## 后续全功能

| 验收 | 需求/模块 | 必须通过 | 通过条件 |
|---|---|---|---|
| ACC-006 全能力与退役 | REQ-FUN-011/015/018～022；MOD-08～14 | TST-SYS-011/012/016/017、全部 TST-SCI、关键 TST-PERF | WGS/CNV/CCF/TMB/RNA/fusion/splice/score/MiXCR 配方完成；未解释差异为零；满足退役清单 |

## 接口最低测试映射

| 接口组 | Unit | Contract | Integration | Scientific |
|---|---|---|---|---|
| IF-IN/REF | TST-UNIT-IN/REF-001 | TST-CONTRACT-REF-001 | TST-INT-READ-001 前置 | 配置/interval identity |
| IF-READ/QC/ALN | TST-UNIT-READ/ALN-001 | TST-CONTRACT-READ/ALN-001 | TST-INT-READ/ALN/BQSR-001 | TST-SCI-READ/ALN-001 |
| IF-VAR/ANN/PHS | TST-UNIT-VAR/ANN-001 | TST-CONTRACT-VAR/CONS/ANN-001 | TST-INT-M2/VS/CONS/ANN-001 | TST-SCI-VAR/ANN-001 |
| IF-HLA | TST-UNIT-HLA-001 | TST-CONTRACT-HLA-001 | TST-INT-HLA-001 | TST-SCI-HLA-001 |
| IF-CNV/PUR/CCF/TMB | TST-UNIT-PUR/CCF/TMB-001 | TST-CONTRACT-CNV/CCF-001 | TST-INT-CNV-001 | TST-SCI-CNV/CCF/TMB-001 |
| IF-RNA/FUS/SPL | TST-UNIT-RNA-001 | TST-CONTRACT-RNA-001 | TST-INT-RNA/FUS-SPL-001 | TST-SCI-RNA-001 |
| IF-NEO/IMM/REP | TST-UNIT-NEO-001 | TST-CONTRACT-NEO-001 | TST-INT-NEO/IMM-001 | TST-SCI-NEO/REP-001 |
| IF-RPT | TST-UNIT-RPT-001 | TST-CONTRACT-RPT-001 | TST-INT-RPT-001 | TST-SCI-RPT-001 |
| IF-PORT | TST-UNIT-CFG/PLG-001 | TST-CONTRACT-BE/STORE-001 | runtime smoke | TST-SYS-003～006 |

## 签署

科学接口由生物信息学负责人签署；Slurm/容器/性能由平台负责人签署；API/质量由软件负责人签署。任何 waived test 必须有风险 ID、负责人、到期日和替代控制。
