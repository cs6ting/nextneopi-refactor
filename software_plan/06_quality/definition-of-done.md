# Definition of Done

一个模块/接口/插件只有满足以下条件才算 Done。

## 设计

- 关联 REQ/NFR、MOD、IF、ADR 和风险。
- 职责/非职责、输入输出、不变量、状态和错误明确。
- capability/实现差异、配置和迁移影响已评审。
- 科学语义由领域负责人确认。

## 实现

- 自研逻辑是可导入 Python；CLI 不含业务逻辑。
- 公共 API 有类型/docstring，数据使用 Pydantic/dataclass。
- 第三方命令通过 adapter、argv 和固定 digest 容器。
- 无运行时下载/patch、无 `shell=True`、无源码/reference 写入。
- 结果使用 typed artifact 和五类 ResultStatus。
- 模块已接入至少一个 recipe，能产生可见工作增量。

## 测试

- 先有失败测试，再实现，再重构。
- 领域分支覆盖率达到目标；边界/property tests 完整。
- 插件 contract 和 native-output collector tests 通过。
- 受影响 integration/system/scientific tests 通过。
- 空、失败、unsupported、resume/cache 和 provenance 有断言。

## 文档与运维

- 接口、配置 Schema/YAML、resource model、容器/reference/license 更新。
- runbook/错误建议可行动；日志脱敏。
- 需求—模块—接口—测试—验收追踪完整。
- Demo 命令、输入、预期输出和验收记录可复现。

## 评审与发布

软件、生物信息、平台评审按变更范围完成；无未解释科学差异或开放 P0 风险；CI 门禁通过；版本/changelog/迁移说明明确。仅“代码已写”不算完成。