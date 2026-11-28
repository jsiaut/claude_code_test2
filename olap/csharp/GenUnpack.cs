// Engendre UnpackGen.cs : une routine de décodage par largeur (dotnet run --file GenUnpack.cs). Le compilateur à la volée ne
// déroule ni ne vectorise la boucle générale ; le banc engendre donc ce code. Un groupe de 64 valeurs occupe W mots :
// la position de chaque valeur est une constante, et le texte sait d'avance lesquelles chevauchent deux mots.
using System.Linq;
using System.Text;

var text = new StringBuilder();
text.Append("// Code engendré par GenUnpack.cs ; ne pas modifier.\nstatic unsafe partial class Olap {\n");
for (int w = 1; w <= 32; w++) {
    ulong mask = (1UL << w) - 1;
    text.Append($"    static void Unpack{w}(ulong* inp, int* outp, int n, uint b) {{\n");
    text.Append($"        for (int o = 0; o < n; o += 64, inp += {w}, outp += 64) {{\n");
    text.Append("            ulong " + string.Join(", ", Enumerable.Range(0, w).Select(k => $"w{k} = inp[{k}]")) + ";\n");
    for (int j = 0; j < 64; j++) {
        int idx = j * w >> 6, sh = j * w & 63;
        string v = sh == 0 ? $"w{idx}" : sh + w <= 64 ? $"(w{idx} >> {sh})" : $"(w{idx} >> {sh} | w{idx + 1} << {64 - sh})";
        text.Append($"            outp[{j}] = (int)((uint)({v} & 0x{mask:X}) + b);\n");
    }
    text.Append("        }\n    }\n");
}
text.Append("    static readonly delegate*<ulong*, int*, int, uint, void>[] UnpackFn = {\n        null, ");
text.Append(string.Join(", ", Enumerable.Range(1, 32).Select(w => $"&Unpack{w}")) + ",\n    };\n}\n");
System.IO.File.WriteAllText("UnpackGen.cs", text.ToString());
