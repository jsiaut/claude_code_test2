! Code produit, lu par run.sh (gfortran-16 -S -O3 -march=native -fopenmp ; -fcheck=bounds pour E6).
module cg
  use iso_c_binding
  use iso_fortran_env
  implicit none
contains
  subroutine st_release(a) bind(c, name='st_release')
    integer(int64), intent(inout) :: a
    !$omp atomic write release
    a = 1
  end subroutine
  subroutine st_seqcst(a) bind(c, name='st_seqcst')
    integer(int64), intent(inout) :: a
    !$omp atomic write seq_cst
    a = 1
  end subroutine
  integer(int64) function add_relaxed(a) bind(c, name='add_relaxed')
    integer(int64), intent(inout) :: a
    !$omp atomic capture relaxed
    add_relaxed = a
    a = a + 1
    !$omp end atomic
  end function
  subroutine flushit(a) bind(c, name='flushit')
    integer(int64), intent(inout) :: a
    a = a + 1
    !$omp flush
  end subroutine
  subroutine axpy(a, b, n) bind(c, name='axpy')
    integer(c_int), value :: n
    real(c_float), intent(inout) :: a(n)
    real(c_float), intent(in) :: b(n)
    integer :: i
    do i = 1, n
      a(i) = a(i) + 2 * b(i)
    end do
  end subroutine
  real(c_float) function sum_plain(a, n) bind(c, name='sum_plain')
    integer(c_int), value :: n
    real(c_float), intent(in) :: a(n)
    integer :: i
    sum_plain = 0
    do i = 1, n
      sum_plain = sum_plain + a(i)
    end do
  end function
  real(c_float) function sum_simd(a, n) bind(c, name='sum_simd')
    integer(c_int), value :: n
    real(c_float), intent(in) :: a(n)
    integer :: i
    real(c_float) :: s
    s = 0
    !$omp simd reduction(+:s)
    do i = 1, n
      s = s + a(i)
    end do
    sum_simd = s
  end function
  real(c_float) function idx(a, n, i) bind(c, name='idx')
    integer(c_int), value :: n, i
    real(c_float), intent(in) :: a(n)
    idx = a(i)
  end function
  integer(int64) function f15c() bind(c, name='f15c')
    integer :: k
    integer(int64), parameter :: f15 = product([(int(k, int64), k = 1, 15)])
    f15c = f15
  end function
end module
