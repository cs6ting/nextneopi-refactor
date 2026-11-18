# ADR-002：执行引擎由 `ExecutionBackend` 隔离

- 状态：Accepted with validation gate
- 关联：REQ-FUN-026～028，NFR-010～016

## 背景

系统必须支持本地与 Slurm、DAG、scatter/gather、缓存、重试和部分失败。直接依赖某一引擎会重现 Nextflow 锁定。

## 决策

定义 `ExecutionBackend` 端口。Pydra 为首选候选，先在本地和真实 Slurm/Apptainer 上完成 walking-skeleton spike；未满足强制门槛时采用 Snakemake backend。领域、配置和插件仅生成通用 `ExecutionSubgraph/TaskSpec`。

## 选择依据

Pydra 是 Python-first，支持科学任务、类型、split/combine、缓存、容器和 Slurm，但当前 1.0 仍为 alpha。Snakemake 的生信、Slurm、资源、重试、job array 和 Apptainer 支持成熟，但 Snakefile DSL 与 SDK 分层不够自然。Parsl/Prefect/CWL 不作为首选。

## 强制门槛

异构资源映射、数千 task、容器 mount、共享 FS latency、node scratch、cache/resume、动态资源重试、取消、日志、case 隔离全部通过。结果记录在 ADR 状态更新中。

## 后果

新增 backend 只实现端口；科学 cache key 和工件由项目定义，不能依赖引擎私有格式作为唯一事实来源。