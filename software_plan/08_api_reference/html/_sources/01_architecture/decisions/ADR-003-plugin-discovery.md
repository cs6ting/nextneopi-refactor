# ADR-003：使用 PyPA entry points 发现插件

- 状态：Accepted
- 关联：REQ-FUN-024，NFR-004、023

## 背景

相同科学 capability 需要持续增加实现。如果维护中央 `if/else` 或扫描源码目录，核心发布与插件生命周期耦合，冲突和安全边界不清晰。

## 决策

插件 distribution 通过命名空间 entry point（建议 `nextneopi.capabilities`）发布 `PluginDescriptor` 与 factory。`PluginRegistry` 使用 `importlib.metadata.entry_points()` 枚举；`CapabilitySelector` 根据请求、能力和 policy 选择。

descriptor 必须包含 capability、implementation ID/version、schema、assay/layout/molecule/MHC 支持、参考、容器 digest、资源、license、scatter、空输入和降级语义。ID 冲突默认失败，不按安装顺序静默覆盖。

## 后果

实现可独立发布；核心 recipe 无需修改。插件属于可执行代码，生产环境必须使用 allow-list、版本锁定、来源审查和 contract test。

## 未选方案

- 手工 registry：核心频繁修改。
- 动态扫描目录：不可复现且冲突行为不稳定。
- 仅用字符串导入路径：缺少 descriptor 与安装元数据。

## 验证

安装测试插件后 `nextneopi plugins` 可发现；卸载后清晰报缺失；重复 ID、版本不兼容和 capability 不匹配在 planning 阶段失败。