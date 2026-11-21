! Noyaux « tuned » Fortran (voir ms.f90). Compilé à part avec -mprefer-vector-width=512 :
! Fortran n'a pas de type vectoriel explicite, la largeur se règle par option ou par simdlen.
module tuned
  use iso_fortran_env
  use iso_c_binding, only: c_loc, c_f_pointer
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
  real(real64) function k1_soa(vx, vy, vz, m) result(e)
    real(real32), intent(in), contiguous :: vx(:), vy(:), vz(:), m(:)
    integer :: i
    e = 0
    !$omp simd reduction(+:e) simdlen(16)
    do i = 1, size(vx)
      e = e + real(0.5 * m(i) * (vx(i) * vx(i) + vy(i) * vy(i) + vz(i) * vz(i)), real64)
    end do
  end function
  ! 4 chaînes de réduction indépendantes (4 accumulateurs vectoriels de 16 f32). Mesuré : gfortran
  ! réduit les 4 vecteurs en fin d'appel par 64 additions scalaires (vaddss), ce qui coûte cher ici.
  real(real32) function k5_tuned(a, b) result(d)
    real(real32), intent(in), contiguous :: a(:), b(:)
    real(real32) :: s0, s1, s2, s3
    integer :: i, q
    q = size(a) / 4
    s0 = 0; s1 = 0; s2 = 0; s3 = 0
    !$omp simd reduction(+:s0,s1,s2,s3) simdlen(16)
    do i = 1, q
      s0 = s0 + a(i) * b(i)
      s1 = s1 + a(i + q) * b(i + q)
      s2 = s2 + a(i + 2 * q) * b(i + 2 * q)
      s3 = s3 + a(i + 3 * q) * b(i + 3 * q)
    end do
    d = (s0 + s1) + (s2 + s3)
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
  ! v4, point 3 (docs/V4_EQUAL.md, R3) : K4 tuned. Fortran n'a pas de SIMD explicite : la meilleure forme trouvée de
  ! la boucle scalaire, vectorisée par gfortran. Tableau déclaré contiguous (Fortran 2008 : sans lui, la boucle sur un
  ! tableau de forme présumée n'est pas vectorisée, 10 à 18 ms au lieu de 1,2), octets >= 128 (négatifs en int8)
  ! comptés b + 256 par merge, accumulateur 32 bits par tranche de 4 Mio (255 x 2^22 < 2^31).
  integer(int64) function k4_tuned(b) result(s)
    integer(int8), intent(in), contiguous :: b(:)
    integer(int32) :: p
    integer :: i, j, n
    n = size(b)
    s = 0
    do j = 1, n, 4194304
      p = 0
      do i = j, min(n, j + 4194303)
        p = p + merge(int(b(i), int32) + 256, 0, b(i) < 0)
      end do
      s = s + p
    end do
  end function
  ! v4, point 4 (docs/V4_CONVERGE.md, 3.3, K4 swar) : octets traités par mots de 64 bits (le tableau d'octets vu comme
  ! tableau d'entiers de 64 bits par c_f_pointer). Le bit de poids fort de chaque octet, ramené au bit 0 de l'octet,
  ! donne m ; ishft(m, 8) - m vaut 0xFF dans chaque octet marqué (l'octet de tête par la retenue de la soustraction ;
  ! les deux termes sont positifs, la différence ne déborde pas), ce qui garde les octets >= 128. Les octets gardés
  ! sont sommés par paires dans quatre voies de 16 bits ; une voie reçoit au plus 2 × 255 = 510 par mot, donc au plus
  ! 128 × 510 = 65 280 < 2^16 en 128 mots : les voies sont vidées dans la somme toutes les 128 mots. Décalages
  ! logiques (ishft), aucun branchement sur les données.
  integer(int64) function k4_swar(b) result(s)
    integer(int8), intent(in), contiguous, target :: b(:)
    integer(int64), parameter :: ONES = int(z'0101010101010101', int64), LO = int(z'00FF00FF00FF00FF', int64)
    integer(int64), parameter :: LO32 = int(z'0000FFFF0000FFFF', int64), M32 = int(z'FFFFFFFF', int64)
    integer(int64), pointer, contiguous :: w(:)
    integer(int64) :: acc, y, m
    integer :: i, j, nw, n
    n = size(b)
    nw = n / 8
    s = 0
    if (nw > 0) call c_f_pointer(c_loc(b(1)), w, [nw])
    do j = 1, nw, 128
      acc = 0
      do i = j, min(nw, j + 127)
        m = iand(ishft(w(i), -7), ONES)
        y = iand(w(i), ishft(m, 8) - m)
        acc = acc + iand(y, LO) + iand(ishft(y, -8), LO)
      end do
      acc = iand(acc, LO32) + iand(ishft(acc, -16), LO32)  ! deux voies de 32 bits
      s = s + iand(acc, M32) + ishft(acc, -32)
    end do
    do i = 8 * nw + 1, n
      s = s + merge(int(b(i), int64) + 256, 0_int64, b(i) < 0)
    end do
  end function
  ! v4, point 4 (docs/V4_CONVERGE.md, 3.5, rq_acc16 ; forme de bench/fortran_exp, remarque sur Fortran) : quatre
  ! accumulateurs écrits comme des tableaux de 16 valeurs, combinés avant une seule réduction finale (Fortran n'a pas
  ! de type vectoriel : la forme K5 tuned_v n'est pas écrivible, celle-ci en tient lieu ; relevé,
  ! results/converge/inventory.md)
  real(real32) function k5_acc16(a, b) result(d)
    real(real32), intent(in), contiguous :: a(:), b(:)
    real(real32) :: s0(16), s1(16), s2(16), s3(16)
    integer :: i
    s0 = 0; s1 = 0; s2 = 0; s3 = 0
    do i = 1, size(a) - 63, 64
      s0 = s0 + a(i:i + 15) * b(i:i + 15)
      s1 = s1 + a(i + 16:i + 31) * b(i + 16:i + 31)
      s2 = s2 + a(i + 32:i + 47) * b(i + 32:i + 47)
      s3 = s3 + a(i + 48:i + 63) * b(i + 48:i + 63)
    end do
    d = sum((s0 + s1) + (s2 + s3))
  end function
  ! v4, point 4 (docs/V4_CONVERGE.md, 3.3, K6 Q1 tuned_s, repli de tuned_v : Fortran n'a pas de SIMD explicite) : une
  ! passe ; les 30 accumulateurs en variables locales ; par ligne, sélection des six groupes par masques (0 ou 1, par
  ! merge), sans branchement ; accumulateurs de 64 bits. La variante tuned publiée agrège par blocs et par groupe.
  subroutine q1_tuned_s(sd, pr, q, d, t, rf, ls, lo, hi, acc)
    integer(int32), intent(in), contiguous :: sd(:), pr(:)
    integer(int8), intent(in), contiguous :: q(:), d(:), t(:), rf(:), ls(:)
    integer, intent(in) :: lo, hi
    integer(int64), intent(inout) :: acc(5, 0:5)
    integer(int64) :: n0, n1, n2, n3, n4, n5, q0, q1, q2, q3, q4, q5, p0, p1, p2, p3, p4, p5
    integer(int64) :: e0, e1, e2, e3, e4, e5, c0, c1, c2, c3, c4, c5
    integer(int64) :: ps, g, m0, m1, m2, m3, m4, m5, qq, pp, dp, ch
    integer :: i
    n0 = 0; n1 = 0; n2 = 0; n3 = 0; n4 = 0; n5 = 0; q0 = 0; q1 = 0; q2 = 0; q3 = 0; q4 = 0; q5 = 0
    p0 = 0; p1 = 0; p2 = 0; p3 = 0; p4 = 0; p5 = 0; e0 = 0; e1 = 0; e2 = 0; e3 = 0; e4 = 0; e5 = 0
    c0 = 0; c1 = 0; c2 = 0; c3 = 0; c4 = 0; c5 = 0
    do i = lo, hi
      ps = merge(1_int64, 0_int64, sd(i) <= 10471)
      g = int(rf(i), int64) * 2 + ls(i)
      qq = q(i)
      pp = pr(i)
      dp = pp * (100 - d(i))
      ch = dp * (100 + t(i))
      m0 = ps * merge(1_int64, 0_int64, g == 0); m1 = ps * merge(1_int64, 0_int64, g == 1)
      m2 = ps * merge(1_int64, 0_int64, g == 2); m3 = ps * merge(1_int64, 0_int64, g == 3)
      m4 = ps * merge(1_int64, 0_int64, g == 4); m5 = ps * merge(1_int64, 0_int64, g == 5)
      n0 = n0 + m0; q0 = q0 + qq * m0; p0 = p0 + pp * m0; e0 = e0 + dp * m0; c0 = c0 + ch * m0
      n1 = n1 + m1; q1 = q1 + qq * m1; p1 = p1 + pp * m1; e1 = e1 + dp * m1; c1 = c1 + ch * m1
      n2 = n2 + m2; q2 = q2 + qq * m2; p2 = p2 + pp * m2; e2 = e2 + dp * m2; c2 = c2 + ch * m2
      n3 = n3 + m3; q3 = q3 + qq * m3; p3 = p3 + pp * m3; e3 = e3 + dp * m3; c3 = c3 + ch * m3
      n4 = n4 + m4; q4 = q4 + qq * m4; p4 = p4 + pp * m4; e4 = e4 + dp * m4; c4 = c4 + ch * m4
      n5 = n5 + m5; q5 = q5 + qq * m5; p5 = p5 + pp * m5; e5 = e5 + dp * m5; c5 = c5 + ch * m5
    end do
    acc(:, 0) = acc(:, 0) + [n0, q0, p0, e0, c0]
    acc(:, 1) = acc(:, 1) + [n1, q1, p1, e1, c1]
    acc(:, 2) = acc(:, 2) + [n2, q2, p2, e2, c2]
    acc(:, 3) = acc(:, 3) + [n3, q3, p3, e3, c3]
    acc(:, 4) = acc(:, 4) + [n4, q4, p4, e4, c4]
    acc(:, 5) = acc(:, 5) + [n5, q5, p5, e5, c5]
  end subroutine
end module
