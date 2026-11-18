# 性能与可靠性测试计划

## 目标

建立可比较的吞吐、延迟、资源和扩展基线，发现调度、I/O、cache 和工具参数回归。性能测试不得改变科学参数来“优化”结果。

## 场景

| ID | 场景 | 主要指标 |
|---|---|---|
| TST-PERF-001 | 单 case WES DNA local | wall time、CPU、max RSS、scratch、I/O |
| TST-PERF-002 | 单 case WES DNA Slurm | queue wait、run time、效率、job 数 |
| TST-PERF-003 | 10/100/500 case plan | planning 内存/时间、DAG/task 数 |
| TST-PERF-004 | 1000/10000 shard 调度 | submit/status rate、backend 内存、事件吞吐 |
| TST-PERF-005 | cold/warm cache | hit ratio、节省时间、lookup 开销 |
| TST-PERF-006 | shared vs node scratch | stage time、I/O 吞吐、总时间 |
| TST-PERF-007 | WGS/RNA/highmem | resource estimate 准确性、OOM/timeout 率 |
| TST-PERF-008 | 部分失败/重试 | 无效重算量、恢复时间 |

## 基线和门槛

首个稳定版本记录硬件、Slurm、存储、镜像、reference 和数据版本，形成相对基线。默认回归门槛建议：同环境关键 stage wall time 或 max RSS 增长 >20% 需分析；planning 在目标最大 DAG 下不得 OOM；状态查询不得超过 site 限流。门槛在实测后由平台负责人批准。

## 测量方法

以 backend/Slurm 记录为主，容器内补充工具 metrics；分离 queue wait 与 execution；重复至少三次并报告中位数/离散度。冷/热缓存分开，禁止混合。

## 可靠性耐久

长时间批次、管理进程重启、Slurm 短暂不可用、磁盘接近上限、节点失败、并发 publish 和日志增长。断言无状态丢失、无半工件、resume 可用。

## 结果

输出机器可读 benchmark JSON 和趋势图；性能退化不自动等同科学失败，但超门槛阻断发布直至解释或批准。