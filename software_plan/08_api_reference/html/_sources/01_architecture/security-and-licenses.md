# 安全与许可证

## 威胁模型

主要边界包括不可信 manifest/路径、第三方镜像与下载、shell 注入、共享 HPC 跨用户访问、license 泄漏、损坏参考/缓存、过度资源请求和日志中的样本信息。系统不是网络服务，但仍处理高价值基因组数据。

## 安全控制

| 风险 | 控制 |
|---|---|
| 命令注入 | 命令以 argv 数组执行，禁止 `shell=True`；ID 和路径经过类型/字符校验。 |
| 路径穿越 | URI 规范化；work/output 根目录边界检查；容器 mount allow-list。 |
| 供应链 | 镜像锁定 digest、SBOM、漏洞扫描、来源和构建记录；禁止 runtime download。 |
| 共享文件权限 | 默认最小权限、umask、case/task 隔离目录；license 只读挂载。 |
| 缓存污染 | checksum、schema、原子提交和 producer identity 校验。 |
| 数据泄漏 | 日志禁止记录 reads/完整变异/密钥；报告发布受目录 ACL 控制。 |
| 拒绝服务 | 配置级 CPU/内存/并发上限，Slurm site profile 限流。 |
| 不可信插件 | 允许插件清单、签名/来源审查、版本 pin 和 contract test。 |

## 许可证模型

`PluginDescriptor` 必须声明：license ID/名称、用途限制、是否可再分发、是否需用户接受、license mount 类型和预检方法。HLA-HD、MiXCR、IEDB 等不得因主项目许可证而假定可自由分发。

缺失许可时：

- 必需 capability：planning 失败，错误 `LICENSE_MISSING`。
- 可选 capability：仅在 recipe policy 明确允许时返回 `SKIPPED_UNSUPPORTED`，并写报告。
- 不得把 license 放入镜像、配置示例、provenance 或日志。

## 数据治理

manifest 应使用去标识化 `case_id/sample_id`。项目不定义临床数据共享政策，部署方必须配置存储、备份、访问和保留策略。公开 benchmark 与真实数据必须分区，测试仓库只允许可再分发的微型/合成数据。

## 安全发布门禁

- 无高危未处置镜像漏洞；例外有时限和负责人。
- 所有镜像、模型、参考有 digest/checksum。
- 第三方许可证清单完整。
- 静态检查确认无 `shell=True`、硬编码密钥和 runtime downloader。
- 离线 Apptainer 系统测试通过。

详细检查见 [`../06_quality/release-readiness-checklist.md`](../06_quality/release-readiness-checklist.md)。