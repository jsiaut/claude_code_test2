# Remarque sur OCaml : sondes de vérification (machine 20, 3 novembre, avant le plan)

Chaîne : OCaml 5.5.2 avec flambda (`/opt/ocaml`) ; binaires de `bench/ocaml_ref` (identique au binaire publié),
`bench/ocaml_fix` et `bench/ocaml_exp`. Temps : médiane d'un processus.

* `q6_tuned_ref.asm.txt` : la boucle de Q6 tuned publiée, deux branchements conditionnels de données (`jl`) issus des
  `&&` ; `q6_tuned_fix.asm.txt` : cinq `setcc`, seul le branchement de fin de boucle reste. Temps : 235,9 → 85,7 ms
  (`mt` : 63,1 → 33,3) ; masque des bits de signe (`ocaml_exp`) : 78,2 et 19,2 ms ; somme 45333132534 partout.
* `k1_aos_e_ref.asm.txt` : la fonction `e` de K1 aos, appelée quatre fois par tour (non inlinée), appelle `pow@plt`
  trois fois. Corrigée (`x *. x`) : 272,4 → 43,7 ms, même somme.
* `k3_work_ref.asm.txt` : `Atomic.fetch_and_add` et `Atomic.set` appellent `caml_atomic_fetch_add_field` et
  `caml_atomic_exchange_field` (fonctions C du runtime).
* `codegen_probe.txt` (`tools/ocaml_check/probes/cg.ml`, `ocamlopt -O3 -S`) : aucun `cmov` (un `max` garde `cmp` et
  `jle`), aucun `popcnt` ni `prefetch` ; `Int.popcount` est écrit en OCaml (`int.ml`).
* `clock_probe.txt` (`tools/ocaml_check/probes/clk.ml`) : `Unix.gettimeofday` et
  `Runtime_events.Timestamp.get_current` coûtent 62 à 73 ns la paire de lectures et n'allouent rien ; écart médian
  entre deux lectures successives 0 ns (résolution à la microseconde) contre 29 ns.
* K8 tuned, `OCAMLRUNPARAM=v=0x400`, mots alloués dans le tas mineur pour 1 puis 3 répétitions : 10 008 136 et
  13 192 119 (binaire publié), 9 910 451 et 12 902 835 (corrigé) ; l'essentiel vient du tri des latences par
  `compare`, hors chrono ; les deux références par requête de l'arène publiée font 65 536 mots par répétition.
  Temps : 200,4 (publié), 205,4 (corrigé), 166,6 ms (par valeur).
* K7 tuned 643,8 → 559,6 ms (deux mots par case) ; K9 tuned 35,9 → 35,5 ms et `mt` 22,4 → 20,1 ms (`floatarray`) ;
  K5 tuned 69,0 → 64,6 ms (huit accumulateurs). Clés inchangées sauf l'horloge : K4 naturel 91,9 → 100,7 ms, K5 tuned
  126,6 (minimum 84,4) → 69,0 ms, K8 naturel 277 et 301 → 270 et 238 ms (un processus chacune : bruit d'un processus
  à l'autre).
