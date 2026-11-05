-- Sonde K3 sous LuaJIT (remarque sur Lua, docs/LUA.md 2) : quatre compteurs incrémentés 2^25 fois chacun, en séquence.
-- jit_volatile : le code publié (tableau FFI volatile, compilé : le JIT ignore volatile) ; jit_table : table Lua,
-- compilée ; interp_ffi / interp_table : la même boucle interprétée (jit.off sur une fonction neuve).
-- Usage : luajit luajit_k3.lua
local ffi = require("ffi")
local src = [[
local c, base, stride, N = ...
for t = 0, 3 do c[base + t * stride] = 0 end
for t = 0, 3 do local idx = base + t * stride; for _ = 1, N do c[idx] = c[idx] + 1 end end
local s = 0
for t = 0, 3 do s = s + tonumber(c[base + t * stride]) end
return s
]]
local N = 33554432
local function run(name, mk, jit_on, stride)
  local f = assert(loadstring(src))
  if not jit_on then jit.off(f, true) end
  local c = mk()
  local t0 = os.clock()
  local s = f(c, 16, stride, N)
  local dt = os.clock() - t0
  print(string.format("%-14s stride %2d : %.3f s, %.2f ns/incrément, somme %d", name, stride, dt, dt / (4 * N) * 1e9, s))
end
local function ffi_arr() return ffi.new("volatile int64_t[?]", 128) end
local function lua_tab() local t = {}; for i = 1, 128 do t[i] = 0 end; return t end
for _, stride in ipairs({ 1, 16 }) do
  run("jit_volatile", ffi_arr, true, stride)
  run("jit_table", lua_tab, true, stride)
  run("interp_ffi", ffi_arr, false, stride)
  run("interp_table", lua_tab, false, stride)
end
