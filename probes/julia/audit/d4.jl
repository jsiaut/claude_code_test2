# D4 : JULIA_EXCLUSIVE=1 épingle les fils de Julia (option globale de l'exécutif) ; Base.setcpuaffinity vise une commande.
cpus = zeros(Int32, Threads.nthreads())
Threads.@threads :static for t in 1:Threads.nthreads()
  cpus[t] = ccall(:sched_getcpu, Int32, ())   # observation seulement
end
println("FACT;D4;JULIA_EXCLUSIVE=", get(ENV, "JULIA_EXCLUSIVE", "0"), " julia -t ", Threads.nthreads(), " : processeurs des fils ", Int.(cpus),
        " ; Base.setcpuaffinity(`grep Cpus_allowed_list /proc/self/status`, [2]), CPU autorisés de la commande : ", strip(split(read(Base.setcpuaffinity(`grep Cpus_allowed_list /proc/self/status`, [2]), String), ':')[2]))
