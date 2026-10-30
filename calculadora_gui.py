"""Calculadora científica con interfaz gráfica (tkinter). Uso: python calculadora_gui.py

Se puede escribir con el teclado (Enter = calcular, Esc = borrar) o con los botones.
Pestaña "Bases": pasa un número entre decimal, binario, octal y hexadecimal.
"""
import tkinter as tk
from tkinter import ttk

from calculadora import ERRORES, calcular, formatear

BG, PANEL, KEY, OP, ACC, FG, DIM, RED = "#1e1e2e", "#181825", "#313244", "#45475a", "#89b4fa", "#cdd6f4", "#7f849c", "#f38ba8"
FONT = "Segoe UI"
COLORES = {"key": (KEY, FG), "op": (OP, FG), "acc": (ACC, "#11111b"), "danger": ("#5b3b4a", RED)}

# (texto del botón, qué hace o inserta, estilo)
FILAS = [
    [("DEG", "deg", "op"), ("sin", "sin(", "op"), ("cos", "cos(", "op"), ("tan", "tan(", "op"), ("π", "π", "op"), ("e", "e", "op")],
    [("ln", "ln(", "op"), ("log", "log(", "op"), ("√", "√(", "op"), ("x²", "^2", "op"), ("xʸ", "^", "op"), ("n!", "fact(", "op")],
    [("(", "(", "op"), (")", ")", "op"), ("mod", "%", "op"), ("Ans", "ans", "op"), ("C", "clear", "danger"), ("⌫", "back", "danger")],
    [("7", "7", "key"), ("8", "8", "key"), ("9", "9", "key"), ("÷", "÷", "op"), ("asin", "asin(", "op"), ("acos", "acos(", "op")],
    [("4", "4", "key"), ("5", "5", "key"), ("6", "6", "key"), ("×", "×", "op"), ("atan", "atan(", "op"), ("exp", "exp(", "op")],
    [("1", "1", "key"), ("2", "2", "key"), ("3", "3", "key"), ("−", "-", "op"), ("abs", "abs(", "op"), ("cbrt", "cbrt(", "op")],
    [("0", "0", "key"), (".", ".", "key"), ("±", "neg", "op"), ("+", "+", "op"), ("=", "eval", "acc")],
]
BASES = {"Decimal": 10, "Binario": 2, "Octal": 8, "Hexadecimal": 16}


class App:
    def __init__(self, root):
        self.root, self.deg, self.ans, self.hist = root, True, 0, []
        root.title("Calculadora")
        root.geometry("820x640")
        root.minsize(720, 600)
        root.configure(bg=BG)
        st = ttk.Style()
        st.theme_use("clam")
        st.configure("TNotebook", background=BG, borderwidth=0)
        st.configure("TNotebook.Tab", background=KEY, foreground=FG, padding=(18, 8), font=(FONT, 11, "bold"), borderwidth=0)
        st.map("TNotebook.Tab", background=[("selected", ACC)], foreground=[("selected", "#11111b")])
        st.configure("TCombobox", fieldbackground=PANEL, background=KEY, foreground=FG, arrowcolor=FG,
                     selectbackground=PANEL, selectforeground=FG)
        st.map("TCombobox", fieldbackground=[("readonly", PANEL)], foreground=[("readonly", FG)],
               selectbackground=[("readonly", PANEL)], selectforeground=[("readonly", FG)])
        root.option_add("*TCombobox*Listbox.background", PANEL)
        root.option_add("*TCombobox*Listbox.foreground", FG)
        root.option_add("*TCombobox*Listbox.selectBackground", ACC)
        root.option_add("*TCombobox*Listbox.selectForeground", "#11111b")
        nb = ttk.Notebook(root)
        nb.pack(fill="both", expand=True, padx=10, pady=10)
        self.tab_calc = tk.Frame(nb, bg=BG)
        self.tab_bases = tk.Frame(nb, bg=BG)
        nb.add(self.tab_calc, text="Calculadora")
        nb.add(self.tab_bases, text="Bases")
        self.build_calc()
        self.build_bases()
        self.entry.focus_set()

    # ---------- calculadora ----------
    def build_calc(self):
        izq = tk.Frame(self.tab_calc, bg=BG)
        izq.pack(side="left", fill="both", expand=True, padx=(0, 8), pady=8)
        der = tk.Frame(self.tab_calc, bg=BG, width=230)
        der.pack(side="right", fill="y", pady=8)
        der.pack_propagate(False)

        self.var = tk.StringVar()
        self.entry = tk.Entry(izq, textvariable=self.var, font=(FONT, 26), bg=PANEL, fg=FG, insertbackground=ACC,
                              relief="flat", justify="right", highlightthickness=2, highlightbackground=KEY,
                              highlightcolor=ACC)
        self.entry.pack(fill="x", ipady=10)
        self.res = tk.Label(izq, text="", font=(FONT, 20, "bold"), bg=BG, fg=ACC, anchor="e")
        self.res.pack(fill="x", pady=(4, 6))
        self.entry.bind("<Return>", lambda e: self.press("eval"))
        self.entry.bind("<KP_Enter>", lambda e: self.press("eval"))
        self.entry.bind("<Escape>", lambda e: self.press("clear"))
        self.entry.bind("<KeyRelease>", lambda e: self.preview())

        grid = tk.Frame(izq, bg=BG)
        grid.pack(fill="both", expand=True)
        for c in range(6):
            grid.columnconfigure(c, weight=1, uniform="c")
        for r, fila in enumerate(FILAS):
            grid.rowconfigure(r, weight=1)
            for c, (txt, accion, estilo) in enumerate(fila):
                bg, fg = COLORES[estilo]
                b = tk.Button(grid, text=txt, font=(FONT, 14, "bold"), bg=bg, fg=fg, activebackground=ACC,
                              activeforeground="#11111b", relief="flat", bd=0, cursor="hand2",
                              command=lambda a=accion: self.press(a))
                b.grid(row=r, column=c, columnspan=2 if txt == "=" else 1, sticky="nsew", padx=2, pady=2)
                b.bind("<Enter>", lambda e, w=b: w.configure(bg=ACC, fg="#11111b"))
                b.bind("<Leave>", lambda e, w=b, x=(bg, fg): w.configure(bg=x[0], fg=x[1]))
                if accion == "deg":
                    self.btn_deg = b

        tk.Label(der, text="Historial", font=(FONT, 13, "bold"), bg=BG, fg=FG, anchor="w").pack(fill="x")
        caja = tk.Frame(der, bg=PANEL)
        caja.pack(fill="both", expand=True, pady=6)
        sb = tk.Scrollbar(caja)
        sb.pack(side="right", fill="y")
        self.lista = tk.Listbox(caja, bg=PANEL, fg=FG, selectbackground=ACC, selectforeground="#11111b",
                                font=("Consolas", 11), relief="flat", highlightthickness=0, activestyle="none",
                                yscrollcommand=sb.set)
        self.lista.pack(fill="both", expand=True)
        sb.config(command=self.lista.yview)
        self.lista.bind("<<ListboxSelect>>", self.usar_historial)
        fila = tk.Frame(der, bg=BG)
        fila.pack(fill="x")
        for txt, cmd in (("Copiar resultado", self.copiar), ("Borrar historial", self.borrar_historial)):
            tk.Button(fila, text=txt, command=cmd, bg=KEY, fg=FG, relief="flat", bd=0, font=(FONT, 10),
                      cursor="hand2").pack(side="left", fill="x", expand=True, padx=2, ipady=6)
        tk.Label(der, text="Clic en una línea del historial\npara recuperar la cuenta.", font=(FONT, 9), bg=BG,
                 fg=DIM, justify="left").pack(anchor="w", pady=(8, 0))

    def press(self, accion):
        e = self.entry
        if accion == "clear":
            self.var.set("")
            self.res.config(text="")
        elif accion == "back":
            if e.selection_present():
                e.delete("sel.first", "sel.last")
            elif e.index(tk.INSERT) > 0:
                e.delete(e.index(tk.INSERT) - 1)
        elif accion == "deg":
            self.deg = not self.deg
            self.btn_deg.config(text="DEG" if self.deg else "RAD")
        elif accion == "neg":
            t = self.var.get()
            self.var.set(t[2:-1] if t.startswith("-(") and t.endswith(")") else "-(" + t + ")")
            e.icursor("end")
        elif accion == "eval":
            self.evaluar()
            return
        else:
            if e.selection_present():
                e.delete("sel.first", "sel.last")
            e.insert(e.index(tk.INSERT), accion)
        e.focus_set()
        self.preview()

    def preview(self):
        t = self.var.get().strip()
        try:
            self.res.config(text="= " + formatear(calcular(t, self.ans, self.deg)) if t else "", fg=ACC)
        except ERRORES:
            self.res.config(text="")

    def evaluar(self):
        t = self.var.get().strip()
        if not t:
            return
        try:
            r = calcular(t, self.ans, self.deg)
        except ZeroDivisionError:
            self.res.config(text="Error: división entre 0", fg=RED)
            return
        except ERRORES as ex:
            msg = str(ex) if isinstance(ex, ValueError) else "expresión no válida"
            self.res.config(text="Error: " + msg, fg=RED)
            return
        s = formatear(r)
        self.hist.append((t, s))
        self.lista.insert("end", "%s = %s" % (t, s))
        self.lista.see("end")
        self.ans = r
        self.var.set(s)
        self.entry.icursor("end")
        self.res.config(text="", fg=ACC)

    def usar_historial(self, _):
        sel = self.lista.curselection()
        if sel:
            self.var.set(self.hist[sel[0]][0])
            self.entry.focus_set()
            self.entry.icursor("end")
            self.preview()

    def copiar(self):
        if self.hist:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.hist[-1][1])

    def borrar_historial(self):
        self.hist.clear()
        self.lista.delete(0, "end")

    # ---------- bases ----------
    def build_bases(self):
        f = tk.Frame(self.tab_bases, bg=BG)
        f.pack(fill="both", expand=True, padx=24, pady=20)
        tk.Label(f, text="Convertir entre bases", font=(FONT, 18, "bold"), bg=BG, fg=FG).pack(anchor="w")
        tk.Label(f, text="Escribe el número, elige en qué base está y verás las demás al instante.",
                 font=(FONT, 11), bg=BG, fg=DIM).pack(anchor="w", pady=(2, 14))
        fila = tk.Frame(f, bg=BG)
        fila.pack(fill="x")
        self.bvar = tk.StringVar()
        self.bbase = tk.StringVar(value="Decimal")
        e = tk.Entry(fila, textvariable=self.bvar, font=("Consolas", 22), bg=PANEL, fg=FG, insertbackground=ACC,
                     relief="flat", highlightthickness=2, highlightbackground=KEY, highlightcolor=ACC)
        e.pack(side="left", fill="x", expand=True, ipady=8)
        ttk.Combobox(fila, textvariable=self.bbase, values=list(BASES), state="readonly", width=14,
                     font=(FONT, 12)).pack(side="left", padx=(10, 0), ipady=6)
        self.bout = {}
        for nombre in BASES:
            r = tk.Frame(f, bg=PANEL)
            r.pack(fill="x", pady=5)
            tk.Label(r, text=nombre, font=(FONT, 12, "bold"), bg=PANEL, fg=ACC, width=13, anchor="w").pack(side="left", padx=10, pady=10)
            self.bout[nombre] = tk.Label(r, text="", font=("Consolas", 18), bg=PANEL, fg=FG, anchor="w")
            self.bout[nombre].pack(side="left", fill="x", expand=True)
        self.bvar.trace_add("write", lambda *_: self.convertir())
        self.bbase.trace_add("write", lambda *_: self.convertir())

    def convertir(self):
        try:
            n = int(self.bvar.get().strip().replace(" ", ""), BASES[self.bbase.get()])
        except ValueError:
            n = None
        for nombre, lab in self.bout.items():
            if n is None:
                lab.config(text="—" if self.bvar.get().strip() else "")
                continue
            s = {10: str, 2: lambda x: format(abs(x), "b"), 8: lambda x: format(abs(x), "o"),
                 16: lambda x: format(abs(x), "X")}[BASES[nombre]](n)
            if BASES[nombre] == 2:
                s = s.zfill(-(-len(s) // 4) * 4)
                s = " ".join(s[i:i + 4] for i in range(0, len(s), 4))
            if BASES[nombre] != 10 and n < 0:
                s = "-" + s
            lab.config(text=s)


def main():
    try:  # nítido en pantallas con escala alta
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
