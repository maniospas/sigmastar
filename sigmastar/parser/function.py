from sigmastar.parser.expressions import *
from sigmastar.parser.types import Type, Primitive


class Function:
    def __init__(self, name: Token, args: dict[str,Type], ret: Type, expressions: list):
        self.name = name
        self.args = args
        self.ret = ret
        self.expressions = expressions
        assert isinstance(ret, Type) or isinstance(ret, Primitive)

    def code(self, nesting):
        ret = ""
        for arg in self.args:
            if ret:
                ret += ","
            ret += arg
        ret = "\ndef "+str(self.name)+"("+ret+", *args):\n"
        nesting += "    "
        if variadic_returns:
            ret += nesting+"args = _flatten(args)\n"
            ret += nesting+"assert len(args) <= "+str(1 if self.ret.is_primitive else len(self.ret.primitives))+", 'Arguments exceeded the limits of "+str(self.ret.alias)+"'\n"
            # for ret_type in self.ret.primitives:
            #     ret += nesting+"assert isinstance(args[0], )"
        for expr in self.expressions:
            ret += expr.code(nesting)
        return ret

    def validate(self, globs: dict[str, "Function"]):
        context = Context(globs, self.args, self.ret)
        for expr in self.expressions:
            expr.validate(context)
        assert self.expressions, "Cannot validate an F (function) with no expressions"

def assert_variable_name(token: Token, message=""):
    name = str(token)
    if not name.isidentifier():
        token.error(f"Invalid variable name: {name!r} {message}")
    if keyword.iskeyword(name):
        token.error(f"Variable name {name!r} is a reserved keyword {message}")