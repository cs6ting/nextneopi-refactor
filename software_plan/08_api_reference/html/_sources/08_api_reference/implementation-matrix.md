# 接口实现与完整性矩阵

[`interface-inventory.json`](interface-inventory.json) 是机器可读规范，逐接口包含 Request/Result、runtime、scatter、resource、implementation、config、reference/license、cache、provenance、唯一 contract test 和 recipe。本文提供实现视图；`NOT_IMPLEMENTED` 不得被 Beta/Experimental 目标稳定性误解为已可用。

| ID | Symbol | v | Module | Normative result | 首个实现 | Contract test | 阶段 | Status |
|---|---|---:|---|---|---|---|---:|---|
| IF-PLG-001 | CapabilityImplementation | 1.0.0 | PLATFORM | ResultEnvelope[ResultT] | core framework | TST-CONTRACT-IF-PLG-001 | 3 | NOT_IMPLEMENTED |
| IF-PORT-001 | ExecutionBackend | 1.0.0 | PLATFORM | RunHandle | Pydra/Snakemake | TST-CONTRACT-IF-PORT-001 | 1 | NOT_IMPLEMENTED |
| IF-PORT-002 | ArtifactStore | 1.0.0 | PLATFORM | ArtifactRef | filesystem store | TST-CONTRACT-IF-PORT-002 | 4 | NOT_IMPLEMENTED |
| IF-IN-001 | LoadCaseManifest | 1.0.0 | MOD-01 | CaseManifest | legacy_csv_v1 | TST-CONTRACT-IF-IN-001 | 5 | NOT_IMPLEMENTED |
| IF-REF-001 | ResolveReferenceBundle | 1.0.0 | MOD-02 | ReferenceBundle | filesystem_bundle_v1 | TST-CONTRACT-IF-REF-001 | 5 | NOT_IMPLEMENTED |
| IF-REF-002 | PlanCallableIntervals | 1.0.0 | MOD-02 | CallableIntervalPlan | wes_capture | TST-CONTRACT-IF-REF-002 | 5 | NOT_IMPLEMENTED |
| IF-READ-001 | MaterializeReads | 1.0.0 | MOD-03 | ArtifactRef[CanonicalReadSet] | FASTQ/samtools | TST-CONTRACT-IF-READ-001 | 6 | NOT_IMPLEMENTED |
| IF-READ-002 | TrimReads | 1.0.0 | MOD-03 | TrimReadsResult | no_trim/fastp | TST-CONTRACT-IF-READ-002 | 6 | NOT_IMPLEMENTED |
| IF-QC-001 | AssessReadQC | 1.0.0 | MOD-03 | ReadQcResult | fastqc | TST-CONTRACT-IF-QC-001 | 6 | NOT_IMPLEMENTED |
| IF-ALN-001 | AlignDNA | 1.0.0 | MOD-04 | ArtifactRef[AlignedBam] | bwa_mem | TST-CONTRACT-IF-ALN-001 | 7 | NOT_IMPLEMENTED |
| IF-ALN-002 | PostprocessDNAAlignment | 1.0.0 | MOD-04 | ArtifactRef[DuplicateMarkedBam] | GATK/Picard | TST-CONTRACT-IF-ALN-002 | 7 | NOT_IMPLEMENTED |
| IF-ALN-003 | RecalibrateBaseQuality | 1.0.0 | MOD-04 | ArtifactRef[RecalibratedBam] | gatk4 | TST-CONTRACT-IF-ALN-003 | 8 | NOT_IMPLEMENTED |
| IF-QC-002 | AssessAlignmentQC | 1.0.0 | MOD-04 | AlignmentQcResult | GATK/mosdepth | TST-CONTRACT-IF-QC-002 | 8 | NOT_IMPLEMENTED |
| IF-VAR-001 | CallSomaticSmallVariants | 1.0.0 | MOD-05 | ArtifactRef[NativeSomaticCallset] | Mutect2/VarScan2 | TST-CONTRACT-IF-VAR-001 | 9 | NOT_IMPLEMENTED |
| IF-VAR-002 | CallSomaticSvCandidates | 1.0.0 | MOD-05 | SomaticSvResult | Manta | TST-CONTRACT-IF-VAR-002 | 15 | NOT_IMPLEMENTED |
| IF-VAR-003 | NormalizeSomaticCallset | 1.0.0 | MOD-05 | ArtifactRef[CanonicalSomaticCallset] | caller normalizers | TST-CONTRACT-IF-VAR-003 | 9 | NOT_IMPLEMENTED |
| IF-VAR-004 | BuildConsensusSomaticCallset | 1.0.0 | MOD-05 | ArtifactRef[ConsensusSomaticCallset] | primary_confirmed_v1 | TST-CONTRACT-IF-VAR-004 | 10 | NOT_IMPLEMENTED |
| IF-VAR-005 | CallAndFilterNormalGermline | 1.0.0 | MOD-06 | ArtifactRef[GermlineContextCallset] | gatk_nvscore | TST-CONTRACT-IF-VAR-005 | 12 | NOT_IMPLEMENTED |
| IF-ANN-001 | AnnotateVariantConsequences | 1.0.0 | MOD-06 | ConsequenceResult | VEP | TST-CONTRACT-IF-ANN-001 | 11 | NOT_IMPLEMENTED |
| IF-PHS-001 | BuildProximalPhaseContext | 1.0.0 | MOD-06 | ArtifactRef[PhaseContext] | read_backed | TST-CONTRACT-IF-PHS-001 | 12 | NOT_IMPLEMENTED |
| IF-HLA-001 | ExtractHlaEvidence | 1.0.0 | MOD-07 | ArtifactRef[HlaEvidence] | samtools | TST-CONTRACT-IF-HLA-001 | 13 | NOT_IMPLEMENTED |
| IF-HLA-002 | TypeHla | 1.0.0 | MOD-07 | ArtifactRef[HlaCallset] | OptiType/HLA-HD | TST-CONTRACT-IF-HLA-002 | 13 | NOT_IMPLEMENTED |
| IF-HLA-003 | ResolveHlaGenotype | 1.0.0 | MOD-07 | ArtifactRef[ResolvedHlaGenotype] | legacy_compatible_v1 | TST-CONTRACT-IF-HLA-003 | 13 | NOT_IMPLEMENTED |
| IF-CNV-001 | InferCopyNumber | 1.0.0 | MOD-08 | ArtifactRef[CopyNumberProfile] | ASCAT/Sequenza | TST-CONTRACT-IF-CNV-001 | 17 | NOT_IMPLEMENTED |
| IF-PUR-001 | ResolvePurityPloidy | 1.0.0 | MOD-08 | ArtifactRef[PurityPloidyResult] | configured/policy | TST-CONTRACT-IF-PUR-001 | 14 | NOT_IMPLEMENTED |
| IF-CCF-001 | EstimateCCF | 1.0.0 | MOD-09 | CcfResult | binomial_grid_v1 | TST-CONTRACT-IF-CCF-001 | 19 | NOT_IMPLEMENTED |
| IF-TMB-001 | ComputeTMB | 1.0.0 | MOD-09 | TmbMetricSet | nextneopi_tmb_v1 | TST-CONTRACT-IF-TMB-001 | 19 | NOT_IMPLEMENTED |
| IF-RNA-001 | AlignAndQuantifyRNA | 1.0.0 | MOD-10 | RnaAnalysisResult | STAR compatible | TST-CONTRACT-IF-RNA-001 | 20 | NOT_IMPLEMENTED |
| IF-FUS-001 | CallGeneFusions | 1.0.0 | MOD-11 | ArtifactRef[FusionCallset] | Arriba | TST-CONTRACT-IF-FUS-001 | 21 | NOT_IMPLEMENTED |
| IF-SPL-001 | CallSpliceEvents | 1.0.0 | MOD-11 | ArtifactRef[SpliceEventCallset] | regtools | TST-CONTRACT-IF-SPL-001 | 22 | NOT_IMPLEMENTED |
| IF-NEO-001 | PredictCanonicalNeoantigens | 1.0.0 | MOD-12 | ArtifactRef[CanonicalNeoantigenTable] | pVACseq | TST-CONTRACT-IF-NEO-001 | 14 | NOT_IMPLEMENTED |
| IF-NEO-002 | PredictFusionNeoantigens | 1.0.0 | MOD-12 | ArtifactRef[FusionNeoantigenTable] | NeoFuse compatible | TST-CONTRACT-IF-NEO-002 | 21 | NOT_IMPLEMENTED |
| IF-NEO-003 | PredictSpliceNeoantigens | 1.0.0 | MOD-12 | ArtifactRef[SpliceNeoantigenTable] | pVACsplice | TST-CONTRACT-IF-NEO-003 | 22 | NOT_IMPLEMENTED |
| IF-IMM-001 | CheckSelfSimilarity | 1.0.0 | MOD-13 | ArtifactRef[SelfSimilarityResult] | blastp_short | TST-CONTRACT-IF-IMM-001 | 23 | NOT_IMPLEMENTED |
| IF-IMM-002 | ScoreImmunogenicity | 1.0.0 | MOD-13 | ImmunogenicityScoreSet | CSiN/GBM | TST-CONTRACT-IF-IMM-002 | 23 | NOT_IMPLEMENTED |
| IF-REP-001 | ProfileImmuneRepertoire | 1.0.0 | MOD-13 | ArtifactRef[RepertoireProfile] | MiXCR | TST-CONTRACT-IF-REP-001 | 24 | NOT_IMPLEMENTED |
| IF-RPT-001 | AssembleQcReport | 1.0.0 | MOD-14 | QcReportBundle | Python/MultiQC | TST-CONTRACT-IF-RPT-001 | 14 | NOT_IMPLEMENTED |
| IF-RPT-002 | AssembleScientificReport | 1.0.0 | MOD-14 | ScientificReportBundle | Python renderer | TST-CONTRACT-IF-RPT-002 | 14 | NOT_IMPLEMENTED |

## 16 项门禁

机器可读清单仍保留 MixMHC2pred 在 IF-IMM-002 的旧登记。科学分类及输入见 [新抗原预测接口](capabilities/neoantigens.md#shared-execution)；补充 Class II 呈递旁路需要独立验收。

每个 inventory entry 必须有：Protocol、Request、Result、字段文档、状态、capability、scatter/gather、resource、container、reference、license、cache、provenance、唯一 tests、YAML/config path、recipe Demo。机器检查缺一项即 API completeness 失败。实现状态只有代码、Schema、测试、容器和 recipe 全通过后才能改为 `IMPLEMENTED`。
