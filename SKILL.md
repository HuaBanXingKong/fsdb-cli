---
name: fsdb-cli
description: AI 辅助 FSDB 波形分析。触发：fsdb、fsdbreport、波形、波形分析、看波形、导出波形、force、SDF 等关键词。
---

## 概述

本 skill 提供两层能力：

1. **CLI 工具** — `fsdb_cli.sh` 封装 fsdbreport 常用操作为快捷命令
2. **AI 分析** — 读取导出的波形文本，做时序检查、数据校验、异常发现

FSDB 默认路径：`work/simulation/wave/tb_top.fsdb`，日志目录：`work/simulation/wave/fsdbreportLog`。

## CLI 工具

### 架构

```
fsdb_cli.sh (入口) → 计算项目根目录、导出环境变量 → fsdb_cli.py (核心)
                                                            │
                                                    构建 fsdbreport 命令行
                                                    执行 fsdbreport
                                                    管理日志输出目录
```

- Shell 层：路径检测、帮助展示、环境初始化
- Python 层：argparse 参数解析、FsdbCli 命令构建、subprocess 执行
- 默认 `-nolog` 抑制日志目录，`--log` 启用后输出到 `$logDir/fsdbreportLog/`

### 命令速查

| 命令 | 必需参数 | 说明 |
|------|----------|------|
| `value` | `-s` `--at` | 查询单个时间点的信号值 |
| `range` | `-s` `--bt` `--et` | 查询信号时间范围内的值变化 |
| `export` | `-s` `--exp` `--bt` `--et` | 条件表达式触发时导出 |
| `strobe` | `--strobe` `-s` `--bt` `--et` | 边沿触发采样导出 |
| `forces` | `-s` | 查找 force/release/deposit 事件 |
| `info` | — | 查看 FSDB 元数据（时间范围、timescale） |
| `scope` | `<scope>` | 列出指定层级下的信号路径 |

通用选项：`--fsdb`(FSDB路径) `--log`(启用日志) `--log-dir`(日志目录) `-o`(输出文件) `--csv`(CSV格式) `--fmt`(b/o/d/u/h，默认 h)

### 使用示例

```bash
# 单点查询
./.claude/skills/fsdb-cli/scripts/fsdb_cli.sh value -s /tb_top/data[31:0] /tb_top/valid --at 500ns

# 时间范围查询
./.claude/skills/fsdb-cli/scripts/fsdb_cli.sh range -s /tb_top/clk /tb_top/rst_n --bt 100ns --et 500ns

# 条件表达式导出
./.claude/skills/fsdb-cli/scripts/fsdb_cli.sh export -s /tb_top/data --exp 'valid==1' --bt 0ns --et 10us --csv

# 边沿采样
./.claude/skills/fsdb-cli/scripts/fsdb_cli.sh strobe --strobe '/tb_top/clk==1' -s /tb_top/data --bt 0ns --et 1us

# 查找 force 事件
./.claude/skills/fsdb-cli/scripts/fsdb_cli.sh forces -s '/tb_top/u_dut/*' --level 2 --bt 100ns

# 查看 FSDB 元数据
./.claude/skills/fsdb-cli/scripts/fsdb_cli.sh info

# 列出层级下信号
./.claude/skills/fsdb-cli/scripts/fsdb_cli.sh scope /tb_top/u_dut --level 2
```

## AI 工作模式

### 模式一：生成导出命令

用户描述了需求但没给数据——"帮我看下 xxx 信号有没有异常"、"检查下 ABZ 时序对不对"。

1. 问清信号路径和分析目标
2. 根据目标确定导出范围（时间、条件）
3. 生成 fsdbreport 命令（优先使用 `fsdb_cli.sh`）
4. 用户贴回数据后，分析回答

### 模式二：分析波形数据

用户直接贴了波形文本——"分析下这段波形"。

1. 确认分析目标（时序检查？数据校验？异常查找？）
2. 解析数据，用表格呈现关键时间点
3. 异常明确标出时间点和数值（✗ 异常，✓ 正常）

### 模式三：仅生成命令

用户只想要命令，不需要分析。简化为输出命令，不做额外解释。

## AI 交互风格

- 简短直接，先出结果再补说明
- 数据多时用表格呈现关键时间点
- 需要补充信息时简短反问

## 附录：fsdbreport 参数速查

| 参数 | 说明 | 示例 |
|------|------|------|
| `-s` | 信号路径（/开头） | `-s "/tb_top/clk"` |
| `-bt` | 开始时间 | `-bt 100ns` |
| `-et` | 结束时间 | `-et 5000ns` |
| `-o` | 输出文件 | `-o wave.txt` |
| `-exp` | 触发条件 | `-exp "valid==1"` |
| `-csv` | CSV 格式输出 | `-csv` |
| `-level` | 层级深度（与 `-s` 配合） | `-level 2` |
| `-find_forces` | 查找 force 事件 | `-find_forces` |
| `-strobe` | 边沿采样条件 | `-strobe "/clk==1"` |
| `-nolog` | 禁止生成 fsdbreportLog | `-nolog` |
| `-log` | 指定日志文件 | `-log err.log` |
| `-of` | 数值格式：b/o/d/u/h | `-of h` |

默认时间单位为 ns。信号路径用 `/` 开头，含通配符 `*` 时需加 `-level`。
