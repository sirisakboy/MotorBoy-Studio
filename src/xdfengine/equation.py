"""Safe evaluator for TunerPro-style MATH equations (no eval/exec).

Supports + - * / // % ** << >> & | ^ ~, parentheses, numbers, the variable
(default ``X``) and a few functions. Includes numeric inverse for writing.
"""
import ast
import math
import operator as op

_BIN = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv, ast.Mod: op.mod, ast.Pow: op.pow,
    ast.LShift: lambda a, b: int(a) << int(b), ast.RShift: lambda a, b: int(a) >> int(b),
    ast.BitAnd: lambda a, b: int(a) & int(b), ast.BitOr: lambda a, b: int(a) | int(b),
    ast.BitXor: lambda a, b: int(a) ^ int(b),
}
_UN = {ast.USub: op.neg, ast.UAdd: op.pos, ast.Invert: lambda a: ~int(a)}
_FUNCS = {"abs": abs, "min": min, "max": max, "round": round, "sqrt": math.sqrt,
          "log": math.log, "log10": math.log10, "exp": math.exp, "pow": pow}


class EquationError(ValueError):
    pass


def _compile(node, var):
    if isinstance(node, ast.Expression):
        return _compile(node.body, var)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        v = node.value
        return lambda x: v
    if isinstance(node, ast.Name):
        if node.id.upper() == var.upper():
            return lambda x: x
        raise EquationError(f"unknown name {node.id!r}")
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN:
        f, l, r = _BIN[type(node.op)], _compile(node.left, var), _compile(node.right, var)
        return lambda x: f(l(x), r(x))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UN:
        f, o = _UN[type(node.op)], _compile(node.operand, var)
        return lambda x: f(o(x))
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id.lower() in _FUNCS and not node.keywords):
        f = _FUNCS[node.func.id.lower()]
        args = [_compile(a, var) for a in node.args]
        return lambda x: f(*[a(x) for a in args])
    raise EquationError(f"unsupported expression element: {type(node).__name__}")


class Equation:
    def __init__(self, text="X", var="X", raw_bits=16, signed=False):
        self.text = (text or "X").strip()
        try:
            self._f = _compile(ast.parse(self.text, mode="eval"), var)
        except SyntaxError as e:
            raise EquationError(f"bad equation {text!r}: {e}") from e
        self.raw_bits, self.signed = raw_bits, signed
        self._lin = self._detect_linear()
        self._table = None

    def __call__(self, x):
        return self._f(x)

    def _detect_linear(self):
        try:
            a, b, c = self._f(0), self._f(1), self._f(2)
        except Exception:
            return None
        slope = b - a
        if abs(c - 2 * b + a) < 1e-9 and abs(slope) > 1e-12:
            return a, slope
        return None

    @property
    def is_identity(self):
        return self._lin is not None and abs(self._lin[0]) < 1e-12 and abs(self._lin[1] - 1) < 1e-12

    def _raw_range(self):
        n = self.raw_bits
        return (-(1 << (n - 1)), (1 << (n - 1)) - 1) if self.signed else (0, (1 << n) - 1)

    def inverse(self, y, clamp=False):
        """Return the integer raw value whose scaled value is closest to y."""
        lo, hi = self._raw_range()
        if self._lin:
            a, s = self._lin
            raw = round((y - a) / s)
        else:
            if self.raw_bits > 16:
                raise EquationError("non-linear equation cannot be inverted for >16-bit data")
            if self._table is None:
                self._table = sorted((self._f(r), r) for r in range(lo, hi + 1))
            raw = min(self._table, key=lambda t: abs(t[0] - y))[1]
        if raw < lo or raw > hi:
            if not clamp:
                raise ValueError(f"value {y} needs raw {raw}, outside [{lo}, {hi}]")
            raw = max(lo, min(hi, raw))
        return int(raw)
