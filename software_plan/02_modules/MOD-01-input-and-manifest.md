# MOD-01 输入与 Manifest

## 目的、职责与非职责

将用户 CSV/YAML 输入转换为规范 `AnalysisRunSpec/Case/Sample/Library`，在昂贵计算前完成身份、配对、路径和输入类型校验。它不读取完整 reads、不决定 caller/HLA 方法，也不提交任务。

## 上下游与当前映射

上游是 CLI/SDK 和配置；下游为全部 recipe。当前行为主要位于 `nextNEOpi.nf:121-317`，FASTQ/BAM 示例见根目录 `example_batchFile_*.csv`。旧代码通过修改 metadata map 构造 join key，目标设计改为显式 `case_id`。

本模块为 A–G 提供统一的病例、样本角色和文库身份。首期仍校验肿瘤与正常 DNA 配对，RNA 缺失时保留病例供 DNA 路径消费。 [两层模块地图](module-map.md#第一层计算能力与第二层算法单元)

## 领域实体与工件

输入：`CaseManifestSource`、`RunConfig`。输出：`CaseManifest`、`Case`、`Sample`、`Library`、可选 `UserHlaCallset`。FASTQ 行必须表达 R1/R2、多 lane 和 layout；BAM 必须区分 raw/unaligned/aligned 语义，首期保持“BAM 转 FASTQ 后重比对”的兼容模式并显式命名。

## 不变量

- 每个 case 至少一份 `TUMOR_DNA` 和一份 `NORMAL_DNA`。
- `case_id/sample_id/library_id` 唯一且使用安全字符集。
- 配对 DNA layout 兼容；PE 必须有成对输入。
- `sex` 归一为 `XX/XY/UNKNOWN`，不能用隐式布尔值。
- 空 HLA 路径不等于存在 custom HLA。

## 接口与实现

提供 `IF-IN-001 LoadCaseManifest`；依赖配置和 URI 访问端口。首期实现 `legacy_csv_v1`，未来可增加 `manifest_yaml`、LIMS adapter。不同实现必须产生相同领域模型，不允许绕过不变量。

## 配置、资源与许可证

配置为 `input.manifest`、可选 case filter 和 legacy 兼容策略。模块无工具容器、参考或第三方许可；路径存在性和可读性校验必须避免泄漏敏感内容。

## 状态、错误与 provenance

manifest 是必需输入，失败为 `INVALID_MANIFEST`、`DUPLICATE_ID`、`MISSING_MATCHED_NORMAL`、`UNSUPPORTED_LAYOUT` 或 `INPUT_NOT_FOUND`，不可返回 `EMPTY`。provenance 记录源 checksum、解析器版本、规范化警告和行号，不记录密钥。

## 测试

- 单元：表头、角色、ID、sex、SE/PE、多 lane、空 HLA、重复记录。
- 契约：所有 loader 对同一逻辑 manifest 产生相同对象。
- 集成：本地/共享 FS URI 可读性。
- 系统：`TST-SYS-001` 配置预检，无效 manifest 不提交 Slurm。

## 验收与风险

验收：REQ-FUN-001、NFR-009、ACC-001。风险：旧 BAM SE/PE key 校验疑似错误、自定义 HLA 空值判断疑似恒真；先建立 characterization fixture，再按新不变量修正并记录差异。
