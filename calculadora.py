"""Calculadora de consola: + - * / // % ** y paréntesis. Uso: python calculadora.py  (vacío o 'salir' para terminar)"""
import ast
import operator as op
import sys

OPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
       ast.FloorDiv: op.floordiv, ast.Mod: op.mod, ast.Pow: op.pow,
       ast.USub: op.neg, ast.UAdd: op.pos}


def calcular(expr):
    def ev(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in OPS:
            a, b = ev(n.left), ev(n.right)
            if isinstance(n.op, ast.Pow) and abs(b) > 1000:  # evita 9**9**9
                raise ValueError("exponente demasiado grande")
            return OPS[type(n.op)](a, b)
        if isinstance(n, ast.UnaryOp) and type(n.op) in OPS:
            return OPS[type(n.op)](ev(n.operand))
        raise ValueError("expresión no válida")
    return ev(ast.parse(expr.replace(",", "."), mode="eval").body)


def test():
    assert calcular("2+3*4") == 14
    assert calcular("(1+2)**2") == 9
    assert calcular("10/4") == 2.5
    assert calcular("7,5*2") == 15
    assert calcular("-3+5") == 2
    for malo in ("__import__('os')", "9**9**9", "1/0"):
        try:
            calcular(malo)
        except (ValueError, ZeroDivisionError):
            continue
        raise AssertionError(malo)
    print("ok")


if __name__ == "__main__":
    if "--test" in sys.argv:
        test()
        sys.exit()
    while (linea := input("> ").strip()) and linea != "salir":
        try:
            print(calcular(linea))
        except (ValueError, SyntaxError, ZeroDivisionError) as e:
            print("error:", e)
