# Σ* 

Σ* or *sigmastar* is an esoteric language where primitives are 
denoted by single characters, thus making strustural types be
comprised by a number of letters equal to their size.
The language interoperates with Python, being able to call 
its modules and be imported as a module.


## ⚡ Quickstart

Here is some a simple Σ* function, using a *ruby* highlighter. 
Its declaration starts from its type. That is a mapping within
the set `RRB3`, indicating the Cartesian product 
*R (reals) x R (reals) x B (booleans) x B (booleans) x B (booleans)*. 
The number `3` expands to three total repetitions of the last symbol. 
The set can also be written as `RRBBB`.

Inputs and outputs are indistinguishable: fewer inputs are 
zero-initialized, whereas more inputs create assertion checks 
that the given value is actually computed. If you have more 
than one consecutive primitives of the same type, you can use 
a number to repeat them. For example `RRB3` is a shorthand for
`RRBBB`. Other primitives are `N` for integers and `S` for
strings. 


```ruby
# example/module.st
*: "sigmastar.ext" # import all from type-hinted Python module

RRB3 compare(x,y) {
    return R.lt(x,y), R.gt(x,y), R.eq(x,y)
}
```

Arguments are variadic: missing ones are 
set to zero (or False, etc) and returned alongside outputs. 
If you give more inputs, respective outputs are not returned
but assert that the provided values are retrieved. 

For example, any `RRB3` definition that is given an `R` argument
yields a value in `RB3`, given an `RRB` argument yields a value in `BB`,
etc. Those returns are independent of how the function definition splt
the type into inputs and outputs. This is a set-based view of function 
spaces. Do note that an exception occurs if asserted outputs are not
validated.

Functions only accept one definition each, but you can namespace them
by prepending `namespace.` to their names; dots are treated as characters,
and from Python they are viewed as `__`. You can also add a `main` function
that lets Σ* directly run the file. Notice that, in the example, we used `[item]`
to obtain an index value. Furthermore, only outcomes that repeat the same 
type can be indexed.

```ruby
N main() {
    result = compare(1.0,2.0)
    B.print(result[0])
    B.print(result[1])
    B.print(result[2])

    return 0
}

```

```bash
python3 -m sigmastar example/module.st
True
False
False
```

## ⚙ Powersets

Type declarations like the above depend on structural matching of arguments.
However, you may want to pass a function as an argument. The function type
must be declared as a new primitive that forms the powerset of a structural type.
Declaring powersets is done with the syntax `character: {type}`. 
**There are no anonymous types.** This new primitive must also be a single character.

```ruby
# example/module.st
*: "sigmastar.ext" # import from .st or .py module
C: {RRB} # powerset

CRRB symmetry(comparison, x,y) {
    return B.eq(comparison(x,y),comparison(y,x))
}

B main() {
    is_symmetric = symmetry(R.eq,1.0,2.0)
    B.print(is_symmetric)

    return True
}
```



## 📚 Importing from Python

You can call Σ* functions from Python, like below. All
returned values are retrieved as flattened tuples, so 
use an unpacking mechanism like `*` or tuple unpacking 
to access them. 

```ruby
# example/module.st
*: "sigmastar.ext" # import all from type-hinted Python module

RRB3 compare(x,y) {
    return R.lt(x,y), R.gt(x,y), R.eq(x,y)
}
```

```python
# example/module.py
import sigmastar as st
test = st.import_module("example/module.st")

print(*test.le(1,2))
print(*test.le(1))
assert not test.le(1,2,True)
print(*test.add_point(1,2,3,4))
```

```bash
python3 example/module.py
True False False
False
0.0 False True False
```