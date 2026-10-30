! Sonde gfortran 16.2 ajoutée le 30/10 après la remarque sur Fortran (docs/FORTRAN.md) : A3, A4, B2.
! Compilée avec -fpack-derived -fopenmp -fopenmp-allocators (run.sh).
module probe_errata_m
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
program probe_errata
  use iso_fortran_env
  use iso_c_binding
  use probe_errata_m
  implicit none
  type :: t
    integer(int8) :: a
    integer(int32) :: b
    integer(int8) :: c
  end type
  type :: anode
    integer(int64) :: v
    integer(int32) :: l, r
  end type
  type(t) :: x(2)
  real, allocatable, target :: a(:)
  type(anode), allocatable :: arena(:)
  integer :: top
  print '(a,i0,a)', 'CAP;A3;0.5;-fpack-derived (option globale) : storage_size(t) = ', storage_size(x(1)) / 8, ' octets'
  !$omp allocators allocate(align(128): a)
  allocate (a(1000))
  print '(a,i0,a,i0)', 'CAP;A4;0.5;directives OpenMP : allouable mod 128 = ', &
    mod(transfer(c_loc(a), 0_c_intptr_t), 128_c_intptr_t), ' ; locale mod 256 = ', local_mod()
  allocate (arena(0:2046))
  top = 0
  arena(top) = anode(42, -1, -1)
  print '(a,i0)', 'CAP;B2;0.5;arène à la main (tableau de nœuds réutilisé), comme en C : ', arena(0)%v
end program
