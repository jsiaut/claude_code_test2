# Remarque sur Julia (docs/JULIA.md) : mécanisme du blocage de K10 tuned. Variantes du producteur-consommateur
# de bench/julia/ms.jl (anneau de 2^14, 2^22 éléments, deux tâches) :
#   V0 : code de la campagne (s capturée par la fermeture et affectée dehors -> Core.Box ; yield() tous les 1024 tours)
#   V1 : V0 sans yield() (attente active pure : la version qui a bloqué pendant la campagne)
#   V2 : sans capture (somme locale à la fermeture), sans yield(), sans GC.safepoint()
#   V3 : sans capture, GC.safepoint() dans les boucles d'attente (correctif de la remarque)
#   V4 : avec capture (Core.Box), GC.safepoint() dans les boucles d'attente, sans yield()
# Usage : julia -O3 -t 4 k10_variants.jl V0|V1|V2|V3|V4 répétitions
const M10 = 1 << 22
const CAP10 = 1 << 14

function run(v::String)
    ctl = AtomicMemory{Int}(undef, 64)
    @atomic ctl[17] = 0; @atomic ctl[49] = 0
    buf = Vector{UInt64}(undef, CAP10)
    capture = v in ("V0", "V1", "V4")
    yld = v == "V0"
    sfp = v in ("V3", "V4")
    prod = Threads.@spawn begin
        w = 0; rc = 0
        for x in UInt64(1):UInt64(M10)
            spins = 0
            while w - rc == CAP10
                rc = @atomic :acquire ctl[49]
                yld && (spins += 1) % 1024 == 0 && yield()
                sfp && GC.safepoint()
            end
            @inbounds buf[(w&(CAP10-1))+1] = x
            w += 1
            @atomic :release ctl[17] = w
        end
    end
    if capture
        cons = Threads.@spawn begin
            rd = 0; wc = 0; s = UInt64(0)
            for _ in 1:M10
                spins = 0
                while rd == wc
                    wc = @atomic :acquire ctl[17]
                    yld && (spins += 1) % 1024 == 0 && yield()
                    sfp && GC.safepoint()
                end
                @inbounds s += buf[(rd&(CAP10-1))+1]
                rd += 1
                @atomic :release ctl[49] = rd
            end
            s
        end
        wait(prod); s = fetch(cons)   # s affectée aussi ici : la fermeture la capture dans une Core.Box
        return s
    else
        cons = Threads.@spawn begin
            rd = 0; wc = 0; acc = UInt64(0)
            for _ in 1:M10
                while rd == wc
                    wc = @atomic :acquire ctl[17]
                    sfp && GC.safepoint()
                end
                @inbounds acc += buf[(rd&(CAP10-1))+1]
                rd += 1
                @atomic :release ctl[49] = rd
            end
            acc
        end
        wait(prod)
        return fetch(cons)
    end
end

v = ARGS[1]; reps = parse(Int, ARGS[2])
for r in 1:reps
    t0 = time_ns(); a0 = Base.gc_num().allocd
    s = run(v)
    dt = (time_ns() - t0) / 1e6
    println("$v rep $r : $(round(dt, digits=1)) ms, somme $(s == UInt64(M10) * (UInt64(M10) + 1) ÷ 2 ? "juste" : "FAUSSE"), ",
            "$(Base.gc_num().allocd - a0) octets alloués")
    flush(stdout)
end
