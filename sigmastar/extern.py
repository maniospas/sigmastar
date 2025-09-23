from sigmastar.parser.types import Primitive
from sigmastar.parser.tokenize import Token
from sigmastar.parser.function import Function


primitives = {
    "N": Primitive("N", "int"),
    "R": Primitive("R", "float"),
    "B": Primitive("B", "boolean"),
    "P": Primitive("P", "pointer"),
    "F": Primitive("F", "function"),
}

builtins = {
    "__add__": Function(Token("__add__", "__builtins__", 0, 0), {"x": primitives["R"], "y": primitives["R"]}, primitives["R"], None),
    "__sub__": Function(Token("__sub__", "__builtins__", 0, 0), {"x": primitives["R"], "y": primitives["R"]}, primitives["R"], None),
    "__mul__": Function(Token("__mul__", "__builtins__", 0, 0), {"x": primitives["R"], "y": primitives["R"]}, primitives["R"], None),
    "__div__": Function(Token("__div__", "__builtins__", 0, 0), {"x": primitives["R"], "y": primitives["R"]}, primitives["R"], None),
    "__abs__": Function(Token("__div__", "__builtins__", 0, 0), {"x": primitives["R"]}, primitives["R"], None),
    "__lt__": Function(Token("__lt__", "__builtins__", 0, 0), {"x": primitives["R"], "y": primitives["R"]}, primitives["B"], None),
    "__le__": Function(Token("__le__", "__builtins__", 0, 0), {"x": primitives["R"], "y": primitives["R"]}, primitives["B"], None),
    "__gt__": Function(Token("__gt__", "__builtins__", 0, 0), {"x": primitives["R"], "y": primitives["R"]}, primitives["B"], None),
    "__ge__": Function(Token("__ge__", "__builtins__", 0, 0), {"x": primitives["R"], "y": primitives["R"]}, primitives["B"], None),
    "__eq__": Function(Token("__eq__", "__builtins__", 0, 0), {"x": primitives["R"], "y": primitives["R"]}, primitives["B"], None),
    "__neq__": Function(Token("__neq__", "__builtins__", 0, 0), {"x": primitives["R"], "y": primitives["R"]}, primitives["B"], None),
    "__not__": Function(Token("__not__", "__builtins__", 0, 0), {"x": primitives["B"]}, primitives["B"], None),
}
