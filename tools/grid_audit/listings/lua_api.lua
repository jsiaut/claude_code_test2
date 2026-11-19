-- API de la bibliothèque standard de Lua 5.5 du banc : noms de _G et des tables de bibliothèque (string, table, math,
-- io, os, coroutine, utf8, debug, package…), un par ligne, avec les méthodes des fichiers et des chaînes, pour
-- tools/grid_audit/search.py.
local out, seen = {}, {}
local function walk(prefix, t, depth)
  if seen[t] or depth > 2 then return end
  seen[t] = true
  for k, v in pairs(t) do
    if type(k) == "string" then
      out[#out + 1] = prefix .. k
      if type(v) == "table" and k ~= "loaded" and k ~= "_G" then walk(prefix .. k .. ".", v, depth + 1) end
    end
  end
end
walk("", _G, 0)
walk("file:", getmetatable(io.stdout).__index, 0)
walk("string-meta:", getmetatable("").__index, 0)
table.sort(out)
for _, l in ipairs(out) do print(l) end
