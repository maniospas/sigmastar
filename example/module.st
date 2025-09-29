* "sigmastar.ext"

compare(x,y) RRB3 {
    return R.lt(x,y), R.gt(x,y), R.eq(x,y)
}

add_point(ax,ay,bx,by) R6 {
    ret = R.add(ax,ay), R.add(bx,by)
    if R.le(R.add(ax,ay),10.0) {
        return 0.0,0.0
    }
    return ret
}

main() {
    result = compare(1.0,2.0)
    B.print(result[0])
    B.print(result[1])
    B.print(result[2])
}