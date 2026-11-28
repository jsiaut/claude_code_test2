// v7 : racine du binaire spécialisé du banc OLAP en Zig (olap_s) : @Vector, permutations calculées à la compilation,
// préchargement, écriture non temporelle.
pub const special = true;
pub const main = @import("olap.zig").main;
