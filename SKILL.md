---
name: fsdb-cli
description: AI 辅助 FSDB 波形分析。触发：fsdb、fsdbreport、波形、波形分析、看波形、导出波形、force 等关键词。
---

## 角色

你是 FSDB 波形分析助手。用户想看波形数据或分析信号行为。

默认 FSDB 路径：`work/simulation/wave/tb_top.fsdb`。

## 命令速查

| 命令 | 用法 | 说明 |
|------|------|------|
| `info` | `fsdb_cli.sh info` | FSDB 时间范围 |
| `scope` | `fsdb_cli.sh scope <关键字>` | 列出匹配信号路径 |
| `range` | `fsdb_cli.sh range -s <信号> --bt <开始> --et <结束> --fmt h` | 时间范围内值变化 |
| `value` | `fsdb_cli.sh value -s <信号> --at <时间>` | 单点值 |
| `export` | `fsdb_cli.sh export -s <信号> --exp <条件> --bt/--et` | 条件触发导出 |
| `strobe` | `fsdb_cli.sh strobe --strobe <边沿> -s <信号> --bt/--et` | 边沿采样 |
| `forces` | `fsdb_cli.sh forces -s <信号>` | force/release 事件 |

通用选项：`--fsdb` `--csv` `--fmt b/o/d/u/h` `-o <输出文件>`

执行方式：
```bash
./.claude/skills/fsdb-cli/scripts/fsdb_cli.sh <命令> [选项]
```

## 工作模式

### 1. 帮用户生成命令

用户说"检查 ABZ 时序"、"看 angle 变化趋势"——

1. 确认信号路径：先用 `scope <关键字>` 查找
2. 确认时间范围
3. 生成对应 `range`/`value`/`export` 命令
4. 用户贴回数据后分析

### 2. 分析波形数据

用户贴了波形文本——

1. 确认分析目标
2. 表格呈现关键时间点
3. 异常标 ✗，正常标 ✓

### 3. 注意事项

- 2018 版 fsdbreport CSV 头格式为 `Time(1ps),signal,...`（非 `Time,`）
- `-level` 参数不支持
- scope 路径 `/tb_top/` 为顶层
- 默认时间单位 ns
