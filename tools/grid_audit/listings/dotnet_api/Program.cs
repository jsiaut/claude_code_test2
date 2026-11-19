// API publique des assemblages de référence d'un répertoire (args[0]), lue par System.Reflection.Metadata sans les
// charger : types visibles hors de leur assemblage, et leurs membres publics ou protégés.
using System.Reflection;
using System.Reflection.Metadata;
using System.Reflection.PortableExecutable;

var outl = new SortedSet<string>(StringComparer.Ordinal);
foreach (var f in Directory.GetFiles(args[0], "*.dll"))
{
    using var fs = File.OpenRead(f);
    using var pe = new PEReader(fs);
    if (!pe.HasMetadata) continue;
    var md = pe.GetMetadataReader();
    string asm = Path.GetFileNameWithoutExtension(f);
    foreach (var th in md.TypeDefinitions)
    {
        var t = md.GetTypeDefinition(th);
        if (!Visible(md, t)) continue;
        string tn = Name(md, t);
        outl.Add($"type {tn} ({asm})");
        foreach (var mh in t.GetMethods())
        {
            var m = md.GetMethodDefinition(mh);
            if (!Vis(m.Attributes) || (m.Attributes & MethodAttributes.SpecialName) != 0 && !md.GetString(m.Name).StartsWith("op_")) continue;
            outl.Add($"méthode {tn}.{md.GetString(m.Name)}");
        }
        foreach (var fh in t.GetFields())
        {
            var fd = md.GetFieldDefinition(fh);
            var a = fd.Attributes & FieldAttributes.FieldAccessMask;
            if (a == FieldAttributes.Public || a == FieldAttributes.Family || a == FieldAttributes.FamORAssem)
                outl.Add($"champ {tn}.{md.GetString(fd.Name)}");
        }
        foreach (var ph in t.GetProperties())
        {
            var p = md.GetPropertyDefinition(ph);
            var acc = p.GetAccessors();
            bool v = (!acc.Getter.IsNil && Vis(md.GetMethodDefinition(acc.Getter).Attributes))
                  || (!acc.Setter.IsNil && Vis(md.GetMethodDefinition(acc.Setter).Attributes));
            if (v) outl.Add($"propriété {tn}.{md.GetString(p.Name)}");
        }
        foreach (var eh in t.GetEvents())
        {
            var e = md.GetEventDefinition(eh);
            var add = e.GetAccessors().Adder;
            if (!add.IsNil && Vis(md.GetMethodDefinition(add).Attributes)) outl.Add($"événement {tn}.{md.GetString(e.Name)}");
        }
    }
}
foreach (var l in outl) Console.WriteLine(l);

static bool Vis(MethodAttributes a)
{
    a &= MethodAttributes.MemberAccessMask;
    return a == MethodAttributes.Public || a == MethodAttributes.Family || a == MethodAttributes.FamORAssem;
}
static bool Visible(MetadataReader md, TypeDefinition t)
{
    var v = t.Attributes & TypeAttributes.VisibilityMask;
    if (v == TypeAttributes.Public) return true;
    if (v == TypeAttributes.NestedPublic || v == TypeAttributes.NestedFamily || v == TypeAttributes.NestedFamORAssem)
        return Visible(md, md.GetTypeDefinition(t.GetDeclaringType()));
    return false;
}
static string Name(MetadataReader md, TypeDefinition t)
{
    string n = md.GetString(t.Name);
    if (!t.GetDeclaringType().IsNil) return Name(md, md.GetTypeDefinition(t.GetDeclaringType())) + "+" + n;
    string ns = md.GetString(t.Namespace);
    return ns.Length > 0 ? ns + "." + n : n;
}
