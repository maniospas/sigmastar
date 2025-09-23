from sigmastar.parser.tokenize import tokenize, Token
from sigmastar.parser.types import Type, Primitive, type
from sigmastar.parser.expressions import *
from sigmastar.parser.function import assert_variable_name, Function
from sigmastar.extern import primitives, builtins
import keyword
import importlib
import os


class Parser:
    def __init__(self, tokens: list[Token], pos: int):
        self.tokens = tokens
        self.pos = int(pos)
        self.types: dict[str,str] = dict()
    
    def next(self) -> Token:
        value = self.tokens[self.pos]
        self.pos += 1
        return value

    def consume(self, symbol: str, message: str):
        value = self.next()
        if str(value) != str(symbol):
            value.error(message)

    def _parse_call(self):
        value = self.next()
        if str(self.tokens[self.pos]) != "(":
            return ExpressionValue(value)
        assert_variable_name(value,) # this is guaranteed to be a function now, so check this
        self.pos += 1 # consume the opening parenthesis
        args = list()
        while self.pos<len(self.tokens):
            if str(self.tokens[self.pos])==")":
                break
            args.append(self._parse_call())
            if str(self.tokens[self.pos])!=")":
                self.consume(",", "Expected comma to separate argument names")
        self.pos += 1
        return ExpressionCall(value, args)

    def _parse_assignment(self, result: Token):
        assert_variable_name(result)
        if self.pos < len(self.tokens) and str(self.tokens[self.pos]) == ",":
            self.tokens[self.pos].error("Multiple variables on the left-hand side are not allowed")
        self.consume("=", "Expected assignment here")
        exprs = [self._parse_call()]
        while self.pos < len(self.tokens) and str(self.tokens[self.pos]) == ",":
            self.pos += 1
            exprs.append(self._parse_call())
        return ExpressionAssign(result, exprs)

    def _parse_function_body(self):
        expressions: list = list()
        while self.pos<len(self.tokens):
            token = self.next()
            if str(token)=="}":
                break
            if str(token) == "return":
                exprs = [self._parse_call()]
                while self.pos < len(self.tokens) and str(self.tokens[self.pos]) == ",":
                    self.pos += 1  # consume comma
                    exprs.append(self._parse_call())
                expressions.append(ExpressionReturn(token, exprs))
            elif str(token) == "if":
                self._parse_if()
            elif str(token) == "while":
                expressions.append(self._parse_while())
            else:
                expressions.append(self._parse_assignment(token))
        return expressions

    def _parse_function(self):
        # always start with a primitive
            self.consume("F", "Expected F (function) declaration here")
            signature = type(self.next(), primitives)
            name = self.next()
            self.consume("(", "Expected opening parenthesis expected here")
            arguments: list[Token] = list()
            token = self.next()
            while str(token) != ")":
                assert_variable_name(token)
                arguments.append(token)
                if len(arguments) >= len(signature.primitives):
                    token.error("There are fewer or equal signature primitives than the number of arguments")
                token = self.next()
                if str(token) != ")":
                    if str(token)!=",":
                        token.error("Expected comma to separate argument names")
                    token = self.next()
            self.consume("{", "Expected ppening parenthesis bracket here")
            body = self._parse_function_body()
            self.pos -= 1
            self.consume("}", "Expected closing parenthesis bracket here")
            return Function(name, 
                {str(arg): sig for arg, sig in zip(arguments, signature.primitives)},
                type(Token("".join([ret.alias for ret in signature.primitives[len(arguments):]]), name.path,name.row,name.col), primitives),
                body,
            )

    def parse(self):
        functions: list[Function] = list()
        while self.pos<len(self.tokens):
            functions.append(self._parse_function())
        func_globs = builtins|{str(function.name): function for function in functions}
        for func in functions:
            func.validate(func_globs)
        code = ""
        code += "def __add__(x,y):\n"
        code += "    return x+y\n"
        code += "def __sub__(x,y):\n"
        code += "    return x-y\n"
        code += "def __mul__(x,y):\n"
        code += "    return x*y\n"
        code += "def __div__(x,y):\n"
        code += "    return x/y\n"
        code += "def __lt__(x,y):\n"
        code += "    return x<y\n"
        code += "def __gt__(x,y):\n"
        code += "    return x>y\n"
        code += "def __le__(x,y):\n"
        code += "    return x<=y\n"
        code += "def __ge__(x,y):\n"
        code += "    return x>=y\n"
        code += "def __eq__(x,y):\n"
        code += "    return x==y\n"
        code += "def __neq__(x,y):\n"
        code += "    return x!=y\n"
        code += "def __not__(x):\n"
        code += "    return not x\n"
        code += "def __abs__(x):\n"
        code += "    return abs(x)\n"
        code += "def _flatten(*x):\n"
        code += "    if not isinstance(x, tuple): return x\n"
        code += "    out = list()\n"
        code += "    for v in x:\n"
        code += "        if isinstance(v, tuple): out.extend(_flatten(*v))\n"
        code += "        else: out.append(v)\n"
        code += "    return tuple(out)\n"
        for func in functions:
            code += func.code(nesting="")
        return code


import importlib
import os
import atexit

def import_module(path):
    tokens = tokenize(path)
    context = Parser(tokens, 0)
    code = context.parse()
    base = os.path.splitext(path)[0]
    py_path = base + "__.py"
    modname = os.path.basename(base) + "__"
    if os.path.exists(py_path):
        raise FileExistsError(f"Temporary file already exists: {py_path}")
    with open(py_path, "w", encoding="utf-8") as file:
        file.write(code)
    atexit.register(lambda: os.path.exists(py_path) and os.remove(py_path))
    try:
        module = importlib.import_module(modname)
    finally:
        if os.path.exists(py_path):
            os.remove(py_path)
    return module
