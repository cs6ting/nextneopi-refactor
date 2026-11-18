# 兼容与科学连续性策略

## 兼容目标

目标是科学结果等价和可解释迁移，不保证目录、排序、压缩、时间戳或文件字节一致。旧流程在迁移期为 baseline，不是所有疑似行为的永久规范。

## 兼容层次

| 层次 | 要求 |
|---|---|
| 输入 | 继续支持 legacy FASTQ/BAM CSV；边界转换为新 manifest，可报告 warning |
| 科学参数 | 建立旧 `conf`→新 methods/policies/reference 映射，记录无法一一映射项 |
| 工具 | 同一版本/镜像/reference 下先验证 adapter 等价 |
| 工件 | BAM/VCF/TSV 保持可交换；内部 typed metadata 新增 |
| 结果 | 按 scientific equivalence plan 比较 identity、字段和容差 |
| 输出布局 | 可提供 legacy renderer，但规范 run manifest 是事实来源 |

## 双轨运行

每个纵向阶段：同一测试 manifest 分别运行旧 Nextflow 与新 recipe；固定工具/reference；生成结构化比较报告；未解释差异阻断阶段出口。真实数据不可用时先用合成，后续追加公开/受控 cohort。

## 候选算法的采纳

同方法迁移先用同工具、模型、参考和规则回放。首期 recipe 若使用较少调用器或配置纯度，可在注释边界回放时注入旧共识 VCF，或直接将旧 VEP 注释 VCF、实际纯度、HLA 和定相上下文用于候选预测。比较报告从被回放的交接点起标明范围。完整旧版对照使用相同调用器集合、纯度策略和所声明的输出阶段。

替代算法用独立 run 或边界回放评估。记录输入、模型与镜像、参考、支持范围、独立真值、指标和旧结果。对于结合、呈递和免疫原性，分别比较对应的实验终点，共同可评分集合之外同时报告覆盖和未评分原因。更改共识、阈值、参考或聚合策略时，分别说明它们造成的候选变化。

采纳前复核接口兼容性、方法对照结果和下游影响。通过项目现有的科学与发布评审后，在 recipe 中明确设置新实现和版本，并保留可恢复的旧运行锁。 [候选与验收](../02_modules/second-layer-algorithm-inventory.md#替换实验与验收) · [首批试点](incremental-roadmap.md#首批算法替代试点)

## 疑似旧缺陷

先建立 characterization test，再分类：

1. 保持兼容；
2. 经科学评审修正并记录 `APPROVED_SCIENTIFIC_CHANGE`；
3. 无法比较，标记 `NOT_COMPARABLE`。

不得为了通过等价复制输出 glob 拼写、错误 key、silent fallback、坐标或 forward-fill 缺陷。

## Schema 与 API

所有 contract/schema 有版本。破坏性变更升 major并提供迁移工具；CLI/SDK 废弃至少一个 minor release。配置迁移生成新文件，不原地覆盖。

## 回滚

每次运行锁定 core/plugin/image/reference/config。发现回归可回滚到上一 lock；新旧结果目录隔离。Nextflow 在退役前继续提供已知稳定路径。

## 签署

格式差异由软件负责人；算法/过滤/候选差异由生物信息负责人；运行/性能差异由平台负责人签署。
