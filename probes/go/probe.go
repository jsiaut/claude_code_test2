package main

import (
	"fmt"
	"math"
	"os"
	"syscall"
	"unsafe"
)

type S struct {
	A uint8
	B uint32
	C float64
}

func main() {
	fmt.Printf("CAP;A2;1;unsafe.Offsetof(S.C)=%d\n", unsafe.Offsetof(S{}.C))
	fmt.Printf("CAP;A5;0.5;math.Float32bits(1)=0x%08x\n", math.Float32bits(1))
	f, _ := os.Open("/opt/msdata/k5_a.f32")
	b, err := syscall.Mmap(int(f.Fd()), 0, 8192, syscall.PROT_READ, syscall.MAP_PRIVATE)
	fl := unsafe.Slice((*float32)(unsafe.Pointer(&b[0])), 2048)
	fmt.Printf("CAP;F4;0.5;syscall.Mmap + unsafe.Slice : %g %v\n", fl[0], err)
	var set [16]uint64
	set[0] = 1
	_, _, e := syscall.RawSyscall(syscall.SYS_SCHED_SETAFFINITY, 0, uintptr(len(set)*8), uintptr(unsafe.Pointer(&set[0])))
	fmt.Printf("CAP;D4;0.5;syscall brut sched_setaffinity errno=%d\n", e)
}
