! B2 : allocateur OpenMP défini par l'utilisateur (traits : réserve de 1 Mio, pas de repli), branché sur ALLOCATE
program b2
  use omp_lib
  implicit none
  integer(omp_allocator_handle_kind) :: pool
  type(omp_alloctrait) :: tr(2)
  real(8), allocatable :: a(:), b(:)
  integer :: st1, st2
  tr(1) = omp_alloctrait(omp_atk_pool_size, 1048576)
  tr(2) = omp_alloctrait(omp_atk_fallback, omp_atv_null_fb)
  pool = omp_init_allocator(omp_default_mem_space, 2, tr)
  !$omp allocators allocate(allocator(pool): a)
  allocate (a(65536), stat=st1)            ! 512 Kio : dans la réserve
  !$omp allocators allocate(allocator(pool): b)
  allocate (b(131072), stat=st2)           ! 1 Mio de plus : la réserve est épuisée, pas de repli
  print '(a,i0,a,i0)', 'stat dans la réserve : ', st1, ' ; stat au-delà de la réserve : ', st2
end program
