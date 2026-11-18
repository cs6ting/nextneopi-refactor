# Python 编码规范

## 架构与依赖

- `domain` 不导入 infrastructure/plugin framework；跨模块只用公开 contract。
- 函数/类保持单一职责；科学 policy 与工具 adapter 分离。
- 不允许全局 mutable state、隐式 singleton、mutable default 参数。
- 时间、UUID、文件系统和进程执行通过端口注入以便测试。

## 类型与数据

- 公共函数全类型标注，strict type-check。
- 稳定配置/外部数据用 Pydantic；内部不可变值对象优先 frozen dataclass。
- 使用 `Path/URI` 类型而非裸字符串；sample/case/reference ID 使用专用类型。
- 大型 BAM/VCF 用 `ArtifactRef` 流转，不整体读入内存。
- 坐标约定、单位、缺失值和 schema version 显式。

## 进程与安全

- `subprocess`/runner 使用 argv；禁止 `shell=True` 和用户输入拼 shell。
- 环境变量 allow-list；stdout/stderr 限制和脱敏。
- 输入/reference 只读，输出写 staging 后原子 commit。
- 网络、下载、安装和 patch 只允许部署构建阶段。

## 错误与日志

- 预期错误转 `NextNeoPiError`，保留 cause；禁止裸 `except`、吞异常或 `|| true`。
- 合法空返回 `EMPTY`；失败不创建假空文件。
- 结构化日志使用 correlation IDs，不记录密钥/reads/完整变异。

## 测试和文档

- 测试名描述 given/when/then；fixture 小且有科学解释。
- 浮点比较明确容差；不依赖行顺序/压缩字节。
- 公共接口 docstring 说明语义、单位、状态和异常。
- TODO 必须关联 issue/风险和退出条件。

## 工具约定

具体 format/lint/type/test 工具与精确版本在项目初始化时锁定；不得使用开放版本范围。生成代码和 vendor 代码单独配置，不能降低自研代码门禁。