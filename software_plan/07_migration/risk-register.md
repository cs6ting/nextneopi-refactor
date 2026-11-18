# 风险登记

| ID | 风险 | 等级 | 缓解与验证 |
|---|---|---|---|
| RISK-001 | Pydra 1.0 alpha 在真实 Slurm 能力/稳定性不足 | 高 | 阶段1 conformance spike；端口隔离；不通过则 Snakemake |
| RISK-002 | 单体流程中隐藏的科学依赖在拆分时丢失 | 高 | 核对分阶段 BAM、HLA 的 RNA reads 入口、NeoFuse 多产物、常规候选的定相与纯度、MixMHC2pred 的 HLA-HD 证据；逐边回放与纵向验证 |
| RISK-003 | 缺少旧版对照工件时，无法证明等价 | 高 | 先固定一个配对 WES DNA 病例的边界工件和实际版本。候选替换另用适用的独立真值，HG008 按具体 draft、范围和数据版本标注 |
| RISK-004 | 第三方工具版本/许可/资源不可再分发 | 高 | descriptor/license preflight、私有镜像、bundle manifest |
| RISK-005 | Strelka/Mutect1 输出 glob 疑似拼写错误导致旧链失败 | 中 | characterization task；新 collector 按真实 companion 校验，不复制 typo |
| RISK-006 | BAM SE/PE 校验旧 key 疑似错误 | 高 | manifest fixture 覆盖 tumor/normal mixed layout；新不变量 fail-fast |
| RISK-007 | 空 custom HLA 被视为存在 | 高 | 无 HLAfile fixture；显式 Optional 值；required MHC plan 检查 |
| RISK-008 | `maleRef` Boolean/字符串比较导致 sex 参数错误 | 高 | XX/XY/UNKNOWN contract 和 CNV集成；不使用裸布尔传播 |
| RISK-009 | 3' tag 分支可能引用未定义 channel | 高 | 旧流程 characterization；新 capability 以 `SKIPPED_UNSUPPORTED` 建模 |
| RISK-010 | HLA RNA parser 参数/可变默认列表疑似缺陷 | 高 | 单元 regression；纯函数/不可变输入；决策 trace |
| RISK-011 | 高置信共识同位置不同 ALT 可能误判支持 | 严重 | normalized allele identity；same-position-different-ALT 必测；科学评审 |
| RISK-012 | `add_CCF.py` ordered merge forward-fill 可能传播错误 CCF | 严重 | unmatched fixture；新 join 必须精确 identity，未匹配为 missing |
| RISK-013 | TMB 坐标、contig>40Mb、denominator 口径隐式 | 严重 | 口径版本化；先比较 numerator/denominator；边界 property tests |
| RISK-014 | `errorStrategy ignore`/optional 输出隐藏关键失败 | 高 | 五类状态、recipe failure policy、报告显示 failed section |
| RISK-015 | cache key 不完整造成错误复用 | 严重 | ADR-004、key sensitivity tests、损坏缓存隔离 |
| RISK-016 | 运行时下载/patch 与 marker 导致供应链漂移 | 高 | digest 镜像、离线 E2E、禁止 runtime network |
| RISK-017 | 参考、VEP、GENCODE、旧数据库版本混搭 | 高 | ReferenceBundle build/dictionary/版本兼容规则和 checksum |
| RISK-018 | Slurm 共享 FS latency、任务洪峰和 scratch 不足 | 中 | site profile、提交/查询限流、node scratch、压力测试 |
| RISK-019 | 新抽象过度通用，抹平方法能力 | 高 | capability dimensions、负例 contract、领域评审 |
| RISK-020 | 80+ 文档与实现漂移 | 中 | CI schema/link/trace checks；DoD 要求同步；接口版本化 |
| RISK-021 | vendored Perl/R/patch ownership 不清 | 高 | 许可审查；不明资产不进入发布镜像；记录来源 |
| RISK-022 | `make_release.sh` 引用漂移文件 | 中 | 不复用为新发布入口；Python packaging/release checklist |
| RISK-023 | 换定相工具后，pVACseq 可能忽略用 GT/`PS` 表示的相位 | 高 | 验证旧版 pVACtools 5.3.0 的 VCF `HP` 读取约定与适配。测试顺反式、跨 phase block、未定相及其 WT/MT 肽 |
| RISK-024 | 将 BA、EL 和 IM 使用同一阈值或综合分数，改变候选去留 | 高 | 按模型和任务记录版本、单位、范围、覆盖与阈值。测试旧版综合百分位、pVAC 更新与 CSiN 等消费者 |
| RISK-025 | 替代模型的评测病例、肽或同源序列进入了训练集 | 高 | 记录训练交集与未知项，按病例、队列及肽簇划分。分别展示共同可评分集合和全部候选的覆盖 |
| RISK-026 | 旧 NetMHCstab 联网路径影响离线复现和数据流向 | 高 | 锁定实际 pVACtools 版本并检查启用配置。使用公开病例或已有稳定性工件验证兼容，记录本地可用能力与回退选择 |

## 管理规则

等级为严重/高的风险必须有负责人、目标里程碑和验证测试后才可进入相关实现阶段。风险关闭需附测试/ADR/等价报告；仅“未再出现”不能关闭。

复盘入口见 [当前代码到目标架构映射](current-to-target-mapping.md) 和 [第二层算法清单](../02_modules/second-layer-algorithm-inventory.md)。替代模型待评估项在 [增量迁移路线](incremental-roadmap.md#首批算法替代试点) 中跟踪。
