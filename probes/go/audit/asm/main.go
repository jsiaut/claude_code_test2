// Audit de la grille, Go, E2 : une fonction écrite dans l'assembleur de Go (fichier add_amd64.s à part).
package main

import "fmt"

func addOne(x int64) int64

func main() { fmt.Println(addOne(41)) }
