# ArtifactStore 契约

## IF-PORT-002 `ArtifactStore` v1.0.0

### 职责

管理 staging、schema/checksum、原子提交、cache、typed descriptor 读取、发布、引用和 GC。`ArtifactRef` 仅表示 `MATERIALIZED/EMPTY` 的 committed artifact；其他结果状态不创建 ArtifactRef。

### Python 契约

```python
DescriptorT = TypeVar("DescriptorT", bound=BaseModel)

class ArtifactStore(Protocol):
    def stage(self, spec: ArtifactSpec) -> StagingHandle: ...
    def commit(
        self, handle: StagingHandle, metadata: ArtifactMetadata
    ) -> ArtifactRef: ...
    def lookup(self, cache_key: CacheKey) -> ArtifactRef | None: ...
    def verify(self, artifact: ArtifactRef) -> VerificationReport: ...
    def read_descriptor(
        self,
        artifact: ArtifactRef[DescriptorT],
        model: type[DescriptorT],
    ) -> DescriptorT: ...
    def publish(
        self, artifact: ArtifactRef, target: PublishTarget
    ) -> PublishedArtifact: ...
    def retain(
        self, run_id: RunId, artifacts: Collection[ArtifactId]
    ) -> None: ...
```

`read_descriptor` 仅解析版本化轻量 metadata/manifest；不得借此整体加载 BAM/VCF/FASTQ。

### 不变量

Commit 前验证文件、companion index、scatter manifest、data schema、checksum 和科学 validator。相同 cache key 的并发提交幂等或安全冲突。`EMPTY` artifact 仍有合法文件/schema/checksum 和非空 reason；`FAILED/NOT_REQUESTED/SKIPPED_UNSUPPORTED` 无 artifact。

### Cache key

Contract/implementation/descriptor/image、parent checksums、reference、科学参数/policy、data schema。资源默认排除，除非 descriptor 明确声明影响结果。

### 错误

`CACHE_MISS` 不是异常；`CHECKSUM_MISMATCH`、`SCHEMA_VIOLATION`、`MISSING_COMPANION`、`INCOMPLETE_SCATTER`、`ATOMIC_COMMIT_FAILED` 产生 `ArtifactError/ErrorRecord`。损坏 hit 隔离并重算。

### 发布和测试

Publish 不改变 artifact identity；硬链接/复制被记录且幂等。Contract tests 覆盖并发、崩溃、半文件、缺索引、typed descriptor schema、只读权限、cache invalidation、publish 和 GC。输出布局见 [`../04_specifications/output-layout.md`](../04_specifications/output-layout.md)。