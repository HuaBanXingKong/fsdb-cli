#!/usr/bin/env python3
# ------------------------------------------------------------------
#  File Name     : check_npi.py
#  Last Modified : 2026-05-27 17:00
#  Description   : 检测 NPI/Python API 是否可用
# ------------------------------------------------------------------
"""python3 check_npi.py [fsdb_path]"""

import os
import sys

FSDB_PATH = sys.argv[1] if len(sys.argv) > 1 else "work/simulation/wave/tb_top.fsdb"

def check(name, ok, detail=""):
    mark = "OK" if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" - {detail}" if detail else ""))

print("=== NPI/Python API 环境检测 ===\n")

# 1. VERDI_HOME
verdi = os.environ.get("VERDI_HOME", "")
check("VERDI_HOME", bool(verdi), verdi)
if not verdi:
    print("\n=> 请先 source Verdi 的环境脚本，设置 VERDI_HOME")
    sys.exit(1)

# 2. pynpi import
print()
try:
    from pynpi import npisys
    from pynpi import waveform
    check("import pynpi", True)
except ImportError as e:
    check("import pynpi", False, str(e))
    npi_path = os.path.join(verdi, "share", "NPI", "python")
    print(f"=> pynpi 路径一般在: {npi_path}")
    print(f"   检查该目录是否存在，或 export PYTHONPATH={npi_path}:$PYTHONPATH")
    sys.exit(1)

# 3. npisys.init
print()
try:
    npisys.init(["check_npi"])
    check("npisys.init", True)
except Exception as e:
    check("npisys.init", False, str(e))
    sys.exit(1)

# 4. FSDB open
print()
if not os.path.exists(FSDB_PATH):
    check("FSDB exists", False, FSDB_PATH)
    print(f"=> 文件不存在，指定实际 FSDB 路径重试: python3 check_npi.py /path/to/wave.fsdb")
    sys.exit(1)

check("FSDB exists", True, FSDB_PATH)

try:
    fsdb = waveform.open(FSDB_PATH)
    if fsdb:
        check("waveform.open", True)
    else:
        check("waveform.open", False, "returned None")
        sys.exit(1)
except Exception as e:
    check("waveform.open", False, str(e))
    sys.exit(1)

# 5. 基本信息
print()
print("=== FSDB 基本信息 ===")
print(f"  min_time:    {fsdb.min_time()}")
print(f"  max_time:    {fsdb.max_time()}")

scopes = fsdb.top_scope_list()
print(f"  top_scopes:  {len(scopes)} 个")
for s in scopes[:5]:
    print(f"    - {s.name()}")

# 6. 信号列表测试 (第一个 top scope)
print()
print("=== 信号读取测试 ===")
scope = scopes[0]
sigs = scope.sig_list()
print(f"  scope '{scope.name()}' 下信号: {len(sigs)} 个")
for sig in sigs[:10]:
    lr = sig.left_range()
    rr = sig.right_range()
    w = max(lr, rr) - min(lr, rr) + 1 if sig.left_range() is not None else 1
    print(f"    {sig.full_name()}  [{w} bit]  dir={sig.direction()}")

# 7. 值读取测试 (第一个信号)
if sigs:
    print()
    sig = sigs[0]
    try:
        values = waveform.sig_hdl_value_between(sig, 0, fsdb.max_time(), waveform.VctFormat_e.BinStrVal)
        print(f"  {sig.full_name()} 的值变化: {len(values)} 次")
        for t, v in values[:5]:
            print(f"    time={t:>10}  val={v}")
        if len(values) > 5:
            print(f"    ... 共 {len(values)} 条")
    except Exception as e:
        check("sig_hdl_value_between", False, str(e))

print()
print("=== NPI 环境可用 ===")
