# 资源与容器模型

## 三层资源对象

1. `ResourceModel`：插件 descriptor 的可移植默认/最小值与 scaling 公式。
2. `ResourceRequest`：planner 对具体 Task 计算出的可移植请求。
3. `ResolvedResourceRequest`：site profile 映射 partition/account/QoS/上限后的执行请求。

```python
class ResourceRequest(BaseModel, frozen=True):
    cpus: int
    memory_mb: int
    runtime_minutes: int
    scratch_mb: int = 0
    gpus: int = 0
    nodes: int = 1
    tasks: int = 1
    partition: str | None = None
    account: str | None = None
    qos: str | None = None
    constraints: tuple[str, ...] = ()
```

`ResourceModel` 与 PluginDescriptor Schema 使用相同 core 字段，并额外声明 `scaling_model` 和 `scientific_resource_fields`。只有后者列出的字段进入 scientific cache key。

## 合并顺序

Implementation estimate → recipe resource class → site mapping → 受控 run override → retry multiplier。Site 不能降低 implementation minimum，也不能覆盖科学参数。

## ContainerSpec

```python
class ContainerSpec(BaseModel, frozen=True):
    oci: str
    digest: str
    runtime: Literal["apptainer"]
    entrypoint: tuple[str, ...]
    environment_allowlist: tuple[str, ...] = ()
```

纯 Python implementation 的 descriptor `container=None`；第三方 ToolAdapter 必须有 ContainerSpec。具体 host/container mount 由 `ContainerTaskSpec` 声明，输入/reference 只读，staging 可写。

## SiteProfile

站点配置独立于 RunConfig，使用 [`schemas/site-profile.schema.json`](schemas/site-profile.schema.json)。它定义 backend、Slurm、limits、container、storage、retry 和 resource classes；解析得到不可变 `ResolvedSiteProfile` 与 fingerprint。

## Slurm 映射

`cpus→--cpus-per-task`、`memory_mb→--mem`、`runtime_minutes→--time`；partition/account/QoS/constraint 仅来自 resolved site。禁止同时生成冲突的 `--mem`/`--mem-per-cpu`。

## Retry 与度量

`RESOURCE_EXHAUSTED` 可提升 memory/runtime，最多 `max_attempts`；CPU 仅在工具声明可扩展时提升。每 attempt 记录请求/实际 CPU、RSS、时间、scratch。Contract test 检查最小值、上限、映射和 cache 字段。