# 发布就绪清单

## 功能与科学

- [ ] release 范围的 recipe 全部可运行。
- [ ] 必需 capability 均有至少一个生产实现。
- [ ] local/Slurm 科学结果等价。
- [ ] 旧/新等价报告无未解释 regression。
- [ ] 所有批准差异有 ADR、迁移说明和领域签署。

## 测试与质量

- [ ] format/lint/strict type/unit/contract/integration/system 全通过。
- [ ] 领域分支覆盖率门槛达到。
- [ ] cache/resume/retry/partial-case/empty/unsupported 场景通过。
- [ ] 性能/资源基线无未解释 >门槛回归。
- [ ] flaky/waived test 有风险、负责人和期限。

## 供应链与安全

- [ ] Python dependency lock、plugin lock、image lock、reference lock 完整。
- [ ] 生产镜像均为 digest，SBOM/漏洞/许可扫描完成。
- [ ] 离线 Apptainer E2E 通过，无 runtime download/patch。
- [ ] 无高危未处置漏洞、硬编码密钥、`shell=True`。
- [ ] license/凭据预检和 mount 验证通过。

## 数据与运维

- [ ] ArtifactStore 原子提交、publish、retain/GC 已验证。
- [ ] run/task/artifact provenance 无断链。
- [ ] Slurm profile 经实际集群负责人签署。
- [ ] 监控、日志、容量、备份、保留和故障 runbook 完整。
- [ ] 配置/Schema/CLI/SDK 文档与 release 一致。

## 发布和回滚

- [ ] 版本、changelog、升级/配置迁移说明完成。
- [ ] Demo 和已知限制已发布。
- [ ] 回滚可恢复上一 core/plugin/image/reference lock。
- [ ] 迁移期未提前删除旧 Nextflow 基线。
- [ ] 达到 [`../07_migration/nextflow-retirement-criteria.md`](../07_migration/nextflow-retirement-criteria.md) 后才允许退役旧流程。