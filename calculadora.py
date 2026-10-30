"""Motor de la calculadora (y versión de consola). Uso: python calculadora.py  (vacío o 'salir' para terminar)

Admite + - * / // % ^ ** paréntesis, multiplicación implícita (2(3+4), 2pi), constantes pi, e, ans
y funciones sqrt cbrt sin cos tan asin acos atan ln log exp abs floor ceil round fact.
"""
import ast
import math
import operator as op
import re
import sys

OPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
       ast.FloorDiv: op.floordiv, ast.Mod: op.mod, ast.Pow: op.pow,
       ast.USub: op.neg, ast.UAdd: op.pos}
ERRORES = (ValueError, SyntaxError, ZeroDivisionError, OverflowError, TypeError)


def _fact(n):
    if n != int(n) or n < 0 or n > 500:
        raise ValueError("factorial solo de enteros entre 0 y 500")
    return math.factorial(int(n))


def _funciones(deg):
    a = math.radians if deg else (lambda x: x)
    b = math.degrees if deg else (lambda x: x)
    return {
        "sqrt": math.sqrt, "cbrt": lambda x: math.copysign(abs(x) ** (1 / 3), x),
        "sin": lambda x: math.sin(a(x)), "cos": lambda x: math.cos(a(x)), "tan": lambda x: math.tan(a(x)),
        "asin": lambda x: b(math.asin(x)), "acos": lambda x: b(math.acos(x)), "atan": lambda x: b(math.atan(x)),
        "ln": math.log, "log": math.log10, "exp": math.exp, "abs": abs,
        "floor": math.floor, "ceil": math.ceil, "round": round, "fact": _fact,
    }


def calcular(expr, ans=0, deg=False):
    texto = (expr.replace(",", ".").replace("×", "*").replace("÷", "/").replace("−", "-")
             .replace("^", "**").replace("π", "pi"))
    texto = re.sub(r"√\s*(\d+(?:\.\d+)?)", r"sqrt(\1)", texto).replace("√", "sqrt")  # √9 y √(9)
    texto = re.sub(r"(\d|\))\s*(?=[(a-zA-Z])", r"\1*", texto)  # 2(3+4), 2pi, )(
    texto = re.sub(r"\)\s*(?=\d)", ")*", texto)
    consts = {"pi": math.pi, "e": math.e, "ans": ans}
    funcs = _funciones(deg)

    def ev(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.Name) and n.id in consts:
            return consts[n.id]
        if isinstance(n, ast.BinOp) and type(n.op) in OPS:
            x, y = ev(n.left), ev(n.right)
            if isinstance(n.op, ast.Pow) and abs(y) > 1000:  # evita 9**9**9
                raise ValueError("exponente demasiado grande")
            return OPS[type(n.op)](x, y)
        if isinstance(n, ast.UnaryOp) and type(n.op) in OPS:
            return OPS[type(n.op)](ev(n.operand))
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in funcs
                and len(n.args) == 1 and not n.keywords):
            return funcs[n.func.id](ev(n.args[0]))
        raise ValueError("expresión no válida")

    r = ev(ast.parse(texto, mode="eval").body)
    if isinstance(r, complex) or (isinstance(r, float) and not math.isfinite(r)):
        raise ValueError("resultado no real")
    return r


def formatear(x):
    if isinstance(x, int):
        return str(x)
    if abs(x) < 1e-12:  # shortcut: sin(180°) da 1e-16, se muestra 0; sube si necesitas valores tan pequeños
        x = 0.0
    if x == int(x) and abs(x) < 1e15:
        return str(int(x))
    return "%.12g" % x


def test():
    casos = {
        "2+3*4": "14", "(1+2)**2": "9", "10/4": "2.5", "7,5*2": "15", "-3+5": "2", "2(3+4)": "14",
        "(2+1)(3+1)": "12", "2^10": "1024", "10%3": "1", "10//3": "3", "0.1+0.2": "0.3", "√9": "3",
        "sqrt(16)": "4", "cbrt(-27)": "-3", "fact(5)": "120", "ln(e)": "1", "log(1000)": "3",
        "2pi": "6.28318530718", "exp(0)": "1", "abs(-4)": "4", "15*1024*8/600": "204.8",
        "4.7*1024": "4812.8", "ans*2": "42",
    }
    for e, esperado in casos.items():
        assert formatear(calcular(e, ans=21)) == esperado, e
    assert formatear(calcular("sin(30)", deg=True)) == "0.5"
    assert formatear(calcular("cos(180)", deg=True)) == "-1"
    assert formatear(calcular("asin(1)", deg=True)) == "90"
    assert formatear(calcular("sin(180)", deg=True)) == "0"
    for malo in ("__import__('os')", "9**9**9", "1/0", "sqrt(-1)", "(-8)**0.5", "open('x')", "fact(1.5)", "2+", "abs()"):
        try:
            calcular(malo)
        except ERRORES:
            continue
        raise AssertionError(malo)
    print("ok")


if __name__ == "__main__":
    if "--test" in sys.argv:
        test()
        sys.exit()
    while (linea := input("> ").strip()) and linea != "salir":
        try:
            print(formatear(calcular(linea)))
        except ERRORES as e:
            print("error:", e)
