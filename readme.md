# fsdb-cli 状态

## 当前进度

已实现 7 个 CLI 命令，覆盖 fsdbreport 主要功能：

| 命令 | 状态 | 说明 |
|------|------|------|
| `value` | 完成 | 单时间点多信号取值，委托 `range` 令 bt==et |
| `range` | 完成 | 时间范围查询，支持 `--fmt` `--csv` |
| `export` | 完成 | 条件表达式触发导出 |
| `strobe` | 完成 | 边沿采样导出 |
| `forces` | 完成 | force/release/deposit 事件查找 |
| `info` | 完成 | FSDB 元数据，优先用 `fsdbdebug -info`，降级为文件信息 |
| `scope` | 完成 | 层级信号发现，用 fsdbreport CSV 头行解析，零 C++ |

架构：Shell（路径检测）→ Python（FsdbCli 类 → fsdbreport 命令行）。纯 Python 标准库，不依赖 NPI。

## NPI/Python API 集成

- **目标**：引入 pynpi 作为可选后端，实现毫秒级查询 + Python 原生数据结构
- **依赖**：`VERDI_HOME/share/NPI/python/pynpi`
- **当前状态**：`check_npi.py` 检测脚本已就绪，用户 @HuaBanXingKong 正在 RockyLinux810 服务器上验证。Verdi 版本 `O-2018.09-SP2`，NPI/python 目录存在，`PYTHONPATH` 待配置后重试

## 参照仓库

分析过以下 GitHub 仓库，已提取可用思路：

| 仓库 | 特点 | 借鉴项 |
|------|------|--------|
| nayiri-k/fsdb-parse | C++ FsdbReader + `fsdbdebug` | `info` 命令的数据源 |
| avidan-efody/wave_rerunner | pynpi `sig_hdl_value_between` | NPI 后端参考 |
| ekiwi/wellen | FST/VCD only（不含 FSDB） | 无关 |

## 不做的

- 不做 C++ 编译——维护成本大于收益，fsdbreport 已覆盖核心查询
- 不做 daemon 进程——xwave 的路子，本 skill 定位是轻量包装，不是平台
- 不做协议级解析（APB/AXI）——这是 AI 分析层的事，不放在 CLI 里
