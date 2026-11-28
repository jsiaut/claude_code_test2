//go:build ignore

// Engendre unpack_gen.go : une routine de décodage par largeur (go run gen_unpack.go). Le langage n'a pas de
// généricité sur les constantes ; son outillage prévoit le code engendré (go generate). Un groupe de 64 valeurs
// occupe W mots : la position de chaque valeur est une constante, et le texte sait d'avance lesquelles chevauchent
// deux mots.
package main

import (
	"fmt"
	"os"
	"strings"
)

func main() {
	var b strings.Builder
	b.WriteString("// Code engendré par gen_unpack.go ; ne pas modifier.\n\npackage main\n")
	for w := 1; w <= 32; w++ {
		mask := uint64(1)<<w - 1
		fmt.Fprintf(&b, "\nfunc unpack%d(in []uint64, out []int32, base uint32) {\n\tfor len(out) >= 64 {\n", w)
		fmt.Fprintf(&b, "\t\t_, _ = in[%d], out[63]\n", w-1)
		for j := 0; j < 64; j++ {
			idx, sh := j*w>>6, j*w&63
			if sh+w <= 64 {
				fmt.Fprintf(&b, "\t\tout[%d] = int32(uint32(in[%d]>>%d&%#x) + base)\n", j, idx, sh, mask)
			} else {
				fmt.Fprintf(&b, "\t\tout[%d] = int32(uint32((in[%d]>>%d|in[%d]<<%d)&%#x) + base)\n", j, idx, sh, idx+1, 64-sh, mask)
			}
		}
		fmt.Fprintf(&b, "\t\tin, out = in[%d:], out[64:]\n\t}\n}\n", w)
	}
	b.WriteString("\nvar unpackFn = [33]func(in []uint64, out []int32, base uint32){\n\tnil,")
	for w := 1; w <= 32; w++ {
		fmt.Fprintf(&b, " unpack%d,", w)
		if w%8 == 0 {
			b.WriteString("\n\t")
		}
	}
	b.WriteString("\n}\n")
	if err := os.WriteFile("unpack_gen.go", []byte(b.String()), 0o644); err != nil {
		panic(err)
	}
}
