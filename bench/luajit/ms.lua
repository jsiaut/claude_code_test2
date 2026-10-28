-- Implémentation LuaJIT 2.1 (dialecte Lua 5.1 + extensions LuaJIT : ffi, bit). Voir docs/SPEC.md.
-- Variante indicative : les « natural » utilisent des tables Lua, les « tuned » la FFI de LuaJIT
-- (tableaux et structures C contigus, compilés par le JIT à traces). Pas de threads.
local ffi = require("ffi")
local bit = require("bit")
local band, bor, rshift, lshift, bxor = bit.band, bit.bor, bit.rshift, bit.lshift, bit.bxor

local DATA = os.getenv("MS_DATA") or "/opt/msdata"
local WARMUP = tonumber(os.getenv("WARMUP") or "3")
local clock = os.clock

local function read_all(name)
  local f = assert(io.open(DATA .. "/" .. name, "rb"))
  local s = f:read("*a")
  f:close()
  return s
end
-- chargement FFI : copie brute dans un tableau C aligné (hors chrono)
local function cload(name, ctype)
  local s = read_all(name)
  local n = #s / ffi.sizeof(ctype)
  local p = ffi.new(ctype .. "[?]", n + 16)
  ffi.copy(p, s, #s)
  return p, n
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
local N1 = 4194304
ffi.cdef [[
typedef struct { float x, y, z, vx, vy, vz, ax, ay, az, mass, charge, radius, temp, pressure, energy, density; } particle;
typedef struct { uint32_t key, count; uint64_t sum; } slot;
typedef struct { int64_t v; int32_t l, r; } anode;
]]
local function k1_natural(ps)
  local e = 0.0
  for i = 1, #ps do local p = ps[i]; e = e + 0.5 * p.mass * (p.vx * p.vx + p.vy * p.vy + p.vz * p.vz) end
  return e
end
local function k1_aos(ps) -- tableau C de structures (AoS valeur, via FFI)
  local e = 0.0
  for i = 0, N1 - 1 do local p = ps[i]; e = e + 0.5 * p.mass * (p.vx * p.vx + p.vy * p.vy + p.vz * p.vz) end
  return e
end
local function k1_soa(vx, vy, vz, m)
  local e = 0.0
  for i = 0, N1 - 1 do local x, y, z = vx[i], vy[i], vz[i]; e = e + 0.5 * m[i] * (x * x + y * y + z * z) end
  return e
end
-- Empreinte K1 (D2a) : octets alloués par LuaJIT après un GC complet, et RSS courant (pages de 4 Kio)
local function live_now() collectgarbage("collect"); collectgarbage("collect"); return math.floor(collectgarbage("count") * 1024) end
local function rss_now()
  local f = io.open("/proc/self/statm", "r")
  if not f then return 0 end
  local _, res = f:read("*n", "*n")
  f:close()
  return math.floor(res * 4096)
end
local function run_k1(v, reps)
  if v == "footprint0" then return result("k1", v, "energy", 0, 0, "0") end
  local raw = cload("k1_particles.f32", "float")
  if v == "footprint_raw" then return result("k1", v, "energy", 0, 0, "0") end
  local f6 = function(x) return string.format("%.6f", x) end
  if v == "aos" then
    -- un pointeur obtenu par ffi.cast ne garde pas l'objet d'origine vivant : sans la référence
    -- à raw dans la fermeture, le GC libère le tableau et le parcours lit de la mémoire libérée (SIGSEGV observé)
    local ps = ffi.cast("particle*", raw)
    return bench("k1", v, "energy", reps, function() local _ = raw; return f6(k1_aos(ps)) end)
  end
  if v == "soa" then
    local function col(k) local c = ffi.new("float[?]", N1); for i = 0, N1 - 1 do c[i] = raw[16 * i + k] end; return c end
    local vx, vy, vz, m = col(3), col(4), col(5), col(9)
    return bench("k1", v, "energy", reps, function() return f6(k1_soa(vx, vy, vz, m)) end)
  end
  local m1, r1 = 0, 0
  if v == "footprint" then m1, r1 = live_now(), rss_now() end -- P1 : tampon brut chargé
  local ps = {}
  for i = 1, N1 do
    local o = 16 * (i - 1)
    ps[i] = { x = raw[o], y = raw[o + 1], z = raw[o + 2], vx = raw[o + 3], vy = raw[o + 4], vz = raw[o + 5], ax = raw[o + 6], ay = raw[o + 7],
      az = raw[o + 8], mass = raw[o + 9], charge = raw[o + 10], radius = raw[o + 11], temp = raw[o + 12], pressure = raw[o + 13],
      energy = raw[o + 14], density = raw[o + 15] }
  end
  if v == "footprint" then
    local m2, r2 = live_now(), rss_now() -- P2 : collection construite, tampon brut encore vivant
    print(string.format("META;mem;live;%d;%d\nMETA;rss;%d;%d\nMETA;raw0;%s", m1, m2, r1, r2, tostring(raw[0])))
    return result("k1", v, "energy", 0, 0, f6(k1_natural(ps)))
  end
  raw = nil; collectgarbage()
  if v == "natural_shuffled" then
    local perm = cload("k1_perm.u32", "uint32_t")
    local s = {}
    for j = 1, N1 do s[j] = ps[perm[j - 1] + 1] end
    ps = s; collectgarbage()
  end
  bench("k1", v, "energy", reps, function() return f6(k1_natural(ps)) end)
end

-- ------------------------------------------------------------------ K2
local function k2_chase(a, h) local i = 0; for _ = 1, h do i = a[i] end; return i end
local function run_k2(v, reps, p)
  local a = cload("k2_chase_" .. p .. ".u32", "uint32_t")
  bench("k2", v, p, reps, function() return tostring(k2_chase(a, 4200000)) end)
end

-- ------------------------------------------------------------------ K3
local function run_k3(v, reps)
  print("META;k3_mechanism;pas de threads dans LuaJIT : exécution séquentielle ; le JIT ignore volatile (compteur maintenu en registre, mesuré ~0,3 ns/incrément)")
  local stride = v:sub(-6) == "padded" and 16 or 1
  local c = ffi.new("volatile int64_t[?]", 128)
  bench("k3", v, "4x2^25", reps, function()
    for t = 0, 3 do c[16 + t * stride] = 0 end
    for t = 0, 3 do local idx = 16 + t * stride; for _ = 1, 33554432 do c[idx] = c[idx] + 1 end end
    local s = 0
    for t = 0, 3 do s = s + tonumber(c[16 + t * stride]) end
    return string.format("%d", s)
  end)
end

-- ------------------------------------------------------------------ K4
local function k4_natural(d, n) local s = 0; for i = 0, n - 1 do local x = d[i]; if x >= 128 then s = s + x end end; return s end
local function k4_branchless(d, n) local s = 0; for i = 0, n - 1 do local x = d[i]; s = s + x * rshift(x, 7) end; return s end
local function run_k4(v, reps)
  local d, n = cload("k4_bytes.u8", "uint8_t")
  if v == "natural_sorted" then
    local cnt = {}
    for b = 0, 255 do cnt[b] = 0 end
    for i = 0, n - 1 do cnt[d[i]] = cnt[d[i]] + 1 end
    local k = 0
    for b = 0, 255 do for _ = 1, cnt[b] do d[k] = b; k = k + 1 end end
  end
  local f = v == "branchless_unsorted" and k4_branchless or k4_natural
  bench("k4", v, "16M", reps, function() return string.format("%d", f(d, n)) end)
end

-- ------------------------------------------------------------------ K5
local function k5_natural(a, b, n) local s = 0.0; for i = 0, n - 1 do s = s + a[i] * b[i] end; return s end
local function k5_tuned(a, b, n)
  local s0, s1, s2, s3 = 0.0, 0.0, 0.0, 0.0
  for i = 0, n - 1, 4 do
    s0 = s0 + a[i] * b[i]; s1 = s1 + a[i + 1] * b[i + 1]; s2 = s2 + a[i + 2] * b[i + 2]; s3 = s3 + a[i + 3] * b[i + 3]
  end
  return (s0 + s1) + (s2 + s3)
end
local function run_k5(v, reps)
  local a, n = cload("k5_a.f32", "float")
  local b = cload("k5_b.f32", "float")
  local f = v == "tuned" and k5_tuned or k5_natural
  bench("k5", v, "2048x65536", reps, function()
    local d = 0.0
    for _ = 1, 65536 do d = f(a, b, n) end
    return string.format("%.4f", d)
  end)
end

-- ------------------------------------------------------------------ K6
local N6 = 16777216
local function q6_natural(c, lo, hi)
  local sd, d, q, pr = c.sd, c.d, c.q, c.pr
  local s = 0
  for i = lo, hi - 1 do if sd[i] >= 8766 and sd[i] < 9131 and d[i] >= 5 and d[i] <= 7 and q[i] < 24 then s = s + pr[i] * d[i] end end
  return s
end
local function q6_tuned(c, lo, hi) -- prédicat arithmétique sans branchement (bit.* sur 32 bits)
  local sd, d, q, pr = c.sd, c.d, c.q, c.pr
  local s = 0
  for i = lo, hi - 1 do
    local dd = d[i]
    -- lo <= x <= hi  <=>  bits de signe de (x - lo) et (hi - x) nuls ; rshift(x - n, 31) = 1 ssi x < n
    local x = sd[i]
    local m = (1 - rshift(bor(x - 8766, 9130 - x), 31)) * (1 - rshift(bor(dd - 5, 7 - dd), 31)) * rshift(q[i] - 24, 31)
    s = s + pr[i] * dd * m
  end
  return s
end
local function q1_natural(c, lo, hi, acc)
  local sd, pr, q, d, t, rf, ls = c.sd, c.pr, c.q, c.d, c.t, c.rf, c.ls
  for i = lo, hi - 1 do
    if sd[i] <= 10471 then
      local g = (rf[i] * 2 + ls[i]) * 5
      local p = pr[i]
      local dp = p * (100 - d[i])
      acc[g] = acc[g] + 1; acc[g + 1] = acc[g + 1] + q[i]; acc[g + 2] = acc[g + 2] + p
      acc[g + 3] = acc[g + 3] + dp; acc[g + 4] = acc[g + 4] + dp * (100 + t[i])
    end
  end
end
local function q1_tuned(c, lo, hi, acc) -- sélection par masque (contributions multipliées par 0/1)
  local sd, pr, q, d, t, rf, ls = c.sd, c.pr, c.q, c.d, c.t, c.rf, c.ls
  for i = lo, hi - 1 do
    local m = rshift(10471 - sd[i], 31) == 0 and 1 or 0
    local g = (rf[i] * 2 + ls[i]) * 5
    local p = pr[i] * m
    local dp = p * (100 - d[i])
    acc[g] = acc[g] + m; acc[g + 1] = acc[g + 1] + q[i] * m; acc[g + 2] = acc[g + 2] + p
    acc[g + 3] = acc[g + 3] + dp; acc[g + 4] = acc[g + 4] + dp * (100 + t[i])
  end
end
local function run_k6(v, reps, p)
  local c = { sd = cload("k6_shipdate.i32", "int32_t"), pr = cload("k6_extendedprice.i32", "int32_t"), q = cload("k6_quantity.u8", "uint8_t"),
    d = cload("k6_discount.u8", "uint8_t"), t = cload("k6_tax.u8", "uint8_t"), rf = cload("k6_returnflag.u8", "uint8_t"), ls = cload("k6_linestatus.u8", "uint8_t") }
  local q1 = p == "q1"
  local nat = v == "natural"
  bench("k6", v, p, reps, function()
    local s = 0
    if q1 then
      local acc = ffi.new("double[30]") -- doubles : sommes exactes (< 2^53)
      if nat then q1_natural(c, 0, N6, acc)
      else for k = 0, 3 do q1_tuned(c, k * N6 / 4, (k + 1) * N6 / 4, acc) end end -- « mt » : 4 morceaux en séquence
      for k = 0, 29 do s = s + acc[k] end
    elseif nat then s = q6_natural(c, 0, N6)
    else for k = 0, 3 do s = s + q6_tuned(c, k * N6 / 4, (k + 1) * N6 / 4) end end
    return string.format("%.0f", s)
  end)
end

-- ------------------------------------------------------------------ K7
local function run_k7(v, reps)
  local keys, n = cload("k7_keys.u32", "uint32_t")
  local vals = cload("k7_vals.u32", "uint32_t")
  for r = -WARMUP, reps - 1 do
    local nk, ws, dt = 0, 0, 0
    if v == "natural" then
      local t0 = clock()
      local m = {}
      for i = 0, n - 1 do
        local k = keys[i]
        local e = m[k]
        if e then e[1] = e[1] + 1; e[2] = e[2] + vals[i] else m[k] = { 1, vals[i] } end
      end
      dt = clock() - t0
      for k, e in pairs(m) do nk = nk + 1; ws = ws + e[2] * (band(k, 1023) + 1) end
    else -- adressage ouvert dans un tableau C de structures (FFI)
      local CAP = 2097152
      local t0 = clock()
      local tab = ffi.new("slot[?]", CAP)
      for i = 0, n - 1 do
        local k = keys[i]
        local s = rshift(tonumber(ffi.cast("uint32_t", k * 2654435761ULL)), 11)
        while tab[s].count ~= 0 and tab[s].key ~= k do s = band(s + 1, CAP - 1) end
        local e = tab[s]
        e.key = k; e.count = e.count + 1; e.sum = e.sum + vals[i]
      end
      dt = clock() - t0
      for s = 0, CAP - 1 do if tab[s].count ~= 0 then nk = nk + 1; ws = ws + tonumber(tab[s].sum) * (band(tab[s].key, 1023) + 1) end end
    end
    if r >= 0 then result("k7", v, "16M/1M", r, dt, string.format("%d:%.0f", nk, ws)) end
  end
end

-- ------------------------------------------------------------------ K8
local cnt8 = 0
local function t_build(d)
  local n = { cnt8, false, false }
  cnt8 = cnt8 + 1
  if d > 0 then n[2] = t_build(d - 1); n[3] = t_build(d - 1) end
  return n
end
local function t_sum(n) if not n then return 0 end; return n[1] + t_sum(n[2]) + t_sum(n[3]) end
local arena = ffi.new("anode[2048]")
local top = 0
local function a_build(d)
  local i = top; top = top + 1
  arena[i].v = cnt8; cnt8 = cnt8 + 1
  if d > 0 then local l = a_build(d - 1); arena[i].l = l; arena[i].r = a_build(d - 1) else arena[i].l = -1; arena[i].r = -1 end
  return i
end
local function a_sum(i) if i < 0 then return 0 end; local nd = arena[i]; return tonumber(nd.v) + a_sum(nd.l) + a_sum(nd.r) end
local function run_k8(v, reps)
  local Q = 16384
  cnt8 = 0
  local keep = t_build(20)
  local lsum = t_sum(keep)
  local lat = {}
  for r = -WARMUP, reps - 1 do
    local total = 0
    local t0 = clock()
    for q = 0, Q - 1 do
      local a = clock()
      cnt8 = q
      local s
      if v == "tuned" then top = 0; s = a_sum(a_build(10)) else s = t_sum(t_build(10)) end
      total = total + s
      lat[q + 1] = (clock() - a) * 1e9
    end
    local dt = clock() - t0
    if r >= 0 then
      result("k8", v, "16384x2047", r, dt, string.format("%.0f", total + lsum))
      table.sort(lat)
      io.write(string.format("LAT;%s;%.0f;%.0f;%.0f;%.0f;%.0f\n", v, lat[math.floor(Q / 2) + 1], lat[math.floor(Q * 9 / 10) + 1], lat[math.floor(Q * 99 / 100) + 1], lat[math.floor(Q * 999 / 1000) + 1], lat[Q]))
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
    for j = 1, M9 - 2 do b[mid + j] = 0.25 * (((a[up + j] + a[dn + j]) + a[mid + j - 1]) + a[mid + j + 1]) end
  end
end
local function run_k9(v, reps)
  for r = -WARMUP, reps - 1 do
    local s, dt = 0.0, 0
    if v == "natural" then
      local a, b = {}, {}
      for i = 1, M9 do a[i], b[i] = {}, {}; for j = 1, M9 do local x = k9_init(i - 1, j - 1); a[i][j] = x; b[i][j] = x end end
      local t0 = clock()
      k9_natural(a, b); k9_natural(b, a); k9_natural(a, b); k9_natural(b, a)
      dt = clock() - t0
      for i = 1, M9 do local row = a[i]; for j = 1, M9 do s = s + row[j] end end
    else
      local a, b = ffi.new("double[?]", M9 * M9), ffi.new("double[?]", M9 * M9)
      for k = 0, M9 * M9 - 1 do local x = k9_init(math.floor(k / M9), k % M9); a[k] = x; b[k] = x end
      local t0 = clock()
      k9_flat(a, b); k9_flat(b, a); k9_flat(a, b); k9_flat(b, a)
      dt = clock() - t0
      for k = 0, M9 * M9 - 1 do s = s + a[k] end
    end
    if r >= 0 then result("k9", v, "2048^2x4", r, dt, string.format("%.15e", s)) end
  end
end

-- ------------------------------------------------------------------ K10
local M10 = 4194304
local CAP10 = 16384
local function run_k10(v, reps)
  bench("k10", v, "2^22", reps, function()
    local s = 0
    if v == "natural" then
      local prod = coroutine.wrap(function() for x = 1, M10 do coroutine.yield(x) end end)
      for _ = 1, M10 do s = s + prod() end
    else
      local buf = ffi.new("int64_t[?]", CAP10)
      local w, rd = 0, 0
      local prod = coroutine.wrap(function()
        local x = 1
        while x <= M10 do
          while w - rd < CAP10 and x <= M10 do buf[band(w, CAP10 - 1)] = x; w = w + 1; x = x + 1 end
          coroutine.yield()
        end
      end)
      for _ = 1, M10 do
        if rd == w then prod() end
        s = s + tonumber(buf[band(rd, CAP10 - 1)]); rd = rd + 1
      end
    end
    return string.format("%.0f", s)
  end)
end

local k, v, reps, p = arg[1], arg[2], tonumber(arg[3]), arg[4] or ""
local fns = { k1 = run_k1, k3 = run_k3, k4 = run_k4, k5 = run_k5, k7 = run_k7, k8 = run_k8, k9 = run_k9, k10 = run_k10 }
if k == "k2" then run_k2(v, reps, p) elseif k == "k6" then run_k6(v, reps, p) elseif fns[k] then fns[k](v, reps) end
