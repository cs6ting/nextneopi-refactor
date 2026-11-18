# HLA 接口

## IF-HLA-001 `ExtractHlaEvidence` v1.0

- **语义/Request/Result**：从肿瘤 DNA 的 `DuplicateMarkedBam` 或已准备的肿瘤 RNA `ReadSet` 提取 typer 所需 evidence。兼容路径的 RNA HLA 直接消费分流的 reads，无需等待 NeoFuse 产出 RNA BAM。 [reads 分流](../../nextNEOpi.nf#L1030) · [DNA 取证](../../nextNEOpi.nf#L4750)
- **Request → Result**：`ExtractHlaEvidenceRequest(sample, source, regions, layout)` → `ResultEnvelope[HlaEvidence]`，含 reads/BAM、molecule、layout、counts。
- **不变量**：sample/molecule/layout 保留；header transform 不破坏 mate identity；DNA MHC+unmapped policy 版本化。
- **实现**：`samtools_mhc_unmapped`、未来 typer-specific extractor；SE/PE capability 声明。
- **错误/状态**：合法零 evidence 为 `EMPTY`；header/mate/reference 错误为 `FAILED`。
- **资源/cache/provenance**：按 sample；低/中 I/O；记录 regions、header transform、工具/镜像。
- **测试/等价**：read names、mate、count、来源；不比较 FASTQ 压缩字节。

```yaml
methods: {hla_evidence_extractor: samtools_mhc_unmapped}
```

## IF-HLA-002 `TypeHla` v1.0

- **语义/Request/Result**：HLA evidence 或 custom source → `HlaCallset`，不执行跨来源仲裁。
- **Result 模型**：call 含 `locus/allele_fields/resolution/zygosity/mhc_class/alpha_beta_chain/evidence_type/source/quality`。
- **实现差异**：OptiType 主要 A/B/C class-I；HLA-HD class-I/II 且有独立资源/许可；custom 是用户证据。descriptor 必须声明覆盖。
- **前置/状态**：必需 class 无兼容实现 plan 失败；成功无 call 为 `EMPTY`；无 license 为失败或允许的 skip。
- **Scatter/资源**：按 sample/typer；各自容器、HLA reference、CPU/内存不同。
- **缓存/provenance**：evidence、reference、typer/容器、参数、license fingerprint；保存原生分型产物引用。旧版 MixMHC2pred 使用原始 DNA HLA-HD 结果和专用等位基因表；规范化来源数据需保留相同配对所需的 locus、链与分辨率，经配对对照验证后可替代原生输入。 [HLA-HD 输出](../../nextNEOpi.nf#L5091) · [补充呈递的等位基因配对](../../bin/HLAHD2mixMHC2pred2.py#L97)
- **测试/等价**：各原生 parser、低分辨率、homozygous、class-II pairing；同实现按 locus/resolution/call 比较。

```yaml
methods:
  hla_typers: [optitype, hlahd]
```

## IF-HLA-003 `ResolveHlaGenotype` v1.0

- **语义/Request/Result**：多个 DNA/RNA/custom `HlaCallset` → `ResolvedHlaGenotype + HlaDecisionTrace`。
- **前置/不变量**：calls 属同 case；按 locus/chain 解析；DNA/RNA 不无差别 union；pVAC unsupported allele 被保留为 rejected evidence；class-II pairing 合法。
- **实现/策略**：纯 Python `legacy_compatible_v1` 首期；可增加 consensus/strict policy。实现能力差异属于 policy 版本。
- **错误/状态**：必需 class 最终无 call 为 `FAILED`；合法可选 class 无 call 为 `EMPTY/SKIPPED_UNSUPPORTED`；冲突按 policy 明示。
- **资源/cache/provenance**：不 scatter或按 case；低资源；key 含所有 callsets、allow-list、policy；逐 call 记录 accepted/rejected/reason。
- **测试/等价**：DNA homozygous+RNA 补充、force DNA/RNA、custom-only、重复、空 HLA、mutable default 回归；比较最终 genotype 和 decision trace。

```yaml
policies:
  hla_resolution:
    strategy: legacy_compatible_v1
    required_mhc_classes: [I, II]
    allow_rna_completion: true
```
