*: "sigmastar.ext" # import statement (_ directly imports)
C: {RRB} # powerset

CRRB symmetry(comparison, x,y) {
    return B.eq(comparison(x,y),comparison(y,x))
}

N main() {
    is_symmetric = symmetry(R.eq,1.0,2.0)
    B.print(is_symmetric)
    return 0
}
