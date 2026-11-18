# API 稳定性

## 级别

| 级别 | 保证 | 使用建议 |
|---|---|---|
| **Stable** | 当前 major 内签名、schema、错误 code 和科学语义保持兼容 | 生产 recipe/插件可依赖 |
| **Beta** | 已测试并可用于研究运行；可能在 minor release 经迁移说明变化 | 首期实现默认级别 |
| **Experimental** | 用于验证能力或算法；可发生破坏变化 | 仅显式 opt-in |
| **Internal** | 无兼容保证，不在公共 index re-export | 禁止外部依赖 |

## 提升条件

Beta → Stable 需要：contract tests 100%、领域分支覆盖率达标、local/Slurm E2E、typed empty/failure、provenance、至少一个 recipe、科学等价和两个发布周期无 P0/P1 回归。Experimental → Beta 还需明确科学语义和 capability matrix。

## 弃用流程

1. 新版本标记 `deprecated_since`、替代 symbol 和迁移示例。
2. 至少保留一个 minor release；Stable API 默认保留两个。
3. 运行时发结构化 deprecation event，文档明显告警。
4. 下一个 major 才删除，除非存在严重安全/科学错误。

## 版本维度

- Core package version：整体发行。
- API contract version：Request/Result 与科学语义。
- Implementation version：具体方法/adapter。
- Data schema version：持久化工件结构。
- Config schema version：YAML 结构。
- Container/reference digest：运行依赖身份。

这些版本必须分别记录，不以 core version 替代。

## 兼容判断

破坏性变化包括：字段删除/重命名、返回状态语义变化、allele identity 改变、minimum caller 计数改变、坐标/单位变化、错误 code 删除、允许失败静默降级。添加 optional summary 字段通常为 minor。

## 设计期规则

本文档中的签名是 Proposed API baseline。实现阶段若发现不可实现或科学不正确，先修改 software plan/ADR/API 文档并评审，再写代码；不得实现后反向宣称文档过期。