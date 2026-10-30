! Copie « standard » de bench/fortran/tuned.f90 pour la confrontation (docs/CONFRONTATION.md, section 4) : compilée
! sans -fopenmp, donc sans directive OpenMP active ; k1_soa et k5_tuned remplacent la réduction « omp simd » par des
! sommes partielles explicites (changements marqués « standard : »). Les directives qui restent sont des commentaires.
! Noyaux « tuned » Fortran (voir ms.f90). Compilé à part avec -mprefer-vector-width=512 :
! Fortran n'a pas de type vectoriel explicite, la largeur se règle par option ou par simdlen.
module tuned
  use iso_fortran_env
  implicit none
  type :: particle
    real(real32) :: x, y, z, vx, vy, vz, ax, ay, az, mass, charge, radius, temp, pressure, energy, density
  end type
contains
  real(real64) function k1_aos(ps) result(e)
    type(particle), intent(in) :: ps(:)
    integer :: i
    e = 0
    !$omp simd reduction(+:e)
    do i = 1, size(ps)
      e = e + real(0.5 * ps(i)%mass * (ps(i)%vx * ps(i)%vx + ps(i)%vy * ps(i)%vy + ps(i)%vz * ps(i)%vz), real64)
    end do
  end function
  ! standard : 16 sommes partielles explicites (les 16 voies de « simdlen(16) »), sans directive OpenMP
  real(real64) function k1_soa(vx, vy, vz, m) result(e)
    real(real32), intent(in), contiguous :: vx(:), vy(:), vz(:), m(:)
    real(real64) :: acc(16)
    integer :: i, k
    acc = 0
    do i = 1, size(vx), 16
      do k = 0, 15
        acc(k + 1) = acc(k + 1) + real(0.5 * m(i + k) * (vx(i + k) * vx(i + k) + vy(i + k) * vy(i + k) &
                                                       + vz(i + k) * vz(i + k)), real64)
      end do
    end do
    e = sum(acc)
  end function
  ! 4 chaînes de réduction indépendantes (4 accumulateurs vectoriels de 16 f32). Mesuré : gfortran
  ! réduit les 4 vecteurs en fin d'appel par 64 additions scalaires (vaddss), ce qui coûte cher ici.
  ! standard : 64 sommes partielles explicites (4 accumulateurs de 16 voies), sans directive OpenMP
  real(real32) function k5_tuned(a, b) result(d)
    real(real32), intent(in), contiguous :: a(:), b(:)
    real(real32) :: s(64), t(16)
    integer :: i, k
    s = 0
    do i = 1, size(a), 64
      do k = 0, 63
        s(k + 1) = s(k + 1) + a(i + k) * b(i + k)
      end do
    end do
    t = (s(1:16) + s(17:32)) + (s(33:48) + s(49:64))
    d = sum(t)
  end function
  integer(int64) function q6_tuned(sd, d, q, pr, lo, hi) result(s)
    integer(int32), intent(in), contiguous :: sd(:), pr(:)
    integer(int8), intent(in), contiguous :: d(:), q(:)
    integer, intent(in) :: lo, hi
    integer :: i, m
    s = 0
    !$omp simd reduction(+:s)
    do i = lo, hi
      m = merge(1, 0, sd(i) >= 8766 .and. sd(i) < 9131 .and. d(i) >= 5 .and. d(i) <= 7 .and. q(i) < 24)
      s = s + pr(i) * d(i) * m
    end do
  end function
  ! Q1 par blocs de 1024 lignes (en L1) : conversions et produits calculés une fois par bloc dans
  ! des tableaux larges, puis une passe vectorisée (masques) par groupe. Mesuré : 4x plus rapide
  ! qu'une passe par groupe lisant directement les colonnes 8 bits (vectorisation en xmm).
  subroutine q1_tuned(sd, pr, q, d, t, rf, ls, lo, hi, acc)
    integer(int32), intent(in), contiguous :: sd(:), pr(:)
    integer(int8), intent(in), contiguous :: q(:), d(:), t(:), rf(:), ls(:)
    integer, intent(in) :: lo, hi
    integer(int64), intent(inout) :: acc(5, 0:5)
    integer, parameter :: B = 1024
    integer(int32) :: gg(B), qv(B), pv(B)
    integer(int64) :: dv(B), cv(B)
    integer :: i0, n, k, grp, ii
    integer(int32) :: c1, c2, c3
    integer(int64) :: c4, c5
    do i0 = lo, hi, B
      n = min(B, hi - i0 + 1)
      !$omp simd private(ii)
      do k = 1, n
        ii = i0 + k - 1
        gg(k) = merge(rf(ii) * 2 + ls(ii), -1, sd(ii) <= 10471)
        qv(k) = q(ii)
        pv(k) = pr(ii)
        dv(k) = pr(ii) * (100 - d(ii))
        cv(k) = dv(k) * (100 + t(ii))
      end do
      do grp = 0, 5
        c1 = 0; c2 = 0; c3 = 0; c4 = 0; c5 = 0
        !$omp simd reduction(+:c1,c2,c3,c4,c5)
        do k = 1, n
          if (gg(k) == grp) then
            c1 = c1 + 1; c2 = c2 + qv(k); c3 = c3 + pv(k); c4 = c4 + dv(k); c5 = c5 + cv(k)
          end if
        end do
        acc(:, grp) = acc(:, grp) + [int(c1, int64), int(c2, int64), int(c3, int64), c4, c5]
      end do
    end do
  end subroutine
  ! K9 : boucles explicites, colonnes contiguës (indice i le plus rapide)
  subroutine k9_cols(a, b, m, j0, j1)
    integer, intent(in) :: m, j0, j1
    real(real64), intent(in) :: a(0:m - 1, 0:m - 1)
    real(real64), intent(inout) :: b(0:m - 1, 0:m - 1)
    integer :: i, j
    do j = j0, j1
      !$omp simd
      do i = 1, m - 2
        b(i, j) = 0.25d0 * (((a(i - 1, j) + a(i + 1, j)) + a(i, j - 1)) + a(i, j + 1))
      end do
    end do
  end subroutine
end module
