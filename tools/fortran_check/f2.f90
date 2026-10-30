! F2 : cotableaux en mémoire partagée (GCC 16, libcaf_shmem livrée avec gfortran)
program f2
  implicit none
  integer :: x[*], s
  x = this_image()
  sync all
  s = x
  call co_sum(s)
  if (this_image() == 1) print '(a,i0,a,i0)', 'images : ', num_images(), ' ; somme des numéros : ', s
end program
