# This file contains helper Python functions that can be imported 
# in sigmastar files by using their typehints.

def R__add(x: float, y: float) -> float: return x + y
def R__sub(x: float, y: float) -> float: return x - y
def R__mul(x: float, y: float) -> float: return x * y
def R__div(x: float, y: float) -> float: return x / y

def R__lt(x: float, y: float) -> bool: return x < y
def R__gt(x: float, y: float) -> bool: return x > y
def R__le(x: float, y: float) -> bool: return x <= y
def R__ge(x: float, y: float) -> bool: return x >= y
def R__eq(x: float, y: float) -> bool: return x == y
def R__neq(x: float, y: float) -> bool: return x != y
def R__abs(x: float) -> float: return x if x >= 0 else -x
def R__print(x: float) -> float: print(x); return x

def B__not(x: bool) -> bool: return not x
def B__eq(x: bool, y: bool) -> bool: return x == y
def B__neq(x: bool, y: bool) -> bool: return x != y
def B__print(x: bool) -> bool: print(x); return x

def S__eq(x: str, y: str) -> bool: return x == y
def S__neq(x: str, y: str) -> bool: return x != y
def S__print(x: str) -> str: print(x); return x
