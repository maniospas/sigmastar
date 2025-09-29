* "sigmastar.ext"           # import all symbols
u {RR}                      # new primitive (primitives have one letter)

generate(offset) Ru {       # in the space of R x u
    return \u offset|R.add  # \u casts anonymous {RR} to u, | is lambda application
}

main() {
    inc = generate(1.0)
    R.print(inc(4.0))       # prints 5.0
}
