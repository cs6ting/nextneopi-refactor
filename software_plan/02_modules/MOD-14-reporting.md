# MOD-14 报告

## 目的、职责与非职责

组装 QC、科学结果、执行状态和 provenance，提供人类可读与机器可读输出。报告模块不重新计算科学结果，也不因 section 缺失将失败解释为成功。

## 上下游与当前映射

上游为所有模块；用户/平台为下游。当前 MultiQC、sample info、Nextflow timeline/report/trace/DAG 和 `workflow.onComplete` 邮件位于 `nextNEOpi.nf:6900-7188,7410-7482`，辅助脚本包括 `mkSampleInfo.py` 与模板 assets。

本模块为 A–G 提供统一发布视图。首期验收报告覆盖配对 WES DNA 的常规全量和过滤候选。方法旁路对照结果单列，保留算法单元、输入版本、模式与适用范围。 [两层模块地图](module-map.md#第一层计算能力与第二层算法单元) · [首轮验收范围](first-layer-functional-design.md#首轮验收范围)

## 输入输出与不变量

输入各模块 `ResultEnvelope`、run/task/attempt provenance 和 resolved config；输出 `QcReportBundle`、`ScientificReportBundle`、`ExecutionReportBundle`。机器可读 summary 是事实来源，HTML/TSV 是视图；每个 section 显示状态、来源、schema 和最后更新时间。

## 接口与实现

提供 `IF-RPT-001 AssembleQcReport`、`IF-RPT-002 AssembleScientificReport`；执行报告由 provenance projection 生成。MultiQC 可作为 QC renderer adapter；Python reporting 负责稳定 summary。未来邮件/通知是独立外部 adapter，不属于科学报告。

## 配置与资源

配置发布目录、需要的格式、section 和失败容忍。报告不依赖隐式 glob；输入 artifact 由 run manifest 给出。MultiQC 使用固定镜像，Python renderer 使用 core image。

## 状态与 provenance

报告可成功生成并包含失败 section；若机器 summary 本身无法生成，则 case/run 失败。`EMPTY`、`NOT_REQUESTED`、`SKIPPED_UNSUPPORTED`、`FAILED` 必须视觉和 JSON 上可区分。发布保留 artifact IDs 和 checksum。

## 测试

单元测试 section 映射、状态、单位；集成测试 MultiQC/HTML/JSON；系统测试部分 case 失败、空候选、resume、发布幂等；结构快照而非整个 HTML 字节比较。追踪 REQ-FUN-022/030。

## 验收与风险

验收 ACC-001/005/006：任一发布结果可反向追踪，成功 run 不隐藏关键失败。风险是旧流程 `errorStrategy ignore`、optional 输出和完成邮件可能给出误导性“完成”；新报告必须基于 typed states。
