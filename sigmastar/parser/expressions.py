from sigmastar.parser.tokenize import Token
from sigmastar.parser.types import Primitive, Powerset, Type, type
from sigmastar.parser.function import *
from sigmastar.parser.function import _flatten
from sigmastar.integration import primitives


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

    def validate(self, context: Context):
        cond_type = self.test.validate(context)
        assert isinstance(cond_type, (Type, Primitive))
        if cond_type.alias != primitives["B"].alias:
            self.test.value.error(f"If condition must be Boolean, got {cond_type.pretty()}")
        for expr in self.body:
            expr.validate(context)
        for expr in self.other:
            expr.validate(context)
        return None
        
class ExpressionWhile:
    def __init__(self, test, body: list):
        self.test = test
        self.body = body

    def code(self, nesting):
        ret = nesting + "while " + self.test.code() + ":\n"
        internal_nesting = nesting + "    "
        assert self.body, "Cannot implement while loop without a body"
        for expr in self.body:
            ret += expr.code(internal_nesting)
        return ret

    def validate(self, context: Context):
        cond_type = self.test.validate(context)
        assert isinstance(cond_type, (Type, Primitive))
        if cond_type.alias != primitives["B"].alias:
            self.test.value.error(f"While condition must be Boolean, got {cond_type.pretty()}")
        for expr in self.body:
            expr.validate(context)
        return None



class ExpressionCall:
    def __init__(self, op: Token, args: list, is_lambda: bool=False):
        assert isinstance(op, Token)
        self.op = op
        self.args = args
        self.is_lambda = is_lambda

    def code(self, nesting=""):
        return nesting+str(self.op)+"("+",".join([arg.code() for arg in self.args])+")"+("\n" if nesting else "")

    def validate(self, context: Context):
        func = context.globals.get(str(self.op), None)
        if not func:
            func = context.locals.get(str(self.op), None)
            if not isinstance(func, Powerset):
                self.op.error("No function definition or {powerset} variable with this name")
            else:
                if len(self.args) > len(func.base.primitives):
                    self.op.error(f"Expected at most {len(func.args)} but got {len(self.args)} arguments")
                func = Function(str(self.op), 
                    args={"__arg"+str(idx): arg for idx, arg in enumerate(func.base.primitives[:len(self.args)])}, 
                    ret=type(
                        Token(",".join([prim.alias for prim in func.base.primitives[len(self.args):]]),
                            self.op.path, self.op.row, self.op.col
                        ), 
                        primitives
                    ),
                    expressions=None
                )
        if len(self.args) != len(func.args):
            self.op.error(f"Expected {len(func.args)} but got {len(self.args)} arguments")
        i = 0
        for self_arg, func_arg in zip(self.args, func.args):
            i += 1
            self_arg_type = self_arg.validate(context)
            assert isinstance(self_arg_type, Type) or isinstance(self_arg_type, Primitive) or isinstance(self_arg_type, Powerset)
            if self_arg_type.comparable() != func.args[func_arg].comparable():
                self.op.error(f"Expected {func.args[func_arg].pretty()} but got {self_arg_type.pretty()} type at argument '{func_arg}' (argument {i})")
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
            self_arg_type = context.globals.get(str(self.value), None)
            if self_arg_type is None:
                self.value.error("No local variable with this name")
            assert isinstance(self_arg_type, Function), "Internal error: need to retrieve function here"
            types = [self_arg_type.args[arg] for arg in self_arg_type.args]+( 
                [self_arg_type.ret] if self_arg_type.ret.is_primitive else [ret for ret in self_arg_type.ret]
            )
            base = type(Token("".join([t.alias for t in types]), self.value.path, self.value.row, self.value.col), primitives)
            self_arg_type = Powerset("", base=base)
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
            ret += nesting + "for _expected, _actual in zip(__args__[-len(ret):], ret):\n"
            ret += nesting + "    if _expected is not None:\n"
            ret += nesting + "        assert _expected == _actual, (\n"
            ret += nesting + "            f'Return mismatch: expected {_expected!r}, returned {_actual!r}'\n"
            ret += nesting + "        )\n"
            ret += nesting + "__args__[-len(ret):] = list(ret)\n"
            ret += nesting + "__args__ = tuple(__args__)\n"
            ret += nesting+"__args__ = tuple(list(__args__[:-len(ret)])+list(ret))\n"
            
            # ret += nesting+"for a, r in zip(args, ret if isinstance(ret, tuple) else (ret,)):\n"
            # for i, primitive in enumerate(self.exprs):
            #     ret += nesting+"    if a is not None: assert a==r, 'Incompatible F (function) spaces'\n"
            ret += nesting+"return __args__[-__numrets__:] if __numrets__ else ()\n"
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


class ExpressionAccess:
    def __init__(self, value_expr, index_expr):
        self.value_expr = value_expr
        self.index_expr = index_expr

    def code(self):
        return f"{self.value_expr.code()}[{self.index_expr.code()}]"

    def validate(self, context: Context):
        container_type = self.value_expr.validate(context)
        assert isinstance(container_type, (Type, Primitive, Powerset))
        if isinstance(container_type, Primitive):
            self.value_expr.value.error(
                f"Cannot index primitive type {container_type.pretty()}"
            )
        idx_type = self.index_expr.validate(context)
        assert isinstance(idx_type, (Type, Primitive))
        if idx_type.alias != primitives["N"].alias:
            self.index_expr.value.error(
                f"Index must be of type {primitives['N'].pretty()}, "
                f"got {idx_type.pretty()}"
            )
        element_type = (
            container_type.base if isinstance(container_type, Powerset)
            else container_type
        )
        assert isinstance(element_type, Type), (
            "Internal error: element_type should be a Type"
        )
        aliases = {prim.alias for prim in element_type.primitives}
        if len(aliases) != 1:
            self.value_expr.value.error(
                "All primitives of the indexed value must have the same type, "
                f"but found {', '.join(sorted(aliases))}"
            )
        only_alias = next(iter(aliases))
        return primitives[only_alias]
