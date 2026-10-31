"""Historique des niveaux de compilation (DOTNET_JitDisasmSummary) de la méthode chaude de chaque clé du binaire
de la campagne, après W échauffements. Usage : tier_diag.py [W] [répertoire de sortie]"""
import os, re, subprocess, sys
ROOT = "/home/user/claude_code_test2"
DLL = f"{ROOT}/bench/csharp/bin/rel/ms.dll"
KEYS = [("k1","natural","","K1Natural"),("k1","aos","","K1AoS"),("k1","soa","","K1SoA"),("k2","tuned","16384","K2Chase"),
        ("k2","tuned","262144","K2Chase"),("k3","sw_padded","","RunK3>b__1"),("k4","natural_unsorted","","K4Natural"),
        ("k4","branchless_unsorted","","K4Branchless"),("k5","natural","","K5Natural"),("k5","tuned","","K5Tuned"),
        ("k6","natural","q6","Q6Natural"),("k6","tuned","q6","Q6Tuned"),("k6","natural","q1","Q1Natural"),
        ("k6","tuned","q1","Q1Tuned"),("k6","mt","q6","Q6Tuned"),("k6","mt","q1","Q1Tuned"),
        ("k9","natural","","K9Natural"),("k9","tuned","","K9Rows"),("k9","mt","","K9Rows")]
W = int(sys.argv[1]) if len(sys.argv) > 1 else 120
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else f"{ROOT}/.work/cs/asm"
for k, v, p, meth in KEYS:
    out = f"{OUTDIR}/tier_{k}_{v}_{p}_{W}.txt"
    env = dict(os.environ, MS_DATA="/opt/msdata", WARMUP=str(W), DOTNET_JitStdOutFile=out, DOTNET_JitDisasmSummary="1",
               DOTNET_CLI_TELEMETRY_OPTOUT="1")
    r = subprocess.run(["/opt/dotnet/dotnet", DLL, k, v, "3"] + ([p] if p else []), env=env, capture_output=True, text=True)
    ts = sorted(float(l.split(";")[5]) for l in r.stdout.splitlines() if l.startswith("RESULT"))
    tiers = []
    for l in open(out):
        if meth in l:
            g = re.search(r"\[([^\[\]]*)\]\s*$", l.strip())
            tiers.append(g.group(1).split(",")[0] if g else "?")
    print(f"{k} {v} {p}: méthode {meth} : {' -> '.join(tiers)} ; médiane {1e3*ts[1]:.2f} ms", flush=True)
