var s {.exportc: "s".} = 0
{.push boundChecks: off, overflowChecks: off.}
for i in `||`(0, 999999, "parallel for reduction(+:s)"):
  s += i
{.pop.}
echo s
