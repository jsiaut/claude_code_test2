! Écrit par build.sh (v4, point 2 : docs/V4_SIZES.md) : tailles de la construction ; sans variable MS_*, les valeurs
! publiées.
module ms_sizes
  implicit none
  integer, parameter :: SIZE_N1 = 4194304, SIZE_INNER5 = 65536
  integer, parameter :: SIZE_N6 = 16777216, SIZE_N7 = 16777216
  integer, parameter :: SIZE_K7_LOG2 = 20, SIZE_K7_NB = 1048573
  integer, parameter :: SIZE_K8_LONG = 20, SIZE_K8_REQ = 10, SIZE_M9 = 2048
end module
