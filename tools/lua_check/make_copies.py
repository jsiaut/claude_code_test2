#!/usr/bin/env python3
"""Copies de la remarque sur Lua (plan : docs/LUA.md, section 3.3), produites par remplacements de texte contrôlés
(chaque texte remplacé doit apparaître exactement une fois ; le reste du fichier est identique à l'octet).

* bench/lua_ref : copie exacte de bench/lua_k9h (le code publié, harnais commun de K9), PUC-Lua 5.5.1.
* bench/lua_fix : corrections publiées : (a) K3, les quatre compteurs dans la partie tableau d'une table préremplie
  (`c = {}` puis les indices 17, 33 et 49 rangeaient trois compteurs « espacés » dans la partie hachée) ; (b) K4, les
  octets décodés en table hors chrono, comme les colonnes de K6 (le code publié appelait `string.byte` à chaque octet,
  dans la zone chronométrée) ; (c) Q6 tuned (et `mt`, qui appelle la même fonction), le masque calculé sans
  branchement, comme le code l'annonce (`cond and 1 or 0` branche dans le bytecode) : bit de signe d'une différence,
  décalé de 63 bits ; (d) K8 naturel, nœuds en enregistrements à champs nommés, le type par défaut (comme K1), au lieu
  de tables positionnelles `{v, false, false}`.
* bench/lua_exp : lua_fix et des variantes nouvelles (sensibilités) : K6 `tuned_n` et `mt_n` (Q6 par tests imbriqués,
  date lue une fois) ; K9 `tuned_s` et `mt_s` (un indice par ligne, voisins glissants) ; K7 `tuned_p` (une table,
  compte et somme tassés dans un entier) ; K8 `tuned_it` (arène itérative, comme c_k8it) ; K1 `soa_h` (le facteur 0,5
  sorti de la boucle) ; K2 `tuned_s` (indices décalés de 1 au chargement).
* bench/luajit_ref : copie exacte de bench/luajit_k9h (l'annexe LuaJIT).
* bench/luajit_fix : (a) K3 conforme : boucle d'incréments interprétée (`jit.off`) sur une table Lua, chaque incrément
  lu et écrit en mémoire (le code compilé ignore `volatile` et garde le compteur en registre) ; (b) K8 naturel à
  champs nommés, comme lua_fix (sensibilité S-LuaJIT).
* bench/python_k8n : bench/python_k9h, K8 naturel sur une classe ordinaire, sans `__slots__` (le type par défaut, comme
  K1 ; conséquence pour Python de la règle appliquée au K8 naturel de Lua).
Usage : make_copies.py"""
import os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOTE = "-- remarque sur Lua (docs/LUA.md) : "


def sub(text, old, new):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"texte trouvé {n} fois (1 attendu) :\n{old[:300]}")
    return text.replace(old, new)


K8_NAMED = [
    ('''local function t_build(d)
  local n = { cnt8, false, false }
  cnt8 = cnt8 + 1
  if d > 0 then n[2] = t_build(d - 1); n[3] = t_build(d - 1) end
  return n
end
local function t_sum(n) if not n then return 0 end; return n[1] + t_sum(n[2]) + t_sum(n[3]) end''',
     NOTE + '''nœud en enregistrement à champs nommés, le type par défaut (comme K1)
local function t_build(d)
  local n = { v = cnt8, l = false, r = false }
  cnt8 = cnt8 + 1
  if d > 0 then n.l = t_build(d - 1); n.r = t_build(d - 1) end
  return n
end
local function t_sum(n) if not n then return 0 end; return n.v + t_sum(n.l) + t_sum(n.r) end'''),
]

FIX = [
    # (a) K3 : compteurs dans la partie tableau
    ('''  local stride = v:sub(-6) == "padded" and 16 or 1
  local c = {}
  bench("k3", v, "4x2^25", reps, function()''',
     '''  local stride = v:sub(-6) == "padded" and 16 or 1
  local c = {}
  for i = 1, 64 do c[i] = 0 end ''' + NOTE + '''les quatre compteurs dans la partie tableau, espacés
  -- comme serrés (avec c = {}, les indices 17, 33 et 49 tombaient dans la partie hachée)
  bench("k3", v, "4x2^25", reps, function()'''),
    # (b) K4 : octets en table, hors chrono
    ('''local function k4_natural(s)
  local acc = 0
  local byte = string.byte
  for i = 1, #s do
    local x = byte(s, i)
    if x >= 128 then acc = acc + x end
  end
  return acc
end
local function k4_branchless(s)
  local acc = 0
  local byte = string.byte
  for i = 1, #s do
    local x = byte(s, i)
    acc = acc + x * (x >> 7)
  end
  return acc
end
local function run_k4(v, reps)
  local s = read_all("k4_bytes.u8")
  if v == "natural_sorted" then
    local cnt = {}
    for b = 0, 255 do cnt[b] = 0 end
    for i = 1, #s do local x = s:byte(i); cnt[x] = cnt[x] + 1 end
    local parts = {}
    for b = 0, 255 do parts[#parts + 1] = string.rep(string.char(b), cnt[b]) end
    s = table.concat(parts)
  end
  local f = v == "branchless_unsorted" and k4_branchless or k4_natural
  bench("k4", v, "16M", reps, function() return tostring(f(s)) end)
end''',
     NOTE + '''octets décodés en table hors chrono, comme les colonnes de K6 (le code publié
-- appelait string.byte à chaque octet, dans la zone chronométrée)
local function k4_natural(t, n)
  local acc = 0
  for i = 1, n do
    local x = t[i]
    if x >= 128 then acc = acc + x end
  end
  return acc
end
local function k4_branchless(t, n)
  local acc = 0
  for i = 1, n do
    local x = t[i]
    acc = acc + x * (x >> 7)
  end
  return acc
end
local function run_k4(v, reps)
  local t, n = bytes("k4_bytes.u8")
  if v == "natural_sorted" then
    local cnt = {}
    for b = 0, 255 do cnt[b] = 0 end
    for i = 1, n do local x = t[i]; cnt[x] = cnt[x] + 1 end
    local k = 1
    for b = 0, 255 do for _ = 1, cnt[b] do t[k] = b; k = k + 1 end end
  end
  local f = v == "branchless_unsorted" and k4_branchless or k4_natural
  bench("k4", v, "16M", reps, function() return tostring(f(t, n)) end)
end'''),
    # (c) Q6 tuned : masque sans branchement
    ('''    local dd = d[i]
    -- prédicat arithmétique : ((x - lo) & 0xFFFFFFFF) < n  <=>  lo <= x < lo + n
    local m = (((sd[i] - 8766) & 0xFFFFFFFF) < 365 and 1 or 0) * (((dd - 5) & 0xFF) <= 2 and 1 or 0) * (q[i] < 24 and 1 or 0)
    s = s + pr[i] * dd * m''',
     '''    local dd = d[i]
    -- prédicat arithmétique : ((x - lo) & 0xFFFFFFFF) < n  <=>  lo <= x < lo + n
    ''' + NOTE + '''masque sans branchement, comme le code l'annonce (cond and 1 or 0
    -- branche dans le bytecode) : une différence négative, décalée de 63 bits (décalage logique), donne 1, sinon 0
    local m = ((((sd[i] - 8766) & 0xFFFFFFFF) - 365) >> 63) & ((((dd - 5) & 0xFF) - 3) >> 63) & ((q[i] - 24) >> 63)
    s = s + pr[i] * dd * m'''),
] + K8_NAMED


def fix(text):
    for a, b in FIX:
        text = sub(text, a, b)
    return text


EXP = [
    # K1 soa_h : 0,5 hors de la boucle (résultat identique au bit : multiplier par 0,5 est exact)
    ('''-- Empreinte K1 (D2a) : octets alloués par Lua après un GC complet''',
     NOTE + '''sensibilité : le facteur 0,5 sorti de la boucle (multiplier par 0,5 est exact :
-- même résultat au bit près)
local function k1_soa_h(vx, vy, vz, m)
  local a0, a1 = 0.0, 0.0
  for i = 1, N1, 2 do
    local x, y, z = vx[i], vy[i], vz[i]
    a0 = a0 + m[i] * (x * x + y * y + z * z)
    x, y, z = vx[i + 1], vy[i + 1], vz[i + 1]
    a1 = a1 + m[i + 1] * (x * x + y * y + z * z)
  end
  return 0.5 * (a0 + a1)
end
-- Empreinte K1 (D2a) : octets alloués par Lua après un GC complet'''),
    ('''  if v == "soa" then''', '''  if v == "soa" or v == "soa_h" then'''),
    ('''    return bench("k1", v, "energy", reps, function() return f6(k1_soa(vx, vy, vz, m)) end)''',
     '''    local f = v == "soa_h" and k1_soa_h or k1_soa
    return bench("k1", v, "energy", reps, function() return f6(f(vx, vy, vz, m)) end)'''),
    # K2 tuned_s : indices décalés de 1 au chargement
    ('''local function run_k2(v, reps, p)
  local a = load("k2_chase_" .. p .. ".u32", "<I4", 4)
  bench("k2", v, p, reps, function() return tostring(k2_chase(a, 4200000)) end)
end''',
     NOTE + '''sensibilité : indices décalés de 1 au chargement (hors chrono), plus d'addition par saut
local function k2_chase_s(a, h)
  local i = 1
  for _ = 1, h do i = a[i] end
  return i - 1
end
local function run_k2(v, reps, p)
  local a = load("k2_chase_" .. p .. ".u32", "<I4", 4)
  if v == "tuned_s" then
    for k = 1, #a do a[k] = a[k] + 1 end
    return bench("k2", v, p, reps, function() return tostring(k2_chase_s(a, 4200000)) end)
  end
  bench("k2", v, p, reps, function() return tostring(k2_chase(a, 4200000)) end)
end'''),
    # K6 tuned_n / mt_n : Q6 par tests imbriqués
    ('''local function q1_natural(c, lo, hi, acc)''',
     NOTE + '''sensibilité : Q6 par tests imbriqués, date et remise lues une fois
local function q6_nested(c, lo, hi)
  local sd, d, q, pr = c.sd, c.d, c.q, c.pr
  local s = 0
  for i = lo, hi do
    local x = sd[i]
    if x >= 8766 and x < 9131 then
      local dd = d[i]
      if dd >= 5 and dd <= 7 and q[i] < 24 then s = s + pr[i] * dd end
    end
  end
  return s
end
local function q1_natural(c, lo, hi, acc)'''),
    ('''      if v == "natural" then s = q6_natural(c, 1, N6)
      else for k = 0, 3 do s = s + q6_tuned(c, k * (N6 // 4) + 1, (k + 1) * (N6 // 4)) end end''',
     '''      if v == "natural" then s = q6_natural(c, 1, N6)
      else
        local f = (v == "tuned_n" or v == "mt_n") and q6_nested or q6_tuned
        for k = 0, 3 do s = s + f(c, k * (N6 // 4) + 1, (k + 1) * (N6 // 4)) end
      end'''),
    # K7 tuned_p : une table, compte et somme tassés
    ('''    else -- deux tables plates clé -> entier (pas de table par entrée)''',
     '''    elseif v == "tuned_p" then ''' + NOTE + '''sensibilité : une seule table, compte et somme tassés dans un
      -- entier (somme <= 2^24 · 999 < 2^34 sur les bits bas, compte <= 2^24 au-dessus du bit 35)
      local t0 = clock()
      local agg = {}
      local ONE = 1 << 35
      for i = 1, n do
        local k = keys[i]
        local e = agg[k]
        if e then agg[k] = e + ONE + vals[i] else agg[k] = ONE + vals[i] end
      end
      dt = clock() - t0
      local MASK = ONE - 1
      for k, e in pairs(agg) do nk = nk + 1; ws = ws + (e & MASK) * ((k & 1023) + 1) end
    else -- deux tables plates clé -> entier (pas de table par entrée)'''),
    # K8 tuned_it : arène itérative
    ('''local function a_sum(i) if i == 0 then return 0 end; return AV[i] + a_sum(AL[i]) + a_sum(AR[i]) end''',
     '''local function a_sum(i) if i == 0 then return 0 end; return AV[i] + a_sum(AL[i]) + a_sum(AR[i]) end
''' + NOTE + '''sensibilité : arène construite et parcourue par itération (piles explicites), mêmes nœuds,
-- mêmes valeurs, même ordre préfixe que a_build et a_sum (comme c_k8it et js_exp)
local stN, stD, stS, stQ = {}, {}, {}, {}
local function a_node()
  top = top + 1
  local i = top
  AV[i] = cnt8; cnt8 = cnt8 + 1; AL[i] = 0; AR[i] = 0
  return i
end
local function a_build_it(d0)
  local root = a_node()
  local sp = 0
  if d0 > 0 then stN[1] = root; stD[1] = d0; stS[1] = 0; sp = 1 end
  while sp > 0 do
    local nd, d = stN[sp], stD[sp]
    local c = a_node()
    if stS[sp] == 0 then stS[sp] = 1; AL[nd] = c else sp = sp - 1; AR[nd] = c end
    if d > 1 then sp = sp + 1; stN[sp] = c; stD[sp] = d - 1; stS[sp] = 0 end
  end
  return root
end
local function a_sum_it(root)
  local s, sp = 0, 1
  stQ[1] = root
  while sp > 0 do
    local nd = stQ[sp]; sp = sp - 1
    s = s + AV[nd]
    if AL[nd] ~= 0 then sp = sp + 1; stQ[sp] = AR[nd]; sp = sp + 1; stQ[sp] = AL[nd] end
  end
  return s
end'''),
    ('''  local tuned = v == "tuned"''', '''  local tuned, it8 = v == "tuned", v == "tuned_it"'''),
    ('''      if tuned then top = 0; s = a_sum(a_build(10)) else s = t_sum(t_build(10)) end''',
     '''      if it8 then top = 0; s = a_sum_it(a_build_it(10))
      elseif tuned then top = 0; s = a_sum(a_build(10)) else s = t_sum(t_build(10)) end'''),
    # K9 tuned_s / mt_s : un indice, voisins glissants
    ('''local function run_k9(v, reps)''',
     NOTE + '''sensibilité : un seul indice par ligne, voisins de gauche et du centre gardés
-- dans des variables (mêmes opérations, même ordre)
local function k9_flat_s(a, b)
  for i = 1, M9 - 2 do
    local mid = i * M9
    local l, c = a[mid + 1], a[mid + 2]
    for j = mid + 2, mid + M9 - 1 do
      local r = a[j + 1]
      b[j] = 0.25 * (((a[j - M9] + a[j + M9]) + l) + r)
      l, c = c, r
    end
  end
end
local function run_k9(v, reps)'''),
    ('''      k9_flat(a, b); k9_flat(b, a); k9_flat(a, b); k9_flat(b, a)''',
     '''      local f = (v == "tuned_s" or v == "mt_s") and k9_flat_s or k9_flat
      f(a, b); f(b, a); f(a, b); f(b, a)'''),
]


def exp(text):
    text = fix(text)
    for a, b in EXP:
        text = sub(text, a, b)
    return text


JIT_FIX = [
    ('''  print("META;k3_mechanism;pas de threads dans LuaJIT : exécution séquentielle ; le JIT ignore volatile (compteur maintenu en registre, mesuré ~0,3 ns/incrément)")
  local stride = v:sub(-6) == "padded" and 16 or 1
  local c = ffi.new("volatile int64_t[?]", 128)
  bench("k3", v, "4x2^25", reps, function()
    for t = 0, 3 do c[16 + t * stride] = 0 end
    for t = 0, 3 do local idx = 16 + t * stride; for _ = 1, 33554432 do c[idx] = c[idx] + 1 end end
    local s = 0
    for t = 0, 3 do s = s + tonumber(c[16 + t * stride]) end
    return string.format("%d", s)
  end)''',
     '''  print("META;k3_mechanism;pas de threads dans LuaJIT : exécution séquentielle ; boucle d'incréments interprétée (jit.off) sur une table, chaque incrément lu et écrit en mémoire (remarque sur Lua : le code compilé ignore volatile)")
  local stride = v:sub(-6) == "padded" and 16 or 1
  local c = {}
  for i = 1, 128 do c[i] = 0 end
  local function inc(idx) for _ = 1, 33554432 do c[idx] = c[idx] + 1 end end
  jit.off(inc)
  bench("k3", v, "4x2^25", reps, function()
    for t = 0, 3 do c[16 + t * stride] = 0 end
    for t = 0, 3 do inc(16 + t * stride) end
    local s = 0
    for t = 0, 3 do s = s + c[16 + t * stride] end
    return string.format("%d", s)
  end)'''),
] + K8_NAMED


def jit_fix(text):
    for a, b in JIT_FIX:
        text = sub(text, a, b)
    return text


PY_K8N = [
    ('''class Node:
    __slots__ = ("v", "l", "r")

    def __init__(self, v, l, r):''',
     '''class Node:  # remarque sur Lua (docs/LUA.md) : classe ordinaire, sans __slots__ (le type par défaut, comme K1)
    def __init__(self, v, l, r):'''),
]


def py_k8n(text):
    for a, b in PY_K8N:
        text = sub(text, a, b)
    return text


def copy(dst, src_dir, name, text):
    d = os.path.join(ROOT, "bench", dst)
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    open(os.path.join(d, name), "w", encoding="utf-8").write(text)
    for f in ("run", "build.sh"):
        shutil.copy2(os.path.join(ROOT, "bench", src_dir, f), os.path.join(d, f))
    print(f"{dst} écrit")


def main():
    lua = open(os.path.join(ROOT, "bench", "lua_k9h", "ms.lua"), encoding="utf-8").read()
    copy("lua_ref", "lua_k9h", "ms.lua", lua)
    copy("lua_fix", "lua_k9h", "ms.lua", fix(lua))
    copy("lua_exp", "lua_k9h", "ms.lua", exp(lua))
    open(os.path.join(ROOT, "bench", "lua_exp", "extra_variants"), "w").write(
        "k1 soa_h energy\nk2 tuned_s 16384\nk2 tuned_s 262144\nk2 tuned_s 8388608\nk6 tuned_n q6\nk6 mt_n q6\n"
        "k7 tuned_p\nk8 tuned_it\nk9 tuned_s\nk9 mt_s\n")
    lj = open(os.path.join(ROOT, "bench", "luajit_k9h", "ms.lua"), encoding="utf-8").read()
    copy("luajit_ref", "luajit_k9h", "ms.lua", lj)
    copy("luajit_fix", "luajit_k9h", "ms.lua", jit_fix(lj))
    py = open(os.path.join(ROOT, "bench", "python_k9h", "ms.py"), encoding="utf-8").read()
    copy("python_k8n", "python_k9h", "ms.py", py_k8n(py))


if __name__ == "__main__":
    main()
