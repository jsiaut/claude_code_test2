# Sonde de mode (v4, point 3 : docs/V4_EQUAL.md, 4) : « 1d » : Vector, « 2d » : Matrix (K9 naturel) ; indices à partir de 1.
function main()
    n = parse(Int, ARGS[2])
    if ARGS[1] == "1d"
        a = ones(n)
        println(a[n + 1])
    else
        g = ones(n, 4)
        println(g[n + 1, 2])
    end
end
main()
