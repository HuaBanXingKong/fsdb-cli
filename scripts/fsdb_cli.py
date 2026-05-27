# ------------------------------------------------------------------
#  File Name     : fsdb_cli.py
#  Last Modified : 2026-05-27 13:34
#  Description   : FSDB 波形查询 CLI 核心逻辑
#    封装 fsdbreport 命令构建、执行和输出管理。
#
#  用法:
#    python fsdb_cli.py <command> [options]
#
#  命令:
#    value   - 查询单个时间点的信号值 (-s 信号 --at 时间)
#    range   - 时间范围内查询信号值 (-s 信号 -bt/--et 时间)
#    export  - 条件表达式触发导出 (-s 信号 --exp 表达式 -bt/--et 时间)
#    strobe  - 边沿采样导出 (--strobe 表达式 -s 信号 -bt/--et 时间)
#    forces  - 查找 force/release/deposit 事件 (-s 信号 [--level N])
#    info    - 查询 FSDB 元数据（时间范围、timescale、版本）
#    scope   - 列出指定层级下的信号路径 (<scope> [--level N])
#
#  通用选项:
#    --fsdb PATH  - FSDB 文件路径 (默认由 shell 传入)
#    --log        - 启用日志输出到 fsdbreportLog 目录
#    -o FILE      - 输出文件 (默认 stdout)
#    --csv        - CSV 格式输出
#    --fmt FMT    - 数值格式: b/o/d/u/h (默认 h)
# ------------------------------------------------------------------
import argparse
import os
import subprocess
import sys
import tempfile

#////////////////////////////////////////////////////////////////////////////
#***************************** Module Variables ****************************#
#////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------
_ENV_FSDB = "FSDB_CLI_DEFAULT_FSDB"
_ENV_LOG_DIR = "FSDB_CLI_DEFAULT_LOG_DIR"

# NPI 输出到 stderr（NPI 库会重定向 stdout）
def _eprint(*a, **kw):
    kw.setdefault("file", sys.stderr)
    print(*a, **kw)

def _init_npi():
    """初始化 2018 NPI API，失败返回 None"""
    try:
        verdi = os.environ.get("VERDI_HOME", "")
        if not verdi:
            return None
        npi_py = os.path.join(verdi, "share", "NPI", "python")
        if npi_py not in sys.path:
            sys.path.insert(0, npi_py)
        import pynpi.wave as wave
        wave.init("test")
        return wave
    except Exception:
        return None

#////////////////////////////////////////////////////////////////////////////
#***************************** Module Functions ****************************#
#////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------
def _resolve_fsdb(cli_fsdb=None):
  if cli_fsdb:
    return os.path.abspath(cli_fsdb)
  env_fsdb = os.environ.get(_ENV_FSDB, "")
  if env_fsdb:
    return os.path.abspath(env_fsdb)
  return os.path.abspath("work/simulation/wave/tb_top.fsdb")

def _resolve_log_dir(cli_log_dir=None):
  if cli_log_dir:
    return cli_log_dir
  return os.environ.get(_ENV_LOG_DIR, "")

def _parse_time(s):
    """解析时间字符串为整数，支持 ns/us/ms/s 后缀，默认 ns"""
    if isinstance(s, (int, float)):
        return int(s)
    s = str(s).strip()
    if not s:
        return None
    multipliers = {"ns": 1, "us": 1000, "ms": 1000000, "s": 1000000000}
    for unit, mul in multipliers.items():
        if s.endswith(unit):
            return int(float(s[:-len(unit)]) * mul)
    return int(float(s))

class FsdbCli:
  """FSDB 波形查询 CLI，封装 fsdbreport 命令"""
  #///////////////////////////////////////////////////////////////////////////#
  #*************************** Class Functions *******************************#
  #///////////////////////////////////////////////////////////////////////////#
  # ---------------------------------------------------------------------------
  def __init__(self, fsdb_path, log_dir=None):
    self.fsdb_path = os.path.abspath(fsdb_path)
    self.log_dir = log_dir

  # ---------------------------------------------------------------------------
  @staticmethod
  def _signal_args(signals):
    """展开信号列表为多个 -s 选项"""
    result = []
    for sig in signals:
      result.extend(["-s", sig])
    return result

  # ---------------------------------------------------------------------------
  def _make_cmd(self, enable_log=False):
    """构建基础 fsdbreport 命令行"""
    cmd = ["fsdbreport", self.fsdb_path]
    if not enable_log:
      cmd.append("-nolog")
    return cmd

  # ---------------------------------------------------------------------------
  def _run(self, cmd, enable_log=False):
    """执行命令，日志模式下切换 cwd 到日志目录"""
    cwd = None
    if enable_log and self.log_dir:
      os.makedirs(self.log_dir, exist_ok=True)
      cwd = self.log_dir
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
      sys.exit(result.returncode)

  # ---------------------------------------------------------------------------
  def range(self, signals, bt, et, fmt="h", csv=False, output=None, enable_log=False):
    """查询信号在时间范围内的值变化（fsdbreport）"""
    cmd = self._make_cmd(enable_log)
    cmd.extend(self._signal_args(signals))
    cmd.extend(["-bt", bt, "-et", et, "-of", fmt])
    if csv:
      cmd.append("-csv")
    if output:
      cmd.extend(["-o", output])
    self._run(cmd, enable_log)
  def value(self, signals, time, fmt="h", output=None, enable_log=False):
    """查询单个时间点的信号值（fsdbreport）"""
    self.range(signals, time, time, fmt=fmt, csv=False, output=output, enable_log=enable_log)

  def export_expr(self, signals, expr, bt, et, fmt="h", csv=False, output=None, enable_log=False):
    """条件表达式为真时导出信号值"""
    cmd = self._make_cmd(enable_log)
    cmd.extend(self._signal_args(signals))
    cmd.extend(["-exp", expr, "-bt", bt, "-et", et, "-of", fmt])
    if csv:
      cmd.append("-csv")
    if output:
      cmd.extend(["-o", output])
    self._run(cmd, enable_log)

  # ---------------------------------------------------------------------------
  def strobe(self, signals, strobe_expr, bt, et, fmt="h", csv=False, output=None, enable_log=False):
    """边沿触发采样导出"""
    cmd = self._make_cmd(enable_log)
    cmd.extend(self._signal_args(signals))
    cmd.extend(["-strobe", strobe_expr, "-bt", bt, "-et", et, "-of", fmt])
    if csv:
      cmd.append("-csv")
    if output:
      cmd.extend(["-o", output])
    self._run(cmd, enable_log)

  # ---------------------------------------------------------------------------
  def forces(self, signal, level=None, bt=None, et=None, no_value=False, output=None, enable_log=False):
    """查找 force/release/deposit 事件"""
    cmd = self._make_cmd(enable_log)
    cmd.append("-find_forces")
    cmd.extend(["-s", signal])
    if level is not None:
      cmd.extend(["-level", str(level)])
    if bt:
      cmd.extend(["-bt", bt])
    if et:
      cmd.extend(["-et", et])
    if no_value:
      cmd.append("-no_value")
    if output:
      cmd.extend(["-o", output])
    self._run(cmd, enable_log)

  # ---------------------------------------------------------------------------
  def info(self):
    """查询 FSDB 元数据（优先 NPI）"""
    wave = _init_npi()
    if wave:
      try:
        fsdb = wave.open(self.fsdb_path)
        if fsdb:
          mt = wave.min_time(fsdb)
          xt = wave.max_time(fsdb)
          _eprint(f"fsdb: {self.fsdb_path}")
          _eprint(f"min_time: {mt[1]} (unit={mt[0]})")
          _eprint(f"max_time: {xt[1]} (unit={xt[0]})")
          _eprint(f"file_size: {round(os.stat(self.fsdb_path).st_size / 1048576, 1)} MB")
          sigs = []
          top = _npi_get_root(wave, fsdb)
          if top:
            _npi_walk_scopes(wave, fsdb, top, lambda s, sc: sigs.append(s))
          _eprint(f"sigs: {len(sigs)}")
          return
      except Exception as e:
        _eprint(f"(NPI skipped: {e})")
    # 降级
    st = os.stat(self.fsdb_path)
    print(f"fsdb: {self.fsdb_path}")
    print(f"file_size_mb: {round(st.st_size / 1048576, 1)}")

  # ---------------------------------------------------------------------------
  def scope(self, scope_path, level=1):
    """列出指定层级下的信号路径（fsdbreport）"""
    if not scope_path.startswith("/"):
      scope_path = "/" + scope_path
    if not scope_path.endswith("*"):
      scope_path = scope_path.rstrip("/") + "/*"
    if not scope_path.startswith("/tb_top/"):
      scope_path = "/tb_top" + scope_path
    if self._scope_try(scope_path, level):
      return
    _eprint(f"(no signals matching '{scope_path}')")

  def _scope_try(self, scope_path, level):
    cmd = ["fsdbreport", self.fsdb_path, "-nolog"]
    cmd.extend(["-s", scope_path, "-bt", "0ns", "-et", "0ns", "-csv"])
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".csv")
    os.close(tmp_fd)
    try:
      cmd.extend(["-o", tmp_path])
      subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
      if not os.path.exists(tmp_path) or os.path.getsize(tmp_path) == 0:
        return False
      with open(tmp_path, "r") as f:
        header = f.readline().strip()
      if header.startswith("Time"):
        sigs = header.split(",")[1:]
        for sig in sigs:
          sys.stdout.write(sig + "\n")
        sys.stdout.flush()
        return len(sigs) > 0
      return False
    finally:
      if os.path.exists(tmp_path):
        os.unlink(tmp_path)

  # ---------------------------------------------------------------------------
  def __repr__(self):
    return f"FsdbCli(fsdb='{self.fsdb_path}')"

  # ---------------------------------------------------------------------------
  @classmethod
  def run_from_args(cls, args):
    """从 argparse 解析结果创建实例并分发到对应命令"""
    fsdb = _resolve_fsdb(args.fsdb)
    log_dir = _resolve_log_dir(args.log_dir)
    cli = cls(fsdb, log_dir)
    if args.command == "value":
      cli.value(args.signals, args.at, fmt=args.fmt, output=args.output, enable_log=args.log)
    elif args.command == "range":
      cli.range(args.signals, args.bt, args.et, fmt=args.fmt, csv=args.csv,
                output=args.output, enable_log=args.log)
    elif args.command == "export":
      cli.export_expr(args.signals, args.exp, args.bt, args.et, fmt=args.fmt,
                      csv=args.csv, output=args.output, enable_log=args.log)
    elif args.command == "strobe":
      cli.strobe(args.signals, args.strobe_expr, args.bt, args.et, fmt=args.fmt,
                 csv=args.csv, output=args.output, enable_log=args.log)
    elif args.command == "forces":
      cli.forces(args.signal, level=args.level, bt=args.bt, et=args.et,
                 no_value=args.no_value, output=args.output, enable_log=args.log)
    elif args.command == "info":
      cli.info()
    elif args.command == "scope":
      cli.scope(args.scope, level=args.level)

#////////////////////////////////////////////////////////////////////////////
#************************* __name__ == "__main__" **************************#
#////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------
if __name__ == "__main__":
  common = argparse.ArgumentParser(add_help=False)
  common.add_argument("--fsdb", default=None, help="FSDB file path")
  common.add_argument("--log-dir", default=None, help="Log directory for fsdbreportLog")
  common.add_argument("--log", action="store_true", default=False, help="Enable fsdbreport logging")
  common.add_argument("-o", "--output", default=None, help="Output report file")

  parser = argparse.ArgumentParser(description="FSDB waveform query CLI (fsdbreport wrapper)")
  subparsers = parser.add_subparsers(dest="command")

  # value ----------------------------------------------------------------
  value_p = subparsers.add_parser("value", parents=[common],
    help="Query signal values at a single time point")
  value_p.add_argument("-s", "--signals", nargs="+", required=True,
    help="Signal paths to query")
  value_p.add_argument("--at", required=True, help="Time point (e.g. 500ns)")
  value_p.add_argument("--fmt", default="h", choices=["b", "o", "d", "u", "h"],
    help="Value format (default: h)")

  # range ----------------------------------------------------------------
  range_p = subparsers.add_parser("range", parents=[common],
    help="Query signal values over a time range")
  range_p.add_argument("-s", "--signals", nargs="+", required=True,
    help="Signal paths to query")
  range_p.add_argument("--bt", required=True, help="Begin time (e.g. 100ns)")
  range_p.add_argument("--et", required=True, help="End time (e.g. 200ns)")
  range_p.add_argument("--fmt", default="h", choices=["b", "o", "d", "u", "h"],
    help="Value format: b=bin o=oct d=dec u=unsigned h=hex (default: h)")
  range_p.add_argument("--csv", action="store_true", help="CSV output format")

  # export ---------------------------------------------------------------
  export_p = subparsers.add_parser("export", parents=[common],
    help="Export signals when expression is true")
  export_p.add_argument("-s", "--signals", nargs="+", required=True,
    help="Signal paths to query")
  export_p.add_argument("--exp", required=True, help="Trigger expression (e.g. \"valid==1\")")
  export_p.add_argument("--bt", required=True, help="Begin time (e.g. 100ns)")
  export_p.add_argument("--et", required=True, help="End time (e.g. 200ns)")
  export_p.add_argument("--fmt", default="h", choices=["b", "o", "d", "u", "h"],
    help="Value format (default: h)")
  export_p.add_argument("--csv", action="store_true", help="CSV output format")

  # strobe ---------------------------------------------------------------
  strobe_p = subparsers.add_parser("strobe", parents=[common],
    help="Edge-triggered sampling export")
  strobe_p.add_argument("--strobe", required=True, dest="strobe_expr",
    help="Strobe expression (e.g. \"top.clk==1\")")
  strobe_p.add_argument("-s", "--signals", nargs="+", required=True,
    help="Signal paths to query")
  strobe_p.add_argument("--bt", required=True, help="Begin time (e.g. 100ns)")
  strobe_p.add_argument("--et", required=True, help="End time (e.g. 200ns)")
  strobe_p.add_argument("--fmt", default="h", choices=["b", "o", "d", "u", "h"],
    help="Value format (default: h)")
  strobe_p.add_argument("--csv", action="store_true", help="CSV output format")

  # forces ---------------------------------------------------------------
  forces_p = subparsers.add_parser("forces", parents=[common],
    help="Find force/release/deposit events")
  forces_p.add_argument("-s", "--signal", required=True, help="Signal or scope to search")
  forces_p.add_argument("--level", type=int, default=None, help="Hierarchy depth under scope")
  forces_p.add_argument("--bt", default=None, help="Begin time (e.g. 100ns)")
  forces_p.add_argument("--et", default=None, help="End time (e.g. 200ns)")
  forces_p.add_argument("--no-value", action="store_true", dest="no_value",
    help="Disable value display")

  # info ----------------------------------------------------------------
  info_p = subparsers.add_parser("info", parents=[common],
    help="Show FSDB metadata (time range, timescale, etc.)")

  # scope ----------------------------------------------------------------
  scope_p = subparsers.add_parser("scope", parents=[common],
    help="List signals under a hierarchy scope")
  scope_p.add_argument("scope", help="Scope path (e.g. /tb_top/u_dut)")
  scope_p.add_argument("--level", type=int, default=1,
    help="Hierarchy depth (default: 1, 0=all levels)")

  args = parser.parse_args()
  if args.command is None:
    parser.print_help()
    sys.exit(1)
  FsdbCli.run_from_args(args)
