# Σ* 

Σ* or *sigmastar* is an esoteric language where primitives are 
denoted by single characters, thus making structural types
consist of a number of letters equal to their size.
The language interoperates with Python, being able to call 
its modules and be imported as a module.


## ⚡ Quickstart

Here is some a simple Σ* function, using a *ruby* highlighter. 
Its declaration contain its type: a mapping within
the set `RRB3`. This notates the Cartesian product 
*R (reals) x R (reals) x B (booleans) x B (booleans) x B (booleans)*. 
The number `3` expands to three total repetitions of the last symbol. 
The set can also be written as `RRBBB`. 
Other primitives are `N` for integers and `S` for strings. 


```ruby
# example/module.st
* "sigmastar.ext" # import all from type-hinted Python module

compare(x,y) RRB3 {
    return R.lt(x,y), R.gt(x,y), R.eq(x,y)
}
```


Inputs and outputs are indistinguishable: fewer inputs are 
zero-initialized, and even more of them are allowed (more on this later).
For example, any `RRB3` definition that is given an `R` argument
yields a value in `RB3`, given an `RRB` argument yields a value in `BB`,
etc. Those returns are independent of how the function definition splt
the type into inputs and outputs. This is a set-based view of function 
spaces.

Functions only accept one definition each, but you can namespace them
by prepending `namespace.` to their names; dots are treated as characters,
and from Python they are viewed as `__`. Add a `main` function
that lets Σ* directly run the file; absense of a type by convention indicates
the empty set `{}`. Notice that, in the example, we used `[item]`
to obtain an index value. Only outcomes that repeat the same 
type can be indexed.

```ruby
main() {
    result = compare(1.0,2.0)
    B.print(result[0])
    B.print(result[1])
    B.print(result[2])
}
```

```bash
python3 -m sigmastar example/module.st
True
False
False
```

## ⚙ Function types

Type declarations like the above depend on structural matching of arguments.
However, you may want to pass a function as an argument. The function type
must be declared as a new primitive with the syntax `character {type}`. 
**There are no anonymous types.** This new primitive must also be denoted by 
a single character, letting us write skip type system complexities.

```ruby
* "sigmastar.ext" # import some python-defined symbols
C {RRB} # function type

symmetry(comparison, x,y) CRRB {
    return B.eq(comparison(x,y),comparison(y,x))
}

main() {
    is_symmetric = symmetry(R.eq,1.0,2.0)
    B.print(is_symmetric)
}
```

Previously, it was mentioned that more than the declared number of inputs are allowed,
in line with covering a Cartesian space. This is done by runtime verification that 
the values of extra inputs match the respective outputs. For example, consider the 
following program, where an additional argument is passed to `addmul`. This argument 
matches the returned outcome of `R.add`, creating an assertion against the latter's 
computd value. At the same time, the return value is of type `R` and holds only the outcome 
of `R.mul`.  


```ruby
#example/verify.st
* "sigmastar.ext"

addmul(x,y) R4 {
    return R.add(x,y), R.mul(x,y)
}

main() {
    result = addmul(2.0, 3.0, 50.0)
    R.print(result)
}
```

```bash
python3 -m sigmastar example/verify.st 
AssertionError: Return mismatch: expected 50.0, returned 5.0
```

## 🧩 Lambdas

*Lambdas are under development.*

You can create a lambda function with partially applied values
by placing `*` before a function call. This grabs argument values
and fixes them as first inputs.

```ruby
* "sigmastar.ext"

main() {
    inc = *R.add(1.0)
    R.print(inc(7.0))  # prints 8.0
}
```


## 📚 Importing from Python

You can call Σ* functions from Python, like below. All
returned values are retrieved as flattened tuples, so 
use an unpacking mechanism like `*` or tuple unpacking 
to access them. 

```ruby
# example/module.st
* "sigmastar.ext" # import all from type-hinted Python module

compare(x,y) RRB3 {
    return R.lt(x,y), R.gt(x,y), R.eq(x,y)  # R. is a decorative mnemonic
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