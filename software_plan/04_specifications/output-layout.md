# 输出布局

## 原则

用户输出是 ArtifactStore 发布视图，不是内部 cache/work 目录。布局稳定但不作为工件身份；机器可读 manifest 是权威索引。

## 建议布局

```text
results/<run_id>/
├── run.json
├── resolved-config.yaml
├── provenance/
│   ├── events.jsonl
│   ├── tasks.json
│   └── artifacts.json
├── cases/<case_id>/
│   ├── case.json
│   ├── qc/
│   ├── alignment/
│   ├── variants/
│   ├── hla/
│   ├── cnv/
│   ├── rna/
│   ├── neoantigens/
│   ├── repertoire/
│   └── reports/
├── cohort/
└── execution/
    ├── summary.json
    └── logs-index.json
```

每个目录只发布 recipe 请求的工件；未请求/不支持/失败 section 的状态仍写入 `case.json` 和报告，但不制造假结果文件。

## 文件命名

使用安全的 `case_id/sample_id`、artifact kind 和 schema version；不在文件名编码全部参数。原生工具文件保存在可选 `native/` 子目录并由 manifest 引用。伴随 BAM/VCF index 同工件发布。

## 原子与幂等发布

先发布到 staging，再原子切换 run/case manifest。重复 publish 相同 artifact 幂等；目标已存在但 checksum 不同则失败，不覆盖。硬链接/复制由 store 决定并记录。

## 兼容视图

迁移期可提供 `legacy-layout` renderer，将规范工件投影为旧目录/文件名；它不是科学事实来源，也不得修改 artifact。兼容视图差异记录在报告。

## 权限与隐私

结果根目录权限由 site profile；日志与 license 不发布到科学目录。case IDs 应去标识化。机器 summary 可用于后续平台导入，schema 版本必须明确。

## 验证

系统测试检查目录、manifest 引用、checksum、伴随索引、空/失败 section、重复发布和跨文件系统行为。