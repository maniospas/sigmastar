from sigmastar.parser.types import Primitive
from sigmastar.parser.tokenize import Token
from sigmastar.parser.function import Function
from typing import get_type_hints
import inspect
import importlib

primitives = {
    "N": Primitive("N", "int"),
    "R": Primitive("R", "float"),
    "S": Primitive("R", "str"),
    "B": Primitive("B", "bool"),
    "A": Primitive("A", "list"),
    "M": Primitive("M", "dict"),
}

type_map = {
    float: primitives["R"],
    bool:  primitives["B"],
    str:  primitives["S"],
    int:  primitives["N"],
}

def make_builtin(name: str, args: dict, ret):
    return Function(Token(name, "__builtins__", 0, 0), args, ret, None)

builtins = {}

import importlib, inspect
from typing import get_type_hints

def load_python(alias: str, name: str):
    ext = importlib.import_module(name)
    original_names = []
    if alias == "*": alias = ""
    else: alias += "__"
    for func_name, func in inspect.getmembers(ext, inspect.isfunction):
        if func_name.startswith("__"):
            continue
        alias_name = f"{alias}{func_name}"
        original_names.append(func_name+" as "+alias_name)
        hints = get_type_hints(func)
        ret_py_type = hints.pop('return', None)
        args = {arg: type_map[hints[arg]] for arg in hints if hints[arg] in type_map}
        ret = type_map[ret_py_type]
        builtins[alias_name] = make_builtin(alias_name, args, ret)

    if not original_names: 
        return ""
    return f"from {name} import {', '.join(original_names)}\n"
