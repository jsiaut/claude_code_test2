#include "textflag.h"

// func addOne(x int64) int64
TEXT ·addOne(SB), NOSPLIT, $0-16
	MOVQ x+0(FP), AX
	INCQ AX
	MOVQ AX, ret+8(FP)
	RET
