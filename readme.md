# fsdb-cli

FSDB 波形查询 CLI + AI 分析 skill。

## 架构

```
fsdb_cli.sh (入口) → fsdb_cli.py (核心)
                        ├── info    → NPI → fsdbdebug
                        ├── scope   → fsdbreport (CSV header parse)
                        ├── value   → fsdbreport
                        ├── range   → fsdbreport
                        ├── export  → fsdbreport
                        ├── strobe  → fsdbreport
                        └── forces  → fsdbreport
```

- Shell: 项目根目录定位、环境变量初始化
- Python: argparse 参数解析、fsdbreport 命令行构建、subprocess 执行
- 纯 Python 标准库，无额外依赖

## 文件说明

| 文件 | 说明 |
|------|------|
| `SKILL.md` | Skill 使用说明（供 AI 读取） |
| `readme.md` | 本文件（供人类阅读） |
| `scripts/fsdb_cli.sh` | Shell 入口 |
| `scripts/fsdb_cli.py` | Python 核心（FsdbCli 类 + argparse） |
| `scripts/check_npi.py` | NPI 环境检测脚本 |

## NPI 状态

Verdi_O-2018.09-SP2 的 pynpi Python API 仅可靠支持以下操作：

| API | 状态 | 说明 |
|-----|------|------|
| `wave.init` / `wave.open` | OK | 初始化与打开 FSDB |
| `wave.min_time` / `wave.max_time` | OK | 返回 `[unit, value]` |
| `wave.scope_by_name` | OK | `scope_by_name(fsdb, name, None)` |
| `wave.iter_child_scope` | OK | `iter_child_scope(scope)` |
| `wave.iter_sig` | OK | `iter_sig(scope)` — 返回句柄但属性不可读 |
| `wave.sig_property_str` | **不可用** | 所有属性返回 None |
| `wave.sig_property` | **不可用** | 返回 `[0, garbage]` |
| `wave.sig_by_name` | **不可用** | 始终返回 None |

结论：2018 版 NPI 不可用于信号查询，信号操作统一走 fsdbreport。

## 开发笔记

- 2018 fsdbreport CSV 头格式 `Time(1ps),...`（非 `Time,`）
- `-level` 参数在 2018 版不支持
- scope 命令 prefix `/tb_top/` 补偿 FSDB 层级
- `subprocess.run(cmd)` 不能用 `stdout=PIPE`，否则 fsdbreport 跳过 CSV 写入
- Python 3.6 兼容：`universal_newlines` 替代 `text`，手动 `stdout/stderr=PIPE` 替代 `capture_output`
