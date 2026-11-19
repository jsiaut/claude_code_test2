-- Audit de la grille, Lua 5.5.1 (interpréteur de référence du banc) : chaque case est exercée et imprime un fait
-- observable (docs/V4_PLAN.md 2.1). Lignes FACT (reprises par run.sh avec les formes refusées et les recherches) et
-- NOTE (contre-épreuves).
local function fact(c, ev) print(("FACT;%s;%s"):format(c, ev)) end
local function note(c, ev) print(("NOTE;%s;%s"):format(c, ev)) end
local function kb() collectgarbage("collect"); collectgarbage("collect"); return collectgarbage("count") end

-- ---------- A
local n = 100000
local k0 = kb()
local arr = {}
for i = 1, n do arr[i] = { x = i + 0.5, y = 0.5, z = 0.5, w = 0.5 } end
local k1 = kb()
fact("A1", ("table de %d tables {x, y, z, w} : %.0f o par élément pour 32 o de données (références vers des tables séparées)"):format(n, (k1 - k0) * 1024 / n))
arr = nil
local packed = string.pack("<BI4", 7, 123456789)
note("A3", ("string.pack('<BI4') range {octet; entier de 4 o} en %d o, dans une chaîne immuable (comme pour A8 : stockage en lecture seule)"):format(#packed))
fact("A5", ("string.unpack('<I4', string.pack('<f', 1.0)) = 0x%08x : réinterprétation par copie dans une chaîne, pas d'union"):format(string.unpack("<I4", string.pack("<f", 1.0))))
local w = { f = {}, n = 2 }
for i = 1, 16 do w.f[i] = 0.0 end
fact("A7", ("{f = {16 nombres}, n} : f est une référence vers une table séparée (type %s)"):format(type(w.f)))
fact("A8", ("math.type(1) = %s, math.type(1.5) = %s : entiers et flottants de 64 bits seulement ; string.pack('<i1 i2 f') donne %d o, en lecture seule"):format(math.type(1), math.type(1.5), #string.pack("<i1 i2 f", 1, 2, 3.0)))

-- ---------- B
collectgarbage("restart")
local c0 = kb()
local peak = c0
for i = 1, 1 << 20 do
  local s = string.rep("x", 1000) .. i
  if i % 65536 == 0 then local c = collectgarbage("count"); if c > peak then peak = c end end
end
fact("B1", ("1 Gio de chaînes de 1 Kio sans référence : la mémoire du tas reste sous %.0f Kio (le ramasse-miettes incrémental les rend de lui-même ; aucune autre façon de les rendre)"):format(peak))
collectgarbage("stop")
local s0 = collectgarbage("count")
for i = 1, 256 * 1024 do local s = string.rep("y", 1000) .. i end
local s1 = collectgarbage("count")
collectgarbage("restart")
collectgarbage("collect")
note("B1", ("collectgarbage('stop') : 256 Mio de chaînes sans référence, tas %.0f → %.0f Mio (rien n'est rendu) ; après 'restart' et 'collect' : %.0f Mio"):format(s0 / 1024, s1 / 1024, collectgarbage("count") / 1024))
local function two(i) return i, i + 1 end
local acc = 0
collectgarbage("stop")
local m0 = collectgarbage("count")
for i = 1, 1000000 do local a, b = two(i); acc = acc + a + b * 0.5 end
local m1 = collectgarbage("count")
local f0 = collectgarbage("count")
local fs = {}
for i = 1, 100000 do fs[1] = function() return i end end
local f1 = collectgarbage("count")
local t0 = collectgarbage("count")
for i = 1, 100000 do fs[1] = { i } end
local t1 = collectgarbage("count")
collectgarbage("restart")
fact("B3", ("un million d'appels à une fonction qui rend deux valeurs (pile de la machine virtuelle) et d'opérations sur des nombres : %.0f octets alloués"):format((m1 - m0) * 1024))
fact("B4", ("allocations implicites : fermeture créée %.0f o, constructeur de table {i} %.0f o (par itération, ramasse-miettes arrêté) ; arithmétique et appels 0 (B3)"):format((f1 - f0) * 1024 / 100000, (t1 - t0) * 1024 / 100000))

-- ---------- C
local st = 42
local big = {}
for i = 1, 1 << 20 do st = (st * 6364136223846793005 + 1442695040888963407); big[i] = ((st >> 11) / 9007199254740992.0) - 0.5 end
local s = 0.0
for i = 1, #big do s = s + big[i] end
local function pw(a, lo, hi)
  if hi - lo <= 8 then local t = 0.0; for i = lo, hi - 1 do t = t + a[i] end; return t end
  local m = (lo + hi) // 2
  return pw(a, lo, m) + pw(a, m, hi)
end
local p = pw(big, 1, #big + 1)
fact("C4", ("un million de nombres : boucle %.17g, somme par paires écrite à la main %.17g (écart %.3g) : l'ordre est gardé"):format(s, p, math.abs(p - s)))

-- ---------- D
local log = {}
local co = {}
for k = 1, 4 do co[k] = coroutine.create(function() for j = 1, 3 do log[#log + 1] = k; coroutine.yield() end end) end
for _ = 1, 3 do for k = 1, 4 do coroutine.resume(co[k]) end end
fact("D1", ("4 coroutines (type %s) alternent sur un seul fil système : ordre %s ; aucune API de fils parallèles"):format(type(co[1]), table.concat(log, "", 1, 8)))

-- ---------- E
local four = { 1, 2, 3, 4 }
fact("E6", ("four[10] = %s : la lecture d'une case absente rend nil ; ni contrôle à couper ni accès non vérifié"):format(tostring(four[10])))

-- ---------- F
local g = { { 1, 2, 3, 4 }, { 5, 6, 7, 8 }, { 9, 10, 11, 12 } }
g[2] = { 0, 0, 0, 0, 0, 0, 0 }
fact("F1", ("pas de tableau multidimensionnel : table de lignes séparées (g[2] remplacée par une ligne de %d)"):format(#g[2]))
fact("F3", ("math.maxinteger + 1 == math.mininteger : %s ; math.ult(1, -1) = %s ; entiers de 64 bits signés seulement"):format(tostring(math.maxinteger + 1 == math.mininteger), tostring(math.ult(1, -1))))
