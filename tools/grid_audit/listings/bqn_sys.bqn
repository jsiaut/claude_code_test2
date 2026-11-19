# Liste des valeurs système de CBQN (•listSys) et, pour celles qui sont des espaces de noms, de leurs membres
# (•ns.Keys) : un nom par ligne. Sert à tools/grid_audit/search.py (introspection : docs/V4_PLAN.md 2.1).
Show ← {
  n ← "•"∾𝕩
  •Out n
  v ← •BQN "•"∾𝕩
  { 6 = •Type v ? •Out¨ {n∾"."∾𝕩}¨ •ns.Keys v ; @ }
}
Show¨ •listSys
