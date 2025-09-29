# This file contains helper Python functions that can be imported 
# in sigmastar files by using their typehints.
import math


def N__add(x: int, y: int) -> int: return x + y
def N__sub(x: int, y: int) -> int: return x - y
def N__mul(x: int, y: int) -> int: return x * y
def N__div(x: int, y: int) -> int: return x // y   # integer division
def N__lt(x: int, y: int) -> bool: return x < y
def N__gt(x: int, y: int) -> bool: return x > y
def N__le(x: int, y: int) -> bool: return x <= y
def N__ge(x: int, y: int) -> bool: return x >= y
def N__eq(x: int, y: int) -> bool: return x == y
def N__neq(x: int, y: int) -> bool: return x != y
def N__abs(x: int) -> int: return x if x >= 0 else -x
def N__print(x: int) -> int: print(x); return x
def N__toS(x: int) -> str: return str(x)
def N__toR(x: int) -> float: return float(x)

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
def R__toS(x: float) -> str: return str(x)
def R__floor(x: float) -> int: return math.floor(x)
def R__round(x: float) -> int: return math.round(x)
def R__ceil(x: float) -> int: return math.ceil(x)

def B__not(x: bool) -> bool: return not x
def B__eq(x: bool, y: bool) -> bool: return x == y
def B__neq(x: bool, y: bool) -> bool: return x != y
def B__print(x: bool) -> bool: print(x); return x
def B__toS(x: bool) -> str: return "True" if x else "False"

def S__eq(x: str, y: str) -> bool: return x == y
def S__neq(x: str, y: str) -> bool: return x != y
def S__print(x: str) -> str: print(x); return x
def S__cat(x: str, y: str) -> str: return x+y
def S__toB(x: str) -> bool: 
    if x=="True": return True
    if x=="False": return False
    raise Exception("String cannot be converted to boolean: \""+x+"\"")
def S__toF(x: str) -> float: return float(x)
def S__toN(x: str) -> int: return int(x)
