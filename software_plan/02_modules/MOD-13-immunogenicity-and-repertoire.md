# MOD-13 免疫原性与免疫组库

## 目的、职责与非职责

为新抗原候选增加自体蛋白相似性和免疫原性评分，并从 DNA/RNA reads 生成独立 TCR/BCR profile。模块不改变上游候选 identity，不把不同模型分数压成无来源的统一 `score`。

## 上下游与当前映射

上游 MOD-03/07/09/12；下游 MOD-14。G1–G4 分别负责参考蛋白匹配、候选 CCF 回填、病例级 CSiN、候选级免疫原性。G5 的 MiXCR 直接消费 MOD-03 的 DNA/RNA reads，候选结果为空时仍可按配置运行。当前 BLAST、CCF 回填、CSiN、GBM 和 MiXCR 约位于 `nextNEOpi.nf:6446-6910`，参考实现脚本位于 `bin/`。 [G 组算法单元](second-layer-algorithm-inventory.md#g-候选证据免疫原性与免疫受体库) · [CCF 回填](../../nextNEOpi.nf#L6466) · [MiXCR 输入](../../nextNEOpi.nf#L6880)

## 输入输出与不变量

输入 `NeoantigenTable`、可选 CCF/TMB、protein database、models、DNA/RNA `ReadSet`；输出 `SelfSimilarityEvidence`、`ImmunogenicityScoreSet`、`RepertoireProfile`。每个分数含模型、版本、适用 MHC/variant 类型、单位/方向和缺失原因；MiXCR 是独立支线。

此模块内的旧 MixMHC2pred 适配器归类为 F4 的呈递能力，输入还包括 pVAC 生成的序列文件和 MOD-07 提供的原始 HLA-HD DNA 分型。其结果作为独立呈递证据，G4 的免疫原性评估可比较 GBM 与 F5 已产出的 IM 模型结果。 [F 组算法单元](second-layer-algorithm-inventory.md#f-新抗原候选构建与呈递预测) · [MixMHC2pred 输入](../../nextNEOpi.nf#L6280)

## 接口与实现差异

提供 `IF-IMM-001 CheckSelfSimilarity`、`IF-IMM-002 ScoreImmunogenicity`、`IF-REP-001 ProfileImmuneRepertoire`。BLAST、CSiN、GBM、MixMHC2pred 的科学终点和适用范围不同；GBM/R 模型视为第三方容器，自研 CSiN/转换 Python 化。MiXCR 声明 material/assay/license capability。

## 配置、容器、参考和许可

配置启用能力、阈值、数据库/模型 ID 和 MiXCR material。BLAST 库、模型 hash 属 ReferenceBundle；MiXCR/IEDB 许可预检。生产不运行下载或 patch。

## 状态、错误与 provenance

未启用为 `NOT_REQUESTED`；不适用为 `SKIPPED_UNSUPPORTED`；无候选为 `EMPTY`；模型或 license 失败为 `FAILED`。可选评分失败是否影响 case 由 recipe policy 决定，必须出现在报告。

## 测试与验收

覆盖 peptide identity、BLAST 无命中/多命中、模型适用范围、缺列、数值回归、DNA/RNA MiXCR、无 license。验收 REQ-FUN-021、ACC-006。风险是旧 GBM `errorStrategy ignore` 和 runtime install 可能形成静默缺失。
