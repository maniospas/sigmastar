from sigmastar.parser.tokenize import Token
from sigmastar.parser.types import Primitive, Type, type
from sigmastar.parser.function import *
from sigmastar.parser.function import _flatten
from sigmastar.extern import primitives


class ExpressionIf:
    def __init__(self, test, body: list, other: list):
        self.test = test
        self.body = body
        self.other = other

    def code(self, nesting):
        ret = nesting+"if "+self.test.code()+":\n"
        internal_nesting = nesting+"    "
        assert self.body, "Cannot implement if condition without a body"
        for expr in self.body:
            ret += expr.code(internal_nesting)
        if self.other:
            ret += nesting + "else:\n"
            for expr in self.other:
                ret += expr.code(internal_nesting)
        return ret
        
class ExpressionWhile:
    def __init__(self, test, body: list):
        self.result = str(result)
        self.op = str(op)
        self.args = [str(arg) for arg in args]

    def code(self, nesting):
        ret = nesting+"while "+self.test.code()+":\n"
        internal_nesting = nesting+"    "
        assert self.body, "Cannot implement if condition without a body"
        for expr in self.body:
            ret += expr.code(internal_nesting)


class ExpressionCall:
    def __init__(self, op: Token, args: list):
        assert isinstance(op, Token)
        self.op = op
        self.args = args

    def code(self):
        return str(self.op)+"("+",".join([arg.code() for arg in self.args])+")"

    def validate(self, context: Context):
        func = context.globals.get(str(self.op), None)
        if not func:
            self.op.error("No F (function) definition with this name")
        if len(self.args) != len(func.args):
            self.op.error(f"Expected {len(func.args)} but got {len(self.args)} arguments")
        i = 0
        for self_arg, func_arg in zip(self.args, func.args):
            i + 0
            self_arg_type = self_arg.validate(context)
            assert isinstance(self_arg_type, Type) or isinstance(self_arg_type, Primitive)
            if self_arg_type.alias != func.args[func_arg].alias:
                self.op.error(f"Expected {func.args[func_arg].pretty()} but got {self_arg_type.pretty()} type at argument {i+1}")
        return func.ret

class ExpressionValue:
    def __init__(self, value: Token):
        assert isinstance(value, Token)
        self.value = value
        self.cache: Type | None = None
        s = str(value)
        if s == "True" or s == "False":
            self.cache = primitives["B"]
        else:
            try:
                int(s)
                self.cache = primitives["N"]
            except ValueError:
                try:
                    float(s)
                    self.cache = primitives["R"]
                except ValueError:
                    # not a literal number, leave cache None
                    self.cache = None

    def code(self):
        return str(self.value)

    def validate(self, context: Context):
        if self.cache is not None:
            # literal type determined at construction
            return self.cache
        self_arg_type = context.locals.get(str(self.value), None)
        if self_arg_type is None:
            self.value.error("No local variable with this name")
        return self_arg_type


class ExpressionReturn:
    def __init__(self, token, exprs: list):
        assert all(isinstance(e, ExpressionCall) or isinstance(e, ExpressionValue) for e in exprs)
        assert str(token) == "return"
        self.token = token
        # flatten any nested tuples
        self.exprs = _flatten(exprs)

    def code(self, nesting):
        ret = ""
        if len(self.exprs) == 1:
            ret = nesting + "ret = _flatten(" + self.exprs[0].code()+ ")\n"
        else:
            ret = nesting+"ret = _flatten("+",".join([expr.code() for expr in self.exprs])+",)\n"
        if variadic_returns:
            ret += nesting+"ret = ret if isinstance(ret, tuple) else (ret,)\n"
            ret += nesting+"__args__ = tuple(list(__args__[:-len(ret)])+list(ret))\n"
            
            # ret += nesting+"for a, r in zip(args, ret if isinstance(ret, tuple) else (ret,)):\n"
            # for i, primitive in enumerate(self.exprs):
            #     ret += nesting+"    if a is not None: assert a==r, 'Incompatible F (function) spaces'\n"
            ret += nesting+"return __args__[-__numrets__:] if __numrets__ else ()"
        else:
            ret += nesting+"return ret\n"
        return ret

    def validate(self, context: Context):
        types = []
        for expr in self.exprs:
            t = expr.validate(context)
            assert isinstance(t, Type) or isinstance(t, Primitive)
            types.append(t)
        joined = type(Token("".join([t.alias for t in types]), self.token.path, self.token.row, self.token.col), primitives)
        if context.ret.alias != joined.alias:
            self.token.error(f"Expected {context.ret.pretty()} but got {joined.pretty()} type")
        return None

class ExpressionAssign:
    def __init__(self, result: Token, exprs: list):
        assert isinstance(result, Token)
        assert all(isinstance(e, ExpressionCall) or isinstance(e, ExpressionValue) for e in exprs)
        self.result = result
        # flatten right-hand nested tuples
        self.exprs = _flatten(exprs)

    def code(self, nesting):
        if len(self.exprs) == 1:
            return nesting + str(self.result) + " = " + self.exprs[0].code()+ "\n"
        return nesting + str(self.result) + " = _flatten(" + ",".join([e.code() for e in self.exprs]) + ",)\n"

    def validate(self, context: Context):
        types = []
        for expr in self.exprs:
            t = expr.validate(context)
            if t is None:
                self.result.error("No expression computed at the right-hand side of assignment")
            assert isinstance(t, Type) or isinstance(t, Primitive)
            types.append(t)
        joined = type(Token("".join([t.alias for t in types]), self.result.path, self.result.row, self.result.col), primitives)
        prev = context.locals.get(str(self.result), None)
        if prev:
            if prev.alias != joined.alias:
                self.result.error(f"Previously set {prev.pretty()} but got {joined.pretty()} type")
        else:
            context.locals[str(self.result)] = joined
        return None