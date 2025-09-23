import re
import bisect


class Token:
    def __init__(self, name: str, path: str, row: int, col: int):
        self.name = name
        self.path = path
        self.row = row
        self.col = col

    def __str__(self):
        return self.name

    def error(self, message):
        with open(self.path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if not (1 <= self.row <= len(lines)):
            print(f"{self.path}:{self.row}:{self.col}: {self.name}")
        line = lines[self.row - 1].rstrip("\n")
        indicator = "\033[31m " * (self.col - 1) + "~" * (len(self.name)-1) + "> " + message + "\033[0m"
        print(f"at {self.path}:{self.row}:{self.col}\n{line}\n{indicator}")
        exit(1)

def tokenize(path: str):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    line_starts = [0]
    for m in re.finditer(r"\n", text):
        line_starts.append(m.end())
    pattern = (
        r"\d+\.\d+(?:[eE][+-]?\d+)?|"     # 12.34 or 12.34e-5
        r"\d+\.(?:[eE][+-]?\d+)?|"        # 42. or 42.e+1
        r"\.\d+(?:[eE][+-]?\d+)?|"        # .5 or .5e3
        r"\d+(?:[eE][+-]?\d+)|"           # 3e8
        r"\w+|[^\w\s]"
    )
    tokens: list[Token] = []
    for m in re.finditer(pattern, text):
        start = m.start()
        line_idx = bisect.bisect_right(line_starts, start) - 1
        row = line_idx + 1
        col = start - line_starts[line_idx] + 1
        tokens.append(Token(m.group(), path, row, col))

    return tokens
