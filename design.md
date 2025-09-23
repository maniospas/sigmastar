
```rust
F R101 dot(x[50], y[50]) {
    i = 0
    ret = 0.0
    loop {
        // automatically end it when out of range
        ret = __add__(ret, __mul__(x[i], y[i]))
        i = i+1
    }
}
```


```rust


F R5 func1(a1,a2,a3,a4) {

}
 
F FR5 func2(func,a1,a2,a3,a4) { // -> we want to change the function while also looking only at its R5 type
    return func(a1,a2,a3,a4)
}


```