"""Génère les IR LLVM des formes tuned_v de Julia (K5, Q6, Q1, K9) ; sortie : texte Julia à insérer."""
def splat(t, v, n=16):
    return "<" + ", ".join(f"{t} {v}" for _ in range(n)) + ">"

K5 = """    declare <16 x float> @llvm.fmuladd.v16f32(<16 x float>, <16 x float>, <16 x float>)
    declare float @llvm.vector.reduce.fadd.v16f32(float, <16 x float>)
    define float @entry(ptr %a, ptr %b, i64 %n) #0 {
    top:
      br label %loop
    loop:
      %i = phi i64 [ 0, %top ], [ %in, %loop ]
""" + "".join(f"      %s{k} = phi <16 x float> [ zeroinitializer, %top ], [ %t{k}, %loop ]\n" for k in range(4)) + "".join(
f"""      %o{k} = add i64 %i, {16 * k}
      %pa{k} = getelementptr inbounds float, ptr %a, i64 %o{k}
      %pb{k} = getelementptr inbounds float, ptr %b, i64 %o{k}
      %va{k} = load <16 x float>, ptr %pa{k}, align 4
      %vb{k} = load <16 x float>, ptr %pb{k}, align 4
      %t{k} = call <16 x float> @llvm.fmuladd.v16f32(<16 x float> %va{k}, <16 x float> %vb{k}, <16 x float> %s{k})
""" for k in range(4)) + """      %in = add i64 %i, 64
      %c = icmp slt i64 %in, %n
      br i1 %c, label %loop, label %done
    done:
      %u01 = fadd <16 x float> %t0, %t1
      %u23 = fadd <16 x float> %t2, %t3
      %u = fadd <16 x float> %u01, %u23
      %r = call reassoc float @llvm.vector.reduce.fadd.v16f32(float -0.0, <16 x float> %u)
      ret float %r
    }
    attributes #0 = { alwaysinline }
"""

Q6 = f"""    declare i64 @llvm.vector.reduce.add.v16i64(<16 x i64>)
    define i64 @entry(ptr %sd, ptr %pr, ptr %d, ptr %q, i64 %nb) #0 {{
    top:
      %z = icmp eq i64 %nb, 0
      br i1 %z, label %none, label %loop
    loop:
      %k = phi i64 [ 0, %top ], [ %kn, %loop ]
      %acc = phi <16 x i64> [ zeroinitializer, %top ], [ %accn, %loop ]
      %off = shl i64 %k, 4
      %psd = getelementptr inbounds i32, ptr %sd, i64 %off
      %ppr = getelementptr inbounds i32, ptr %pr, i64 %off
      %pd = getelementptr inbounds i8, ptr %d, i64 %off
      %pq = getelementptr inbounds i8, ptr %q, i64 %off
      %vsd = load <16 x i32>, ptr %psd, align 4
      %vpr = load <16 x i32>, ptr %ppr, align 4
      %vd8 = load <16 x i8>, ptr %pd, align 1
      %vq8 = load <16 x i8>, ptr %pq, align 1
      %vd = zext <16 x i8> %vd8 to <16 x i32>
      %vq = zext <16 x i8> %vq8 to <16 x i32>
      %m1 = icmp sge <16 x i32> %vsd, {splat("i32", 8766)}
      %m2 = icmp slt <16 x i32> %vsd, {splat("i32", 9131)}
      %m3 = icmp sge <16 x i32> %vd, {splat("i32", 5)}
      %m4 = icmp sle <16 x i32> %vd, {splat("i32", 7)}
      %m5 = icmp slt <16 x i32> %vq, {splat("i32", 24)}
      %ma = and <16 x i1> %m1, %m2
      %mb = and <16 x i1> %ma, %m3
      %mc = and <16 x i1> %mb, %m4
      %m = and <16 x i1> %mc, %m5
      %p = mul <16 x i32> %vpr, %vd
      %ps = select <16 x i1> %m, <16 x i32> %p, <16 x i32> zeroinitializer
      %p64 = sext <16 x i32> %ps to <16 x i64>
      %accn = add <16 x i64> %acc, %p64
      %kn = add i64 %k, 1
      %c = icmp ult i64 %kn, %nb
      br i1 %c, label %loop, label %done
    done:
      %r = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %accn)
      ret i64 %r
    none:
      ret i64 0
    }}
    attributes #0 = {{ alwaysinline }}
"""

# Q1 : nb tours de 16 lignes (nb <= 256), résultats ajoutés dans out (Matrix{Int64}(5, 6), colonne g : 5 agrégats)
q1 = ["""    declare i16 @llvm.ctpop.i16(i16)
    declare i64 @llvm.vector.reduce.add.v16i64(<16 x i64>)
    define void @entry(ptr %sd, ptr %pr, ptr %q, ptr %d, ptr %t, ptr %rf, ptr %ls, ptr %out, i64 %nb) #0 {
    top:
      br label %loop
    loop:
      %k = phi i64 [ 0, %top ], [ %kn, %loop ]
"""]
for g in range(6):
    q1.append(f"      %cnt{g} = phi i64 [ 0, %top ], [ %cntn{g}, %loop ]\n")
    for a in ("aq", "ap", "adp"):
        q1.append(f"      %{a}{g} = phi <16 x i32> [ zeroinitializer, %top ], [ %{a}n{g}, %loop ]\n")
    q1.append(f"      %ach{g} = phi <16 x i64> [ zeroinitializer, %top ], [ %achn{g}, %loop ]\n")
q1.append("      %off = shl i64 %k, 4\n")
for name, ty in (("sd", "i32"), ("pr", "i32")):
    q1.append(f"      %p{name} = getelementptr inbounds {ty}, ptr %{name}, i64 %off\n"
              f"      %v{name} = load <16 x {ty}>, ptr %p{name}, align 4\n")
for name in ("q", "d", "t", "rf", "ls"):
    q1.append(f"      %p{name} = getelementptr inbounds i8, ptr %{name}, i64 %off\n"
              f"      %b{name} = load <16 x i8>, ptr %p{name}, align 1\n"
              f"      %v{name} = zext <16 x i8> %b{name} to <16 x i32>\n")
q1.append(f"""      %pass = icmp sle <16 x i32> %vsd, {splat("i32", 10471)}
      %rf2 = shl <16 x i32> %vrf, {splat("i32", 1)}
      %vg = add <16 x i32> %rf2, %vls
      %c100d = sub <16 x i32> {splat("i32", 100)}, %vd
      %vdp = mul <16 x i32> %vpr, %c100d
      %vt100 = add <16 x i32> %vt, {splat("i32", 100)}
      %dp64 = sext <16 x i32> %vdp to <16 x i64>
      %t64 = zext <16 x i32> %vt100 to <16 x i64>
      %ch = mul <16 x i64> %dp64, %t64
""")
for g in range(6):
    q1.append(f"""      %eq{g} = icmp eq <16 x i32> %vg, {splat("i32", g)}
      %m{g} = and <16 x i1> %pass, %eq{g}
      %bits{g} = bitcast <16 x i1> %m{g} to i16
      %pc{g} = call i16 @llvm.ctpop.i16(i16 %bits{g})
      %pc64{g} = zext i16 %pc{g} to i64
      %cntn{g} = add i64 %cnt{g}, %pc64{g}
      %sq{g} = select <16 x i1> %m{g}, <16 x i32> %vq, <16 x i32> zeroinitializer
      %aqn{g} = add <16 x i32> %aq{g}, %sq{g}
      %sp{g} = select <16 x i1> %m{g}, <16 x i32> %vpr, <16 x i32> zeroinitializer
      %apn{g} = add <16 x i32> %ap{g}, %sp{g}
      %sdp{g} = select <16 x i1> %m{g}, <16 x i32> %vdp, <16 x i32> zeroinitializer
      %adpn{g} = add <16 x i32> %adp{g}, %sdp{g}
      %sch{g} = select <16 x i1> %m{g}, <16 x i64> %ch, <16 x i64> zeroinitializer
      %achn{g} = add <16 x i64> %ach{g}, %sch{g}
""")
q1.append("""      %kn = add i64 %k, 1
      %c = icmp ult i64 %kn, %nb
      br i1 %c, label %loop, label %done
    done:
""")
for g in range(6):
    vals = [f"%cntn{g}"]
    for j, a in enumerate(("aqn", "apn", "adpn")):
        q1.append(f"      %w{a}{g} = sext <16 x i32> %{a}{g} to <16 x i64>\n"
                  f"      %r{a}{g} = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %w{a}{g})\n")
        vals.append(f"%r{a}{g}")
    q1.append(f"      %rach{g} = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %achn{g})\n")
    vals.append(f"%rach{g}")
    for j, val in enumerate(vals):
        idx = 5 * g + j
        q1.append(f"      %po{g}_{j} = getelementptr inbounds i64, ptr %out, i64 {idx}\n"
                  f"      %o{g}_{j} = load i64, ptr %po{g}_{j}, align 8\n"
                  f"      %on{g}_{j} = add i64 %o{g}_{j}, {val}\n"
                  f"      store i64 %on{g}_{j}, ptr %po{g}_{j}, align 8\n")
q1.append("""      ret void
    }
    attributes #0 = { alwaysinline }
""")
Q1 = "".join(q1)

K9 = """    define void @entry(ptr %a, ptr %b, i64 %j0, i64 %j1) #0 {
    top:
      br label %col
    col:
      %j = phi i64 [ %j0, %top ], [ %jn, %rowend ]
      %base = mul i64 %j, $M9
      %pm = getelementptr inbounds double, ptr %a, i64 %base
      %pl = getelementptr inbounds double, ptr %pm, i64 -$M9
      %pr = getelementptr inbounds double, ptr %pm, i64 $M9
      %po = getelementptr inbounds double, ptr %b, i64 %base
      br label %row
    row:
      %i = phi i64 [ 1, %col ], [ %in, %row ]
      %im = add i64 %i, -1
      %ip = add i64 %i, 1
      %pu = getelementptr inbounds double, ptr %pm, i64 %im
      %pd = getelementptr inbounds double, ptr %pm, i64 %ip
      %pli = getelementptr inbounds double, ptr %pl, i64 %i
      %pri = getelementptr inbounds double, ptr %pr, i64 %i
      %poi = getelementptr inbounds double, ptr %po, i64 %i
      %vu = load <8 x double>, ptr %pu, align 8
      %vd = load <8 x double>, ptr %pd, align 8
      %vl = load <8 x double>, ptr %pli, align 8
      %vr = load <8 x double>, ptr %pri, align 8
      %s1 = fadd <8 x double> %vu, %vd
      %s2 = fadd <8 x double> %s1, %vl
      %s3 = fadd <8 x double> %s2, %vr
      %vo = fmul <8 x double> """ + splat("double", "0.25", 8) + """, %s3
      store <8 x double> %vo, ptr %poi, align 8
      %in = add i64 %i, 8
      %in8 = add i64 %in, 8
      %cr = icmp sle i64 %in8, $(M9 - 1)
      br i1 %cr, label %row, label %tail
    tail:
      %ti = phi i64 [ %in, %row ], [ %tin, %tail ]
      %tm = add i64 %ti, -1
      %tp = add i64 %ti, 1
      %qu = getelementptr inbounds double, ptr %pm, i64 %tm
      %qd = getelementptr inbounds double, ptr %pm, i64 %tp
      %ql = getelementptr inbounds double, ptr %pl, i64 %ti
      %qr = getelementptr inbounds double, ptr %pr, i64 %ti
      %qo = getelementptr inbounds double, ptr %po, i64 %ti
      %xu = load double, ptr %qu, align 8
      %xd = load double, ptr %qd, align 8
      %xl = load double, ptr %ql, align 8
      %xr = load double, ptr %qr, align 8
      %y1 = fadd double %xu, %xd
      %y2 = fadd double %y1, %xl
      %y3 = fadd double %y2, %xr
      %yo = fmul double 0.25, %y3
      store double %yo, ptr %qo, align 8
      %tin = add i64 %ti, 1
      %ct = icmp slt i64 %tin, $(M9 - 1)
      br i1 %ct, label %tail, label %rowend
    rowend:
      %jn = add i64 %j, 1
      %cj = icmp sle i64 %jn, %j1
      br i1 %cj, label %col, label %done
    done:
      ret void
    }
    attributes #0 = { alwaysinline }
"""
import sys
out = sys.argv[1]
open(out, "w").write("\n".join([
    'const K5_IR = ("""\n' + K5 + '    """, "entry")',
    'const Q6_IR = ("""\n' + Q6 + '    """, "entry")',
    'const Q1_IR = ("""\n' + Q1 + '    """, "entry")',
    'const K9_IR = ("""\n' + K9 + '    """, "entry")']) + "\n")
print(len(Q1.splitlines()), "lignes d'IR pour Q1")
