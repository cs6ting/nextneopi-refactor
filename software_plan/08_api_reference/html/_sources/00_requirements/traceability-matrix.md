# 需求追踪矩阵

本矩阵建立“需求 → ADR → 模块 → 接口 → 配置 → 测试 → 验收”链路。详细测试见 [`../05_testing/acceptance-test-matrix.md`](../05_testing/acceptance-test-matrix.md)。任何一列缺失均视为设计债务。

| 需求 | ADR | 模块 | 接口 | 配置 | 核心测试 | 验收 |
|---|---|---|---|---|---|---|
| REQ-FUN-001 | ADR-001 | MOD-01 | IF-IN-001 | CFG-input | TST-UNIT-IN-001、TST-SYS-001 | ACC-001 |
| REQ-FUN-002～003 | ADR-004 | MOD-02 | IF-REF-001～002 | CFG-reference | TST-CONTRACT-REF-001、TST-SYS-001 | ACC-001 |
| REQ-FUN-004～005 | ADR-005 | MOD-03 | IF-READ-001～002、IF-QC-001 | CFG-methods | TST-INT-READ-001、TST-SYS-002 | ACC-001 |
| REQ-FUN-006～007 | ADR-002、005 | MOD-04 | IF-ALN-001～003、IF-QC-002 | CFG-methods/execution | TST-INT-ALN-001、TST-SYS-004 | ACC-001～003 |
| REQ-FUN-008～011 | ADR-003～005 | MOD-05 | IF-VAR-001～004 | CFG-methods/policies | TST-CONTRACT-VAR-001、TST-SCI-VAR-001 | ACC-001、004 |
| REQ-FUN-012 | ADR-003、005 | MOD-06 | IF-VAR-005、IF-ANN-001、IF-PHS-001 | CFG-methods/policies | TST-INT-ANN-001、TST-SCI-PHS-001 | ACC-001 |
| REQ-FUN-013～014 | ADR-003、005 | MOD-07 | IF-HLA-001～003 | CFG-methods/policies | TST-UNIT-HLA-001、TST-SCI-HLA-001 | ACC-001、004 |
| REQ-FUN-016 | ADR-001、003 | MOD-08 | IF-PUR-001 | CFG-policies.purity | TST-UNIT-PUR-001、TST-SYS-001 | ACC-001 |
| REQ-FUN-015、017 | ADR-003～005 | MOD-12 | IF-NEO-001～003 | CFG-methods/policies | TST-INT-NEO-001、TST-SCI-NEO-001 | ACC-001、006 |
| REQ-FUN-018 | ADR-003、005 | MOD-08 | IF-CNV-001、IF-PUR-001 | CFG-methods/policies | TST-CONTRACT-CNV-001、TST-SCI-CNV-001 | ACC-006 |
| REQ-FUN-019 | ADR-001、004 | MOD-09 | IF-CCF-001、IF-TMB-001 | CFG-policies | TST-UNIT-CCF-001、TST-SCI-TMB-001 | ACC-006 |
| REQ-FUN-020 | ADR-003、005 | MOD-10～11 | IF-RNA-001、IF-FUS-001、IF-SPL-001 | CFG-workflow/methods | TST-INT-RNA-001、TST-SYS-011 | ACC-006 |
| REQ-FUN-021 | ADR-003、005 | MOD-13 | IF-IMM-001～002、IF-REP-001 | CFG-methods | TST-CONTRACT-IMM-001、TST-SYS-012 | ACC-006 |
| REQ-FUN-022 | ADR-004 | MOD-14 | IF-RPT-001～002 | CFG-output | TST-INT-RPT-001、TST-SYS-010 | ACC-001、006 |
| REQ-FUN-023 | ADR-001 | MOD-01～14 | 配置 Schema | CFG-* | TST-UNIT-CFG-001、TST-SYS-001 | ACC-005 |
| REQ-FUN-024 | ADR-003 | 全部插件模块 | IF-PLG-001 | CFG-methods | TST-CONTRACT-PLG-001、TST-SYS-007 | ACC-004 |
| REQ-FUN-025、029 | ADR-001 | interfaces | SDK/CLI | CFG-* | TST-INT-CLI-001、TST-SYS-001 | ACC-005 |
| REQ-FUN-026～028 | ADR-002、004 | infrastructure | IF-PORT-001～002 | CFG-execution/site | TST-SYS-003～009 | ACC-002～003 |
| REQ-FUN-030 | ADR-004～005 | MOD-14 | IF-PORT-002、IF-RPT-002 | CFG-provenance | TST-SYS-010 | ACC-005 |
| NFR-001～006 | ADR-001、003 | 全部 | 全部公共接口 | CFG-schema | TST-UNIT-*、TST-CONTRACT-* | ACC-004～005 |
| NFR-007～012 | ADR-002、004～005 | infrastructure | IF-PORT-001～002 | CFG-execution | TST-SYS-003～010 | ACC-002～003 |
| NFR-013～017 | ADR-002 | infrastructure | IF-PORT-001 | CFG-site/resource | TST-PERF-001～003 | ACC-002 |
| NFR-018～026 | ADR-003～005 | 全部 | artifact/plugin/report | CFG-* | TST-SCI-*、发布门禁 | ACC-005～006 |

## 变更规则

1. 新需求必须先分配 ID，并补齐模块、接口和测试。
2. 新 implementation 不新增功能需求时，至少补充 capability、contract test 和配置追踪。
3. 科学 policy 变化必须新增或修订 `TST-SCI-*`。
4. 删除旧行为前必须在 [`../07_migration/compatibility-strategy.md`](../07_migration/compatibility-strategy.md) 记录决策。

## 算法替代试点追踪

二级算法编号用于定位分析条目。现有需求与接口编号继续用于实现和测试。方法性能对照的执行要求见 [科学等价测试计划](../05_testing/scientific-equivalence-plan.md)。

| 分析条目 | 现有需求与能力 | 基线测试 | 候选评估 |
|---|---|---|---|
| A2 DNA 比对 | REQ-FUN-006、MOD-04、IF-ALN-001 | TST-INT-ALN-001、TST-SCI-ALN-001 | BWA-MEM2 的比对一致性、下游 VCF/候选影响和资源开销 |
| C1 DNA HLA 分型 | REQ-FUN-013～014、MOD-07、IF-HLA-001～003 | TST-UNIT-HLA-001、TST-SCI-HLA-001 | SpecHLA 的位点级分型真值、无结果率和实际可评分覆盖 |
| F3/F4 结合与呈递 | REQ-FUN-015、017，MOD-12、IF-NEO-001 | TST-INT-NEO-001、TST-SCI-NEO-001 | NetMHCpan 4.2 / NetMHCIIpan 4.3 分别对照结合实验和免疫肽组数据 |
