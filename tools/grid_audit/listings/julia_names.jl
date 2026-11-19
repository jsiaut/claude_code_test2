# Liste des noms publics de Julia (Base, Core, leurs sous-modules et toutes les bibliothèques standard livrées), un par
# ligne, « Module.nom ». Sert à tools/grid_audit/search.py (introspection : docs/V4_PLAN.md 2.1, classe [recherche]).
seen = Set{Module}()
out = String[]
function walk(m::Module, depth=0)
  m in seen && return
  push!(seen, m)
  for n in names(m; all=false, imported=false)
    s = string(n)
    push!(out, string(nameof(m) == :Main ? "" : string(m) * ".", s))
    if depth < 2 && isdefined(m, n)
      v = getfield(m, n)
      v isa Module && v !== m && parentmodule(v) === m && walk(v, depth + 1)
    end
  end
end
walk(Core); walk(Base)
for sub in (:Threads, :Experimental, :Libc, :Iterators, :Sys, :GC, :Filesystem, :Meta, :Broadcast, :Checked, :SimdLoop, :MathConstants, :Order)
  isdefined(Base, sub) && walk(getfield(Base, sub), 1)
end
stdlib = joinpath(Sys.BINDIR, "..", "share", "julia", "stdlib", "v$(VERSION.major).$(VERSION.minor)")
for d in sort(readdir(stdlib))
  isfile(joinpath(stdlib, d, "Project.toml")) || continue
  try
    @eval using $(Symbol(d))
    walk(getfield(Main, Symbol(d)), 1)
  catch
  end
end
foreach(println, sort(unique(out)))
