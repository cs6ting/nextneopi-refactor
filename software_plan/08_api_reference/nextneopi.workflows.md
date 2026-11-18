# `nextneopi.workflows`

Workflow recipe 通过 capability request 构建 DAG，不依赖具体工具 implementation。

## API Summary

| Symbol | 描述 |
|---|---|
| `WorkflowRecipe` | Recipe 构建协议 |
| `RecipeDescriptor` | ID、版本、需求和必需/可选 capability |
| `WorkflowContext` | 配置、case、reference 和 selector |
| `WorkflowGraphBuilder` | 添加 capability node、scatter 和 join |
| `wes_dna_canonical` | 首期内置 recipe |
| `wes_full`, `wgs_full`, `wes_rna_full` | 后续 recipe IDs，Experimental |

## `WorkflowRecipe`

```python
class WorkflowRecipe(Protocol):
    descriptor: RecipeDescriptor

    def validate(
        self, config: RunConfig, context: WorkflowContext
    ) -> ValidationReport: ...

    def build(
        self, config: RunConfig, context: WorkflowContext
    ) -> WorkflowGraph: ...
```

Recipe 只能引用 `IF-*` 和 typed Request/Result。implementation 由 `CapabilitySelector` 绑定；recipe 不出现 `mutect2` 命令、SIF 路径或 Slurm partition。

## `RecipeDescriptor`

```python
class RecipeDescriptor(BaseModel, frozen=True):
    recipe_id: RecipeId
    version: SemVer
    stability: ApiStability
    supported_assays: frozenset[AssayKind]
    required_capabilities: tuple[CapabilityRequirement, ...]
    optional_capabilities: tuple[CapabilityRequirement, ...]
    output_contracts: tuple[ArtifactContract, ...]
```

## `WorkflowGraphBuilder`

```python
class WorkflowGraphBuilder(Protocol):
    def add_capability(
        self,
        capability_id: CapabilityId,
        request: BaseModel,
        *,
        depends_on: Sequence[NodeId] = (),
        optional: bool = False,
    ) -> NodeId: ...

    def scatter(
        self, node: NodeId, *, axis: ScatterAxis, items: Sequence[BaseModel]
    ) -> tuple[NodeId, ...]: ...

    def gather(
        self, nodes: Sequence[NodeId], *, policy: GatherPolicy
    ) -> NodeId: ...

    def build(self) -> WorkflowGraph: ...
```

Builder 保证 DAG 无环、typed edge 兼容、所有必需输出有消费者或 publish target。

## `wes_dna_canonical`

Stable target / Beta implementation。顺序：manifest/reference/interval → reads/QC → DNA alignment/BQSR → Mutect2+confirming → normalization/consensus → germline/VEP/phase → DNA HLA → explicit purity → pVACseq → report。

```python
from nextneopi.workflows import recipes

recipe = recipes.get("wes_dna_canonical")
report = recipe.validate(config, context)
report.raise_for_errors()
graph = recipe.build(config, context)
```

## 扩展规则

新增 recipe 必须有 descriptor、配置 schema、DAG snapshot、local Demo、至少一个 system test 和需求追踪。可选节点失败是否影响 case 必须在 recipe policy 声明。