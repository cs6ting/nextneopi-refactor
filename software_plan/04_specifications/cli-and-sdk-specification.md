# CLI 与 Python SDK 规范

## 原则

CLI 是 SDK 薄封装。RunConfig 与 SiteProfile 分别加载一次；SDK submit 始终返回 handle，CLI `--detach` 仅决定命令是否等待。

## CLI

| 命令 | 功能 | 关键参数 |
|---|---|---|
| `nextneopi validate` | Run/Site Schema、capability、reference、license 预检 | `--config --profile --json` |
| `nextneopi plan` | 不可变 DAG、实现、资源、cache 预测 | `--config --profile --out` |
| `nextneopi run` | 创建 run；默认等待，`--detach` 仅控制 CLI | `--config --profile --detach` |
| `nextneopi resume` | 恢复既有 run | `RUN_ID --retry-failed` |
| `nextneopi status` | Run/case/task/attempt | `RUN_ID --watch --json` |
| `nextneopi plugins` | Descriptor/capability/config Schema | `list/show/check` |
| `nextneopi schema` | Run/site/artifact/result/plugin/manifest Schema | Schema name |
| `nextneopi inspect` | Artifact/task/run/provenance | ID |

退出码：0成功、2配置/输入、3 capability/reference/license、4执行失败、5部分 case 失败、6 backend、7内部。

## SDK

```python
run_config = load_run_config("run.yaml")
site_profile = load_site_profile("slurm-site.yaml")
client = NextNeoPiClient.from_profile(site_profile)
report = client.validate(run_config)
report.raise_for_errors()
plan = client.plan(run_config, options=PlanOptions(predict_cache=True))
handle = client.run(plan)
result = handle.wait(timeout=None)
```

Client API 和 `RunHandle/RunResult/CapabilityExecutor` 详见 [`../08_api_reference/nextneopi.application.md`](../08_api_reference/nextneopi.application.md)。

## 错误和状态

配置/planning 使用 ValidationIssue/异常；已提交工具失败形成 FAILED ResultSlot/ResultEnvelope；backend 控制面异常抛 ExecutionError。科学 empty 不抛异常。CLI JSON 与 SDK model 必须规范相等。

## 安全与测试

不回显 token/license；debug 也脱敏。Validate/plan 无下载/写 reference/提交。测试退出码、Ctrl-C/cancel、CLI detach、SDK wait/async_wait/timeout、partial success、resume、profile mismatch 和直接 capability execution。