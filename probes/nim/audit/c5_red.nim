var s = 0
{.push boundChecks: off, overflowChecks: off.}
for i in `||`(0, 999, "parallel for reduction(+:s)"):
  s += i
{.pop.}
echo s
