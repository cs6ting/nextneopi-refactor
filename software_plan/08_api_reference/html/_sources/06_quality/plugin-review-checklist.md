# 插件评审清单

## 身份与能力

- [ ] capability/implementation ID 与版本唯一。
- [ ] contract/core 兼容范围明确。
- [ ] assay、molecule、layout、variant/MHC/features/protocol 支持真实准确。
- [ ] 不支持组合在 planning fail-fast；降级有 policy 和 reason。

## 输入输出

- [ ] Request/Result 和 artifact schema 完整。
- [ ] reference/build/coordinate/sample 不变量校验。
- [ ] native output 与 normalized output 分离。
- [ ] `EMPTY`、`FAILED`、`SKIPPED_UNSUPPORTED` 测试齐全。
- [ ] companion index、scatter/gather 完整性校验。

## 执行与安全

- [ ] `validate` 无副作用；`plan` 确定。
- [ ] argv 执行，无 `shell=True`。
- [ ] container 使用 OCI digest，mount 最小且 input/reference 只读。
- [ ] 正式运行无下载/安装/patch。
- [ ] license、凭据和日志脱敏。
- [ ] 资源默认、minimum、scaling 和 retry 类别合理。

## 缓存与 provenance

- [ ] scientific cache fields 完整。
- [ ] descriptor/container/collector/schema 变化会失效。
- [ ] provenance 含实现、镜像、参数、parents 和 decision。

## 测试与集成

- [ ] 通用 conformance suite 通过。
- [ ] 正常/空/损坏/schema drift native fixtures 齐全。
- [ ] 至少一个固定容器 integration test。
- [ ] 同实现科学等价规则和基线明确。
- [ ] 可选算法候选记录可评测范围、待执行项或实测结果、显式启用及回退方式。若拟修改默认实现，按[科学评测计划](../05_testing/scientific-equivalence-plan.md#首批可选算法评测)提交覆盖、独立对照指标和下游变化。
- [ ] 已接入 recipe、配置示例、Demo 和追踪矩阵。

## 评审

- [ ] 软件负责人批准契约/安全。
- [ ] 生物信息负责人批准科学语义。
- [ ] 平台负责人批准镜像/资源/Slurm（如适用）。
