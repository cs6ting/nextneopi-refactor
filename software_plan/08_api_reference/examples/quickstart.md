# Python API 快速开始

> 目标 API；当前仓库尚未实现可导入 package。该示例是未来 doc-test/type-check 基线。

## 1. 加载唯一配置来源

```python
import nextneopi

run_config = nextneopi.load_run_config("run.yaml")
site_profile = nextneopi.load_site_profile("slurm-site.yaml")
client = nextneopi.create_client(site_profile=site_profile)
```

RunConfig 只引用 `execution.profile` ID；SiteProfile 只加载一次。二者 ID/backend 不一致会在 validate 中返回 `PROFILE_MISMATCH`。

## 2. Validate 与 Plan

```python
from nextneopi.application import PlanOptions

report = client.validate(run_config)
for issue in report.issues:
    print(issue.severity, issue.code, issue.path, issue.message)
report.raise_for_errors()

plan = client.plan(
    run_config,
    options=PlanOptions(
        predict_cache=True,
        include_optional_nodes=True,
        explain_selection=True,
    ),
)
print(plan.run_id, len(plan.tasks))
```

Validate/plan 不下载、不提交任务。Plan 可审查 capability、implementation、资源、镜像、inputs 和 cache prediction。

## 3. 执行、等待和查询

```python
handle = client.run(plan)
print(handle.run_id)

status = handle.status()
for case in status.cases:
    print(case.case_id, case.state)

result = handle.wait(timeout=None)
for case in result.cases:
    print(case.case_id, case.state, case.error)
print("failed:", [case.case_id for case in result.failed_cases])
```

SDK 始终返回 handle；CLI 的 `--detach` 只控制 CLI 是否调用 `wait()`。`wait(timeout)` 超时不取消 run。

异步：

```python
result = await handle.async_wait(timeout=3600)
```

## 4. Resume

```python
from nextneopi.models import ResumePolicy

resumed = client.resume(
    handle.run_id,
    ResumePolicy(retry_failed=True, reuse_verified_cache=True),
)
resumed_result = resumed.wait()
```

只有 checksum/schema/producer 有效的 committed ArtifactRef 可复用。

## 5. Inspect

```python
report_slot = result.cases[0].scientific_report
report_slot.raise_for_failure()
assert report_slot.value is not None

inspection = client.inspect(report_slot.value.artifact_id)
print(inspection.provenance.parents)
print(inspection.provenance.container_digests)
```

## 6. 执行单个 Capability

```python
from nextneopi.capabilities.variants import BuildConsensusRequest

request = BuildConsensusRequest(
    case_id="case-001",
    callsets=(mutect2_callset, varscan_callset),
    policy=consensus_policy,
)
result = client.capabilities.execute("IF-VAR-004", request)
result.raise_for_failure()
```

`CapabilityExecutor.execute()` 等价于 submit+wait，仍经过 selector/backend/store/provenance。

## 7. CLI

```bash
nextneopi validate --config run.yaml --profile slurm-site.yaml
nextneopi plan --config run.yaml --profile slurm-site.yaml --out plan.json
nextneopi run --config run.yaml --profile slurm-site.yaml --detach
nextneopi status RUN_ID --json
nextneopi resume RUN_ID --retry-failed
nextneopi inspect ARTIFACT_ID
```

CLI 是 SDK 薄封装。`--detach` 是 CLI 生命周期选项，不进入 SDK/backend scientific API。