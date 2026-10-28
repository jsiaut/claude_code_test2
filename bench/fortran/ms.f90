! Implémentation Fortran 2018 (+ OpenMP 5 pour les threads et atomiques) des noyaux de docs/SPEC.md.
! Compilateurs : gfortran 16 (bench/fortran) et flang 23 (bench/fortran_flang), mêmes sources.
! Les noyaux « tuned » sont dans tuned.f90, compilé avec -mprefer-vector-width=512 (option documentée).
! « natural » : type dérivé + tableau allouable, syntaxe tableau, intrinsèques (dot_product),
! pointeurs pour les structures chaînées. « tuned » : directives OpenMP SIMD (réduction,
! simdlen), sections alignées sur 64 o, accumulateurs multiples, OpenMP pour le parallélisme.
module harness
  use iso_fortran_env
  use iso_c_binding
  implicit none
  integer :: warm = 1
  real(real32), volatile :: vzero = 0.0
  real(real32), volatile :: vsink
contains
  real(real64) function now()
    integer(int64) :: c, r
    call system_clock(c, r)
    now = real(c, real64) / real(r, real64)
  end function
  integer(int64) function now_ns()
    integer(int64) :: c, r
    call system_clock(c, r)
    now_ns = c * (1000000000_int64 / r)
  end function
  function path(name) result(p)
    character(*), intent(in) :: name
    character(:), allocatable :: p
    character(512) :: d
    integer :: l, st
    call get_environment_variable("MS_DATA", d, l, st)
    if (st /= 0) d = "/opt/msdata"
    p = trim(d) // "/" // name
  end function
  function itoa(i) result(s)
    integer(int64), intent(in) :: i
    character(:), allocatable :: s
    character(24) :: b
    write (b, '(i0)') i
    s = trim(b)
  end function
  subroutine result(k, v, p, rep, sec, chk)
    character(*), intent(in) :: k, v, p, chk
    integer, intent(in) :: rep
    real(real64), intent(in) :: sec
    character(32) :: s
    write (s, '(f0.9)') sec
    write (output_unit, '(a)') 'RESULT;' // k // ';' // v // ';' // p // ';' // itoa(int(rep, int64)) // ';' // trim(s) // ';' // chk
    flush (output_unit)
  end subroutine
  integer(int64) function fsize(name)
    character(*), intent(in) :: name
    inquire (file=path(name), size=fsize)
    if (fsize < 0) error stop "fichier introuvable"
  end function
  subroutine load_i32(name, a)
    character(*), intent(in) :: name
    integer(int32), allocatable, intent(out) :: a(:)
    integer :: u
    allocate (a(fsize(name) / 4))
    open (newunit=u, file=path(name), access='stream', form='unformatted', status='old', action='read')
    read (u) a
    close (u)
  end subroutine
  subroutine load_r32(name, a)
    character(*), intent(in) :: name
    real(real32), allocatable, intent(out) :: a(:)
    integer :: u
    allocate (a(fsize(name) / 4))
    open (newunit=u, file=path(name), access='stream', form='unformatted', status='old', action='read')
    read (u) a
    close (u)
  end subroutine
  subroutine load_i8(name, a)
    character(*), intent(in) :: name
    integer(int8), allocatable, intent(out) :: a(:)
    integer :: u
    allocate (a(fsize(name)))
    open (newunit=u, file=path(name), access='stream', form='unformatted', status='old', action='read')
    read (u) a
    close (u)
  end subroutine
  ! section de buf commençant sur une frontière de 64 octets (Fortran n'a pas d'attribut d'alignement standard)
  function align64_r32(buf, n) result(p)
    real(real32), target, intent(in) :: buf(:)
    integer, intent(in) :: n
    real(real32), pointer, contiguous :: p(:)
    integer(int64) :: addr, off
    addr = transfer(c_loc(buf(1)), addr)
    off = mod(64 - mod(addr, 64_int64), 64_int64) / 4
    p => buf(1 + off:off + n)
  end function
  function align64_r64(buf, n) result(p)
    real(real64), target, intent(in) :: buf(:)
    integer(int64), intent(in) :: n
    real(real64), pointer, contiguous :: p(:)
    integer(int64) :: addr, off
    addr = transfer(c_loc(buf(1)), addr)
    off = mod(64 - mod(addr, 64_int64), 64_int64) / 8
    p => buf(1 + off:off + n)
  end function
end module

! ------------------------------------------------------------------ K1
module k1m
  use harness
  use tuned
  implicit none
  integer, parameter :: N1 = 4194304
contains
  real(real64) function k1_natural(ps) result(e)
    type(particle), intent(in) :: ps(:)
    integer :: i
    e = 0
    do i = 1, size(ps)
      e = e + 0.5d0 * ps(i)%mass * (ps(i)%vx**2 + ps(i)%vy**2 + ps(i)%vz**2)
    end do
  end function
  subroutine run_k1(v, reps)
    character(*), intent(in) :: v
    integer, intent(in) :: reps
    type(particle), allocatable :: ps(:)
    real(real32), allocatable :: raw(:)
    real(real32), allocatable, target :: cbuf(:)
    real(real32), pointer, contiguous :: cols(:, :)
    integer(int32), allocatable :: perm(:)
    integer :: r, k, u
    real(real64) :: t0, t1, e
    character(64) :: s
    if (v == "footprint0") then
      call result("k1", v, "energy", 0, 0d0, "0")
      return
    end if
    if (v == "soa") then
      call load_r32("k1_particles.f32", raw)
      allocate (cbuf(16 * N1 + 16))
      cols(1:N1, 0:15) => align64_r32(cbuf, 16 * N1)  ! 16 colonnes alignées sur 64 o
      do k = 0, 15
        cols(:, k) = raw(1 + k::16)
      end do
      deallocate (raw)
      do r = -warm, reps - 1
        t0 = now()
        e = k1_soa(cols(:, 3), cols(:, 4), cols(:, 5), cols(:, 9))
        t1 = now()
        write (s, '(f0.6)') e
        if (r >= 0) call result("k1", v, "energy", r, t1 - t0, trim(s))
      end do
      return
    end if
    allocate (ps(N1))
    open (newunit=u, file=path("k1_particles.f32"), access='stream', form='unformatted', status='old', action='read')
    read (u) ps
    close (u)
    if (v == "footprint") then
      write (s, '(f0.6)') k1_natural(ps)
      call result("k1", v, "energy", 0, 0d0, trim(s))
      return
    end if
    if (v == "natural_shuffled") then
      call load_i32("k1_perm.u32", perm)
      ps = ps(perm + 1)
    end if
    do r = -warm, reps - 1
      t0 = now()
      if (v == "aos") then
        e = k1_aos(ps)
      else
        e = k1_natural(ps)
      end if
      t1 = now()
      write (s, '(f0.6)') e
      if (r >= 0) call result("k1", v, "energy", r, t1 - t0, trim(s))
    end do
  end subroutine
end module

! ------------------------------------------------------------------ K2..K5
module k25m
  use harness
  use tuned
  use omp_lib
  implicit none
contains
  integer(int32) function k2_chase(a, h) result(i)
    integer(int32), intent(in) :: a(0:)
    integer, intent(in) :: h
    integer :: k
    i = 0
    do k = 1, h
      i = a(i)
    end do
  end function
  subroutine run_k2(v, reps, p)
    character(*), intent(in) :: v, p
    integer, intent(in) :: reps
    integer(int32), allocatable :: a(:)
    integer :: r
    integer(int32) :: i
    real(real64) :: t0, t1
    call load_i32("k2_chase_" // p // ".u32", a)
    do r = -warm, reps - 1
      t0 = now()
      i = k2_chase(a, 4200000)
      t1 = now()
      if (r >= 0) call result("k2", v, p, r, t1 - t0, itoa(int(i, int64)))
    end do
  end subroutine

  subroutine run_k3(v, reps)
    character(*), intent(in) :: v
    integer, intent(in) :: reps
    integer(int64), allocatable :: c(:)
    integer(int64) :: x
    integer :: r, t, stride, idx, i
    logical :: rmw
    real(real64) :: t0, t1
    rmw = v(1:3) == "rmw"
    stride = merge(16, 1, index(v, "padded") > 0)  ! en int64 : 128 o ou 8 o
    if (rmw) then
      write (output_unit, '(a)') "META;k3_mechanism;OpenMP atomic update (relaxed par défaut, lock add)"
    else
      write (output_unit, '(a)') "META;k3_mechanism;OpenMP atomic read/write (relaxed, mov)"
    end if
    allocate (c(16 + 4 * 16))
    do r = -warm, reps - 1
      c = 0
      t0 = now()
      !$omp parallel num_threads(4) private(t, idx, i, x)
      t = omp_get_thread_num()
      idx = 1 + t * stride
      if (rmw) then
        do i = 1, 33554432
          !$omp atomic update
          c(idx) = c(idx) + 1
        end do
      else
        do i = 1, 33554432
          !$omp atomic read
          x = c(idx)
          !$omp atomic write
          c(idx) = x + 1
        end do
      end if
      !$omp end parallel
      t1 = now()
      if (r >= 0) call result("k3", v, "4x2^25", r, t1 - t0, itoa(sum(c)))
    end do
  end subroutine

  integer(int64) function k4_natural(b) result(s)
    integer(int8), intent(in) :: b(:)
    integer :: i, x
    s = 0
    do i = 1, size(b)
      x = iand(int(b(i)), 255)
      if (x >= 128) s = s + x
    end do
  end function
  integer(int64) function k4_branchless(b) result(s)
    integer(int8), intent(in) :: b(:)
    integer :: i, x
    s = 0
    do i = 1, size(b)
      x = iand(int(b(i)), 255)
      s = s + x * ishft(x, -7)
    end do
  end function
  subroutine run_k4(v, reps)
    character(*), intent(in) :: v
    integer, intent(in) :: reps
    integer(int8), allocatable :: b(:)
    integer(int64) :: cnt(0:255), s
    integer :: r, x, i, k
    real(real64) :: t0, t1
    call load_i8("k4_bytes.u8", b)
    if (v == "natural_sorted") then  ! tri par comptage, hors chrono
      cnt = 0
      do i = 1, size(b)
        x = iand(int(b(i)), 255)
        cnt(x) = cnt(x) + 1
      end do
      k = 1
      do x = 0, 255
        b(k:k + cnt(x) - 1) = int(merge(x, x - 256, x < 128), int8)
        k = k + int(cnt(x))
      end do
    end if
    do r = -warm, reps - 1
      t0 = now()
      if (v == "branchless_unsorted") then
        s = k4_branchless(b)
      else
        s = k4_natural(b)
      end if
      t1 = now()
      if (r >= 0) call result("k4", v, "16M", r, t1 - t0, itoa(s))
    end do
  end subroutine

  subroutine run_k5(v, reps)
    character(*), intent(in) :: v
    integer, intent(in) :: reps
    real(real32), allocatable, target :: ra(:), rb(:), ba(:), bb(:)
    real(real32), pointer, contiguous :: a(:), b(:)
    real(real32) :: d
    integer :: r, it
    real(real64) :: t0, t1
    character(32) :: s
    call load_r32("k5_a.f32", ra)
    call load_r32("k5_b.f32", rb)
    allocate (ba(size(ra) + 16), bb(size(rb) + 16))
    a => align64_r32(ba, size(ra))
    b => align64_r32(bb, size(rb))
    a = ra
    b = rb
    do r = -warm, reps - 1
      d = 0
      t0 = now()
      do it = 1, 65536
        a(1) = a(1) + vzero  ! écriture opaque : le compilateur ne peut pas sortir le calcul de la boucle
        if (v == "tuned") then
          d = k5_tuned(a, b)
        else
          d = dot_product(a, b)
        end if
        vsink = d
      end do
      t1 = now()
      write (s, '(f0.4)') d
      if (r >= 0) call result("k5", v, "2048x65536", r, t1 - t0, trim(s))
    end do
  end subroutine
end module

! ------------------------------------------------------------------ K6
module k6m
  use harness
  use tuned
  use omp_lib
  implicit none
  integer, parameter :: N6 = 16777216
  integer(int32), allocatable :: sd(:), pr(:)
  integer(int8), allocatable :: q(:), d(:), t(:), rf(:), ls(:)
contains
  integer(int64) function q6_natural(lo, hi) result(s)
    integer, intent(in) :: lo, hi
    integer :: i
    s = 0
    do i = lo, hi
      if (sd(i) >= 8766 .and. sd(i) < 9131 .and. d(i) >= 5 .and. d(i) <= 7 .and. q(i) < 24) s = s + pr(i) * d(i)
    end do
  end function
  subroutine q1_natural(lo, hi, acc)
    integer, intent(in) :: lo, hi
    integer(int64), intent(inout) :: acc(5, 0:5)
    integer :: i, g
    integer(int64) :: p, dp
    do i = lo, hi
      if (sd(i) <= 10471) then
        g = rf(i) * 2 + ls(i)
        p = pr(i)
        dp = p * (100 - d(i))
        acc(1, g) = acc(1, g) + 1
        acc(2, g) = acc(2, g) + q(i)
        acc(3, g) = acc(3, g) + p
        acc(4, g) = acc(4, g) + dp
        acc(5, g) = acc(5, g) + dp * (100 + t(i))
      end if
    end do
  end subroutine
  subroutine run_k6(v, reps, par)
    character(*), intent(in) :: v, par
    integer, intent(in) :: reps
    integer(int64) :: acc(5, 0:5), s6
    integer :: r, th, lo, hi
    real(real64) :: t0, t1
    logical :: isq1
    call load_i32("k6_shipdate.i32", sd)
    call load_i32("k6_extendedprice.i32", pr)
    call load_i8("k6_quantity.u8", q)
    call load_i8("k6_discount.u8", d)
    call load_i8("k6_tax.u8", t)
    call load_i8("k6_returnflag.u8", rf)
    call load_i8("k6_linestatus.u8", ls)
    isq1 = par == "q1"
    do r = -warm, reps - 1
      acc = 0
      s6 = 0
      t0 = now()
      if (v == "mt") then
        !$omp parallel do num_threads(4) private(lo, hi) reduction(+:s6, acc) schedule(static, 1)
        do th = 0, 3
          lo = 1 + N6 / 4 * th
          hi = N6 / 4 * (th + 1)
          if (isq1) then
            call q1_tuned(sd, pr, q, d, t, rf, ls, lo, hi, acc)
          else
            s6 = s6 + q6_tuned(sd, d, q, pr, lo, hi)
          end if
        end do
        !$omp end parallel do
      else if (v == "tuned") then
        if (isq1) then
          call q1_tuned(sd, pr, q, d, t, rf, ls, 1, N6, acc)
        else
          s6 = q6_tuned(sd, d, q, pr, 1, N6)
        end if
      else
        if (isq1) then
          call q1_natural(1, N6, acc)
        else
          s6 = q6_natural(1, N6)
        end if
      end if
      t1 = now()
      if (isq1) s6 = sum(acc)
      if (r >= 0) call result("k6", v, par, r, t1 - t0, itoa(s6))
    end do
  end subroutine
end module

! ------------------------------------------------------------------ K7
module k7m
  use harness
  implicit none
  integer, parameter :: N7 = 16777216
  type :: hnode
    integer(int64) :: key, cnt, sum
    type(hnode), pointer :: next => null()
  end type
  type :: bucket
    type(hnode), pointer :: head => null()
  end type
  type, bind(c) :: slot  ! 16 octets, 4 par ligne de cache
    integer(c_int32_t) :: key, cnt
    integer(c_int64_t) :: sum
  end type
contains
  subroutine run_k7(v, reps)
    character(*), intent(in) :: v
    integer, intent(in) :: reps
    integer(int32), allocatable :: keys(:), vals(:)
    type(bucket), allocatable :: tab(:)
    type(slot), allocatable :: st(:)
    type(hnode), pointer :: p, nx
    integer, parameter :: NB = 1048573, LOG = 21, CAP = 2**LOG, BATCH = 16
    integer(int64) :: nk, ws, k
    integer :: r, i, b, s, h(BATCH)
    integer(int32) :: k0(BATCH), touch
    real(real64) :: t0, t1
    call load_i32("k7_keys.u32", keys)
    call load_i32("k7_vals.u32", vals)
    do r = -warm, reps - 1
      nk = 0
      ws = 0
      if (v == "natural") then  ! pas de table de hachage standard : chaînage séparé avec pointeurs
        t0 = now()
        allocate (tab(0:NB - 1))
        do i = 1, N7
          k = iand(int(keys(i), int64), 4294967295_int64)
          p => tab(mod(k, int(NB, int64)))%head
          do while (associated(p))
            if (p%key == k) exit
            p => p%next
          end do
          if (.not. associated(p)) then
            allocate (p)
            p%key = k
            p%cnt = 0
            p%sum = 0
            p%next => tab(mod(k, int(NB, int64)))%head
            tab(mod(k, int(NB, int64)))%head => p
          end if
          p%cnt = p%cnt + 1
          p%sum = p%sum + vals(i)
        end do
        t1 = now()
        do b = 0, NB - 1
          p => tab(b)%head
          do while (associated(p))
            nx => p%next
            nk = nk + 1
            ws = ws + p%sum * (iand(p%key, 1023_int64) + 1)
            deallocate (p)
            p => nx
          end do
        end do
        deallocate (tab)
      else  ! adressage ouvert, sondage linéaire ; chargements anticipés par lots (pas d'intrinsèque prefetch)
        t0 = now()
        allocate (st(0:CAP - 1))
        st = slot(0, 0, 0_int64)
        touch = 0
        do i = 1, N7, BATCH
          do b = 1, BATCH
            k = iand(int(keys(i + b - 1), int64), 4294967295_int64)
            h(b) = int(iand(ishft(k * 40503_int64, -11), int(CAP - 1, int64)))
            k0(b) = st(h(b))%cnt  ! charge la ligne : les 16 accès mémoire sont indépendants
          end do
          do b = 1, BATCH
            s = h(b)
            touch = ieor(touch, k0(b))
            do while (st(s)%cnt /= 0 .and. st(s)%key /= keys(i + b - 1))
              s = iand(s + 1, CAP - 1)
            end do
            st(s)%key = keys(i + b - 1)
            st(s)%cnt = st(s)%cnt + 1
            st(s)%sum = st(s)%sum + vals(i + b - 1)
          end do
        end do
        t1 = now()
        if (r == reps - 1) write (output_unit, '(a)') "META;k7_touch;" // itoa(int(touch, int64))
        do s = 0, CAP - 1
          if (st(s)%cnt /= 0) then
            nk = nk + 1
            ws = ws + st(s)%sum * (iand(int(st(s)%key, int64), 1023_int64) + 1)
          end if
        end do
        deallocate (st)
      end if
      if (r >= 0) call result("k7", v, "16M/1M", r, t1 - t0, itoa(nk) // ":" // itoa(ws))
    end do
  end subroutine
end module

! ------------------------------------------------------------------ K8
module k8m
  use harness
  implicit none
  type :: node
    integer(int64) :: v
    type(node), pointer :: l => null(), r => null()
  end type
  integer(int64), allocatable :: av(:)
  integer(int32), allocatable :: al(:), ar(:)
contains
  recursive function t_build(dep, c) result(n)
    integer, intent(in) :: dep
    integer(int64), intent(inout) :: c
    type(node), pointer :: n
    allocate (n)
    n%v = c
    c = c + 1
    if (dep > 0) then
      n%l => t_build(dep - 1, c)
      n%r => t_build(dep - 1, c)
    end if
  end function
  recursive integer(int64) function t_sum(n) result(s)
    type(node), pointer, intent(in) :: n
    if (.not. associated(n)) then
      s = 0
    else
      s = n%v + t_sum(n%l) + t_sum(n%r)
    end if
  end function
  recursive subroutine t_free(n)
    type(node), pointer :: n
    if (.not. associated(n)) return
    call t_free(n%l)
    call t_free(n%r)
    deallocate (n)
  end subroutine
  recursive integer(int32) function a_build(top, dep, c) result(i)
    integer(int32), intent(inout) :: top
    integer, intent(in) :: dep
    integer(int64), intent(inout) :: c
    integer(int32) :: l
    i = top
    top = top + 1
    av(i) = c
    c = c + 1
    if (dep > 0) then
      l = a_build(top, dep - 1, c)
      al(i) = l
      ar(i) = a_build(top, dep - 1, c)
    else
      al(i) = -1
      ar(i) = -1
    end if
  end function
  recursive integer(int64) function a_sum(i) result(s)
    integer(int32), intent(in) :: i
    if (i < 0) then
      s = 0
    else
      s = av(i) + a_sum(al(i)) + a_sum(ar(i))
    end if
  end function
  subroutine sort_u64(a)  ! tri par tas (pas de tri dans la bibliothèque standard Fortran), hors chrono
    integer(int64), intent(inout) :: a(:)
    integer :: n, i, e
    integer(int64) :: x
    n = size(a)
    do i = n / 2, 1, -1
      call sift(i, n)
    end do
    do e = n, 2, -1
      x = a(1); a(1) = a(e); a(e) = x
      call sift(1, e - 1)
    end do
  contains
    subroutine sift(s0, last)
      integer, intent(in) :: s0, last
      integer :: rt, ch
      integer(int64) :: y
      rt = s0
      do while (2 * rt <= last)
        ch = 2 * rt
        if (ch < last) then
          if (a(ch + 1) > a(ch)) ch = ch + 1
        end if
        if (a(rt) >= a(ch)) return
        y = a(rt); a(rt) = a(ch); a(ch) = y
        rt = ch
      end do
    end subroutine
  end subroutine
  subroutine run_k8(v, reps)
    character(*), intent(in) :: v
    integer, intent(in) :: reps
    integer, parameter :: Q = 16384
    type(node), pointer :: keep, tr
    integer(int64) :: cnt, lsum, total, c, s, a, lat(Q)
    integer(int32) :: top, root
    integer :: r, qq
    real(real64) :: t0, t1
    allocate (av(0:2046), al(0:2046), ar(0:2046))
    cnt = 0
    keep => t_build(20, cnt)
    lsum = t_sum(keep)
    do r = -warm, reps - 1
      total = 0
      t0 = now()
      do qq = 0, Q - 1
        a = now_ns()
        c = qq
        if (v == "tuned") then
          top = 0
          root = a_build(top, 10, c)
          s = a_sum(root)
        else
          tr => t_build(10, c)
          s = t_sum(tr)
          call t_free(tr)
        end if
        total = total + s
        lat(qq + 1) = now_ns() - a
      end do
      t1 = now()
      if (r >= 0) then
        call result("k8", v, "16384x2047", r, t1 - t0, itoa(total + lsum))
        call sort_u64(lat)
        write (output_unit, '(a)') "LAT;" // v // ";" // itoa(lat(Q / 2 + 1)) // ";" // itoa(lat(Q * 9 / 10 + 1)) // ";" // &
          itoa(lat(Q * 99 / 100 + 1)) // ";" // itoa(lat(Q * 999 / 1000 + 1)) // ";" // itoa(lat(Q))
      end if
    end do
    call t_free(keep)
  end subroutine
end module

! ------------------------------------------------------------------ K9
module k9m
  use harness
  use tuned
  implicit none
  integer, parameter :: M9 = 2048, IT9 = 4
contains
  subroutine k9_init(g)
    real(real64), intent(out) :: g(0:M9 - 1, 0:M9 - 1)
    integer :: i, j
    do j = 0, M9 - 1
      do i = 0, M9 - 1
        g(i, j) = real(mod(i * 31 + j * 17, 1024), real64) / 1024d0
      end do
    end do
  end subroutine
  subroutine run_k9(v, reps)
    character(*), intent(in) :: v
    integer, intent(in) :: reps
    real(real64), allocatable :: a(:, :), b(:, :)
    real(real64), allocatable, target :: ba(:), bb(:)
    real(real64), pointer, contiguous :: pa(:), pb(:), tmp(:)
    integer :: r, it, th
    real(real64) :: t0, t1
    character(40) :: s
    integer(int64), parameter :: NN = int(M9, int64) * M9
    if (v /= "natural") then
      allocate (ba(NN + 8), bb(NN + 8))
      pa => align64_r64(ba, NN)
      pb => align64_r64(bb, NN)
    end if
    do r = -warm, reps - 1
      if (v == "natural") then  ! tableau 2D allouable + syntaxe tableau (idiome Fortran)
        allocate (a(0:M9 - 1, 0:M9 - 1))
        call k9_init(a)
        b = a
        t0 = now()
        do it = 1, IT9
          b(1:M9 - 2, 1:M9 - 2) = 0.25d0 * (((a(0:M9 - 3, 1:M9 - 2) + a(2:M9 - 1, 1:M9 - 2)) + a(1:M9 - 2, 0:M9 - 3)) + a(1:M9 - 2, 2:M9 - 1))
          call swap2(a, b)
        end do
        t1 = now()
        write (s, '(es22.15e2)') sum(a)
        deallocate (a, b)
      else
        call k9_init(pa)
        pb = pa
        t0 = now()
        do it = 1, IT9
          if (v == "tuned") then
            call k9_cols(pa, pb, M9, 1, M9 - 2)
          else
            !$omp parallel do num_threads(4) schedule(static, 1)
            do th = 0, 3
              call k9_cols(pa, pb, M9, 1 + (M9 - 2) * th / 4, (M9 - 2) * (th + 1) / 4)
            end do
            !$omp end parallel do
          end if
          tmp => pa; pa => pb; pb => tmp
        end do
        t1 = now()
        write (s, '(es22.15e2)') sum(pa)
      end if
      if (r >= 0) call result("k9", v, "2048^2x4", r, t1 - t0, trim(adjustl(s)))
    end do
  contains
    subroutine swap2(x, y)
      real(real64), allocatable, intent(inout) :: x(:, :), y(:, :)
      real(real64), allocatable :: z(:, :)
      call move_alloc(x, z)
      call move_alloc(y, x)
      call move_alloc(z, y)
    end subroutine
  end subroutine
end module

! ------------------------------------------------------------------ K10
module k10m
  use harness
  use omp_lib
  implicit none
  integer, parameter :: M10 = 4194304, CAP10 = 16384
contains
  subroutine run_k10(v, reps)
    character(*), intent(in) :: v
    integer, intent(in) :: reps
    integer(int64), allocatable :: buf(:), idx(:)
    integer(int64) :: total, w, rd, cache, x, s
    integer(kind=omp_lock_kind) :: lk
    integer(int64) :: head, tail
    integer :: r
    logical :: done
    real(real64) :: t0, t1
    allocate (buf(0:CAP10 - 1), idx(0:63))
    do r = -warm, reps - 1
      idx = 0
      total = 0
      head = 0
      tail = 0
      call omp_init_lock(lk)
      t0 = now()
      !$omp parallel num_threads(2) private(w, rd, cache, x, s, done)
      if (v == "tuned") then
        ! anneau SPSC : write_idx = idx(16), read_idx = idx(48) (lignes distinctes), copies locales
        if (omp_get_thread_num() == 1) then  ! producteur
          w = 0
          cache = 0
          do x = 1, M10
            do while (w - cache == CAP10)
              !$omp atomic read acquire
              cache = idx(48)
            end do
            buf(iand(w, int(CAP10 - 1, int64))) = x
            w = w + 1
            !$omp atomic write release
            idx(16) = w
          end do
        else  ! consommateur
          rd = 0
          cache = 0
          s = 0
          do x = 1, M10
            do while (rd == cache)
              !$omp atomic read acquire
              cache = idx(16)
            end do
            s = s + buf(iand(rd, int(CAP10 - 1, int64)))
            rd = rd + 1
            !$omp atomic write release
            idx(48) = rd
          end do
          total = s
        end if
      else
        ! naturel : file bornée protégée par un verrou OpenMP (OpenMP n'a pas de variable de condition)
        if (omp_get_thread_num() == 1) then
          do x = 1, M10
            done = .false.
            do while (.not. done)
              call omp_set_lock(lk)
              if (tail - head < CAP10) then
                buf(mod(tail, int(CAP10, int64))) = x
                tail = tail + 1
                done = .true.
              end if
              call omp_unset_lock(lk)
            end do
          end do
        else
          s = 0
          do x = 1, M10
            done = .false.
            do while (.not. done)
              call omp_set_lock(lk)
              if (tail > head) then
                s = s + buf(mod(head, int(CAP10, int64)))
                head = head + 1
                done = .true.
              end if
              call omp_unset_lock(lk)
            end do
          end do
          total = s
        end if
      end if
      !$omp end parallel
      t1 = now()
      call omp_destroy_lock(lk)
      if (r >= 0) call result("k10", v, "2^22", r, t1 - t0, itoa(total))
    end do
  end subroutine
end module

program ms
  use harness
  use k1m
  use k25m
  use k6m
  use k7m
  use k8m
  use k9m
  use k10m
  implicit none
  character(32) :: k, v, p, a3
  integer :: reps, l, st
  character(16) :: w
  call get_command_argument(1, k)
  call get_command_argument(2, v)
  call get_command_argument(3, a3)
  call get_command_argument(4, p)
  read (a3, *) reps
  call get_environment_variable("WARMUP", w, l, st)
  if (st == 0) read (w, *) warm
  select case (trim(k))
  case ("k1"); call run_k1(trim(v), reps)
  case ("k2"); call run_k2(trim(v), reps, trim(p))
  case ("k3"); call run_k3(trim(v), reps)
  case ("k4"); call run_k4(trim(v), reps)
  case ("k5"); call run_k5(trim(v), reps)
  case ("k6"); call run_k6(trim(v), reps, trim(p))
  case ("k7"); call run_k7(trim(v), reps)
  case ("k8"); call run_k8(trim(v), reps)
  case ("k9"); call run_k9(trim(v), reps)
  case ("k10"); call run_k10(trim(v), reps)
  case default; error stop "kernel inconnu"
  end select
end program
