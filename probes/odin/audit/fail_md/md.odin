package md
import "core:fmt"
import "core:os"
main :: proc() { n := len(os.args) + 3; m: [n][3]f32; fmt.println(m[0][0]) }
