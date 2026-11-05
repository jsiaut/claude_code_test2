-- Sonde des faits de la remarque sur Lua (docs/LUA.md, 2) : version, nouveautés de la 5.5, empreinte d'une particule,
-- allocations cachées (B4), valeurs et retours multiples hors du tas (B3), stockage étroit par string.pack (A8).
-- Usage : /opt/lua55/bin/lua facts.lua
print(_VERSION, "table.create : " .. tostring(table.create ~= nil))
print("collectgarbage('param', 'pause') : " .. tostring(pcall(collectgarbage, "param", "pause")) .. " "
      .. tostring(select(2, pcall(collectgarbage, "param", "pause"))))
print("mode incrémental : " .. tostring(collectgarbage("incremental")) .. " (mode précédent)")
local function kb() collectgarbage("collect"); collectgarbage("collect"); return collectgarbage("count") * 1024 end
collectgarbage("stop")
-- empreinte : N tables vides, N tables à 16 champs nommés, cases d'un tableau
local N = 100000
local hold, b0
b0 = kb(); hold = {}; for i = 1, N do hold[i] = {} end
local per_ref = (kb() - b0) / N
hold = nil
b0 = kb(); hold = table.create(N); local base = kb() - b0
for i = 1, N do hold[i] = {} end
local per_empty = (kb() - b0 - base) / N
print(string.format("table vide : %.1f o ; case du tableau qui la contient : %.1f o", per_empty, base / N))
hold = nil
b0 = kb(); hold = table.create(N); base = kb() - b0
for i = 1, N do
  local x = i + 0.5
  hold[i] = { x = x, y = x, z = x, vx = x, vy = x, vz = x, ax = x, ay = x, az = x, mass = x, charge = x, radius = x,
    temp = x, pressure = x, energy = x, density = x }
end
local per16 = (kb() - b0 - base) / N
print(string.format("particule à 16 champs nommés : %.1f o (+ %.1f o de case) = %.1f o", per16, base / N, per16 + base / N))
hold = nil
b0 = kb(); hold = table.create(1000000); for i = 1, 1000000 do hold[i] = i + 0.5 end
print(string.format("case d'un tableau de flottants : %.2f o", (kb() - b0) / 1000000))
hold = nil
-- B4 : arithmétique, retours multiples, varargs ; puis concaténation, fermetures, croissance d'une table
local function delta(f) local a = kb(); f(); return kb() - a end
collectgarbage("stop")
local function mid() collectgarbage("stop"); return collectgarbage("count") * 1024 end
local function run(f) local a = mid(); f(); return collectgarbage("count") * 1024 - a end
print(string.format("1e6 opérations flottantes et entières : %d o alloués", run(function()
  local s, k = 0.0, 0; for i = 1, 1000000 do s = s + i * 0.5; k = k + (i & 7) end end)))
local function three(i) return i, i + 1.5, i * 2 end
print(string.format("1e6 appels à trois retours : %d o alloués", run(function()
  local s = 0; for i = 1, 1000000 do local a, b, c = three(i); s = s + a + b + c end end)))
local function va(...) local a, b, c = ...; return a + b + c + select("#", ...) end
print(string.format("1e6 appels variadiques (3 arguments) : %d o alloués", run(function()
  local s = 0; for i = 1, 1000000 do s = s + va(i, i, i) end end)))
print(string.format("1e5 concaténations : %d o alloués", run(function()
  local t = {}; for i = 1, 100000 do t[1] = "k" .. i end end)))
print(string.format("1e5 fermetures : %d o alloués", run(function()
  local f; for i = 1, 100000 do f = function() return i end end end)))
print(string.format("une table de 1e5 entiers construite par t[#t+1] : %d o alloués", run(function()
  local t = {}; for i = 1, 100000 do t[#t + 1] = i end end)))
collectgarbage("restart")
-- A8 : stockage étroit en lecture seule par string.pack
local s = string.pack("<i1i2i4f", -5, 1000, 70000, 0.1)
print("string.pack('<i1i2i4f') : " .. #s .. " octets ; relu : " .. table.concat({ string.unpack("<i1i2i4f", s) }, ", ", 1, 4))
print("écriture en place dans une chaîne : " .. tostring(pcall(function() s[1] = 0 end)))
