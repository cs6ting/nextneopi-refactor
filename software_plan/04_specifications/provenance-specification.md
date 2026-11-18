# Provenance 规范

## 目标

记录 run、case、task、attempt、result、artifact、agent 和 decision，使结果可复现、审计和解释。首期使用 JSON/JSONL；可导出 RO-Crate，未来可映射 GA4GH WES。

## 状态边界

- `ResultEnvelope/ResultSlot` 记录五态及 reason。
- 只有 `MATERIALIZED/EMPTY` result 可以引用 committed `ArtifactRef`。
- `ArtifactRef.state` 仅为 `MATERIALIZED/EMPTY`。
- `FAILED/NOT_REQUESTED/SKIPPED_UNSUPPORTED` 记录 result/event，不制造 URI/checksum。

## Run

记录 `run_id`、recipe、core/version/commit、提交时间、提交者别名、resolved config URI/digest、reference digest、plugin lock、resolved site profile fingerprint、backend 和逐 case 状态。

## Task 与 Attempt

Task 记录 capability/contract、implementation、scientific cache key、parents、portable/resource-resolved requests 和依赖。Attempt 记录 backend job/node、容器 digest、脱敏 argv/env/mount、开始/结束、exit/ErrorRecord、重试来源和实际资源。

## Artifact

采用 [`schemas/artifact.schema.json`](schemas/artifact.schema.json)：metadata/data schema、URI、checksum、artifact state、case/sample/role、assay/reference、producer、参数 digest、parents/companions、created_at 和发布位置。

## Result 与 Decision

采用 [`schemas/result-envelope.schema.json`](schemas/result-envelope.schema.json)。复合 capability 为每个子输出记录 `ResultSlot`。Decision 必须覆盖插件候选/排除、consensus allele support、HLA accepted/rejected、purity provider、phase evidence 和 skip 理由。

算法对照报告关联两次 run 或两次边界回放的输入与产物摘要，写明比较范围、实际版本、参考与模型摘要、领域判定、缺失原因及期望差异。候选评分记录模型、任务类型、分数方向、单位或百分位定义和适用范围，分别追踪结合、呈递和免疫原性。复用 NeoFuse 的 RNA 与融合产物时，各结果记录同一执行来源和各自的产物状态。

## Events

`RUN_PLANNED`、`TASK_SUBMITTED`、`TASK_STARTED`、`CACHE_HIT`、`TASK_RETRY`、`ARTIFACT_COMMITTED`、`TASK_EMPTY`、`TASK_FAILED`、`CASE_COMPLETED`、`RUN_COMPLETED`。追加写且含 UTC/correlation IDs。

## 隐私与完整性

敏感 argv/env/license 脱敏；不记录 reads 或完整变异。Run 完成生成 manifest digest；事件不可改写。Cache hit 指向原 artifact/run，同时记录新 run 使用关系。发布 artifact 必须可遍历到输入、reference、config、implementation 和 image；断链阻断发布。
