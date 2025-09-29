* "sigmastar.ext" # import statement (* directly imports)
C {RRB} # function type

symmetry(comparison, x,y) CRRB {
    return B.eq(comparison(x,y),comparison(y,x))
}

main() N {
    is_symmetric = symmetry(R.eq,1.0,2.0)
    B.print(is_symmetric)
    return 0
}
