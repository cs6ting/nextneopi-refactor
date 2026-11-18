# `nextneopi.capabilities.input_reference`

Manifest、ReferenceBundle 和 callable interval API。

## API Summary

| Symbol | ID | 描述 | Stability |
|---|---|---|---|
| `LoadCaseManifest` | IF-IN-001 | 外部 manifest → 规范 case/sample/library | Beta |
| `ResolveReferenceBundle` | IF-REF-001 | 解析并校验不可变参考集合 | Beta |
| `PlanCallableIntervals` | IF-REF-002 | 按 assay 生成 callable/scatter intervals | Beta |

## `LoadCaseManifest`

```python
class LoadCaseManifest(
    CapabilityImplementation[LoadCaseManifestRequest, CaseManifest], Protocol
): ...

class LoadCaseManifestRequest(BaseModel, frozen=True):
    source: Uri
    format: ImplementationId = "legacy_csv_v1"
    compatibility_policy: ManifestCompatibilityPolicy
    case_ids: tuple[CaseId, ...] | None = None
```

将 CSV/YAML/LIMS 输入归一化，不读取完整 reads。

**Parameters:** `source` 必需且可读；`format` 选择 loader；`case_ids` 可过滤但不能改变 identity。

**Returns:** `ResultEnvelope[CaseManifest]`。manifest 为必需输入，成功状态必须是 `MATERIALIZED`。

**Raises/Issues:** `INVALID_MANIFEST`、`DUPLICATE_ID`、`MISSING_MATCHED_NORMAL`、`UNSUPPORTED_LAYOUT`、`INPUT_NOT_FOUND`。

**不变量:** 每 case 至少一对 tumor/normal DNA；ID 唯一安全；PE mates 完整；sex 归一为 XX/XY/UNKNOWN；空 HLA URI 不算 custom。

**Implementations:** `legacy_csv_v1`（首期）、`yaml_v1`、未来 `lims`。纯 Python、无容器、无 scatter。Cache key 含 source checksum、loader/contract 和 compatibility policy；provenance 保留源行号与 warning。

```python
request = LoadCaseManifestRequest(
    source=Uri("samples.csv"),
    compatibility_policy=ManifestCompatibilityPolicy.STRICT,
)
```

**Tests:** FASTQ/BAM、SE/PE、多 lane、重复 ID、缺 normal、空 HLA、非法路径；不同 loader 的规范对象应相等。

## `ResolveReferenceBundle`

```python
class ResolveReferenceBundle(
    CapabilityImplementation[ResolveReferenceBundleRequest, ReferenceBundle], Protocol
): ...

class ResolveReferenceBundleRequest(BaseModel, frozen=True):
    bundle_id: ReferenceBundleId
    manifest_uri: Uri
    required_capabilities: frozenset[ReferenceCapability]
    verify_checksums: bool = True
```

解析预备完成的参考集合，不下载或修复资源。

**Returns:** `ResultEnvelope[ReferenceBundle]`，包含 FASTA/FAI/dict、assembly、dictionary digest，以及按 recipe 所需 VEP、known-sites、HLA、CNV、BLAST 等资源。

**Raises:** `REFERENCE_MISSING`、`REFERENCE_INCOMPATIBLE`、`CHECKSUM_MISMATCH`、`LICENSE_MISSING`。

**不变量:** 所有资源 immutable/read-only；assembly/contig dictionary 相容；被请求 capability 的资源必需。实现 `filesystem_bundle_v1` 首期，未来 registry/object-store 只能改变定位方式。

无 scatter、低资源；cache/provenance 由 bundle manifest 和逐文件 digest 决定。

```python
bundle = client.capabilities.execute(
    "IF-REF-001",
    ResolveReferenceBundleRequest(
        bundle_id="grch38-nextneopi-v1",
        manifest_uri="/ref/nextneopi/manifest.json",
        required_capabilities={ReferenceCapability.VEP, ReferenceCapability.GATK},
    ),
)
```

## `PlanCallableIntervals`

```python
class PlanCallableIntervals(
    CapabilityImplementation[PlanCallableIntervalsRequest, CallableIntervalPlan], Protocol
): ...

class PlanCallableIntervalsRequest(BaseModel, frozen=True):
    reference: ReferenceBundleRef
    assay: AssayDesign
    scatter_count: int = Field(ge=1)
    padding_bp: int = Field(default=250, ge=0)

class CallableIntervalPlan(BaseModel, frozen=True):
    callable_regions: ArtifactRef[IntervalSet]
    padded_regions: ArtifactRef[IntervalSet]
    shards: tuple[IntervalShard, ...]
    coordinate_convention: CoordinateConvention
```

**Implementations:** `wes_capture` 需要 target/bait；`wgs_non_n_regions` 使用 contig/N-region policy，二者不等价。

**Errors:** `ASSAY_RESOURCE_MISSING`、`EMPTY_CALLABLE_REGION`、`INTERVAL_OUT_OF_BOUNDS`、`INCOMPLETE_SCATTER`。

**Scatter:** 本接口输出稳定 shard ID 和顺序；shard union 必须覆盖计划范围。可使用 GATK/htslib 容器。Cache key 含 dictionary、targets、assay、padding、scatter policy；科学等价比较规范 interval union，而非行顺序。

```yaml
workflow: {assay: WES}
reference: {bundle: grch38-nextneopi-v1, capture_kit: agilent_v7}
execution: {scatter_count: 40}
```