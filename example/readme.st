C = {RRB}// f: f(0,0,False) and f(1,0)!=f(0,1)}

CRRB symmetry(comparison, x,y) {
    return __eq__(comparison(x,y),comparison(y,x))
}

B main() {
    print(symmetry(gt,1.0,2.0))
    return True
}
