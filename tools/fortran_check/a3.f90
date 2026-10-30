! A3 : -fpack-derived (option globale de gfortran) compacte les types dérivés
program a3
  use iso_fortran_env
  implicit none
  type :: t
    integer(int8) :: a
    integer(int32) :: b
    integer(int8) :: c
  end type
  type(t) :: x(2)
  print '(a,i0,a)', 'storage_size(t) = ', storage_size(x(1)) / 8, ' octets'
end program
