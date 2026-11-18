# Slurm 与容器测试计划

## 目标

证明同一科学 plan 在真实 Slurm/Apptainer 环境可执行、可恢复、可审计，并且正式运行无网络、无隐式 HOME、无源/reference 写入。

## 环境预检

- `sbatch/sacct/squeue/scancel` 可用，account/partition/QoS 有权限。
- shared work/cache 与 node-local scratch 路径、配额、latency 明确。
- Apptainer 支持 clean environment 和所需 bind。
- 所有镜像预拉取，OCI digest 与 lock 一致。
- reference bundle checksum 通过；license 只读 mount 存在。
- 管理进程允许在 login/interactive/专用调度节点运行。

## 测试场景

| ID | 场景 | 断言 |
|---|---|---|
| TST-SLURM-001 | 单 task 提交/查询/取消 | job ID、状态、日志、取消一致 |
| TST-SLURM-002 | fan-out/fan-in 与 job array | shard identity、并发上限、完整 gather |
| TST-SLURM-003 | heterogeneous small/compute/highmem | 正确 partition、CPU/mem/time 映射 |
| TST-SLURM-004 | node fail/preemption | 分类为 transient、重试到不同 attempt |
| TST-SLURM-005 | OOM/timeout | 资源提升、上限和失败原因正确 |
| TST-SLURM-006 | shared FS latency | latency wait，不误报缺失输出 |
| TST-SLURM-007 | node scratch stage | stage-in/out checksum、清理和失败恢复 |
| TST-SLURM-008 | 数千 task | 提交/状态查询限流，管理进程内存稳定 |
| TST-CONT-001 | 完全断网 E2E | 无下载、DNS/网络依赖 |
| TST-CONT-002 | clean environment | HOME/env 不影响结果，敏感变量不透传 |
| TST-CONT-003 | mount 权限 | input/reference 只读、work 可写、路径无越界 |
| TST-CONT-004 | digest mismatch | 在执行前失败，不使用 mutable tag |
| TST-CONT-005 | license 缺失 | 必需 fail-fast；可选明确 skip |

## Pydra/Snakemake 决策门槛

候选 backend 必须通过上述 P0 场景、local/Slurm 科学等价、resume/cache 和部分 case 隔离。Pydra 任一强制条件无法在限定时间内可靠实现时，记录 ADR 更新并采用 Snakemake backend。

## 产物

每次验证保存 site profile 脱敏版、backend/core/plugin/image lock、Slurm 版本、运行事件、资源效率与已知限制。平台负责人签署方可用于生产。