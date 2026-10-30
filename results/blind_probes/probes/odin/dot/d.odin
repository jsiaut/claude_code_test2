package dot
@(export, fast_math={.Allow_Reassoc, .Allow_Contract})
dot :: proc "c" (a, b: []f32) -> (sum: f32) {
	for _, i in a { sum += a[i]*b[i] }
	return
}
