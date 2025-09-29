import sigmastar as st
test = st.import_module("example/module.st")

print(*test.compare(1,2))
print(*test.compare(1))
assert not test.compare(1,2,True)
print(*test.compare(1,2,3,4))