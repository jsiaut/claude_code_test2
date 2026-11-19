! Audit de la grille (docs/V4_PLAN.md 2.1) : sonde exécutée de Fortran (gfortran 16.2, -O3 -march=native -fopenmp),
! cas positifs. run.sh y ajoute le code produit, les échecs et les recherches d'absence.
module audit_m
  use iso_c_binding
  use iso_fortran_env
  implicit none
  type, bind(c) :: part
    real(c_float) :: x, y, z
    integer(c_int8_t) :: m
  end type
  type :: inl
    integer(int32) :: n
    real(real32) :: a(16)
  end type
  interface
    integer(c_int) function gettid() bind(c, name='gettid')   ! observation seulement
      import :: c_int
    end function
    integer(c_int) function sched_getcpu() bind(c, name='sched_getcpu') ! observation seulement
      import :: c_int
    end function
  end interface
contains
  integer(c_intptr_t) function adr(p)
    type(c_ptr), intent(in) :: p
    adr = transfer(p, 0_c_intptr_t)
  end function
  integer function threads_now()
    character(len=256) :: line
    integer :: u, ios
    threads_now = -1
    open(newunit=u, file='/proc/self/status', action='read', iostat=ios)
    do
      read(u, '(a)', iostat=ios) line
      if (ios /= 0) exit
      if (line(1:8) == 'Threads:') read(line(9:), *) threads_now
    end do
    close(u)
  end function
end module

program audit
  use audit_m
  use omp_lib
  implicit none
  type(part), target :: v(8)
  type(inl), target :: w
  integer(int8), target :: b8(1000)
  real, target :: local(1024)
  real, allocatable, target :: heap(:)
  real, allocatable, target :: m(:,:)
  integer :: ids(0:3), n, i, k, nd
  integer(int64) :: parts(0:3)
  integer(int64), parameter :: f15 = product([(int(k, int64), k = 1, 15)])   ! expression constante
  character(len=40) :: arg

  ! A1
  v = part(1.0, 2.0, 3.0, 4_c_int8_t)
  print '(a,i0,a,i0,a)', 'CAP;A1;1;[exécutée] tableau de type dérivé bind(c) : pas de ', &
    adr(c_loc(v(2))) - adr(c_loc(v(1))), ' o = storage_size/8 ', storage_size(v(1)) / 8, &
    ' ; les composantes sont stockées en ligne dans le tableau'
  ! A2 (½ : bind(c)/sequence, pas d'offsetof)
  print '(a,i0,a,i0,a)', 'FACT;A2;type bind(c) : disposition du C, décalage de z mesuré par c_loc = ', &
    adr(c_loc(v(1)%z)) - adr(c_loc(v(1))), ' o, de m = ', adr(c_loc(v(1)%m)) - adr(c_loc(v(1))), ' o'
  ! A7, A8
  print '(a,i0,a,i0,a)', 'CAP;A7;1;[exécutée] type (n : int32, a(16) : real32) : ', storage_size(w) / 8, &
    ' o, a(1) à ', adr(c_loc(w%a(1))) - adr(c_loc(w)), ' o du début (tableau en ligne)'
  print '(a,4(i0,a))', 'CAP;A8;1;[exécutée] int8/int16/real32 (iso_fortran_env) : ', storage_size(0_int8) / 8, '/', &
    storage_size(0_int16) / 8, '/', storage_size(0.0_real32) / 8, ' o ; tableau de 1000 int8 : ', &
    storage_size(b8) / 8 * size(b8), ' o'
  ! B1
  print '(a,i0,a)', 'CAP;B1;1;[exécutée] aucun ramasse-miettes : allouables libérés à la sortie de portée ou par deallocate ; ', &
    threads_now(), ' fil (Threads: de /proc/self/status, aucun fil de collecteur)'
  ! B3
  allocate(heap(1000))
  call stack_probe(adr(c_loc(heap)), adr(c_loc(b8)))
  ! D1, D4 (OpenMP, livré avec gfortran)
  ids = 0
  parts = 0
  !$omp parallel num_threads(4) private(i)
  ids(omp_get_thread_num()) = gettid()
  do i = omp_get_thread_num() * 1000, omp_get_thread_num() * 1000 + 999
    parts(omp_get_thread_num()) = parts(omp_get_thread_num()) + i
  end do
  !$omp end parallel
  nd = 0
  do i = 0, 3
    if (all(ids(0:i-1) /= ids(i))) nd = nd + 1
  end do
  print '(a,i0,a,i0,a)', 'CAP;D1;1;[exécutée] !$omp parallel (OpenMP livré avec gfortran) : 4 fils, ', nd, &
    ' identifiants de fil (gettid) distincts, somme ', sum(parts), ' (attendu 7998000) ; ½ en v1 (pas de fils dans la norme)'
  k = -1
  !$omp parallel num_threads(1)
  k = sched_getcpu()
  !$omp end parallel
  print '(a,i0,a,a)', 'FACT;D4;fil OpenMP sous OMP_PLACES={1} OMP_PROC_BIND=true : sched_getcpu() = ', k, &
    ', omp_get_proc_bind() = ', trim(merge('true ', 'other', omp_get_proc_bind() == omp_proc_bind_true))
  ! E7 (½ : expressions constantes, pas de génériques)
  print '(a,i0)', 'FACT;E7;expression constante product([(k, k = 1, 15)]) = ', f15
  ! F1
  call get_command_argument(1, arg)
  n = command_argument_count() + 3
  allocate(m(n, 4))
  print '(a,i0,a,i0,a,i0,a)', 'CAP;F1;1;[exécutée] real, allocatable :: m(:,:), m(', n, ', 4) alloué à l''exécution : m(2,1) - m(1,1) = ', &
    adr(c_loc(m(2,1))) - adr(c_loc(m(1,1))), ' o, m(1,2) - m(', n, ',1) = ' // trim(adjustl(itoa(int(adr(c_loc(m(1,2))) - adr(c_loc(m(n,1))))))) // ' o (contigu, par colonnes)'
contains
  subroutine stack_probe(aheap, astatic)
    integer(c_intptr_t), intent(in) :: aheap, astatic
    real, target :: loc(1024)
    integer, target :: marker
    loc(1) = 1
    marker = int(loc(1))
    print '(a,i0,a,i0,a)', 'CAP;B3;1;[exécutée] real loc(1024) local à une procédure à ', abs(adr(c_loc(loc)) - adr(c_loc(marker))), &
      ' o d''une autre variable locale, à ', abs(aheap - adr(c_loc(loc))), ' o d''un allouable : sur la pile (tableaux locaux automatiques)'
    if (astatic < 0) print *, astatic
  end subroutine
  function itoa(x) result(s)
    integer, intent(in) :: x
    character(len=16) :: s
    write(s, '(i0)') x
  end function
end program
