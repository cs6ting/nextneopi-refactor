# 配置规范

## CFG-001 `RunConfig` v1

RunConfig 与 SiteProfile 分离加载。RunConfig 包含 `schema_version`、`workflow`、`input`、`reference`、`methods`、`policies`、`implementation_configs`、`execution`、`output`；SiteProfile 另有严格 Schema。运行只消费二者解析得到的不可变 `ResolvedConfiguration`。

## 全功能 methods

Schema 允许首期及后续 implementation 键：reads/QC/alignment/BQSR、somatic callers/SV、germline/VEP/phase/HLA、copy number/CCF、RNA/fusion/splice、三类 neoantigen、self-similarity、immunogenicity scorers、immune repertoire。哪些字段必需由 recipe validator 决定，而不是全局 Schema 强制所有流程启用。

## Policies

支持 variant normalization、somatic consensus、phase fallback、HLA resolution、purity、TMB、RNA、fusion DNA evidence、unsupported protocol 和 report policy。Methods 只选实现，policies 决定跨实现科学语义。

替代试点使用独立的 run 配置和结果目录，在 `methods` 或相应插件配置内声明要比较的实现或模型。优先固定科学策略、参考和公共输入。调用器集合、共识规则、纯度来源、阈值与报告聚合发生变化时，分别记录影响，便于区分模型改动和策略改动。进入默认 recipe 的条件见 [迁移兼容策略](../07_migration/compatibility-strategy.md)。

## Implementation configs

```yaml
implementation_configs:
  fastp:
    qualified_quality_phred: 20
    minimum_length: 30
```

根 Schema 只验证 ID→object；PluginRegistry 根据 descriptor 的 `implementation_config_schema` 严格验证对象。不存在的插件 ID、缺必需项和未知字段失败。

## SiteProfile

```python
run = load_run_config("run.yaml")
site = load_site_profile("slurm-site.yaml")
resolved = resolve_configuration(run, site, registry.plugin_schemas())
```

`run.execution.profile` 与 `site.profile_id`、backend 必须一致。Site profile 不能覆盖 methods/policies/reference。

## 校验

Run/Site Schema → WES capture/caller/HLA/purity cross-field → recipe required capabilities → plugin config → reference/container/license → site resource limits → DAG。全部错误一次汇总，validate 无副作用。

## Hash

Scientific hash 包含 workflow、input checksum、reference、methods、policies、影响科学结果的 implementation config 和 Schema。Site/resources/output 通常不含，但完整记录 provenance；descriptor 的 `scientific_resource_fields` 可声明例外。

## 版本迁移

Run/Site/implementation config 独立版本化。迁移输出新文件和警告，不原地修改；旧 schema 不直接进入 planner。

## 文件

- [RunConfig Schema](schemas/run-config.schema.json)
- [SiteProfile Schema](schemas/site-profile.schema.json)
- [PluginDescriptor Schema](schemas/plugin-descriptor.schema.json)
- [WES canonical](examples/wes-dna-canonical.yaml)
- [Local profile](examples/local-profile.yaml)
- [Slurm profile](examples/slurm-profile.yaml)
