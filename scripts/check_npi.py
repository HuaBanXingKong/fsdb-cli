#!/usr/bin/env python3
# ------------------------------------------------------------------
#  File Name     : check_npi.py
#  Last Modified : 2026-05-27 17:00
#  Description   : 检测 NPI/Python API 是否可用
#    兼容 Verdi_O-2018.09-SP2 函数式 API
# ------------------------------------------------------------------
"""python3 check_npi.py [fsdb_path]"""

import os
import sys

FSDB_PATH = sys.argv[1] if len(sys.argv) > 1 else "work/simulation/wave/tb_top.fsdb"
if not os.path.isabs(FSDB_PATH):
    FSDB_PATH = os.path.abspath(FSDB_PATH)

def _print(*a, **kw):
    sys.stderr.write(" ".join(str(x) for x in a) + "\n")
    sys.stderr.flush()

errors = []

def check(name, ok, detail=""):
    mark = "OK" if ok else "FAIL"
    line = f"  [{mark}] {name}" + (f" - {detail}" if detail else "")
    _print(line)
    if not ok:
        errors.append(name)
    return ok

def main():
    _print("=== NPI/Python API 环境检测 ===\n")

    # 1. VERDI_HOME
    verdi = os.environ.get("VERDI_HOME", "")
    if not check("VERDI_HOME", bool(verdi), verdi):
        _print("=> 请先 source Verdi 的环境脚本，设置 VERDI_HOME")
        return False

    # 2. pynpi.wave import
    try:
        npi_py = os.path.join(verdi, "share", "NPI", "python")
        if npi_py not in sys.path:
            sys.path.insert(0, npi_py)
        import pynpi.wave as wave
        check("import pynpi.wave", True)
    except ImportError as e:
        check("import pynpi.wave", False, str(e))
        _print(f"=> export PYTHONPATH={os.path.join(verdi, 'share', 'NPI', 'python')}:$PYTHONPATH")
        return False

    # 3. wave.init
    try:
        wave.init("test")
        check("wave.init", True)
    except Exception as e:
        check("wave.init", False, str(e))
        return False

    # 4. FSDB open
    if not os.path.exists(FSDB_PATH):
        check("FSDB exists", False, FSDB_PATH)
        return False
    check("FSDB exists", True, FSDB_PATH)

    fsdb = None
    try:
        fsdb = wave.open(FSDB_PATH)
        if fsdb:
            check("wave.open", True)
        else:
            check("wave.open", False, "returned None")
            return False
    except Exception as e:
        check("wave.open", False, str(e))
        return False

    # 5. 基本信息
    try:
        mt = wave.min_time(fsdb)
        xt = wave.max_time(fsdb)
        _print(f"  min_time:    {mt[1]} (unit={mt[0]})")
        _print(f"  max_time:    {xt[1]} (unit={xt[0]})")
    except Exception as e:
        check("FSDB info", False, str(e))

    # 6. 信号数量统计
    try:
        sig = wave.iter_top_sig(fsdb)
        count = 0
        first = ""
        while sig:
            if count == 0:
                first = wave.SigFullName(sig)
            sig = wave.iter_sig_next()
            count += 1
        wave.iter_sig_stop(fsdb)
        _print(f"  top sigs:    {count} 个 (first: {first})")
    except Exception as e:
        _print(f"  top sigs:    (skipped: {e})")

    if not errors:
        _print("\n=== NPI 环境可用 ===")
        return True
    else:
        _print(f"\n=== {len(errors)} 项检查失败 ===")
        return False

if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
