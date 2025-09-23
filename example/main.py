import sigmastar as st
test = st.import_module("example/module.st")

print(*test.le(1,2))
print(*test.le(1))
assert not test.le(1,2,True)
print(*test.add_point(1,2,3,4))