# ADR-001：自研系统采用 Python 端口/适配器架构

- 状态：Accepted
- 日期：设计基线
- 关联：NFR-001～006，REQ-FUN-023～025

## 背景

现有 Nextflow DSL1、Groovy、Python、R、Perl、AWK 和 Shell 混合了承担编排、领域策略和格式转换。逐 process 翻译会保留耦合，无法可靠增加替代方法。

## 决策

所有自研控制与业务逻辑使用 Python，并分为 `domain`、`application`、`ports`、`plugins`、`infrastructure`、`workflows`、`interfaces` 和 `reporting`。领域层仅依赖标准 Python/领域类型；第三方算法通过 adapter 与容器保留其原语言。

接口按科学职责定义；一个 capability 实现可以规划多个原子执行任务。CLI 调用 SDK，配置映射 Pydantic 模型。

## 结果

优点：边界可测、实现可替换、科学 policy 独立、避免 DSL1 锁定。代价：需要设计 typed artifact、插件与执行抽象；迁移期间新旧系统并存。

## 未选方案

- 逐行转换 Nextflow 为 Python：保留单体耦合。
- 保持多语言自研脚本：测试和依赖治理困难。
- 重写所有第三方算法：科学与成本风险不可接受。

## 验证

公共领域 API strict type-check；领域测试不启动容器；依赖图无向外层反向依赖；每个插件可在核心无修改下注册。