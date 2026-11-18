# `nextneopi.capabilities.reporting`

QC 与科学报告组装 API。机器可读 JSON 是事实来源，HTML/TSV 是视图。

## API Summary

| Symbol | ID | Contract | Stability |
|---|---|---|---|
| `AssembleQcReport` | IF-RPT-001 | 1.0.0 | Beta |
| `AssembleScientificReport` | IF-RPT-002 | 1.0.0 | Beta |

## 输入与 section 模型

```python
class ReportSectionResult(BaseModel, frozen=True):
    section_id: str
    result: ResultSlot[ArtifactRef]
    required: bool

class CaseQcResults(BaseModel, frozen=True):
    case_id: CaseId
    sections: Mapping[CapabilityId, ReportSectionResult]

class CaseScientificResults(BaseModel, frozen=True):
    case_id: CaseId
    variants: ReportSectionResult
    hla: ReportSectionResult
    copy_number: ReportSectionResult
    ccf_tmb: ReportSectionResult
    rna: ReportSectionResult
    neoantigens: ReportSectionResult
    immunity: ReportSectionResult
    repertoire: ReportSectionResult
```

每个 section 保留五态，解决 optional output 的 `None` 歧义。

## `AssembleQcReport`

```python
class AssembleQcReport(CapabilityImplementation[AssembleQcReportRequest, QcReportBundle], Protocol): ...

class AssembleQcReportRequest(BaseModel, frozen=True):
    run_id: RunId
    case_results: tuple[CaseQcResults, ...]
    formats: frozenset[Literal["json", "tsv", "html"]]
    policy: ReportPolicy

class QcReportBundle(BaseModel, frozen=True):
    summary: ArtifactRef[QcSummaryJson]
    tables: tuple[ArtifactRef[TabularReport], ...]
    html: ResultSlot[ArtifactRef[HtmlReport]]
    sections: tuple[ReportSectionResult, ...]
```

Python summary 必需；MultiQC HTML 可选。可选 section 失败仍生成带 FAILED section 的 summary；summary 自身失败使外层 FAILED。按 case→run gather。Tests：`TST-CONTRACT-RPT-001`、`TST-INT-RPT-001`。

## `AssembleScientificReport`

```python
class AssembleScientificReport(CapabilityImplementation[AssembleScientificReportRequest, ScientificReportBundle], Protocol): ...

class AssembleScientificReportRequest(BaseModel, frozen=True):
    run_id: RunId
    cases: tuple[CaseScientificResults, ...]
    provenance: RunProvenanceRef
    resolved_config: ResolvedConfigRef
    formats: frozenset[Literal["json", "tsv", "html"]]
    policy: ReportPolicy

class ScientificReportBundle(BaseModel, frozen=True):
    summary: ArtifactRef[ScientificSummaryJson]
    case_reports: tuple[ArtifactRef[CaseReport], ...]
    cohort_tables: tuple[ArtifactRef[TabularReport], ...]
    html: ResultSlot[ArtifactRef[HtmlReport]]
```

报告不重新计算科学值；使用稳定 identity join。Errors：`REPORT_INPUT_INCOMPLETE`、`REPORT_IDENTITY_CONFLICT`、`REPORT_SCHEMA_FAILURE`、`PUBLISH_FAILED`。按 case→run gather，不读取完整 BAM/VCF。Tests：`TST-CONTRACT-RPT-002`、`TST-SCI-RPT-001`。

```yaml
output:
  qc_report_formats: [json, html]
  scientific_report_formats: [json, tsv, html]
  include_provenance: true
```