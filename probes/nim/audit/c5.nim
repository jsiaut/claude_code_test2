# C5 : itérateur || du module system (OpenMP), avec -fopenmp. Le corps de boucle ne doit pas sauter hors du bloc
# parallèle : les vérifications de bornes et de débordement y sont coupées localement.
import std/sequtils
proc gettid(): cint {.importc: "gettid", header: "<unistd.h>".} # observation seulement
var ids: array[4000, cint]
{.push boundChecks: off, overflowChecks: off.}
for i in `||`(0, 3999):
  ids[i] = gettid()
{.pop.}
echo "FACT;C5;for i in ||(0, 3999) avec -fopenmp, vérifications coupées dans le corps : ", ids.toSeq.deduplicate.len, " fils distincts (gettid)"
