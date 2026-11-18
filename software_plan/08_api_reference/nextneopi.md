# `nextneopi`

顶层 namespace 只 re-export 高频稳定 API；高级接口从明确子模块导入。

## API Summary

| Symbol | 描述 | 稳定性 |
|---|---|---|
| `load_run_config`, `load_site_profile` | 分别加载 Run/Site 配置 | Beta |
| `create_client` | 使用唯一 SiteProfile 创建 Client | Beta |
| `validate`, `plan`, `run` | 显式 Client 的便捷函数 | Beta |
| `NextNeoPiClient`, `RunConfig`, `SiteProfile` | 核心类型 | Beta |
| `ArtifactRef`, `ResultSlot`, `ResultEnvelope` | 工件与五态结果 | Beta |

## 配置与 Client

```python
def load_run_config(
    source: str | os.PathLike[str],
    *,
    overrides: Sequence[ConfigOverride] = (),
) -> RunConfig: ...

def load_site_profile(source: str | os.PathLike[str]) -> SiteProfile: ...

def create_client(
    *,
    site_profile: SiteProfile | str | os.PathLike[str],
    plugin_policy: PluginPolicy | None = None,
) -> NextNeoPiClient: ...
```

SiteProfile 只加载一次；RunConfig 的 profile ID/backend 必须与 Client 一致。

## Convenience functions

```python
def validate(config: RunConfig, *, client: NextNeoPiClient) -> ValidationReport: ...
def plan(config: RunConfig, *, client: NextNeoPiClient, options: PlanOptions | None = None) -> ExecutionPlan: ...
def run(config: RunConfig, *, client: NextNeoPiClient, options: PlanOptions | None = None) -> RunHandle: ...
```

`run()` 完成 validate/plan 后提交并立即返回 `RunHandle`。SDK 没有 `detach`；CLI `--detach` 仅决定命令进程是否等待。

## Example

```python
import nextneopi

config = nextneopi.load_run_config("run.yaml")
site = nextneopi.load_site_profile("slurm-site.yaml")
client = nextneopi.create_client(site_profile=site)

report = nextneopi.validate(config, client=client)
report.raise_for_errors()
handle = nextneopi.run(config, client=client)
result = handle.wait(timeout=None)
print(result.state, result.failed_cases)
```

## Exceptions

配置/预检错误见 `ValidationReport`；`plan` 可抛 `ValidationFailedError/PluginResolutionError/PlanInvariantError`；backend 控制面抛 `ExecutionError`。已提交工具失败通过 case/task `ResultEnvelope(FAILED)` 和 RunResult 汇总。