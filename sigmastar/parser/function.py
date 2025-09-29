from sigmastar.parser.types import Type, Primitive
from sigmastar.parser.tokenize import Token
import keyword

variadic_returns = True


def _flatten(values):
    out = []
    for v in values:
        if isinstance(v, (list, tuple)):
            out.extend(_flatten(v))
        elif hasattr(v, "exprs") and isinstance(v.exprs, list):
            out.extend(_flatten(v.exprs))
        else:
            out.append(v)
    return out

class Context:
    def __init__(self, globs: dict[str, "Function"], locals, ret):
        self.globals = globs
        self.locals: dict[str, Type] = {k: v for k, v in locals.items()}
        self.ret = ret

class Function:
    def __init__(self, name: Token, args: dict[str,Type], ret: Type, expressions: list, is_lambda=False):
        assert isinstance(ret, Type) or isinstance(ret, Primitive)
        self.name = name
        self.args = args
        self.ret = ret
        self.expressions = expressions
        self.is_lambda = is_lambda

    def debug(self):
        print("function:", self.name)
        print("args:")
        for arg in self.args:
            print("  "+arg+":", self.args[arg].pretty())
        print("return:", self.ret.pretty())

    def code(self, nesting):
        ret = ""
        for arg in self.args:
            if ret:
                ret += ","
            ret += arg
        if variadic_returns:
            ret = "\ndef "+str(self.name)+"(*__args__):\n"
            nesting += "    "
            ret += nesting+"__args__ = _flatten(__args__)\n"
            requisite_args = str((1 if self.ret.is_primitive else len(self.ret.primitives))+len(self.args))
            ret += nesting+f"__numrets__ = {requisite_args}-len(__args__)\n"
            ret += nesting+f"assert __numrets__>=0, 'Extra return arguments exceeded the limits of {self.ret.alias}'\n"
            ret += nesting+f"if __numrets__>0: __args__ = tuple(list(__args__)+[None]*__numrets__)\n"
            i = 0
            ret += nesting+"__args__ = list(__args__)\n"
            for arg_name, arg_type in self.args.items():
                ret += nesting+f"{arg_name} = __args__[{i}] = {arg_type.actual}(0 if __args__[{i}] is None else __args__[{i}])\n"
                i += 1
            # for ret_type in self.ret.primitives:
            #     ret += nesting+"assert isinstance(args[0], )"
        else:
            ret = "\ndef "+str(self.name)+"("+ret+"):\n"
            nesting += "    "
        for expr in self.expressions:
            ret += expr.code(nesting)
        return ret

    def validate(self, globs: dict[str, "Function"]):
        context = Context(globs, self.args, self.ret)
        for expr in self.expressions:
            expr.validate(context)
        assert self.expressions, "Cannot validate a function with no expressions"

def assert_variable_name(token: Token, message=""):
    name = str(token)
    if not name.isidentifier():
        token.error(f"Invalid variable name: {name!r} {message}")
    if keyword.iskeyword(name):
        token.error(f"Variable name {name!r} is a reserved keyword {message}")