function dot(a, b, n) result(s)
  integer, intent(in) :: n
  real, intent(in) :: a(n), b(n)
  real :: s
  integer :: i
  s = 0.0
  do i = 1, n
    s = s + a(i) * b(i)
  end do
end function dot
