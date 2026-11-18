# 单元测试计划

## 范围

纯 Python 领域、配置、selector、collector transform 和数值算法；禁止启动容器/Slurm或访问网络。领域逻辑分支覆盖率目标不低于 90%，关键 consensus/HLA/CCF/TMB 还需 mutation/property testing。

## 模块用例

| ID | 对象 | 关键用例 |
|---|---|---|
| TST-UNIT-IN-001 | `LoadCaseManifest` | FASTQ/BAM、SE/PE、多 lane、缺 normal、重复 ID、空 HLA、XX/XY/unknown |
| TST-UNIT-REF-001 | interval/reference | BED/VCF 坐标、padding、chr alias、N 区、shard union |
| TST-UNIT-READ-001 | reads models | mate/lane identity、NoTrim、零 reads |
| TST-UNIT-ALN-001 | RG/resources | RG 构造、sample/ref invariants、资源估算 |
| TST-UNIT-VAR-001 | allele normalization | 同位置不同 ALT、多等位、left normalization、indel、排序 |
| TST-UNIT-VAR-002 | consensus | primary、confirming、空/失败 caller、support trace |
| TST-UNIT-ANN-001 | consequence transform | SNV/frameshift、多 transcript、empty |
| TST-UNIT-HLA-001 | HLA resolver | homozygous DNA+RNA、force、custom、class-II pairing、rejected reason |
| TST-UNIT-PUR-001 | purity policy | configured、ASCAT→Sequenza、全部失败、范围错误 |
| TST-UNIT-CCF-001 | CCF | binomial grid、credible set、segment 边界、unmatched 禁止 forward-fill |
| TST-UNIT-TMB-001 | TMB | numerator/denominator、0 mutation、0 denominator、coding/clonal |
| TST-UNIT-RNA-001 | RNA states | not measured vs 0、3' tag capability、strand |
| TST-UNIT-NEO-001 | candidate identity | variant/transcript/peptide/HLA/MHC、聚合去重 |
| TST-UNIT-RPT-001 | reports | 五类 ResultStatus、部分失败、单位和 section |
| TST-UNIT-CFG-001 | config | unknown field、merge、methods/policies、schema migration、hash |
| TST-UNIT-PLG-001 | selector | capability 维度、冲突 ID、优先列表、fail-fast |

## Property tests

- normalized allele 的幂等性与排序无关性；
- consensus 不加入 primary 不含的 allele；
- scatter→gather 保持集合完整；
- manifest serialize/parse round-trip；
- Artifact cache key 对科学字段敏感、对无关资源字段稳定；
- HLA resolver 输出无重复且 decision trace 覆盖所有输入；
- TMB numerator、denominator 非负，0 denominator 永不产生数值。

## 数值容差

CCF/TMB/score 测试使用明确 `abs/rel` 容差并测试阈值两侧；不得用宽松 rounding 掩盖偏差。浮点平台差异与算法差异分别记录。

## Fixture 规则

fixture 最小、可读，附预期科学解释；从生产结果截取时必须脱敏和确认许可。所有 regression fixture 关联缺陷/风险 ID。