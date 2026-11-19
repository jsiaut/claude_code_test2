! F3 : type unsigned, extension de gfortran 15 (-funsigned) ; les entiers signés ne sont pas modulaires (débordement interdit).
program f3
  implicit none
  unsigned :: u
  integer :: n
  u = 4294967295u
  n = command_argument_count()
  u = u + 1u + uint(n)
  print '(a,i0)', 'unsigned 4294967295u + 1u = ', int(u)
end program
