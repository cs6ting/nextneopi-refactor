# 质量门禁

## 合并门禁

| 门禁 | 必须条件 | 证据 |
|---|---|---|
| QG-001 Scope | 变更关联 REQ/MOD/IF/TST，边界与非职责未破坏 | PR 追踪表 |
| QG-002 Format/Lint | Python format、lint 零错误 | CI 报告 |
| QG-003 Types | 公共 API strict type-check 通过 | type-check 报告 |
| QG-004 Unit | 相关单元/property 测试通过；领域分支覆盖率 ≥90% | coverage |
| QG-005 Contract | 新/改插件 conformance suite 100% 通过 | contract 报告 |
| QG-006 Integration | 受影响容器链 smoke 通过 | run bundle |
| QG-007 Schema | Pydantic/JSON Schema/example 一致且可解析 | schema check |
| QG-008 Security | 无 `shell=True`、硬编码密钥、runtime download/patch | static/security scan |
| QG-009 Reproducibility | 容器 digest、reference/model checksum 和 provenance 完整 | lock/provenance |
| QG-010 Documentation | 接口、配置、风险和追踪同步，链接有效 | docs check |

## 里程碑门禁

首期还需 local E2E、真实 Slurm/Apptainer E2E、cache/resume、部分 case 失败、离线运行和科学等价报告。全功能发布需 WGS/CNV/RNA/扩展分析、性能基线和退役条件。

设计交付核对边界、测试与验收映射，以及计划中所需的基线工件、独立数据和对照指标。运行验收采用实际工件和差异报告。第一轮以配对 WES DNA 到 pVACseq 常规候选全量表和过滤表为比较范围。调用器或纯度策略不同时，仅对冻结工件之后的回放下结论。

同方法重构用旧行为刻画和回放报告判定科学等价。替代算法先用可选配置旁路，确认接口、支持范围和回退。需要提升为默认方法时，按现有科学评审和变更记录流程提交独立留出集表现、覆盖及下游候选差异。单个方法的性能结果适用于该评测数据、assay 与支持范围。参见[验收矩阵](../05_testing/acceptance-test-matrix.md#首轮科学对照)和[首批可选算法评测](../05_testing/scientific-equivalence-plan.md#首批可选算法评测)。

## 禁止性门禁

以下任一项直接阻断：静默 fallback purity、失败伪装 empty、未知字段被忽略、mutable 生产镜像 tag、输入/reference 可写、缺失 license 预检、未解释科学回归、插件未接 recipe、跨层反向依赖。

## 豁免

豁免必须包含风险 ID、范围、理由、替代控制、负责人和到期日；P0 科学正确性、数据完整性、密钥泄漏和未固定容器不得长期豁免。

## 度量

按 release 统计 escaped defect、flaky tests、coverage、contract 覆盖、E2E 成功率、未解释科学差异、cache correctness 和高危漏洞。指标用于改进，不通过删除测试或放宽容差优化。
