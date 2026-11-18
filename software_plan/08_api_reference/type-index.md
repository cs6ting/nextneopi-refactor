# 类型索引

公共 symbol 的唯一命名空间。未列出类型不应出现在公共签名中，新增时必须同时更新此表和 typed-edge matrix。

| Symbol | Namespace | 用途 |
|---|---|---|
| `AlignedBam`, `DuplicateMarkedBam`, `RecalibratedBam` | `nextneopi.models` | 分阶段 DNA 比对工件描述 |
| `AnalysisRunSpec` | `nextneopi.models` | 不可变运行领域规格 |
| `ArtifactId`, `TaskId`, `AttemptId`, `ProvenanceId` | `nextneopi.models` | 强类型执行/血缘 ID |
| `ArtifactRef[T]`, `ArtifactSpec`, `ArtifactState` | `nextneopi.models` | Committed 工件、预期输出和双态 |
| `AssayDesign`, `AssayKind` | `nextneopi.models` | WES/WGS 设计 |
| `BiologicalSex` | `nextneopi.models` | XX/XY/UNKNOWN |
| `CacheKey`, `Digest`, `SemVer`, `Uri` | `nextneopi.models` | 内容/版本/位置 identity |
| `CallableIntervalPlan` | `capabilities.input_reference` | Callable/padded/shards |
| `CancelReport`, `CancelScope` | `nextneopi.models` | 取消 API |
| `CanonicalReadSet`, `TrimmedReadSet` | `capabilities.reads_qc` | 规范 reads descriptor |
| `CanonicalSomaticCallset`, `ConsensusSomaticCallset` | `capabilities.variants` | 规范/共识 callset |
| `Case`, `CaseId`, `CaseManifest` | `nextneopi.models` | 分析 case |
| `CaseRunResult`, `RunHandle`, `RunResult`, `RunStatus` | `nextneopi.application` | 运行 API |
| `CaseQcResults`, `CaseScientificResults` | `capabilities.reporting` | Report 输入聚合 |
| `CcfRecord`, `CcfResult`, `CcfTable` | `capabilities.ccf_tmb` | CCF |
| `CollectionContext`, `PlanningContext` | `nextneopi.plugins` | 实现上下文 |
| `ContainerSpec`, `MountSpec`, `ContainerTaskSpec` | `nextneopi.models` | 安全容器任务 |
| `CopyNumberProfile`, `PurityPloidyResult` | `capabilities.copy_number` | CNV/purity |
| `ErrorRecord`, `NextNeoPiError` | `nextneopi.errors` | 可序列化错误/异常 |
| `ExecutionPlan`, `ExecutionRecord`, `ExecutionSubgraph` | `nextneopi.models` | DAG/attempt |
| `ExpressionMatrix`, `RnaAnalysisResult` | `capabilities.rna` | RNA expression/子输出 slots |
| `FusionCallset`, `FusionEvent`, `SpliceEventCallset` | `capabilities.events` | Fusion/splice events |
| `HlaAllele`, `HlaAlleleCall`, `HlaCallset` | `capabilities.hla` | HLA call |
| `HlaEvidence` | `capabilities.hla` | 来源可追溯的 HLA reads/BAM 证据 |
| `HlaClassIiPair`, `ResolvedHlaGenotype` | `capabilities.hla` | HLA pairing/resolution |
| `InspectionResult`, `ProvenanceSummary` | `nextneopi.application` | Run/task/artifact 检查 |
| `Library`, `LibraryId`, `LibraryRef` | `nextneopi.models` | 测序 library |
| `MhcClass`, `MoleculeType`, `LibraryLayout` | `nextneopi.models` | 科学枚举 |
| `ModelRef`, `ImmunogenicityScoreSet` | `capabilities.immunity` | 模型与逐模型 score slots |
| `NeoantigenCandidate`, `NeoantigenIdentity`, `NeoantigenTable` | `capabilities.neoantigens` | 三类候选共享基类 |
| `PhaseContext` | `capabilities.annotation` | 定相证据及等级 |
| `PluginDescriptor`, `CapabilityImplementation`, `ToolAdapter` | `nextneopi.plugins` | 插件 API |
| `ReferenceBundle`, `ReferenceBundleRef`, `ReferenceIdentity` | `nextneopi.models` | 参考集合与 identity |
| `ResolvedConfiguration`, `ResolvedSiteProfile`, `SiteProfile` | `nextneopi.config` | 配置解析结果 |
| `ResourceModel` | `nextneopi.plugins` | Implementation 资源模型 |
| `ResourceRequest` | `nextneopi.models` | 具体任务资源请求 |
| `ResultReason`, `ResultSlot[T]`, `ResultEnvelope[T]` | `nextneopi.models` | 五态结果模型 |
| `RunConfig` | `nextneopi.config` | 运行配置 |
| `RunEvent`, `RunProvenanceRef` | `nextneopi.models` | 事件和血缘引用 |
| `Sample`, `SampleId`, `SampleRef`, `SampleRole` | `nextneopi.models` | 样本 |
| `ScientificReportBundle`, `QcReportBundle` | `capabilities.reporting` | 报告 bundle |
| `TmbMetric`, `TmbMetricSet` | `capabilities.ccf_tmb` | 逐 metric ResultSlot |
| `ValidationIssue`, `ValidationReport` | `nextneopi.models` | 聚合预检 |
| `VariantIdentity`, `AnnotatedSomaticCallset` | `nextneopi.models` / `capabilities.annotation` | 变异 identity 与注释 callset |
| `WorkflowGraph`, `WorkflowRecipe` | `nextneopi.workflows` | Typed recipe DAG |

Request 类型遵循 `<Operation>Request`；Result 类型使用领域名。Alias 必须在本表说明，禁止 `AnnotatedVcf`/`AnnotatedSomaticCallset` 等无声明双名。
