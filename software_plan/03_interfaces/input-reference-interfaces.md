# 输入与参考接口

共享约定见 [interface-conventions.md](interface-conventions.md)。

## IF-IN-001 `LoadCaseManifest` v1.0

- **语义/模块**：将外部 manifest 规范化为 MOD-01 的 case/sample/library 聚合；不读取完整 reads。
- **Request → Result**：`LoadCaseManifestRequest(source: Uri, format, compatibility_policy)` → `ResultEnvelope[CaseManifest]`；source 必需，legacy aliases 可选。
- **前置/不变量**：source 可读；ID 唯一安全；每 case 有 tumor/normal DNA；PE mates 完整；sex 为 XX/XY/UNKNOWN；空 HLA 不算 custom。
- **能力/实现**：`legacy_csv_v1` 首期，未来 `yaml_v1/lims`；所有实现输出同一 schema。
- **错误/状态**：`INVALID_MANIFEST`、`DUPLICATE_ID`、`MISSING_MATCHED_NORMAL`、`UNSUPPORTED_LAYOUT`；必需输入不得 `EMPTY`。
- **执行**：不 scatter；纯 Python、低 CPU/内存、无容器/参考/许可。
- **缓存/provenance**：source checksum、parser/contract version、规范化警告和源行号进入 key/记录。
- **测试/等价**：边界表头、FASTQ/BAM、SE/PE、多 lane、空 HLA；不同 loader 的领域对象规范 JSON 相等。

```yaml
input:
  manifest: samples.csv
  manifest_format: legacy_csv_v1
```

## IF-REF-001 `ResolveReferenceBundle` v1.0

- **语义/模块**：解析并验证同一科学版本的参考集合；不下载资源。
- **Request → Result**：`ResolveReferenceBundleRequest(bundle_id, manifest_uri, required_capabilities)` → `ResultEnvelope[ReferenceBundle]`。
- **必需/可选**：FASTA/FAI/dict 和 dictionary digest 必需；annotation、known-sites、HLA/CNV/BLAST 资源按 recipe 可选但被请求时必需。
- **不变量**：文件 checksum、assembly、contig dictionary 兼容；资源 immutable/read-only。
- **实现差异**：`filesystem_bundle_v1` 首期；未来 registry/object store 仅改变定位，不改变 bundle 语义。
- **错误/状态**：`REFERENCE_MISSING/INCOMPATIBLE/CHECKSUM_MISMATCH/LICENSE_MISSING`；不允许 typed empty。
- **执行**：纯 Python metadata + 可选轻量验证工具；无 scatter，资源低。
- **缓存/provenance**：bundle manifest checksum 和每项 checksum；记录来源、许可、验证时间。
- **测试/等价**：缺索引、dictionary mismatch、资源版本；等价以 bundle ID+digest，不以路径。

```yaml
reference:
  bundle: grch38-nextneopi-v1
```

## IF-REF-002 `PlanCallableIntervals` v1.0

- **语义/模块**：按 `AssayDesign` 生成 callable、padded 和稳定 scatter intervals。
- **Request → Result**：`PlanCallableIntervalsRequest(reference, assay, scatter_count, padding)` → `ResultEnvelope[CallableIntervalPlan]`。
- **前置/不变量**：WES 有 capture targets/baits；WGS 有 contig inclusion/N-region policy；坐标约定显式；shard union 符合计划且顺序稳定。
- **实现差异**：`wes_capture` 与 `wgs_non_n_regions` 并存，不可互换；实现可调用 GATK/htslib 容器。
- **错误/状态**：`ASSAY_RESOURCE_MISSING`、`EMPTY_CALLABLE_REGION`、`INTERVAL_OUT_OF_BOUNDS`、`INCOMPLETE_SCATTER`。
- **scatter/资源**：输出本身定义 interval scatter；低到中等资源，参考只读。
- **缓存/provenance**：assay、targets checksum、dictionary、padding、算法/scatter count 进入 key；记录坐标 transform。
- **测试/等价**：chr/no-chr、边界、padding、N 区、shard coverage；比较规范 interval 集与 union，不比较行顺序。

```yaml
workflow:
  assay: WES
reference:
  capture_kit: agilent_v7
execution:
  scatter_count: 40
```