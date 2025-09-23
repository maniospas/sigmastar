# Σ* 

Σ* or *sigmastar* is an esoteric language where primitives are 
denoted by single characters, thus making strustural types be
comprised by a number of letters equal to their size.
The language interoperates with Python, being able to call 
its modules and be imported as a module.


## ⚡ Quickstart

Here is some a simple Σ* function, using a *Java* highlighter. 
Its declaration starts from its type. That is a mapping within
the set `RRB3`, indicating the Cartesian product *R (reals) x R (reals) x B (booleans) x B (booleans) x B (booleans)*. The number `3` expands to three total repetitions of the last symbol. The set can also be
written as `RRBBB`.

Inputs and outputs are indistinguishable: fewer inputs are 
zero-initialized, whereas more inputs create assertion checks 
that the given value is actually computed. If you have more 
than one consecutive primitives of the same type, you can use 
a number to repeat them. For example `RRB3` is a shorthand for
`RRBBB`. Other primitives are `N` for integers and `S` for
strings.


```java
// example/module.st
RRB3 compare(x,y) {
    return __lt__(x,y), __gt__(x,y), __eq__(x,y)
}
```

You can call this function from Python like below. All
returned values are retrieved as flattened tuples, so 
use an unpacking mechanism like `*` or tuple unpacking 
to access them. Arguments are variadic: missing ones are 
set to zero (or False, etc) and returned alongside outputs. 
If you give more inputs, respective outputs are not returned
but assert that the provided values are retrieved. 

For example, any `RRB3` definition that is given an `R` argument
yields a value in `RB3`, given an `RRB` argument yields a value in `BB`,
etc. Those returns are independent of how the function definition splt
the type into inputs and outputs. This is a set-based view of function 
spaces. Do note that an exception occurs if asserted outputs are not
validated.

```python
# example/main.py
import sigmastar as st
test = st.import_module("example/test.st")

print(*test.le(1,2))             # returns B3
print(*test.le(1,2,True, False)) # asserts and returns B
print(*test.le(1))               # zero defaults for missing values, returned RB3
```

```bash
python3 example/main.py
True False False
False
0.0 False True False
```


## ⚙ Advanced concepts

*Under implementation.*

Type declarations like the above depend on structural matching of arguments.
However, you may want to pass a function as an argument. The function type
declaration includes a whitespace (in truth, this is a parametric type, but 
more on this later). But you can name the function type like below.

```java
C = {RRB} // powerset

CRRB symmetry(comparison, x,y) {
    return __eq__(comparison(x,y),comparison(y,x))
}

B main() {
    print(symmetry(__lt__,1.0,2.0))
    return True
}
```
