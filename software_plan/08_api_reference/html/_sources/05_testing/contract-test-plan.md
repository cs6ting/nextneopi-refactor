# 契约测试计划

## 目标

同 capability 的所有 implementation 通过统一 conformance suite；验证 adapter 的 `validate/plan/collect`、descriptor、命令安全和 typed result，不把工具科学结果彼此强行等价。

## 通用插件套件 `TST-CONTRACT-PLG-001`

1. descriptor 通过 JSON Schema，ID/version 唯一。
2. 支持/不支持 request 与 capability 声明一致。
3. `validate` 无网络、无写入、错误可汇总。
4. `plan` 确定性，argv 独立且无 `shell=True`。
5. mount 最小权限，reference/input 只读，license 脱敏。
6. resources 满足 minimum 且可被 site override。
7. `collect` 区分 materialized/empty/failed，拒绝缺文件/索引/字段。
8. container/collector/schema 变化使 cache key 变化。
9. provenance 含 implementation、镜像、参数、parents。

## 领域套件

| ID | 接口 | 必测差异 |
|---|---|---|
| TST-CONTRACT-READ-001 | IF-READ-* | FASTQ/BAM、SE/PE、NoTrim/fastp |
| TST-CONTRACT-ALN-001 | IF-ALN-* | RG/index/reference、scatter gather |
| TST-CONTRACT-VAR-001 | IF-VAR-001～003 | Mutect/VarScan/Strelka native FORMAT、empty VCF |
| TST-CONTRACT-CONS-001 | IF-VAR-004 | primary-confirmed 与失败 caller |
| TST-CONTRACT-ANN-001 | IF-ANN/PHS | VEP schema、phase evidence level |
| TST-CONTRACT-HLA-001 | IF-HLA-* | class-I/II、custom、resolution、pairing |
| TST-CONTRACT-CNV-001 | IF-CNV/PUR | feature flags、segment/purity、fallback |
| TST-CONTRACT-CCF-001 | IF-CCF/TMB | required capabilities、numeric schema |
| TST-CONTRACT-RNA-001 | IF-RNA/FUS/SPL | protocol、strand、unsupported state |
| TST-CONTRACT-NEO-001 | IF-NEO/IMM/REP | candidate identity、model applicability、license |
| TST-CONTRACT-RPT-001 | IF-RPT-* | section states、machine-readable summary |

## Backend/Store 契约

`TST-CONTRACT-BE-001` 对 local/Pydra/Snakemake backend 运行同一 DAG：fan-out/fan-in、retry、cancel、case isolation、events。`TST-CONTRACT-STORE-001` 验证 staging/commit/cache/publish/GC、并发和损坏缓存。

## Native output fixture

每个 tool adapter 至少包含：正常结果、合法空结果、缺必需文件、旧/新小版本 schema 差异、非零退出和损坏内容。fixture metadata 记录工具/镜像/reference/命令/checksum。

## 通过标准

conformance suite 100% 通过；不支持用 expected-failure 长期绕过。差异能力应在 descriptor 排除 request，而不是在运行后随机失败。