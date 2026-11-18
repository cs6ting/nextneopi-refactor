# 实现一个 Capability 插件

本例为 `IF-READ-002 TrimReads` 实现 `fastp` ToolAdapter；字段与当前 API/JSON Schema 一致。占位镜像 digest 使用合法格式但实现时必须替换为真实已批准 digest。

## 1. Implementation config

```python
class FastpConfig(BaseModel, frozen=True, extra="forbid"):
    qualified_quality_phred: int = Field(default=20, ge=0, le=41)
    minimum_length: int = Field(default=30, ge=1)
    detect_adapter_for_pe: bool = True
```

## 2. Descriptor

```python
FASTP_DESCRIPTOR = PluginDescriptor(
    schema_version=1,
    capability_id="IF-READ-002",
    implementation_id="fastp",
    contract_version="1.0.0",
    implementation_version="0.24.0+adapter.1",
    core_compatibility=">=0.1,<1.0",
    supports=CapabilitySupport(
        assays={"WES", "WGS"},
        molecules={"DNA", "RNA"},
        layouts={"SINGLE_END", "PAIRED_END"},
        mhc_classes=set(),
        variant_kinds=set(),
        features={"TRIM_READS", "TRIM_METRICS"},
        protocols={"FULL_LENGTH", "THREE_PRIME_TAG"},
    ),
    inputs=(
        ArtifactContract(
            name="reads",
            artifact_kind="CANONICAL_READ_SET",
            schema_version="1.0.0",
            required=True,
        ),
    ),
    outputs=(
        ArtifactContract("reads", "TRIMMED_READ_SET", "1.0.0", True),
        ArtifactContract("metrics", "TRIM_METRICS", "1.0.0", True),
    ),
    reference_requirements=(),
    container=ContainerSpec(
        oci="quay.io/biocontainers/fastp",
        digest="sha256:1111111111111111111111111111111111111111111111111111111111111111",
        runtime="apptainer",
        entrypoint=("fastp",),
        environment_allowlist=("OMP_NUM_THREADS",),
    ),
    resources=ResourceModel(
        cpus=8,
        memory_mb=4096,
        runtime_minutes=120,
        scratch_mb=16384,
        gpus=0,
        nodes=1,
        tasks=1,
        scaling_model="scratch=max(16384,input_bytes*2)",
        scientific_resource_fields=(),
    ),
    license=LicenseRequirement(
        id="MIT",
        redistributable=True,
        acceptance_required=False,
        mount_required=False,
    ),
    scatter=ScatterCapability(
        supported=True,
        axes={"sample"},
        partial_gather=False,
    ),
    empty_input=EmptyInputBehavior.REJECT,
    degradation=(),
    implementation_config_schema="pkg://nextneopi_fastp/fastp-config-v1.json",
)
```

## 3. Adapter

```python
class FastpTrimReads(ToolAdapter[TrimReadsRequest, TrimReadsResult]):
    descriptor = FASTP_DESCRIPTOR

    def validate(self, request, context) -> ValidationReport:
        issues = []
        if request.reads.state not in {ArtifactState.MATERIALIZED, ArtifactState.EMPTY}:
            issues.append(error("READS_STATE_INVALID", "reads.state"))
        reads = context.artifact_store.read_descriptor(
            request.reads,
            CanonicalReadSet,
        )
        if reads.layout.value not in self.descriptor.supports.layouts:
            issues.append(error("LAYOUT_UNSUPPORTED", "reads.layout"))
        return ValidationReport(issues=tuple(issues))

    def plan(self, request, context) -> ExecutionSubgraph:
        reads = context.artifact_store.read_descriptor(
            request.reads,
            CanonicalReadSet,
        )
        argv = [
            "fastp",
            "--in1", container_path(reads.r1),
            "--out1", "out/trimmed_R1.fastq.gz",
            "--json", "out/fastp.json",
            "--html", "out/fastp.html",
            "--thread", str(context.resources.cpus),
        ]
        if reads.r2 is not None:
            argv += ["--in2", container_path(reads.r2), "--out2", "out/trimmed_R2.fastq.gz"]
        return ExecutionSubgraph.single(
            ContainerTaskSpec(
                argv=tuple(argv),
                container=self.descriptor.container,
                mounts=readonly_inputs_and_writable_staging(request, context),
                resources=context.resources,
                expected_outputs=context.expected_outputs,
                shell=False,
            )
        )

    def collect(self, execution, context) -> ResultEnvelope[TrimReadsResult]:
        execution.require_success()
        metrics = parse_fastp_json(execution.output("out/fastp.json"))
        reads = validate_trimmed_reads(execution, expected_layout=metrics.layout)
        if metrics.after_filtering.total_reads == 0:
            empty_artifact = commit_empty_trim_result(metrics, context)
            return ResultEnvelope.empty(
                value=empty_artifact,
                reason=ResultReason(code="ALL_READS_FILTERED", message="fastp removed all reads"),
                provenance_id=context.provenance_id,
            )
        return commit_trim_result(reads, metrics, context)
```

`ExecutionRecord.require_success()` 将工具失败转为可序列化 ErrorRecord，runner/collector boundary 负责生成 `FAILED` ResultEnvelope。Adapter 使用 argv，禁止 shell/download/reference 写入。

## 4. Entry point

```toml
[project.entry-points."nextneopi.capabilities"]
fastp = "nextneopi_fastp.plugin:create_plugin"
```

```python
class FastpFactory(CapabilityFactory):
    descriptor = FASTP_DESCRIPTOR
    config_model = FastpConfig
    def create(self) -> FastpTrimReads: return FastpTrimReads()

def create_plugin() -> CapabilityFactory:
    return FastpFactory()
```

## 5. Run configuration

```yaml
methods:
  read_trimmer: fastp
implementation_configs:
  fastp:
    qualified_quality_phred: 20
    minimum_length: 30
    detect_adapter_for_pe: true
```

该对象先受 RunConfig 扩展点校验，再由 FastpConfig 严格校验。

## 6. Tests 与完成条件

```python
@pytest.mark.contract("IF-READ-002@1.0.0")
def test_fastp_contract(contract_suite, plugin):
    contract_suite.verify(plugin)

def test_plan_uses_argv_without_shell(plugin, paired_request, context):
    task = plugin.plan(paired_request, context).single_task()
    assert task.argv[0] == "fastp"
    assert task.shell is False
```

还必须覆盖正常 PE/SE、全部过滤、缺 R2、损坏 JSON、工具失败、Schema drift、descriptor JSON Schema、implementation config、cache key、离线镜像和 recipe wiring。只有这些门禁和 provenance 全部通过才算实现完成。