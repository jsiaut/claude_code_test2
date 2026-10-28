program probe
  use iso_fortran_env
  use iso_c_binding
  implicit none
  integer(int32) :: u
  real(real32), target :: buf(64)
  real(real32), pointer :: q(:)
  integer :: i
  real(real64) :: s(8)
  u = transfer(1.0_real32, u)
  write (*, '(a,z8)') "CAP;A5;1;TRANSFER(1.0) = 0x", u
  call c_f_pointer(c_loc(buf(1)), q, [64])
  q(1) = 2.0
  write (*, '(a,f4.1)') "CAP;B5;1;c_loc + c_f_pointer : ", buf(1)
  do concurrent (i = 1:8)
    s(i) = i * 2.0d0
  end do
  write (*, '(a,f6.1)') "CAP;C5;1;do concurrent : ", sum(s)
end program
