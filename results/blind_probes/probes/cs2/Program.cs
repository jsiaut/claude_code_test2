using System; using System.Linq; using System.Reflection;
class P { static void Main() {
  var core = typeof(object).Assembly;
  foreach (var t in core.GetTypes().Where(t => t.Name.Contains("Padding") || t.Name.Contains("Padded") || t.Name.Contains("CacheLine")))
    Console.WriteLine($"type {t.FullName} public={t.IsPublic||t.IsNestedPublic}");
  foreach (var t in core.GetTypes()) foreach (var f in t.GetFields(BindingFlags.Static|BindingFlags.NonPublic|BindingFlags.Public|BindingFlags.DeclaredOnly).Where(f => f.Name.Contains("CACHE_LINE") || f.Name.Contains("CacheLine")))
    { object v = null; try { v = f.IsLiteral ? f.GetRawConstantValue() : null; } catch {} Console.WriteLine($"field {t.FullName}.{f.Name}={v} public={f.IsPublic && t.IsPublic}"); }
  var vol = typeof(System.Threading.Volatile).GetMethods().Select(m=>m.Name).Distinct(); Console.WriteLine("Volatile: " + string.Join(",", vol));
  var il = typeof(System.Threading.Interlocked).GetMethods().Select(m=>m.Name).Distinct(); Console.WriteLine("Interlocked: " + string.Join(",", il));
}}
