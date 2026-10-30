! A4 : alignement par OpenMP (gfortran 16.2) : directive allocate (variable locale) et allocators (allouable)
module a4m
  use iso_c_binding
  implicit none
contains
  integer function local_mod() result(m)
    real, target :: buf(100)
    !$omp allocate(buf) align(256)
    buf = 1
    m = int(mod(transfer(c_loc(buf), 0_c_intptr_t), 256_c_intptr_t))
  end function
end module
program a4
  use a4m
  implicit none
  real, allocatable, target :: a(:)
  integer :: k, bad, badl
  bad = 0; badl = 0
  do k = 1, 50
    !$omp allocators allocate(align(128): a)
    allocate (a(1000 + k))
    if (mod(transfer(c_loc(a), 0_c_intptr_t), 128_c_intptr_t) /= 0) bad = bad + 1
    deallocate (a)
    if (local_mod() /= 0) badl = badl + 1
  end do
  print '(a,i0,a,i0)', 'allouables mal alignés (128) sur 50 : ', bad, ' ; variables locales mal alignées (256) sur 50 : ', badl
end program
