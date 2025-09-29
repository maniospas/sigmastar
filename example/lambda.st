* "sigmastar.ext"
b {R}

generate() b {
    return \b 1.0|2.0|R.add
}

main() N {
    inc = generate()
    R.print(inc(4.0))  # prints 3.0
    return 0
}