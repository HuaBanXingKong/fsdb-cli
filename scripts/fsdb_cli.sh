#!/bin/bash
# ------------------------------------------------------------------
#  File Name     : fsdb_cli.sh
#  Last Modified : 2026-05-27 17:00
#  Description   : FSDB 波形查询 CLI 入口
#    计算项目根目录默认路径，导出环境变量后委托 Python 核心执行。
# ------------------------------------------------------------------
set -euo pipefail

# ---------------------------------------------------------------------------
# 路径计算
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"

export FSDB_CLI_DEFAULT_FSDB="$PROJECT_ROOT/work/simulation/wave/tb_top.fsdb"
export FSDB_CLI_DEFAULT_LOG_DIR="$PROJECT_ROOT/work/simulation/wave/fsdbreportLog"

# ---------------------------------------------------------------------------
# 无参数时显示帮助
if [ $# -eq 0 ]; then
  echo "Usage: fsdb_cli.sh <command> [options]"
  echo ""
  echo "FSDB 波形查询 CLI，封装 fsdbreport 命令。"
  echo ""
  echo "Commands:"
  echo "  value   查询单个时间点的信号值"
  echo "  range   查询信号时间范围内的值变化"
  echo "  export  条件表达式触发时导出信号值"
  echo "  strobe  边沿触发采样导出"
  echo "  forces  查找 force/release/deposit 事件"
  echo "  info    查看 FSDB 元数据（时间范围、timescale）"
  echo "  scope   列出指定层级下的信号路径"
  echo ""
  echo "Common options:"
  echo "  --fsdb PATH   FSDB 文件 (默认: work/simulation/wave/tb_top.fsdb)"
  echo "  --log-dir DIR 日志目录 (默认: work/simulation/wave/fsdbreportLog)"
  echo "  --log         启用日志输出"
  echo "  -o FILE       输出文件 (默认: stdout)"
  echo "  --csv         CSV 格式输出"
  echo "  --fmt FMT     数值格式: b/o/d/u/h (默认: h)"
  echo ""
  echo "Tip: 表达式含 \$ * 等特殊字符时，用单引号包裹以避免 shell 展开。"
  echo ""
  echo "Examples:"
  echo "  fsdb_cli.sh value -s /tb_top/data[31:0] /tb_top/valid --at 500ns"
  echo "  fsdb_cli.sh range -s /tb_top/clk /tb_top/rst_n --bt 100ns --et 500ns"
  echo "  fsdb_cli.sh export -s /tb_top/data --exp 'valid==1' --bt 0ns --et 10us --csv"
  echo "  fsdb_cli.sh strobe --strobe '/tb_top/clk==1' -s /tb_top/data --bt 0ns --et 1us"
  echo "  fsdb_cli.sh forces -s '/tb_top/u_dut/*' --level 2 --bt 100ns"
  echo "  fsdb_cli.sh info"
  echo "  fsdb_cli.sh scope /tb_top/u_dut --level 2"
  echo ""
  echo "Run 'fsdb_cli.sh <command> --help' for command-specific options."
  exit 1
fi

# ---------------------------------------------------------------------------
# 委托 Python
python3 "$SCRIPT_DIR/fsdb_cli.py" "$@"
