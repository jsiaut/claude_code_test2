"""v4, point 5 (docs/V4_COST.md, 3.4 et 3.5) : constructions recherchées dans les régions.

UNCHECKED[langage] : constructions qui contournent une vérification de sûreté mémoire du mode publié, avec leur portée :
  line    : la ligne qui porte la construction ;
  brace   : la ligne et le bloc entre accolades qui commence à la première accolade ouvrante à partir de la construction
            (blocs et fonctions `unsafe` de Rust, méthodes et blocs `unsafe` et `fixed` de C#, fermetures `withUnsafe…`
            de Swift, `#no_bounds_check` d'Odin) ;
  indent  : Julia, `@inbounds` suivi d'un bloc (`for`, `while`, `begin`, `let`, `if`) : la ligne, les lignes plus
            indentées qui suivent et le `end` qui ferme le bloc ; sinon la ligne seule ;
  pushpop : Nim, du `{.push … : off.}` au `{.pop.}` qui suit ;
  unit    : Ada, `pragma Suppress` : le sous-programme qui le contient (de son en-tête à son `end Nom;`) ;
  ir      : Julia, `llvmcall` : la ligne et la chaîne d'IR de LLVM qu'elle reçoit (constante « const NOM = ( » suivie d'une chaîne longue sur plusieurs lignes).
Écarts datés du 22 novembre (docs/V4_COST.md, 10), fixés avant tout comptage :
* C# : `unsafe` en modificateur de classe (`static unsafe class Ms`) n'est ni un bloc ni une méthode et n'ouvre pas de
  portée ; il rend toutes les méthodes de la classe « unsafe » au sens du langage. Une méthode dont la signature déclare
  un type pointeur (paramètre ou résultat) est une méthode `unsafe` (portée : la méthode) ; une ligne qui déclare ou
  convertit un type pointeur (`float*`, `(double*)`) porte une construction de la liste ;
* Julia : `llvmcall` ajouté (l'IR qu'il reçoit s'exécute sans aucune vérification) ;
* Mojo : `UntrackedOrigin` ajouté (pointeurs dont l'origine n'est pas suivie : ni durée de vie ni bornes).
NO_CHECK_MODE : langages dont le mode publié n'a pas de vérification de bornes (part absolue = 1).
ARCH : constructions propres à une architecture (toutes à la ligne), communes et par langage. Écart daté du 22 novembre
(docs/V4_COST.md, 10) : une barrière de compilateur à gabarit vide (`asm volatile("" : … : "memory")`, macros BARRIER et
KEEP du harnais de C, opaque et keep de C++) n'émet aucune instruction et n'est propre à aucune architecture : elle
n'est pas comptée (EMPTY_ASM).
Chaque occurrence trouvée est listée dans results/cost/matches.md pour être examinée ; un ajout ou un retrait dans ces
listes est un écart daté (docs/V4_COST.md)."""
import re

NO_CHECK_MODE = {"zig", "c3", "chapel", "d", "fpc", "c", "cpp", "fortran"}

UNCHECKED = {
    "rust": [(r"\bunsafe\b", "brace"), (r"\bget_unchecked\w*", "line"), (r"\bfrom_raw_parts\w*", "line"),
             (r"\btransmute\b", "line"), (r"\*const\b|\*mut\b", "line"), (r"\.add\(|\.offset\(", "line")],
    "swift": [(r"\bwithUnsafe\w*", "brace"), (r"\bUnsafe\w*Pointer\b", "line"), (r"\bunsafeBitCast\b", "line"),
              (r"\bassumingMemoryBound\b", "line"), (r"&\+|&-|&\*", "line")],
    "nim": [(r"\{\.\s*push\b[^}]*\b(checks|boundChecks|overflowChecks|rangeChecks)\s*:\s*off", "pushpop"),
            (r"\{\.\s*(checks|boundChecks|overflowChecks|rangeChecks)\s*:\s*off", "line"),
            (r"\bptr\s+UncheckedArray\b", "line"), (r"\bcast\[", "line"), (r"\baddr\b", "line"),
            (r"\bunsafeAddr\b", "line"), (r"\bcopyMem\b", "line")],
    "ada": [(r"\bpragma\s+Suppress\b", "unit"), (r"\bUnchecked_(Conversion|Access)\b", "line"),
            (r"'Address\b", "line"), (r"\bAddress_To_Access_Conversions\b", "line")],
    "odin": [(r"#no_bounds_check\b", "brace"), (r"\brawptr\b", "line"), (r"\btransmute\b", "line"),
             (r"\[\^\]", "line"), (r"\bmem\.ptr_offset\b", "line")],
    "julia": [(r"@inbounds\b", "indent"), (r"\bunsafe_\w+", "line"), (r"\bpointer\(", "line"),
              (r"\bllvmcall\b", "ir")],
    "mojo": [(r"\bUnsafePointer\b", "line"), (r"\bunsafe_\w+", "line"), (r"\bbitcast\b", "line"),
             (r"\b\w*UntrackedOrigin\b", "line")],
    "csharp": [(r"\bunsafe\b", "brace"), (r"\bfixed\s*\(", "brace"), (r"\bstackalloc\b", "line"),
               (r"\bUnsafe\.", "line"), (r"\bMemoryMarshal\.", "line"),
               (r"^\s*(?:(?:public|private|internal|protected|static|readonly|unsafe|extern)\s+)+"
                r"(?:[\w<>\[\],.?]+\*\s+\w+\s*(?:<[^>()]*>)?\s*\(|[\w<>\[\],.?]+\s+\w+\s*(?:<[^>()]*>)?\s*\([^)]*\w\*)",
                "brace"),
               (r"\b[A-Za-z_]\w*\*(?=[\s)\],>\[])", "line")],
    "java": [(r"\bsun\.misc\.Unsafe\b|\bjdk\.internal\.misc\.Unsafe\b", "line")],
    "go": [(r"\bunsafe\.", "line")],
    "haskell": [(r"\bunsafe[A-Z]\w*", "line"), (r"\bPtr\b", "line"), (r"\b(peek|poke)\w*", "line"),
                (r"\bplusPtr\b", "line"), (r"\b\w+OffAddr\w*#", "line"), (r"\b(index|read|write)\w*Array#", "line")],
    "ocaml": [(r"\bunsafe_(get|set|blit|fill)\w*", "line"), (r"\bObj\.magic\b", "line")],
    # part marginale seulement (langages sans vérification dans leur mode publié)
    "zig": [(r"@ptrCast|@ptrFromInt|@intFromPtr|@setRuntimeSafety\(\s*false\s*\)|\[\*\]", "line")],
    "chapel": [(r"\bc_ptr\w*\b|\bc_ptrTo\b", "line")],
    "d": [(r"\.ptr\b", "line"), (r"\bcast\s*\([^)]*\*\s*\)", "line")],
    "fpc": [(r"\bMove\s*\(", "line"), (r"\w\^|\^\w", "line")],
    "c": [], "cpp": [], "c3": [], "fortran": [],
    "js": [], "python": [], "lua": [], "php": [], "bqn": [],
}

ARCH_COMMON = [r"\b_mm\d*_\w+", r"\b__m(128|256|512)\w*", r"\b(imm|x86|xmm|emm|pmm|tmm|smm|nmm|wmm)intrin\.h\b",
               r"\b__builtin_ia32_\w+", r"\bllvm\.x86\."]
ARCH = {
    "rust": [r"\b(std|core)::arch\b", r"#\[target_feature", r"\bis_x86_feature_detected\b", r"\basm!"],
    "d": [r"\bgccbuiltins_x86\b", r"\basm\b"],
    "csharp": [r"\bSystem\.Runtime\.Intrinsics\.X86\b",
               r"\b(Avx\w*|Sse\w*|Bmi\d\w*|Popcnt|Lzcnt|X86Base|Fma|Pclmulqdq|Aes|Avx10v\d)\.(?!IsSupported)"],
    "go": [r"\bsimd/archsimd\b", r"\barchsimd\."],
    "ada": [r"\bSystem\.Machine_Code\b", r"\bAsm\s*\("],
    "c": [r"\b__asm__\b|\basm\b"], "cpp": [r"\b__asm__\b|\basm\b"], "zig": [r"\basm\b"], "odin": [r"\basm\b"],
    "c3": [r"\basm\b"], "nim": [r"\basm\b"], "fpc": [r"\basm\b"], "haskell": [r"-m(avx|sse|bmi)\w*"],
}


EMPTY_ASM = re.compile(r'\b(__asm__|asm)\s*(volatile|__volatile__)?\s*\(\s*""')


def unchecked(lang):
    return [(re.compile(p), s) for p, s in UNCHECKED.get(lang, [])]


def arch(lang):
    return [re.compile(p) for p in ARCH_COMMON + ARCH.get(lang, [])]
