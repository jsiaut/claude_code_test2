! témoin : les mêmes allocations sans directive
program a4n
  use iso_c_binding
  implicit none
  real, allocatable, target :: a(:)
  integer :: k, bad
  bad = 0
  do k = 1, 50
    allocate (a(1000 + k))
    if (mod(transfer(c_loc(a), 0_c_intptr_t), 128_c_intptr_t) /= 0) bad = bad + 1
    deallocate (a)
  end do
  print '(a,i0)', 'témoin sans directive, allouables mal alignés (128) sur 50 : ', bad
end program
