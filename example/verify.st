*: "sigmastar.ext"

R4 addmul(x,y) {
    return R.add(x,y), R.mul(x,y)
}

N main() {
    result = addmul(2.0, 3.0, 5.0)
    R.print(result)
    return 0
}
