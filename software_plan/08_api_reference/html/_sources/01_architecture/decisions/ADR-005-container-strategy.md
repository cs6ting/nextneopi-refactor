# ADR-005：第三方工具采用 digest 固定的离线容器

- 状态：Accepted
- 关联：NFR-007～009、023～024

## 背景

现有流程存在运行时下载、patch、marker 文件和大一统环境，影响离线集群、并发、供应链和版本复现。部分工具还具有独立许可条件。

## 决策

第三方工具由 Python adapter 规划并在 Apptainer 中运行。生产身份使用 OCI digest；镜像在 run 前构建、扫描、预拉取和 smoke test。优先 BioContainers/Bioconda，特殊/受限工具使用受控镜像。mount、环境和 license 均由 typed descriptor 声明。

禁止运行时下载、安装、patch、mutable tag、`curl -k`、写入源码仓库以及在镜像中嵌入 license。输入/reference 只读，work 可写，默认 clean environment。

## 后果

部署前准备增加，但运行稳定、可审计、适合 Slurm 离线节点。镜像升级必须产生新 digest 和科学等价回归。

## 验证

断网环境完成 E2E；镜像 digest 与 descriptor 一致；缺 license 在 planning 失败或按可选 policy 跳过；SBOM、漏洞和许可检查纳入发布门禁。