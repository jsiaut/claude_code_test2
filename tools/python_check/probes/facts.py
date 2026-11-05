"""Sonde des faits de la remarque sur Python (docs/PYTHON.md, 2) : build, GIL, JIT, sous-interpréteurs, ramasse-miettes,
entiers de largeur fixe, bibliothèques tierces. Usage : python3.15 facts.py ; python3.15t facts.py"""
import gc, importlib.util, sys, sysconfig

print(f"version {sys.version.split()[0]} ; Py_GIL_DISABLED={sysconfig.get_config_var('Py_GIL_DISABLED')} ; "
      f"GIL actif={sys._is_gil_enabled()}")
jit = getattr(sys, "_jit", None)
print("sys._jit :", "absent" if jit is None else
      f"is_available={jit.is_available()} is_enabled={jit.is_enabled()}")
print("options de configuration contenant JIT :",
      sorted(a for a in (sysconfig.get_config_var("CONFIG_ARGS") or "").split() if "jit" in a.lower()) or "aucune")
print("concurrent.interpreters :", importlib.util.find_spec("concurrent.interpreters") is not None)
for mod in ("numpy", "numba", "polars", "duckdb", "cffi"):
    print(f"module tiers {mod} :", importlib.util.find_spec(mod) is not None)
# ramasse-miettes de cycles
print("gc.get_threshold() =", gc.get_threshold(), "; générations (get_stats) :", len(gc.get_stats()))
gc.disable(); print("gc.disable() : gc.isenabled() =", gc.isenabled()); gc.enable()
x = [[i] for i in range(1000)]
gc.freeze(); print("gc.freeze() : gc.get_freeze_count() =", gc.get_freeze_count()); gc.unfreeze()
# entiers de largeur fixe (F3)
import ctypes
print("c_uint32(2**32 + 5) =", ctypes.c_uint32(2**32 + 5).value, "; c_int32(2**31) =", ctypes.c_int32(2**31).value,
      "; c_uint8(300) =", ctypes.c_uint8(300).value, "; c_int64(2**63) =", ctypes.c_int64(2**63).value)
a = (ctypes.c_uint32 * 2)(); a[0] = 2**32 + 7; a[1] = -1
print("tableau c_uint32 : a[0] = 2**32 + 7 ->", a[0], "; a[1] = -1 ->", a[1])
u = ctypes.c_uint32(0xFFFFFFFF); u.value += 1
print("c_uint32(0xFFFFFFFF), value += 1 ->", u.value)
print("masque : (0xFFFFFFFF + 1) & 0xFFFFFFFF =", (0xFFFFFFFF + 1) & 0xFFFFFFFF)
from array import array
try:
    array("I", [2**32])
except OverflowError as e:
    print("array('I', [2**32]) : OverflowError :", e)
