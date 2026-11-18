# 配置架构

## 单一解析路径

RunConfig 描述科学/流程选择；SiteProfile 描述部署站点。二者分别加载一次，再由 `resolve_configuration(run_config, site_profile, plugin_schemas)` 生成不可变 `ResolvedConfiguration`。`RunConfig.execution.profile` 必须等于 `SiteProfile.profile_id`；不一致 fail-fast。Client 不得再次加载另一份 profile。

## 配置分区

| 分区 | 内容 | 科学 hash |
|---|---|---|
| `workflow` | recipe、assay、可选 section | 是 |
| `input` | manifest、case filter | 输入 checksum |
| `reference` | bundle/capture | 是 |
| `methods` | capability implementation IDs | 是 |
| `policies` | consensus/HLA/purity/TMB/RNA 等 | 是 |
| `implementation_configs` | 按 implementation ID 的严格插件配置 | 按 descriptor 声明 |
| `execution` | backend、profile ID、scatter、retry | 通常否 |
| `output` | publish/格式/provenance | 通常否 |
| 独立 SiteProfile | Slurm、limits、storage、container cache | 否，完整记录 |

## 插件配置扩展

RunConfig 根 Schema 允许 `implementation_configs.<implementation_id>` 对象，但每个对象必须由已解析插件的 `implementation_config_schema` 再验证。未知 implementation ID 或未知字段失败，不是自由字典。

## 合并与覆盖

内置非科学默认 → recipe defaults → run YAML → 受控 CLI scientific override。SiteProfile 不与 RunConfig 深合并，而是在 resolve 阶段只映射 execution/resource。列表默认整体替换。

## 方法与策略

```yaml
methods:
  somatic_callers: [mutect2, varscan2]
policies:
  somatic_consensus:
    implementation: primary_confirmed_v1
    strategy: primary_confirmed
    primary: mutect2
    minimum_callers: 2
implementation_configs:
  mutect2:
    minimum_allele_depth: 5
```

Implementation 不决定跨方法 policy；ASCAT/Sequenza fallback、HLA 仲裁同理。

## 校验顺序

Run Schema → Site Schema → profile ID/backend 一致 → recipe requirements → plugin config Schema → capability/reference/license → resource/site limits → DAG。所有错误聚合；validate/plan 无下载和执行。

## 版本与敏感信息

Run/Site/Plugin config 分别版本化。迁移生成新文件，不原地覆盖。License/token 仅保存 secret reference，resolved provenance 记录类型和指纹，不记录内容。

## Schema

- [RunConfig](../04_specifications/schemas/run-config.schema.json)
- [SiteProfile](../04_specifications/schemas/site-profile.schema.json)
- [PluginDescriptor](../04_specifications/schemas/plugin-descriptor.schema.json)
