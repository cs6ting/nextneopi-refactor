# MOD-02 参考资源与区间

## 目的、职责与非职责

把参考基因组、注释、已知位点、HLA/CNV/预测资源组织为版本化 `ReferenceBundle`，并按 assay 生成 callable/scatter interval。模块不下载资源、不选择分析方法，也不容忍 build 混用。

## 上下游与当前映射

上游为 MOD-01 的 assay/sex 和配置；下游为 alignment、caller、VEP、HLA、CNV、TMB。当前路径集中在 `conf/resources.config`、`conf/params.config`，WES/WGS interval 过程位于 `nextNEOpi.nf` 前半段；`bin/make_merged_exon_bed.sh` 是待 Python 化的资源构建逻辑。

本模块为 A–G 提供版本化资源。旁路算法按同一参考定义和资源校验规则比较。A2 更换比对器时，为同一 FASTA 另建并记录该比对器的索引。 [两层模块地图](module-map.md#第一层计算能力与第二层算法单元) · [优先旁路试点](module-map.md#优先旁路试点)

## 实体、输入输出与不变量

输入 `ReferenceBundleSpec + AssayDesign`；输出 `ReferenceBundle`、`CallableRegions`、`ScatterSet[IntervalShard]`。bundle 必须记录 assembly、FASTA/FAI/dict、contig dictionary digest、annotation/VEP 版本、known-sites、capture kit、HLA/CNV/BLAST 资源 checksum。

不变量：所有基因组工件 build/dictionary 一致；BED 为 0-based half-open，VCF 为 1-based；WES 必须声明 capture targets/baits；WGS 主/非主 contig policy 明确；scatter shard 集合可证明覆盖范围且 gather 顺序稳定。

## 接口与实现

提供 `IF-REF-001 ResolveReferenceBundle`、`IF-REF-002 PlanCallableIntervals`。实现可包括 `filesystem_bundle_v1`、未来 registry/object-store bundle；interval 实现包括 `wes_capture`、`wgs_non_n_regions`。二者 capability 不等价。

## 配置、容器和许可

配置为 `reference.bundle`、`assay.kind/capture_kit`、padding、scatter count。资源预构建可用受控 GATK/htslib 容器；正式 run 只读。每项数据库许可证进入 bundle manifest。

## 状态与 provenance

必需资源缺失/校验错误为 `REFERENCE_MISSING`、`REFERENCE_INCOMPATIBLE`、`CHECKSUM_MISMATCH`；空 callable interval 为失败而非 `EMPTY`。记录 bundle ID、所有 digest、interval policy 和 transform 版本。

## 测试与验收

单元覆盖坐标、padding、contig 过滤；契约验证 bundle schema；集成验证 GATK/htslib 可消费；系统覆盖 WES/WGS、chr/no-chr、XX/XY。验收 REQ-FUN-002～003、NFR-007、ACC-001。风险是旧资源版本混搭和路径存在即兼容，目标实现必须严格拒绝。
