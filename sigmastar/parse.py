from sigmastar.parser.function import assert_variable_name, Function
from sigmastar.parser.tokenize import tokenize, Token
from sigmastar.parser.expressions import *
from sigmastar.parser.types import Type, Primitive, Powerset, type
from sigmastar.integration import primitives, builtins, load_python
import importlib
import atexit
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
        if self.pos < len(self.tokens) and str(self.tokens[self.pos]) == "[":
            self.pos += 1
            index_expr = self._parse_call()
            self.consume("]", "Expected right bracket to close index access")
            base_expr = ExpressionValue(value)
            return ExpressionAccess(base_expr, index_expr)
            
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

    def _parse_if(self):
        # parse condition
        test = self._parse_call()
        self.consume("{", "Expected '{' to start if body")
        body = self._parse_function_body()
        # backtrack one token because _parse_function_body consumes the '}'
        self.pos -= 1
        self.consume("}", "Expected '}' to end if body")

        other = []
        # check for optional else
        if self.pos < len(self.tokens) and str(self.tokens[self.pos]) == "else":
            self.pos += 1
            self.consume("{", "Expected '{' to start else body")
            other = self._parse_function_body()
            self.pos -= 1
            self.consume("}", "Expected '}' to end else body")
        return ExpressionIf(test, body, other)

    def _parse_while(self):
        # parse condition
        test = self._parse_call()
        self.consume("{", "Expected '{' to start while body")
        body = self._parse_function_body()
        self.pos -= 1
        self.consume("}", "Expected '}' to end while body")
        return ExpressionWhile(test, body)

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
                expressions.append(self._parse_if())
            elif str(token) == "while":
                expressions.append(self._parse_while())
            elif self.pos<len(self.tokens) and str(self.tokens[self.pos]) == "(":
                self.pos -= 1
                expressions.append(self._parse_call())
            else:
                expressions.append(self._parse_assignment(token))
        return expressions

    def _parse_function(self):
        # always start with a primitive
        #self.consume("F", "Expected F (function) declaration here")
        signature = Type(self.next(), primitives)
        name = self.next()
        self.consume("(", "Expected opening parenthesis")
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
                    token.error("Expected comma between argument names")
                token = self.next()
        self.consume("{", "Expected opening bracket")
        body = self._parse_function_body()
        self.pos -= 1
        self.consume("}", "Expected closing bracket")
        return Function(name, 
            {str(arg): sig for arg, sig in zip(arguments, signature.primitives)},
            type(Token("".join([ret.alias for ret in signature.primitives[len(arguments):]]), name.path,name.row,name.col), primitives),
            body,
        )

    def parse(self):
        custom_imports: list[str] = list()
        functions: list[Function] = list()
        while self.pos<len(self.tokens):
            if self.pos<len(self.tokens)-1 and str(self.tokens[self.pos+1])==":":
                key = self.next()
                key_str = str(key)
                self.consume(":", "Expected double dots")
                value = self.next()
                value_str = str(value)
                if len(value_str)>=2 and value_str[0]=="\"" and value_str[-1]=="\"":
                    try: custom_imports.append(load_python(key_str, value_str[1:-1]))
                    except ModuleNotFoundError as e: value.error(str(e))
                    except Exception as e: value.error(str(e))
                else:
                    self.pos -= 1
                    if key_str in primitives:
                        key.error("Primitive already exists: "+primitives[key_str].pretty())
                    if len(key_str) != 1:
                        key.error("Primitive names must be a single character")
                    self.consume("{", "Expected opening bracket")
                    signature = type(self.next(), primitives)
                    self.consume("}", "Expected closing bracket")
                    primitives[key_str] = Powerset(key_str, signature)
            else: 
                functions.append(self._parse_function())
        func_globs = builtins|{str(function.name): function for function in functions}

        code = "\n".join(custom_imports)
        for func in functions:
            func.validate(func_globs)
        code += "def __Rprint__(x):\n"
        code += "    print(x)\n"
        code += "    return x\n"
        code += "def _assert_callable(x):\n"
        code += "    if not callable(x): raise Exception('Not yet implemented default callables')\n"
        code += "    return x\n"
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



def import_module(path):
    tokens = tokenize(path)
    context = Parser(tokens, 0)
    code = context.parse()
    base = os.path.splitext(path)[0]
    py_path = base + "__.py"
    modname = os.path.basename(base) + "__"
    if os.path.exists(py_path):
        raise FileExistsError(f"Temporary file already exists: {py_path}")
    os.makedirs(os.path.dirname(py_path), exist_ok=True)
    with open(py_path, "w", encoding="utf-8") as file:
        file.write(code)
    atexit.register(lambda: os.path.exists(py_path) and os.remove(py_path))
    try:
        spec = importlib.util.spec_from_file_location(modname, py_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module from {py_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        if os.path.exists(py_path):
            os.remove(py_path)
    return module
