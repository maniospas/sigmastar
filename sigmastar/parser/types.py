from sigmastar.parser.tokenize import Token
import re


class Primitive:
    def __init__(self, alias: str, actual: str):
        assert len(alias)==1, "Primitives can only be one character each"
        self.alias = str(alias)
        self.actual = str(actual)
        self.is_primitive = True

    def pretty(self):
        return self.alias+" ("+self.actual+")"

class Type:
    def __init__(self, token: Token, primitives: dict[str, "Primitive"]):
        assert isinstance(token, Token)
        self.alias = str(token)
        pattern = re.compile(r"([A-Za-z])(\d*)")
        pos = 0
        self.primitives = []
        for m in pattern.finditer(self.alias):
            if m.start() != pos:
                token.error(f"Invalid syntax near '{self.alias[pos:m.start()]}'")
            pos = m.end()
            letter, count = m.groups()
            if letter not in primitives:
                token.error(f"Not found primitive: {letter}")
            if count:
                try:
                    n = int(count)
                except ValueError:
                    token.error(f"Invalid number after {letter}: {count}")
                if n <= 0:
                    token.error(f"Repetition count for {letter} must be positive")
            else:
                n = 1
            self.primitives.extend([primitives[letter]] * n)
        if pos != len(self.alias):
            token.error( f"Unexpected trailing characters: {self.alias[pos:]}")
        if not self.primitives:
            token.error("Cannot declare an empty type")
        self.is_primitive = False
        normalized_alias = ""
        for primitive in self.primitives:
            normalized_alias += primitive.alias
        self.alias = normalized_alias

    def pretty(self):
        return self.alias

def type(token: Token, primitives: dict[str, "Primitive"]):
    t = Type(token, primitives)
    if not t.primitives:
        token.error("Types must consist of at least one primitive")
    if len(t.primitives) == 1:
        return t.primitives[0]
    return t
