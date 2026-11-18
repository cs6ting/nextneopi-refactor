# ADR-004：项目自有 typed artifact 与内容寻址缓存

- 状态：Accepted
- 关联：REQ-FUN-027、030，NFR-007、010～012、018～020

## 背景

当前流程依赖路径、glob、空文件和 channel 存在性表达数据和状态，容易把失败误判为空结果。执行引擎缓存也不足以充当长期 provenance。

## 决策

所有持久边界使用版本化 `ArtifactRef` 与 `ResultEnvelope`。`ArtifactStore` 负责 staging、schema/checksum、伴随文件、原子提交、cache lookup、publish 和引用保护。cache key 包含 capability/implementation、镜像、父工件、参考、科学参数、policy 和 schema。

状态明确区分 `MATERIALIZED`、`EMPTY`、`NOT_REQUESTED`、`SKIPPED_UNSUPPORTED`、`FAILED`。引擎缓存可以优化执行，但项目 run manifest 与 artifact metadata 是事实来源。

## 后果

增加 metadata 和存储治理成本，但获得跨 backend 恢复、可审计发布和可靠空结果。大型文件不整体哈希时必须使用记录在案的分块/清单策略。

## 验证

损坏文件、缺索引、schema 错误和不完整 shard 无法提交；配置/输入/镜像变化导致 miss；仅资源 profile 变化默认不改变科学 key；并发提交无半成品。