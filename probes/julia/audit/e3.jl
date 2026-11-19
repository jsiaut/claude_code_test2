# E3 : llvm.expect par llvmcall en forme module (alwaysinline) : le poids survit-il dans l IR optimisé ?
using InteractiveUtils
@inline unlikely(b::Bool) = Base.llvmcall(("""
  declare i1 @llvm.expect.i1(i1, i1)
  define i8 @entry(i8 %0) #0 {
    %b = trunc i8 %0 to i1
    %r = call i1 @llvm.expect.i1(i1 %b, i1 false)
    %z = zext i1 %r to i8
    ret i8 %z
  }
  attributes #0 = { alwaysinline }""", "entry"), Bool, Tuple{Bool}, b)
@noinline ext(x) = (Base.donotdelete(x); nothing)
h_unl(x::Int) = (r = x; if unlikely(x == 7); ext(x); r = 5x; end; r + 1)
h_non(x::Int) = (r = x; if x == 9; ext(x); r = 7x; end; r + 3)
for f in (h_unl, h_non)
  s = sprint(io -> code_llvm(io, f, (Int,); debuginfo=:none, raw=true))
  n = sprint(io -> code_native(io, f, (Int,); debuginfo=:none, syntax=:att))
  println("FACT;E3;", f, " : ", count(_ -> true, eachmatch(r"!prof", s)), " poids et ", count(_ -> true, eachmatch(r"llvm\.expect", s)), " llvm.expect dans l IR")
end
