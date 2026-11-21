! Sonde de mode (v4, point 3 : docs/V4_EQUAL.md, 4) : « 1d » : tableau allouable, « 2d » : tableau 2D allouable.
program probe
  implicit none
  character(len=16) :: c, s
  integer :: n
  real(8), allocatable :: a(:), g(:, :)
  call get_command_argument(1, c)
  call get_command_argument(2, s)
  read (s, *) n
  if (c(1:1) == '1') then
    allocate (a(0:n - 1))
    a = 1d0
    print *, a(n)
  else
    allocate (g(0:n - 1, 0:3))
    g = 1d0
    print *, g(n, 1)
  end if
end program
