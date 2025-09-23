# Σ* 

Σ* or *sigmastar* is an esoteric language where primitives are 
denoted by single characters, thus making strustural types be
comprised by a number of letters equal to their size.
The language interoperates with Python, being able to call 
its modules and be imported as a module.


# ⚡ Quickstart

Here is some a simple Σ* function, using a *Java* highlighter. 
Its declaration startz from its type `F`, which indicates
a function pointer. It is then followed by the set in which 
the function is a mapping, namely on the Cartesian project 
of *R (reals) x R (reals) x B (booleans)*. Inputs and outputs
are indistinguishable in this mapping: fewer inputs are 
zero-initialized, whereas more inputs create assertion checks 
that the given value is actually computed.


```java
// module.st
F RRB le(x,y) {
    return __le__(x,y)
}
```

You can call this function from Python like below. All
returned values are retrieved as flattened tuples, 
so use an unpacking mechanism like `*` to retrieve values.


```python
# main.py
import sigmastar as st
test = st.import_module("test.st")

print(*test.le(1,2))
print(*test.le(1,2,True)) # call while asserting that first output is true
```
