* "sigmastar.ext"

addmul(x,y) R4 {
    return R.add(x,y), R.mul(x,y)
}

main() N {
    result = addmul(2.0, 3.0, 5.0)
    R.print(result)
    return 0
}
