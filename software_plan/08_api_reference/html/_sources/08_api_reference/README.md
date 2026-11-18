# nextNEOpi Reference API

> 设计版本：`0.1` · Python API 基线：`v1` · 状态：Proposed

本目录定义重构后 `nextneopi` Python package 的公共接口，是后续实现、测试和插件开发的直接契约。组织方式参考 [PyTorch Reference API](https://docs.pytorch.org/docs/2.14/pytorch-api.html)：顶层按 namespace 索引，namespace 页面先列 API Summary，再展开签名、参数、返回值、异常与示例。参考页面仅用于信息架构研究，本文内容均根据 nextNEOpi 需求重新设计。

## Python API

| Namespace | 用途 |
|---|---|
| [`nextneopi`](nextneopi.md) | 顶层便捷函数和稳定 re-export |
| [`nextneopi.config`](nextneopi.config.md) | 版本化配置、加载、合并和 Schema |
| [`nextneopi.models`](nextneopi.models.md) | 领域实体、工件、状态、任务和结果模型 |
| [`nextneopi.application`](nextneopi.application.md) | Client、planner、selector 和 recipe registry |
| [`nextneopi.ports`](nextneopi.ports.md) | Execution、Artifact、Container、Plugin、Provenance 端口 |
| [`nextneopi.plugins`](nextneopi.plugins.md) | 插件 descriptor、实现协议和 entry point |
| [`nextneopi.workflows`](nextneopi.workflows.md) | Workflow recipe 和 DAG 构建 API |
| [`nextneopi.errors`](errors.md) | 异常、错误类别和错误码 |

## Scientific Capability API

| Namespace | Interface IDs | 描述 |
|---|---|---|
| [`nextneopi.capabilities.input_reference`](capabilities/input_reference.md) | IF-IN-001、IF-REF-001～002 | Manifest、ReferenceBundle、interval |
| [`nextneopi.capabilities.reads_qc`](capabilities/reads_qc.md) | IF-READ-001～002、IF-QC-001 | Reads materialization、trim、read QC |
| [`nextneopi.capabilities.alignment`](capabilities/alignment.md) | IF-ALN-001～003、IF-QC-002 | DNA alignment、postprocess、BQSR、QC |
| [`nextneopi.capabilities.variants`](capabilities/variants.md) | IF-VAR-001～004 | Somatic/SV caller、normalization、consensus |
| [`nextneopi.capabilities.annotation`](capabilities/annotation_phasing.md) | IF-VAR-005、IF-ANN-001、IF-PHS-001 | Germline context、VEP、phase |
| [`nextneopi.capabilities.hla`](capabilities/hla.md) | IF-HLA-001～003 | HLA evidence、typing、resolution |
| [`nextneopi.capabilities.copy_number`](capabilities/copy_number.md) | IF-CNV-001、IF-PUR-001 | CNV、purity、ploidy |
| [`nextneopi.capabilities.ccf_tmb`](capabilities/ccf_tmb.md) | IF-CCF-001、IF-TMB-001 | CCF 与 TMB |
| [`nextneopi.capabilities.rna`](capabilities/rna.md) | IF-RNA-001 | RNA alignment、expression、evidence |
| [`nextneopi.capabilities.events`](capabilities/fusion_splicing.md) | IF-FUS-001、IF-SPL-001 | Fusion 与 splice events |
| [`nextneopi.capabilities.neoantigens`](capabilities/neoantigens.md) | IF-NEO-001～003 | Canonical/fusion/splice neoantigen |
| [`nextneopi.capabilities.immunity`](capabilities/immunogenicity_repertoire.md) | IF-IMM-001～002、IF-REP-001 | Similarity、score、MiXCR repertoire |
| [`nextneopi.capabilities.reporting`](capabilities/reporting.md) | IF-RPT-001～002 | QC 与科学报告 |

## 指南与索引

- [API 使用约定](api-conventions.md)
- [稳定性和兼容策略](stability.md)
- [目标 package 布局](package-layout.md)
- [类型索引](type-index.md)
- [Typed DAG Edge Matrix](typed-edge-matrix.md)
- [接口实现与完整性矩阵](implementation-matrix.md)
- [机器可读接口 Inventory](interface-inventory.json)
- [快速开始](examples/quickstart.md)
- [实现一个插件](examples/implement-plugin.md)

## 使用边界

这些接口是**目标系统设计**，尚不代表当前仓库已有可导入的 `nextneopi` package。实现必须：

1. 遵守本文签名和科学语义；
2. 通过对应 Unit/Contract/Integration/Scientific tests；
3. 对破坏性变化提升 contract major；
4. 不通过 `dict[str, Any]`、裸路径或通用 `run_tool()` 绕过类型；
5. 不把 `EMPTY`、`NOT_REQUESTED`、`SKIPPED_UNSUPPORTED` 和 `FAILED` 混用。

首轮科学对照覆盖配对 WES DNA 至常规候选全量表和过滤表。固定输入、工具和策略验证同方法等价，二级候选算法通过独立配置比较。 [第一层功能设计](../02_modules/first-layer-functional-design.md) · [第二层算法清单](../02_modules/second-layer-algorithm-inventory.md) · [验收测试矩阵](../05_testing/acceptance-test-matrix.md)

## 离线文档

安装 Pandoc 后，从仓库根目录运行 `python3 software_plan/08_api_reference/package_windows.py`。生成的浏览入口是 `software_plan/08_api_reference/html/index.html`，离线压缩包是 `software_plan/08_api_reference/dist/nextneopi-api-docs-windows.zip`。若更新 `software_plan/` 顶层的分发副本，将新压缩包同步到该位置。

## 来源说明

内容依据 [`../`](../README.md) 中的需求、架构、模块、接口、规格、测试和迁移文档。PyTorch 文档内容未被复制；仅借鉴其 namespace 索引和 API Summary 信息组织方式。
