# 报告接口

## IF-RPT-001 `AssembleQcReport` v1.0

- **语义/Request/Result**：read/alignment QC `ResultEnvelope` 集合 → `QcReportBundle`，包含规范 JSON、表格和可选 HTML。
- **必需/可选输入**：case/sample identity、read/alignment metrics 必需于对应已请求 stage；native FastQC/MultiQC 可选。
- **不变量**：机器 summary 是事实来源；每 section 显示状态、工具/版本、单位；不从 glob 猜输入。
- **实现差异**：Python summary renderer 必需；MultiQC 可作为 HTML adapter，指标覆盖差异显式。
- **错误/状态**：某 QC section 失败仍可生成带 `FAILED` section 的报告；summary 无法生成才使接口失败。
- **Scatter/资源**：按 run/case gather，不允许串 case；低/中资源，HTML adapter 可容器运行。
- **缓存/provenance**：所有输入 artifact IDs、renderer/schema/version；报告父工件完整。
- **测试/等价**：section 状态、单位、缺失、部分失败、HTML 结构；比较规范 JSON，不比较 HTML 字节。

```yaml
output:
  qc_report_formats: [json, tsv, html]
```

## IF-RPT-002 `AssembleScientificReport` v1.0

- **语义/Request/Result**：variant/HLA/CNV/CCF/TMB/RNA/neoantigen/score/repertoire 结果及 provenance → `ScientificReportBundle`。
- **Request/Result**：输入为按 case 分类的 typed results；输出含 case summary、候选表、状态矩阵、resolved config/provenance 引用。
- **不变量**：不重新计算科学值；同一候选用稳定 identity join；`EMPTY/NOT_REQUESTED/SKIPPED_UNSUPPORTED/FAILED` 可区分；单位/口径明确。
- **实现**：Python renderer；通知/email 属独立外围 adapter，不改变报告状态。
- **错误/状态**：可选 section 失败不阻止报告生成，但必需 section 缺失使 case 失败；发布采用原子提交。
- **Scatter/资源**：按 case 组装，再 run gather；不得整体读取大型 BAM/VCF，只引用。
- **缓存/provenance**：report schema、renderer、全部父工件/decision traces；发布 URI 不改变 identity。
- **测试/等价**：空候选、部分 case 失败、resume、幂等发布、单位和状态；比较 JSON schema/identity/值容差。

```yaml
output:
  scientific_report_formats: [json, tsv, html]
  include_provenance: true
```