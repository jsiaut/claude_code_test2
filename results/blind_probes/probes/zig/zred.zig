export fn red_opt(v: *const @Vector(16, f32)) f32 {
    @setFloatMode(.optimized);
    return @reduce(.Add, v.*);
}
export fn red_strict(v: *const @Vector(16, f32)) f32 {
    return @reduce(.Add, v.*);
}
