# skill install

安装官方 rabetbase skill 包。

> **风险等级：write** — 全局安装 npm 包。

## 命令

```bash
rabetbase skill install

# 别名
rabetbase skills
```

## 参数

无。

## 行为

执行 `npx -y skills add lovrabet/rabetbase --global`，全局安装 rabetbase skill。

若设置了环境变量 `RABETBASE_SKIP_NPX_SKILLS=1`，则跳过安装（假定 skill 已存在）。

## 输出

- 成功：`rabetbase skill installed`
- 跳过：`Skipped npx (RABETBASE_SKIP_NPX_SKILLS=1); assuming skill is already present.`
- 失败：报错并提示检查网络

## 提示

- 通常在 `rabetbase project upgrade` 的第 6 步自动执行
- 手动执行仅当 skill 丢失或需要重装时
- `rabetbase skills` 是 deprecated alias

## 参考

- [SKILL.md](../SKILL.md)
- [project upgrade](rabetbase-project-upgrade.md)
