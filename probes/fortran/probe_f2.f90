! Sonde gfortran 16.2 (30/10, docs/FORTRAN.md) : F2, cotableaux en mémoire partagée par libcaf_shmem (GCC 16).
program probe_f2
  implicit none
  integer :: x[*], s
  x = this_image()
  sync all
  s = x
  call co_sum(s)
  if (this_image() == 1) print '(a,i0,a,i0)', 'CAP;F2;0.5;cotableaux sur un nœud (libcaf_shmem) : images ', &
    num_images(), ', somme ', s
end program
