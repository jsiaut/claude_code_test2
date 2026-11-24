-- Implémentation Lua 5.5 (PUC-Rio, bibliothèque standard seule). Voir docs/SPEC.md.
-- Lua standard n'a ni threads ni tableaux typés : les noyaux multi-threads s'exécutent
-- en séquence (ou en coroutines). Horloge : os.clock() (temps CPU du processus, seule
-- horloge sub-seconde de la bibliothèque standard ; identique au temps mural en mono-thread).

local DATA = os.getenv("MS_DATA") or "/opt/msdata"
local WARMUP = tonumber(os.getenv("WARMUP") or "1")
local clock = os.clock

local function read_all(name)
  local f = assert(io.open(DATA .. "/" .. name, "rb"))
  local s = f:read("a")
  f:close()
  return s
end
-- décode un fichier binaire en table Lua (hors chrono)
local function load(name, fmt, size)
  local s = read_all(name)
  local n = #s // size
  local t = table.create and table.create(n) or {}
  local unpack = string.unpack
  local pos = 1
  local chunk = 64
  local f64 = string.rep(fmt, chunk)
  local i = 1
  while i + chunk - 1 <= n do
    local vals = { unpack(f64, s, pos) }
    for k = 1, chunk do t[i + k - 1] = vals[k] end
    pos = pos + chunk * size
    i = i + chunk
  end
  while i <= n do t[i], pos = unpack(fmt, s, pos); i = i + 1 end
  return t, n
end
local function bytes(name)
  local s = read_all(name)
  local t = table.create and table.create(#s) or {}
  for i = 1, #s, 4096 do
    local b = { s:byte(i, math.min(i + 4095, #s)) }
    for k = 1, #b do t[i + k - 1] = b[k] end
  end
  return t, #s
end
local function result(k, v, p, rep, sec, chk)
  io.write(string.format("RESULT;%s;%s;%s;%d;%.9f;%s\n", k, v, p, rep, sec, chk)); io.flush()
end
local function bench(k, v, p, reps, f)
  for r = -WARMUP, reps - 1 do
    local t0 = clock()
    local chk = f()
    local dt = clock() - t0
    if r >= 0 then result(k, v, p, r, dt, chk) end
  end
end

-- ------------------------------------------------------------------ K1
local N1 = 1 << 22
local function k1_natural(ps)
  local e = 0.0
  for i = 1, #ps do
    local p = ps[i]
    e = e + 0.5 * p.mass * (p.vx * p.vx + p.vy * p.vy + p.vz * p.vz)
  end
  return e
end
local function k1_aos(f) -- table plate entrelacée (pas de 16)
  local a0, a1 = 0.0, 0.0
  for i = 0, N1 * 16 - 1, 32 do
    a0 = a0 + 0.5 * f[i + 10] * (f[i + 4] * f[i + 4] + f[i + 5] * f[i + 5] + f[i + 6] * f[i + 6])
    a1 = a1 + 0.5 * f[i + 26] * (f[i + 20] * f[i + 20] + f[i + 21] * f[i + 21] + f[i + 22] * f[i + 22])
  end
  return a0 + a1
end
local function k1_soa(vx, vy, vz, m)
  local a0, a1 = 0.0, 0.0
  for i = 1, N1, 2 do
    local x, y, z = vx[i], vy[i], vz[i]
    a0 = a0 + 0.5 * m[i] * (x * x + y * y + z * z)
    x, y, z = vx[i + 1], vy[i + 1], vz[i + 1]
    a1 = a1 + 0.5 * m[i + 1] * (x * x + y * y + z * z)
  end
  return a0 + a1
end
-- Empreinte K1 (D2a) : octets alloués par Lua après un GC complet, et RSS courant (pages de 4 Kio)
local function live_now() collectgarbage("collect"); collectgarbage("collect"); return math.floor(collectgarbage("count") * 1024) end
local function rss_now()
  local f = io.open("/proc/self/statm", "r")
  if not f then return 0 end
  local _, res = f:read("n", "n")
  f:close()
  return math.floor(res * 4096)
end
local function run_k1(v, reps)
  if v == "footprint0" then return result("k1", v, "energy", 0, 0, "0") end
  local raw = load("k1_particles.f32", "<f", 4)
  if v == "footprint_raw" then return result("k1", v, "energy", 0, 0, "0") end
  local f6 = function(x) return string.format("%.6f", x) end
  if v == "aos" then return bench("k1", v, "energy", reps, function() return f6(k1_aos(raw)) end) end
  if v == "soa" then
    local function col(k) local c = {}; for i = 1, N1 do c[i] = raw[16 * (i - 1) + k + 1] end; return c end
    local vx, vy, vz, m = col(3), col(4), col(5), col(9)
    raw = nil; collectgarbage()
    return bench("k1", v, "energy", reps, function() return f6(k1_soa(vx, vy, vz, m)) end)
  end
  local m1, r1 = 0, 0
  if v == "footprint" then m1, r1 = live_now(), rss_now() end -- P1 : tampon brut chargé
  local ps = {}
  for i = 1, N1 do
    local o = 16 * (i - 1)
    ps[i] = { x = raw[o + 1], y = raw[o + 2], z = raw[o + 3], vx = raw[o + 4], vy = raw[o + 5], vz = raw[o + 6], ax = raw[o + 7], ay = raw[o + 8],
      az = raw[o + 9], mass = raw[o + 10], charge = raw[o + 11], radius = raw[o + 12], temp = raw[o + 13], pressure = raw[o + 14],
      energy = raw[o + 15], density = raw[o + 16] }
  end
  if v == "footprint" then
    local m2, r2 = live_now(), rss_now() -- P2 : collection construite, tampon brut encore vivant
    print(string.format("META;mem;live;%d;%d\nMETA;rss;%d;%d\nMETA;raw0;%s", m1, m2, r1, r2, tostring(raw[1])))
    return result("k1", v, "energy", 0, 0, f6(k1_natural(ps)))
  end
  raw = nil; collectgarbage()
  if v == "natural_shuffled" then
    local perm = load("k1_perm.u32", "<I4", 4)
    local s = {}
    for j = 1, N1 do s[j] = ps[perm[j] + 1] end
    ps = s; collectgarbage()
  end
  bench("k1", v, "energy", reps, function() return f6(k1_natural(ps)) end)
end

-- ------------------------------------------------------------------ K2
local function k2_chase(a, h)
  local i = 0
  for _ = 1, h do i = a[i + 1] end
  return i
end
local function run_k2(v, reps, p)
  local a = load("k2_chase_" .. p .. ".u32", "<I4", 4)
  bench("k2", v, p, reps, function() return tostring(k2_chase(a, 4200000)) end)
end

-- ------------------------------------------------------------------ K3
local ITER3 = 1 << 25
local function run_k3(v, reps)
  print("META;k3_mechanism;pas de threads en Lua standard : 4 « threads » exécutés en séquence sur un seul cœur")
  local stride = v:sub(-6) == "padded" and 16 or 1
  local c = {}
  for i = 1, 64 do c[i] = 0 end -- remarque sur Lua (docs/LUA.md) : les quatre compteurs dans la partie tableau, espacés
  -- comme serrés (avec c = {}, les indices 17, 33 et 49 tombaient dans la partie hachée)
  bench("k3", v, "4x2^25", reps, function()
    for t = 0, 3 do c[1 + t * stride] = 0 end
    for t = 0, 3 do
      local idx = 1 + t * stride
      for _ = 1, ITER3 do c[idx] = c[idx] + 1 end
    end
    local s = 0
    for t = 0, 3 do s = s + c[1 + t * stride] end
    return tostring(s)
  end)
end

-- ------------------------------------------------------------------ K4
-- remarque sur Lua (docs/LUA.md) : octets décodés en table hors chrono, comme les colonnes de K6 (le code publié
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
-- v4, point 3 (docs/V4_EQUAL.md, R3) : variante tuned. Lua n'a pas de SIMD : la meilleure forme trouvée lit huit octets
-- par mot de 64 bits (string.unpack « <I8 ») : masque des octets >= 128 par leur bit de poids fort, sommes par paires
-- d'octets puis par multiplication (0,21 s, contre 0,71 pour la boucle naturelle et 0,24 pour huit octets par appel de
-- string.byte).
local function k4_tuned(s)
  local acc, n = 0, #s
  local i = 1
  local unpack, byte = string.unpack, string.byte
  while i + 7 <= n do
    local w = unpack("<I8", s, i)
    local y = w & (((w >> 7) & 0x0101010101010101) * 0xFF)
    local p = (y & 0x00FF00FF00FF00FF) + ((y >> 8) & 0x00FF00FF00FF00FF)
    acc = acc + ((p * 0x0001000100010001) >> 48)
    i = i + 8
  end
  for k = i, n do
    local x = byte(s, k)
    if x >= 128 then acc = acc + x end
  end
  return acc
end
-- v4, point 4 (docs/V4_CONVERGE.md, 3.3, swar) : huit octets par mot de 64 bits (string.unpack « <I8 » sur la chaîne
-- des octets tels qu'ils sont stockés), voies de 16 bits accumulées sur 128 mots puis vidées (au plus 128 × 510 =
-- 65 280 < 2^16 par voie ; entiers de Lua sur 64 bits, décalages logiques). La variante tuned du point 3 vide ses
-- voies à chaque mot, par une multiplication. Les n mod 8 derniers octets : x * (x >> 7).
local function k4_swar(s)
  local n = #s
  local nw = n // 8
  local unpack = string.unpack
  local t, i = 0, 1
  for w0 = 0, nw - 1, 128 do
    local e = math.min(w0 + 128, nw)
    local acc = 0
    for _ = w0, e - 1 do
      local w = unpack("<I8", s, i)
      i = i + 8
      local y = w & (((w >> 7) & 0x0101010101010101) * 0xFF)
      acc = acc + (y & 0x00FF00FF00FF00FF) + ((y >> 8) & 0x00FF00FF00FF00FF)
    end
    acc = (acc & 0x0000FFFF0000FFFF) + ((acc >> 16) & 0x0000FFFF0000FFFF)
    t = t + (acc & 0xFFFFFFFF) + (acc >> 32)
  end
  for k = nw * 8 + 1, n do local x = string.byte(s, k); t = t + x * (x >> 7) end
  return t
end
local function run_k4(v, reps)
  if v == "swar" then
    local s = read_all("k4_bytes.u8")
    bench("k4", v, "16M", reps, function() return tostring(k4_swar(s)) end)
    return
  end
  if v == "tuned" then  -- v4, point 3 (R3) : mots de 64 bits lus dans la chaîne des octets tels qu'ils sont stockés
    local s = read_all("k4_bytes.u8")
    bench("k4", v, "16M", reps, function() return tostring(k4_tuned(s)) end)
    return
  end
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
end

-- ------------------------------------------------------------------ K5
local INNER5 = 1 << 16
local function k5_natural(a, b)
  local s = 0.0
  for i = 1, #a do s = s + a[i] * b[i] end
  return s
end
local function k5_tuned(a, b)
  local s0, s1, s2, s3 = 0.0, 0.0, 0.0, 0.0
  for i = 1, #a, 4 do
    s0 = s0 + a[i] * b[i]; s1 = s1 + a[i + 1] * b[i + 1]; s2 = s2 + a[i + 2] * b[i + 2]; s3 = s3 + a[i + 3] * b[i + 3]
  end
  return (s0 + s1) + (s2 + s3)
end
local function run_k5(v, reps)
  local a = load("k5_a.f32", "<f", 4)
  local b = load("k5_b.f32", "<f", 4)
  local f = v == "tuned" and k5_tuned or k5_natural
  bench("k5", v, "2048x65536", reps, function()
    local d = 0.0
    for _ = 1, INNER5 do d = f(a, b) end
    return string.format("%.4f", d)
  end)
end

-- ------------------------------------------------------------------ K6
local N6 = 1 << 24
local function q6_natural(c, lo, hi)
  local sd, d, q, pr = c.sd, c.d, c.q, c.pr
  local s = 0
  for i = lo, hi do
    if sd[i] >= 8766 and sd[i] < 9131 and d[i] >= 5 and d[i] <= 7 and q[i] < 24 then s = s + pr[i] * d[i] end
  end
  return s
end
local function q6_tuned(c, lo, hi)
  local sd, d, q, pr = c.sd, c.d, c.q, c.pr
  local s = 0
  for i = lo, hi do
    local dd = d[i]
    -- prédicat arithmétique : ((x - lo) & 0xFFFFFFFF) < n  <=>  lo <= x < lo + n
    -- remarque sur Lua (docs/LUA.md) : masque sans branchement, comme le code l'annonce (cond and 1 or 0
    -- branche dans le bytecode) : une différence négative, décalée de 63 bits (décalage logique), donne 1, sinon 0
    local m = ((((sd[i] - 8766) & 0xFFFFFFFF) - 365) >> 63) & ((((dd - 5) & 0xFF) - 3) >> 63) & ((q[i] - 24) >> 63)
    s = s + pr[i] * dd * m
  end
  return s
end
-- v4, point 4 (docs/V4_CONVERGE.md, 3.5, forme propre au runtime) : rq_nest, la forme de la remarque sur Lua
-- (bench/lua_exp, tuned_n ; docs/LUA.md : × 0,51), recopiée : Q6 par tests imbriqués, date et remise lues une fois
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
-- v4, point 4 (3.3, Q1 tuned_s) : une passe, les 30 accumulateurs en variables locales ; par ligne, ps = 1 si
-- shipdate <= 10471 (bit de signe de shipdate - 10472, décalage logique) et, pour chaque groupe k,
-- mk = ps & (bit de signe de (g ~ k) - 1), 1 si g = k ; additions des produits par mk, sans branchement
local function q1_tuned_s(c, lo, hi)
  local sd, pr, q, d, t, rf, ls = c.sd, c.pr, c.q, c.d, c.t, c.rf, c.ls
  local n0, q0, p0, e0, c0, n1, q1, p1, e1, c1, n2, q2, p2, e2, c2 = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
  local n3, q3, p3, e3, c3, n4, q4, p4, e4, c4, n5, q5, p5, e5, c5 = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
  for i = lo, hi do
    local ps = (sd[i] - 10472) >> 63
    local g = rf[i] * 2 + ls[i]
    local qq, p = q[i], pr[i]
    local dp = p * (100 - d[i])
    local ch = dp * (100 + t[i])
    local m = ps & ((g - 1) >> 63)
    n0 = n0 + m; q0 = q0 + qq * m; p0 = p0 + p * m; e0 = e0 + dp * m; c0 = c0 + ch * m
    m = ps & (((g ~ 1) - 1) >> 63)
    n1 = n1 + m; q1 = q1 + qq * m; p1 = p1 + p * m; e1 = e1 + dp * m; c1 = c1 + ch * m
    m = ps & (((g ~ 2) - 1) >> 63)
    n2 = n2 + m; q2 = q2 + qq * m; p2 = p2 + p * m; e2 = e2 + dp * m; c2 = c2 + ch * m
    m = ps & (((g ~ 3) - 1) >> 63)
    n3 = n3 + m; q3 = q3 + qq * m; p3 = p3 + p * m; e3 = e3 + dp * m; c3 = c3 + ch * m
    m = ps & (((g ~ 4) - 1) >> 63)
    n4 = n4 + m; q4 = q4 + qq * m; p4 = p4 + p * m; e4 = e4 + dp * m; c4 = c4 + ch * m
    m = ps & (((g ~ 5) - 1) >> 63)
    n5 = n5 + m; q5 = q5 + qq * m; p5 = p5 + p * m; e5 = e5 + dp * m; c5 = c5 + ch * m
  end
  return n0 + q0 + p0 + e0 + c0 + n1 + q1 + p1 + e1 + c1 + n2 + q2 + p2 + e2 + c2
    + n3 + q3 + p3 + e3 + c3 + n4 + q4 + p4 + e4 + c4 + n5 + q5 + p5 + e5 + c5
end
local function q1_natural(c, lo, hi, acc)
  local sd, pr, q, d, t, rf, ls = c.sd, c.pr, c.q, c.d, c.t, c.rf, c.ls
  for i = lo, hi do
    if sd[i] <= 10471 then
      local g = (rf[i] * 2 + ls[i]) * 5
      local p = pr[i]
      local dp = p * (100 - d[i])
      acc[g + 1] = acc[g + 1] + 1; acc[g + 2] = acc[g + 2] + q[i]; acc[g + 3] = acc[g + 3] + p
      acc[g + 4] = acc[g + 4] + dp; acc[g + 5] = acc[g + 5] + dp * (100 + t[i])
    end
  end
end
local function q1_tuned(c, lo, hi, acc) -- accumulateurs locaux par groupe (pas d'indexation de table)
  local sd, pr, q, d, t, rf, ls = c.sd, c.pr, c.q, c.d, c.t, c.rf, c.ls
  local A = {}
  for g = 0, 5 do A[g] = { 0, 0, 0, 0, 0 } end
  for i = lo, hi do
    if sd[i] <= 10471 then
      local a = A[rf[i] * 2 + ls[i]]
      local p = pr[i]
      local dp = p * (100 - d[i])
      a[1] = a[1] + 1; a[2] = a[2] + q[i]; a[3] = a[3] + p; a[4] = a[4] + dp; a[5] = a[5] + dp * (100 + t[i])
    end
  end
  for g = 0, 5 do for k = 1, 5 do acc[g * 5 + k] = acc[g * 5 + k] + A[g][k] end end
end
local function run_k6(v, reps, p)
  local c = { sd = load("k6_shipdate.i32", "<i4", 4), pr = load("k6_extendedprice.i32", "<i4", 4), q = bytes("k6_quantity.u8"),
    d = bytes("k6_discount.u8"), t = bytes("k6_tax.u8"), rf = bytes("k6_returnflag.u8"), ls = bytes("k6_linestatus.u8") }
  collectgarbage()
  local q1 = p == "q1"
  bench("k6", v, p, reps, function()
    local s = 0
    -- v4, point 4 : tuned_s (Q6 : la variante tuned publiée en est déjà la forme) ; rq_nest et rq_nest_mt (Q6, tests
    -- imbriqués : un bloc, ou quatre morceaux en séquence comme mt)
    if q1 and v == "tuned_s" then return string.format("%d", q1_tuned_s(c, 1, N6)) end
    if not q1 and v == "rq_nest" then return string.format("%d", q6_nested(c, 1, N6)) end
    if not q1 and v == "rq_nest_mt" then
      for k = 0, 3 do s = s + q6_nested(c, k * (N6 // 4) + 1, (k + 1) * (N6 // 4)) end
      return string.format("%d", s)
    end
    if q1 then
      local acc = {}
      for k = 1, 30 do acc[k] = 0 end
      if v == "natural" then q1_natural(c, 1, N6, acc)
      else -- "mt" : pas de threads, 4 morceaux traités en séquence
        for k = 0, 3 do q1_tuned(c, k * (N6 // 4) + 1, (k + 1) * (N6 // 4), acc) end
      end
      for k = 1, 30 do s = s + acc[k] end
    else
      if v == "natural" then s = q6_natural(c, 1, N6)
      else for k = 0, 3 do s = s + q6_tuned(c, k * (N6 // 4) + 1, (k + 1) * (N6 // 4)) end end
    end
    return string.format("%d", s)
  end)
end

-- ------------------------------------------------------------------ K7
-- v4, point 4 (3.3, K7 tuned_oa : forme de repli, Lua n'ayant pas de préchargement) : la table de tuned_pf sans
-- préchargement : capacité 2^(LOG2+1), une case = deux entiers consécutifs de la partie tableau d'une table Lua (clé << 32
-- | compte, somme : 16 octets de données), allouée (table.create) et remise à zéro dans le chrono, hachage de Fibonacci
-- (clé × 0x9E3779B1 mod 2^32) >> (32 − LOG), sondage linéaire ; une case est vide si son premier entier vaut 0
local function k7_tuned_oa(keys, vals, n, log)
  local cap = 1 << log
  local msk, sh = cap - 1, 32 - log
  local tab = table.create(2 * cap)
  for s = 1, 2 * cap do tab[s] = 0 end
  for i = 1, n do
    local k = keys[i]
    local s = ((k * 0x9E3779B1) & 0xFFFFFFFF) >> sh
    while true do
      local w = tab[2 * s + 1]
      if w == 0 then tab[2 * s + 1] = (k << 32) | 1; tab[2 * s + 2] = vals[i]; break end
      if (w >> 32) == k then tab[2 * s + 1] = w + 1; tab[2 * s + 2] = tab[2 * s + 2] + vals[i]; break end
      s = (s + 1) & msk
    end
  end
  return tab
end
local function run_k7(v, reps)
  local keys = load("k7_keys.u32", "<I4", 4)
  local vals = load("k7_vals.u32", "<I4", 4)
  local n = #keys
  for r = -WARMUP, reps - 1 do
    local nk, ws, dt = 0, 0, 0
    if v == "natural" then
      local t0 = clock()
      local m = {}
      for i = 1, n do
        local k = keys[i]
        local e = m[k]
        if e then e[1] = e[1] + 1; e[2] = e[2] + vals[i] else m[k] = { 1, vals[i] } end
      end
      dt = clock() - t0
      for k, e in pairs(m) do nk = nk + 1; ws = ws + e[2] * ((k & 1023) + 1) end
    elseif v == "tuned_oa" then
      local t0 = clock()
      local tab = k7_tuned_oa(keys, vals, n, 21)
      dt = clock() - t0
      for s = 1, #tab, 2 do
        local w = tab[s]
        if w ~= 0 then nk = nk + 1; ws = ws + tab[s + 1] * (((w >> 32) & 1023) + 1) end
      end
    elseif v == "rq_pack" then -- v4, point 4 (3.5) : forme de la remarque sur Lua (bench/lua_exp, tuned_p ; docs/LUA.md :
      -- × 0,71), propre au runtime (représentation des tables de Lua) : une seule table, compte et somme tassés dans un
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
    else -- deux tables plates clé -> entier (pas de table par entrée)
      local t0 = clock()
      local cnt, sum = {}, {}
      for i = 1, n do
        local k = keys[i]
        local c = cnt[k]
        if c then cnt[k] = c + 1; sum[k] = sum[k] + vals[i] else cnt[k] = 1; sum[k] = vals[i] end
      end
      dt = clock() - t0
      for k, s in pairs(sum) do nk = nk + 1; ws = ws + s * ((k & 1023) + 1) end
    end
    if r >= 0 then result("k7", v, "16M/1M", r, dt, nk .. ":" .. ws) end
  end
end

-- ------------------------------------------------------------------ K8
local cnt8 = 0
-- remarque sur Lua (docs/LUA.md) : nœud en enregistrement à champs nommés, le type par défaut (comme K1)
local function t_build(d)
  local n = { v = cnt8, l = false, r = false }
  cnt8 = cnt8 + 1
  if d > 0 then n.l = t_build(d - 1); n.r = t_build(d - 1) end
  return n
end
local function t_sum(n) if not n then return 0 end; return n.v + t_sum(n.l) + t_sum(n.r) end
local AV, AL, AR, top = {}, {}, {}, 0
local function a_build(d)
  top = top + 1
  local i = top
  AV[i] = cnt8; cnt8 = cnt8 + 1
  if d > 0 then AL[i] = a_build(d - 1); AR[i] = a_build(d - 1) else AL[i] = 0; AR[i] = 0 end
  return i
end
local function a_sum(i) if i == 0 then return 0 end; return AV[i] + a_sum(AL[i]) + a_sum(AR[i]) end
-- v4, point 4 (3.3, K8 tuned_val) : la même arène (AV, AL, AR, indices depuis 1, 0 = pas d'enfant), construite en ordre
-- préfixe ; l'état passe par valeur (i : indice du nœud ; q : numéro de requête, valeur du nœud = q + i - 1), le
-- prochain indice libre revient en résultat ; ni variable globale d'état (top, cnt8). Somme : a_sum (récursive).
local function a_build_val(i, d, q)
  AV[i] = q + i - 1
  if d == 0 then AL[i] = 0; AR[i] = 0; return i + 1 end
  local l = i + 1
  local r = a_build_val(l, d - 1, q)
  AL[i] = l; AR[i] = r
  return a_build_val(r, d - 1, q)
end
-- v4, point 4 (3.3, K8 tuned_it) : la forme de la remarque sur Lua (bench/lua_exp ; docs/LUA.md), recopiée : arène
-- construite et parcourue par itération, piles explicites (tables) ; mêmes nœuds, mêmes valeurs, même ordre préfixe.
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
end
local function run_k8(v, reps)
  local Q = 16384
  cnt8 = 0
  local keep = t_build(20)
  local lsum = t_sum(keep)
  local lat = {}
  local tuned = v == "tuned"
  local tval, tit = v == "tuned_val", v == "tuned_it" -- v4, point 4
  for r = -WARMUP, reps - 1 do
    local total = 0
    local t0 = clock()
    for q = 0, Q - 1 do
      local a = clock()
      cnt8 = q
      local s
      if tval then a_build_val(1, 10, q); s = a_sum(1)
      elseif tit then top = 0; s = a_sum_it(a_build_it(10))
      elseif tuned then top = 0; s = a_sum(a_build(10)) else s = t_sum(t_build(10)) end
      total = total + s
      lat[q + 1] = (clock() - a) * 1e9
    end
    local dt = clock() - t0
    if r >= 0 then
      result("k8", v, "16384x2047", r, dt, string.format("%d", total + lsum))
      table.sort(lat)
      io.write(string.format("LAT;%s;%.0f;%.0f;%.0f;%.0f;%.0f\n", v, lat[Q // 2 + 1], lat[Q * 9 // 10 + 1], lat[Q * 99 // 100 + 1], lat[Q * 999 // 1000 + 1], lat[Q]))
    end
  end
end

-- ------------------------------------------------------------------ K9
local M9 = 2048
local function k9_init(i, j) return ((i * 31 + j * 17) % 1024) / 1024 end
local function k9_natural(a, b)
  for i = 2, M9 - 1 do
    local up, mid, dn, o = a[i - 1], a[i], a[i + 1], b[i]
    for j = 2, M9 - 1 do o[j] = 0.25 * (((up[j] + dn[j]) + mid[j - 1]) + mid[j + 1]) end
  end
end
local function k9_flat(a, b)
  for i = 1, M9 - 2 do
    local up, mid, dn = (i - 1) * M9, i * M9, (i + 1) * M9
    for j = 2, M9 - 1 do b[mid + j] = 0.25 * (((a[up + j] + a[dn + j]) + a[mid + j - 1]) + a[mid + j + 1]) end
  end
end
-- v4, point 4 (docs/V4_CONVERGE.md, 3.5 et 4.2, forme propre au runtime) : rq_slide, la forme de la remarque sur Lua
-- (bench/lua_exp, tuned_s ; docs/LUA.md : × 0,87), recopiée : voisins de gauche et du centre gardés dans des variables.
-- rq_slide_mt : le même code (la variante mt de Lua, sans fils, est celle de tuned).
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
local function run_k9(v, reps)
  -- harnais commun de K9 (docs/K9.md) : grilles allouées une fois par processus, réinitialisées hors chrono
  local ga, gb = {}, {}
  if v == "natural" then for i = 1, M9 do ga[i], gb[i] = {}, {} end end
  for r = -WARMUP, reps - 1 do
    local s, dt = 0.0, 0
    if v == "natural" then
      local a, b = ga, gb
      for i = 1, M9 do
        for j = 1, M9 do local x = k9_init(i - 1, j - 1); a[i][j] = x; b[i][j] = x end
      end
      local t0 = clock()
      k9_natural(a, b); k9_natural(b, a); k9_natural(a, b); k9_natural(b, a)
      dt = clock() - t0
      for i = 1, M9 do local row = a[i]; for j = 1, M9 do s = s + row[j] end end
    else  -- tuned, mt et (v4, point 3, R2) natural_flat : la boucle naturelle sur une table plate
      local a, b = ga, gb
      for k = 0, M9 * M9 - 1 do local x = k9_init(k // M9, k % M9); a[k + 1] = x; b[k + 1] = x end
      local f = (v == "rq_slide" or v == "rq_slide_mt") and k9_flat_s or k9_flat
      local t0 = clock()
      f(a, b); f(b, a); f(a, b); f(b, a)
      dt = clock() - t0
      for k = 1, M9 * M9 do s = s + a[k] end
    end
    if r >= 0 then result("k9", v, "2048^2x4", r, dt, string.format("%.15e", s)) end
  end
end

-- ------------------------------------------------------------------ K10
local M10 = 1 << 22
local CAP10 = 1 << 14
local function run_k10(v, reps)
  bench("k10", v, "2^22", reps, function()
    local s = 0
    if v == "natural" then -- coroutines : mécanisme de concurrence natif de Lua (producteur/consommateur)
      local prod = coroutine.wrap(function() for x = 1, M10 do coroutine.yield(x) end end)
      for _ = 1, M10 do s = s + prod() end
    else -- anneau borné + coroutine qui remplit par lots (moins de commutations)
      local buf, w, rd = {}, 0, 0
      local prod = coroutine.wrap(function()
        local x = 1
        while x <= M10 do
          while w - rd < CAP10 and x <= M10 do buf[(w & (CAP10 - 1)) + 1] = x; w = w + 1; x = x + 1 end
          coroutine.yield()
        end
      end)
      for _ = 1, M10 do
        if rd == w then prod() end
        s = s + buf[(rd & (CAP10 - 1)) + 1]; rd = rd + 1
      end
    end
    return string.format("%d", s)
  end)
end

local k, v, reps, p = arg[1], arg[2], tonumber(arg[3]), arg[4] or ""
if k == "k1" then run_k1(v, reps)
elseif k == "k2" then run_k2(v, reps, p)
elseif k == "k3" then run_k3(v, reps)
elseif k == "k4" then run_k4(v, reps)
elseif k == "k5" then run_k5(v, reps)
elseif k == "k6" then run_k6(v, reps, p)
elseif k == "k7" then run_k7(v, reps)
elseif k == "k8" then run_k8(v, reps)
elseif k == "k9" then run_k9(v, reps)
elseif k == "k10" then run_k10(v, reps) end
