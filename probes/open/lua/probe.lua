-- v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de Lua
-- (D1 : lua-llthreads2 0.1.6 ; F1 : vmsl 1.1). Modules C construits sous /opt/open/lua/lib.
package.cpath = "/opt/open/lua/lib/?.so;" .. package.cpath
local llthreads = require("llthreads2")
local matrix = require("matrix")
local vectors = require("vectors")

local function d1()
  local code = [[
    local i, n = ...
    local s = 0
    for k = i * n + 1, (i + 1) * n do s = s + k end
    return s
  ]]
  local n = 25000000
  local th, total = {}, 0
  local start = os.clock()
  -- temps écoulé lu par date(1) hors des boucles ; os.clock() donne le temps processeur du processus
  local function now() local f = io.popen("date +%s.%N"); local v = tonumber(f:read("l")); f:close(); return v end
  local a = now()
  for i = 0, 3 do th[i] = llthreads.new(code, i, n); th[i]:start() end
  for i = 0, 3 do local ok, s = th[i]:join(); total = total + s end
  local b = now()
  local cpu = os.clock() - start
  local s1 = 0
  for k = 1, 4 * n do s1 = s1 + k end
  local c = now()
  print(string.format("RESULT;D1;lua-llthreads2;4 fils llthreads2 (états Lua séparés, arguments copiés) : somme = %d (attendu %d) en %.2f s écoulées et %.2f s de processeur, contre %.2f s pour la même boucle dans le fil principal ; aucune mémoire partagée entre états",
    total, s1, b - a, cpu, c - b))
end

local function f1()
  local m, n = 300, 500
  local a = matrix.CreateMatrix(m, n)
  a[{3, 4}] = 7.0   -- indices à partir de 1 : ligne 3, colonne 4
  local idx = -1
  for k = 1, m * n do if a[k] == 7.0 then idx = k end end
  local v1 = vectors.CreateVector(1, 2, 3, 4)
  local v2 = vectors.CreateVector(4, 3, 2, 1)
  print(string.format("RESULT;F1;vmsl;matrix.CreateMatrix(%d, %d) de dimensions connues à l'exécution : a[{3, 4}] = 7 lu à l'accès linéaire a[%d] = (3-1)*%d+4 (tampon double contigu, par lignes) ; vecteurs : (1,2,3,4) * (4,3,2,1) = %g",
    m, n, idx, n, v1 * v2))
end

d1()
f1()
