# `nextneopi.config`

严格、版本化的 RunConfig、SiteProfile、加载与解析 API。

## API Summary

| Symbol | 描述 |
|---|---|
| `RunConfig` | 科学/流程配置 |
| `SiteProfile` | 独立站点/Slurm/存储配置 |
| `ResolvedConfiguration` | 二者与插件 Schema 的不可变解析结果 |
| `MethodsConfig`, `PoliciesConfig` | 全部 capability 的方法与 policy |
| `ImplementationConfigs` | 实现 ID→插件专用严格配置 |
| `load_run_config`, `load_site_profile` | 分别加载一次 |
| `resolve_configuration` | 检查 profile/backend 并解析插件配置 |
| `migrate_config` | 显式 Schema 迁移 |
| `run_config_json_schema`, `site_profile_json_schema` | Draft 2020-12 Schema |

## 核心模型

```python
class RunConfig(BaseModel, frozen=True, extra="forbid"):
    schema_version: Literal[1]
    workflow: WorkflowConfig
    input: InputConfig
    reference: ReferenceConfig
    methods: MethodsConfig
    policies: PoliciesConfig
    implementation_configs: Mapping[ImplementationId, Mapping[str, JsonValue]] = Field(default_factory=dict)
    execution: ExecutionConfig
    output: OutputConfig

class SiteProfile(BaseModel, frozen=True, extra="forbid"):
    schema_version: Literal[1]
    profile_id: SiteProfileId
    backend: Literal["local", "slurm"]
    slurm: SlurmConfig | None
    limits: SiteLimits
    container: SiteContainerConfig
    storage: SiteStorageConfig
    retry: SiteRetryConfig | None = None
    resource_classes: Mapping[str, ResourceClass] = Field(default_factory=dict)

class ResolvedSiteProfile(BaseModel, frozen=True):
    profile: SiteProfile
    fingerprint: Digest

class ResolvedConfiguration(BaseModel, frozen=True):
    run: RunConfig
    site: ResolvedSiteProfile
    implementation_configs: Mapping[ImplementationId, BaseModel]
    scientific_digest: Digest
    site_fingerprint: Digest
```

`MethodsConfig` 覆盖全部 35 科学 IF 的 implementation 选择；字段可选性由 recipe 决定。`PoliciesConfig` 覆盖 normalization/consensus/phase/HLA/purity/TMB/RNA/fusion/splice/report。

## Functions

```python
def load_run_config(
    source: PathLike,
    *,
    overrides: Sequence[ConfigOverride] = (),
) -> RunConfig: ...

def load_site_profile(source: PathLike) -> SiteProfile: ...

def resolve_configuration(
    run: RunConfig,
    site: SiteProfile,
    *,
    implementation_schemas: Mapping[ImplementationId, type[BaseModel]],
) -> ResolvedConfiguration: ...

def migrate_config(
    raw: Mapping[str, JsonValue],
    *,
    kind: Literal["run", "site", "implementation"],
    target_version: int,
) -> ConfigMigrationResult: ...

def run_config_json_schema() -> dict[str, JsonValue]: ...
def site_profile_json_schema() -> dict[str, JsonValue]: ...
```

不再允许 `load_run_config(profile=...)` 与 Client 各加载一份 profile。`create_client(site_profile)` 只接收已经解析的 SiteProfile；`resolve_configuration` 验证 `run.execution.profile == site.profile_id` 和 backend 一致。

## Raises

`ConfigParseError`、`ConfigSchemaError`、`ConfigMigrationError`、`ProfileMismatchError`、`ImplementationConfigError`、`ForbiddenConfigOverrideError`。

## Example

```python
from nextneopi.config import load_run_config, load_site_profile, resolve_configuration

run = load_run_config("run.yaml")
site = load_site_profile("slurm-site.yaml")
resolved = resolve_configuration(
    run,
    site,
    implementation_schemas=registry.plugin_schemas(),
)
assert resolved.run.policies.purity.configured_value == 0.95
```

Schema：[Run](../04_specifications/schemas/run-config.schema.json) · [Site](../04_specifications/schemas/site-profile.schema.json)。