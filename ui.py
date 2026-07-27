"""
ui.py
Windows 11-style UI for the Advanced Scientific Calculator, built with
CustomTkinter. Tabs: Calculator, Graphing, Converter, Programmer,
Percentage & Tip. Includes history, dark/light theme, memory buttons,
and keyboard shortcuts (Calculator tab only).
"""

import random
import tkinter as tk

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from calculator import Calculator, CalculatorError
from history import HistoryManager
from theme import get_theme
from converter import CATEGORIES, convert, units_for, ConverterError
from baseconv import parse_int, all_bases, apply_operation, BaseConvError

THEME_ORDER = ["Dark", "Light", "Cartoon"]
NEXT_THEME_LABEL = {"Dark": "☀️ Light", "Light": "🎪 Cartoon", "Cartoon": "🌙 Dark"}


class CalculatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.calc = Calculator()
        self.history_mgr = HistoryManager()
        self.memory_value = 0.0
        self.mode = "Dark"
        self.colors = get_theme(self.mode)
        self.current_tab = "Calculator"

        self.title("Advanced Scientific Calculator")
        self.geometry("980x680")
        self.minsize(820, 560)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.configure(fg_color=self.colors["bg"])

        self._init_state_vars()
        self._build_layout()
        self._bind_keys()
        self._refresh_history_panel()
        self._plot_graph()

    # ------------------------------------------------------------------
    # Persistent state (survives theme-toggle rebuilds)
    # ------------------------------------------------------------------
    def _init_state_vars(self):
        # Calculator
        self.expr_var = ctk.StringVar(value="")
        self.result_var = ctk.StringVar(value="0")

        # Graphing
        self.graph_expr_var = ctk.StringVar(value="sin(x)")
        self.graph_xmin_var = ctk.StringVar(value="-10")
        self.graph_xmax_var = ctk.StringVar(value="10")
        self.graph_error_var = ctk.StringVar(value="")

        # Converter
        self.conv_category_var = ctk.StringVar(value="Length")
        self.conv_from_var = ctk.StringVar(value="Meters")
        self.conv_to_var = ctk.StringVar(value="Feet")
        self.conv_value_var = ctk.StringVar(value="1")
        self.conv_result_var = ctk.StringVar(value="")

        # Programmer
        self.prog_base_var = ctk.StringVar(value="DEC")
        self.prog_input_var = ctk.StringVar(value="255")
        self.prog_bin_var = ctk.StringVar(value="")
        self.prog_oct_var = ctk.StringVar(value="")
        self.prog_dec_var = ctk.StringVar(value="")
        self.prog_hex_var = ctk.StringVar(value="")
        self.prog_opA_var = ctk.StringVar(value="12")
        self.prog_opB_var = ctk.StringVar(value="10")
        self.prog_op_var = ctk.StringVar(value="AND")
        self.prog_result_var = ctk.StringVar(value="")

        # Percentage
        self.pct_value_var = ctk.StringVar(value="50")
        self.pct_percent_var = ctk.StringVar(value="20")
        self.pct_result_var = ctk.StringVar(value="")

        # Tip
        self.tip_bill_var = ctk.StringVar(value="100")
        self.tip_percent_var = ctk.StringVar(value="15")
        self.tip_people_var = ctk.StringVar(value="1")
        self.tip_amount_var = ctk.StringVar(value="")
        self.tip_total_var = ctk.StringVar(value="")
        self.tip_per_person_var = ctk.StringVar(value="")

    # ------------------------------------------------------------------
    # Top-level layout
    # ------------------------------------------------------------------
    def _build_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_top_bar()

        self.tabview = ctk.CTkTabview(
            self, fg_color=self.colors["bg"],
            segmented_button_fg_color=self.colors["history_bg"],
            segmented_button_selected_color=self.colors["accent_bg"],
            segmented_button_selected_hover_color=self.colors["accent_hover"],
            segmented_button_unselected_color=self.colors["btn_bg"],
        )
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

        for name in ["Calculator", "Graphing", "Converter", "Programmer", "Percentage & Tip"]:
            self.tabview.add(name)

        self._build_calculator_tab(self.tabview.tab("Calculator"))
        self._build_graphing_tab(self.tabview.tab("Graphing"))
        self._build_converter_tab(self.tabview.tab("Converter"))
        self._build_programmer_tab(self.tabview.tab("Programmer"))
        self._build_percentage_tab(self.tabview.tab("Percentage & Tip"))

        self.tabview.set(self.current_tab)

    def _build_top_bar(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))
        bar.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            bar, text="Advanced Scientific Calculator",
            font=ctk.CTkFont(family=self.colors.get("font_family", "Segoe UI"), size=18, weight="bold"),
            text_color=self.colors["display_fg"],
        )
        title.grid(row=0, column=0, sticky="w")

        theme_label = NEXT_THEME_LABEL[self.mode]
        self.theme_btn = ctk.CTkButton(
            bar, text=theme_label, width=90, command=self._toggle_theme,
            fg_color=self.colors["accent_bg"], hover_color=self.colors["accent_hover"],
            text_color="#ffffff",
        )
        self.theme_btn.grid(row=0, column=1, sticky="e", padx=4)

    # ==================================================================
    # TAB 1: Calculator
    # ==================================================================
    def _build_calculator_tab(self, tab):
        tab.grid_columnconfigure(0, weight=3)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        left_frame = ctk.CTkFrame(tab, fg_color=self.colors["bg"])
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        self._build_display(left_frame)
        self._build_keypad(left_frame)

        history_frame = ctk.CTkFrame(tab, fg_color=self.colors["history_bg"], corner_radius=12)
        history_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        self._build_history_panel(history_frame)

    def _build_display(self, parent):
        display_frame = ctk.CTkFrame(
            parent, fg_color=self.colors["display_bg"],
            corner_radius=self.colors.get("corner_radius", 10),
            border_width=self.colors.get("border_width", 0),
            border_color=self.colors.get("border_color", self.colors["display_bg"]),
        )
        display_frame.grid(row=0, column=0, sticky="new", pady=(0, 10))
        display_frame.grid_columnconfigure(0, weight=1)
        self.display_frame = display_frame

        font_family = self.colors.get("font_family", "Segoe UI")

        self.expr_label = ctk.CTkLabel(
            display_frame, textvariable=self.expr_var,
            font=ctk.CTkFont(family=font_family, size=16), anchor="e",
            text_color=self.colors["display_fg"],
        )
        self.expr_label.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 0))

        self.result_label = ctk.CTkLabel(
            display_frame, textvariable=self.result_var,
            font=ctk.CTkFont(family=font_family, size=40, weight="bold"), anchor="e",
            text_color=self.colors["display_fg"],
        )
        self.result_label.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 14))

    def _build_keypad(self, parent):
        keypad = ctk.CTkFrame(parent, fg_color="transparent")
        keypad.grid(row=1, column=0, sticky="nsew")
        parent.grid_rowconfigure(1, weight=1)

        for i in range(8):
            keypad.grid_columnconfigure(i, weight=1)
        for i in range(5):
            keypad.grid_rowconfigure(i, weight=1)

        buttons = [
            ("MC", 0, 0, 1, "mem"), ("MR", 0, 1, 1, "mem"), ("M+", 0, 2, 1, "mem"), ("M-", 0, 3, 1, "mem"),
            ("sin", 0, 4, 1, "func"), ("cos", 0, 5, 1, "func"), ("tan", 0, 6, 1, "func"), ("C", 0, 7, 1, "op"),

            ("asin", 1, 4, 1, "func"), ("acos", 1, 5, 1, "func"), ("atan", 1, 6, 1, "func"), ("⌫", 1, 7, 1, "op"),
            ("7", 1, 0, 1, "num"), ("8", 1, 1, 1, "num"), ("9", 1, 2, 1, "num"), ("÷", 1, 3, 1, "op"),

            ("4", 2, 0, 1, "num"), ("5", 2, 1, 1, "num"), ("6", 2, 2, 1, "num"), ("×", 2, 3, 1, "op"),
            ("log", 2, 4, 1, "func"), ("ln", 2, 5, 1, "func"), ("√", 2, 6, 1, "func"), ("(", 2, 7, 1, "op"),

            ("1", 3, 0, 1, "num"), ("2", 3, 1, 1, "num"), ("3", 3, 2, 1, "num"), ("-", 3, 3, 1, "op"),
            ("x²", 3, 4, 1, "func"), ("x^y", 3, 5, 1, "func"), ("n!", 3, 6, 1, "func"), (")", 3, 7, 1, "op"),

            ("0", 4, 0, 1, "num"), (".", 4, 1, 1, "num"), ("π", 4, 2, 1, "num"), ("+", 4, 3, 1, "op"),
            ("e", 4, 4, 1, "num"), ("%", 4, 5, 1, "op"), ("±", 4, 6, 1, "op"), ("=", 4, 7, 1, "accent"),
        ]

        for (label, row, col, span, kind) in buttons:
            btn = self._make_button(keypad, label, kind)
            btn.grid(row=row, column=col, columnspan=span, sticky="nsew", padx=4, pady=4)

    def _make_button(self, parent, label, kind):
        if kind == "num":
            fg, hover = self.colors["btn_bg"], self.colors["btn_hover"]
            text_color = self.colors["btn_fg"]
        elif kind == "accent":
            fg, hover = self.colors["accent_bg"], self.colors["accent_hover"]
            text_color = "#ffffff"
        else:
            fg, hover = self.colors["op_btn_bg"], self.colors["op_btn_hover"]
            text_color = self.colors["btn_fg"]

        font_family = self.colors.get("font_family", "Segoe UI")
        btn = ctk.CTkButton(
            parent, text=label, fg_color=fg, hover_color=hover,
            text_color=text_color, text_color_disabled=text_color,
            corner_radius=self.colors.get("corner_radius", 10),
            border_width=self.colors.get("border_width", 0),
            border_color=self.colors.get("border_color", fg),
            font=ctk.CTkFont(family=font_family, size=15, weight="bold"),
            command=lambda l=label: self._on_button(l),
        )
        return btn

    def _build_history_panel(self, parent):
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 4))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="History", font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["history_fg"],
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            header, text="Clear", width=60, command=self._clear_history,
            fg_color=self.colors["accent_bg"], hover_color=self.colors["accent_hover"],
            text_color="#ffffff",
        ).grid(row=0, column=1, sticky="e")

        self.history_scroll = ctk.CTkScrollableFrame(parent, fg_color=self.colors["history_bg"])
        self.history_scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 12))
        self.history_scroll.grid_columnconfigure(0, weight=1)

    def _on_button(self, label):
        actions = {
            "=": self._calculate, "C": self._clear_entry, "⌫": self._backspace,
            "±": self._negate, "MC": self._memory_clear, "MR": self._memory_recall,
            "M+": self._memory_add, "M-": self._memory_subtract,
        }
        if label in actions:
            actions[label]()
            return

        insert_map = {
            "×": "*", "÷": "/", "√": "sqrt(", "x²": "**2", "x^y": "**",
            "n!": "fact(", "sin": "sin(", "cos": "cos(", "tan": "tan(",
            "asin": "asin(", "acos": "acos(", "atan": "atan(",
            "log": "log(", "ln": "ln(", "%": "/100",
        }
        text = insert_map.get(label, label)
        self.expr_var.set(self.expr_var.get() + text)

    def _calculate(self):
        expr = self.expr_var.get()
        try:
            result = self.calc.evaluate(expr)
            display_result = self._format_result(result)
            self.result_var.set(display_result)
            self.history_mgr.save(expr, display_result)
            self._refresh_history_panel()
            if self.mode == "Cartoon":
                self._celebrate()
        except CalculatorError as e:
            self.result_var.set(f"Error: {e}")

    @staticmethod
    def _format_result(value):
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        return str(value)

    def _clear_entry(self):
        self.expr_var.set("")
        self.result_var.set("0")

    def _backspace(self):
        self.expr_var.set(self.expr_var.get()[:-1])

    def _negate(self):
        expr = self.expr_var.get()
        if expr.startswith("-"):
            self.expr_var.set(expr[1:])
        else:
            self.expr_var.set("-" + expr)

    def _memory_clear(self):
        self.memory_value = 0.0

    def _memory_recall(self):
        self.expr_var.set(self.expr_var.get() + str(self.memory_value))

    def _memory_add(self):
        try:
            self.memory_value += self.calc.evaluate(self.expr_var.get() or self.result_var.get())
        except CalculatorError:
            pass

    def _memory_subtract(self):
        try:
            self.memory_value -= self.calc.evaluate(self.expr_var.get() or self.result_var.get())
        except CalculatorError:
            pass

    def _clear_history(self):
        self.history_mgr.clear()
        self._refresh_history_panel()

    def _refresh_history_panel(self):
        for widget in self.history_scroll.winfo_children():
            widget.destroy()

        entries = list(reversed(self.history_mgr.load()))
        for i, entry in enumerate(entries):
            row = ctk.CTkFrame(self.history_scroll, fg_color="transparent")
            row.grid(row=i, column=0, sticky="ew", pady=2)
            row.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                row, text=f"{entry['expression']} = {entry['result']}",
                text_color=self.colors["history_fg"], anchor="w",
                font=ctk.CTkFont(size=13),
            ).grid(row=0, column=0, sticky="ew")

            row.bind("<Button-1>", lambda e, r=entry["result"]: self._use_history(r))

    def _use_history(self, result):
        self.expr_var.set(str(result))

    # ------------------------------------------------------------------
    # Cartoon-theme celebration effects (pop bounce + confetti burst)
    # ------------------------------------------------------------------
    def _celebrate(self):
        self._pop_result_label()
        self._spawn_confetti()

    def _pop_result_label(self):
        font_family = self.colors.get("font_family", "Segoe UI")
        big_font = ctk.CTkFont(family=font_family, size=52, weight="bold")
        normal_font = ctk.CTkFont(family=font_family, size=40, weight="bold")
        self._safe_configure(self.result_label, font=big_font)
        self.after(160, lambda: self._safe_configure(self.result_label, font=normal_font))

    @staticmethod
    def _safe_configure(widget, **kwargs):
        try:
            widget.configure(**kwargs)
        except tk.TclError:
            pass

    def _spawn_confetti(self):
        colors = self.colors.get("confetti_colors", ["#ff6b6b", "#ffd93d", "#4ea8de"])
        try:
            width = self.display_frame.winfo_width() or 400
            height = self.display_frame.winfo_height() or 120
        except tk.TclError:
            return

        canvas = tk.Canvas(
            self.display_frame, width=width, height=height,
            highlightthickness=0, bg=self.colors["display_bg"],
        )
        canvas.place(x=0, y=0)

        particles = []
        for _ in range(18):
            x = random.randint(0, max(width - 12, 1))
            y = random.randint(-40, 0)
            size = random.randint(6, 12)
            color = random.choice(colors)
            pid = canvas.create_oval(x, y, x + size, y + size, fill=color, outline="")
            vy = random.uniform(3, 6)
            particles.append((pid, vy))

        state = {"frame": 0}

        def animate():
            state["frame"] += 1
            try:
                for pid, vy in particles:
                    canvas.move(pid, 0, vy)
            except tk.TclError:
                return
            if state["frame"] < 20:
                self.after(35, animate)
            else:
                try:
                    canvas.destroy()
                except tk.TclError:
                    pass

        animate()

    # ==================================================================
    # TAB 2: Graphing
    # ==================================================================
    def _build_graphing_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        controls = ctk.CTkFrame(tab, fg_color="transparent")
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(controls, text="f(x) =", text_color=self.colors["display_fg"]).grid(
            row=0, column=0, padx=(0, 6)
        )
        expr_entry = ctk.CTkEntry(controls, textvariable=self.graph_expr_var)
        expr_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        ctk.CTkLabel(controls, text="x min", text_color=self.colors["display_fg"]).grid(row=0, column=2, padx=(0, 4))
        ctk.CTkEntry(controls, textvariable=self.graph_xmin_var, width=70).grid(row=0, column=3, padx=(0, 10))

        ctk.CTkLabel(controls, text="x max", text_color=self.colors["display_fg"]).grid(row=0, column=4, padx=(0, 4))
        ctk.CTkEntry(controls, textvariable=self.graph_xmax_var, width=70).grid(row=0, column=5, padx=(0, 10))

        ctk.CTkButton(
            controls, text="Plot", command=self._plot_graph,
            fg_color=self.colors["accent_bg"], hover_color=self.colors["accent_hover"],
            text_color="#ffffff",
        ).grid(row=0, column=6)

        ctk.CTkLabel(
            tab, textvariable=self.graph_error_var, text_color="#e05555",
            font=ctk.CTkFont(size=12),
        ).grid(row=2, column=0, sticky="w", pady=(4, 0))

        self.graph_container = ctk.CTkFrame(tab, fg_color=self.colors["display_bg"], corner_radius=12)
        self.graph_container.grid(row=1, column=0, sticky="nsew")
        self.graph_container.grid_columnconfigure(0, weight=1)
        self.graph_container.grid_rowconfigure(0, weight=1)

    def _plot_graph(self):
        self.graph_error_var.set("")
        try:
            xmin = float(self.graph_xmin_var.get())
            xmax = float(self.graph_xmax_var.get())
        except ValueError:
            self.graph_error_var.set("x min / x max must be numbers")
            return
        if xmin >= xmax:
            self.graph_error_var.set("x min must be less than x max")
            return

        expr = self.graph_expr_var.get().strip() or "x"
        n_points = 400
        xs, ys = [], []
        step = (xmax - xmin) / (n_points - 1)
        for i in range(n_points):
            x = xmin + i * step
            try:
                y = self.calc.evaluate_at(expr, "x", x)
                xs.append(x)
                ys.append(y)
            except CalculatorError:
                continue

        if not xs:
            self.graph_error_var.set("Could not evaluate expression for any x in range")

        bg = self.colors["display_bg"]
        fg = self.colors["display_fg"]

        fig = Figure(figsize=(5, 4), dpi=100, facecolor=bg)
        ax = fig.add_subplot(111)
        ax.set_facecolor(bg)
        ax.plot(xs, ys, color=self.colors["accent_bg"], linewidth=2)
        ax.axhline(0, color=fg, linewidth=0.5, alpha=0.4)
        ax.axvline(0, color=fg, linewidth=0.5, alpha=0.4)
        ax.grid(True, alpha=0.2, color=fg)
        ax.tick_params(colors=fg, labelsize=8)
        for spine in ax.spines.values():
            spine.set_color(fg)
            spine.set_alpha(0.3)
        ax.set_title(f"f(x) = {expr}", color=fg, fontsize=11)

        for widget in self.graph_container.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_container)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

    # ==================================================================
    # TAB 3: Converter
    # ==================================================================
    def _build_converter_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)

        frame = ctk.CTkFrame(tab, fg_color=self.colors["display_bg"], corner_radius=12)
        frame.grid(row=0, column=0, sticky="new", pady=10, padx=10)
        for i in range(3):
            frame.grid_columnconfigure(i, weight=1)

        ctk.CTkLabel(frame, text="Category", text_color=self.colors["display_fg"]).grid(
            row=0, column=0, sticky="w", padx=14, pady=(14, 4)
        )
        category_menu = ctk.CTkOptionMenu(
            frame, values=list(CATEGORIES.keys()), variable=self.conv_category_var,
            command=self._on_converter_category_change,
            fg_color=self.colors["btn_bg"], button_color=self.colors["accent_bg"],
            button_hover_color=self.colors["accent_hover"],
        )
        category_menu.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 14))

        ctk.CTkLabel(frame, text="Value", text_color=self.colors["display_fg"]).grid(
            row=0, column=1, sticky="w", padx=14, pady=(14, 4)
        )
        value_entry = ctk.CTkEntry(frame, textvariable=self.conv_value_var)
        value_entry.grid(row=1, column=1, sticky="ew", padx=14, pady=(0, 14))
        self.conv_value_var.trace_add("write", lambda *a: self._do_convert())

        ctk.CTkButton(
            frame, text="⇄ Swap", command=self._swap_converter_units,
            fg_color=self.colors["op_btn_bg"], hover_color=self.colors["op_btn_hover"],
            text_color=self.colors["btn_fg"],
        ).grid(row=1, column=2, sticky="ew", padx=14, pady=(0, 14))

        ctk.CTkLabel(frame, text="From", text_color=self.colors["display_fg"]).grid(
            row=2, column=0, sticky="w", padx=14
        )
        self.conv_from_menu = ctk.CTkOptionMenu(
            frame, values=units_for(self.conv_category_var.get()), variable=self.conv_from_var,
            command=lambda *_: self._do_convert(),
            fg_color=self.colors["btn_bg"], button_color=self.colors["accent_bg"],
            button_hover_color=self.colors["accent_hover"],
        )
        self.conv_from_menu.grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 14))

        ctk.CTkLabel(frame, text="To", text_color=self.colors["display_fg"]).grid(
            row=2, column=1, sticky="w", padx=14
        )
        self.conv_to_menu = ctk.CTkOptionMenu(
            frame, values=units_for(self.conv_category_var.get()), variable=self.conv_to_var,
            command=lambda *_: self._do_convert(),
            fg_color=self.colors["btn_bg"], button_color=self.colors["accent_bg"],
            button_hover_color=self.colors["accent_hover"],
        )
        self.conv_to_menu.grid(row=3, column=1, sticky="ew", padx=14, pady=(0, 14))

        ctk.CTkLabel(
            frame, textvariable=self.conv_result_var, font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.colors["display_fg"], anchor="w",
        ).grid(row=4, column=0, columnspan=3, sticky="ew", padx=14, pady=(0, 18))

        self._do_convert()

    def _on_converter_category_change(self, *_):
        category = self.conv_category_var.get()
        units = units_for(category)
        self.conv_from_menu.configure(values=units)
        self.conv_to_menu.configure(values=units)
        self.conv_from_var.set(units[0])
        self.conv_to_var.set(units[1] if len(units) > 1 else units[0])
        self._do_convert()

    def _swap_converter_units(self):
        f, t = self.conv_from_var.get(), self.conv_to_var.get()
        self.conv_from_var.set(t)
        self.conv_to_var.set(f)
        self._do_convert()

    def _do_convert(self):
        try:
            value = float(self.conv_value_var.get())
            result = convert(
                self.conv_category_var.get(), self.conv_from_var.get(),
                self.conv_to_var.get(), value,
            )
            self.conv_result_var.set(
                f"{value:g} {self.conv_from_var.get()} = {result:.6g} {self.conv_to_var.get()}"
            )
        except (ValueError, ConverterError):
            self.conv_result_var.set("Enter a valid number")

    # ==================================================================
    # TAB 4: Programmer
    # ==================================================================
    def _build_programmer_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)

        frame = ctk.CTkFrame(tab, fg_color=self.colors["display_bg"], corner_radius=12)
        frame.grid(row=0, column=0, sticky="new", padx=10, pady=10)
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame, text="Input base", text_color=self.colors["display_fg"]).grid(
            row=0, column=0, sticky="w", padx=14, pady=(14, 4)
        )
        base_menu = ctk.CTkOptionMenu(
            frame, values=["BIN", "OCT", "DEC", "HEX"], variable=self.prog_base_var,
            command=lambda *_: self._do_base_convert(),
            fg_color=self.colors["btn_bg"], button_color=self.colors["accent_bg"],
            button_hover_color=self.colors["accent_hover"], width=100,
        )
        base_menu.grid(row=0, column=1, sticky="w", padx=14, pady=(14, 4))

        ctk.CTkLabel(frame, text="Value", text_color=self.colors["display_fg"]).grid(
            row=1, column=0, sticky="w", padx=14
        )
        input_entry = ctk.CTkEntry(frame, textvariable=self.prog_input_var)
        input_entry.grid(row=1, column=1, sticky="ew", padx=14, pady=(0, 14))
        self.prog_input_var.trace_add("write", lambda *a: self._do_base_convert())

        rows_grid = ctk.CTkFrame(frame, fg_color="transparent")
        rows_grid.grid(row=2, column=0, columnspan=2, sticky="ew", padx=14, pady=(0, 14))
        rows_grid.grid_columnconfigure(1, weight=1)

        for i, (label, var) in enumerate([
            ("BIN", self.prog_bin_var), ("OCT", self.prog_oct_var),
            ("DEC", self.prog_dec_var), ("HEX", self.prog_hex_var),
        ]):
            ctk.CTkLabel(
                rows_grid, text=label, width=50, text_color=self.colors["display_fg"],
                font=ctk.CTkFont(weight="bold"),
            ).grid(row=i, column=0, sticky="w", pady=3)
            ctk.CTkLabel(
                rows_grid, textvariable=var, text_color=self.colors["display_fg"],
                font=ctk.CTkFont(size=15), anchor="w",
            ).grid(row=i, column=1, sticky="ew", pady=3)

        # Bitwise / arithmetic operation section
        op_frame = ctk.CTkFrame(tab, fg_color=self.colors["display_bg"], corner_radius=12)
        op_frame.grid(row=1, column=0, sticky="new", padx=10, pady=(0, 10))
        for i in range(4):
            op_frame.grid_columnconfigure(i, weight=1)

        ctk.CTkLabel(op_frame, text="A (decimal)", text_color=self.colors["display_fg"]).grid(
            row=0, column=0, sticky="w", padx=14, pady=(14, 4)
        )
        ctk.CTkEntry(op_frame, textvariable=self.prog_opA_var).grid(
            row=1, column=0, sticky="ew", padx=14, pady=(0, 14)
        )

        ctk.CTkLabel(op_frame, text="Operation", text_color=self.colors["display_fg"]).grid(
            row=0, column=1, sticky="w", padx=14, pady=(14, 4)
        )
        ctk.CTkOptionMenu(
            op_frame, values=["AND", "OR", "XOR", "NOT", "<<", ">>", "+", "-", "*", "/"],
            variable=self.prog_op_var, command=lambda *_: self._do_base_operation(),
            fg_color=self.colors["btn_bg"], button_color=self.colors["accent_bg"],
            button_hover_color=self.colors["accent_hover"],
        ).grid(row=1, column=1, sticky="ew", padx=14, pady=(0, 14))

        ctk.CTkLabel(op_frame, text="B (decimal)", text_color=self.colors["display_fg"]).grid(
            row=0, column=2, sticky="w", padx=14, pady=(14, 4)
        )
        ctk.CTkEntry(op_frame, textvariable=self.prog_opB_var).grid(
            row=1, column=2, sticky="ew", padx=14, pady=(0, 14)
        )

        ctk.CTkButton(
            op_frame, text="Calculate", command=self._do_base_operation,
            fg_color=self.colors["accent_bg"], hover_color=self.colors["accent_hover"],
            text_color="#ffffff",
        ).grid(row=1, column=3, sticky="ew", padx=14, pady=(0, 14))

        ctk.CTkLabel(
            op_frame, textvariable=self.prog_result_var, font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["display_fg"], anchor="w",
        ).grid(row=2, column=0, columnspan=4, sticky="ew", padx=14, pady=(0, 14))

        self._do_base_convert()
        self._do_base_operation()

    def _do_base_convert(self):
        base_map = {"BIN": 2, "OCT": 8, "DEC": 10, "HEX": 16}
        base = base_map[self.prog_base_var.get()]
        try:
            value = parse_int(self.prog_input_var.get(), base)
            bases = all_bases(value)
            self.prog_bin_var.set(bases["BIN"])
            self.prog_oct_var.set(bases["OCT"])
            self.prog_dec_var.set(bases["DEC"])
            self.prog_hex_var.set(bases["HEX"])
        except BaseConvError as e:
            self.prog_bin_var.set(str(e))
            self.prog_oct_var.set("-")
            self.prog_dec_var.set("-")
            self.prog_hex_var.set("-")

    def _do_base_operation(self):
        try:
            a = int(float(self.prog_opA_var.get()))
            b = int(float(self.prog_opB_var.get()))
            result = apply_operation(self.prog_op_var.get(), a, b)
            bases = all_bases(result)
            self.prog_result_var.set(
                f"Result: DEC {bases['DEC']}  |  BIN {bases['BIN']}  |  HEX {bases['HEX']}  |  OCT {bases['OCT']}"
            )
        except (ValueError, BaseConvError) as e:
            self.prog_result_var.set(f"Error: {e}")

    # ==================================================================
    # TAB 5: Percentage & Tip
    # ==================================================================
    def _build_percentage_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)

        # Quick percentage calculator
        pct_frame = ctk.CTkFrame(tab, fg_color=self.colors["display_bg"], corner_radius=12)
        pct_frame.grid(row=0, column=0, sticky="new", padx=10, pady=10)
        for i in range(3):
            pct_frame.grid_columnconfigure(i, weight=1)

        ctk.CTkLabel(
            pct_frame, text="What is X% of Y?", font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.colors["display_fg"],
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=14, pady=(14, 6))

        ctk.CTkLabel(pct_frame, text="Percent (%)", text_color=self.colors["display_fg"]).grid(
            row=1, column=0, sticky="w", padx=14
        )
        pct_entry = ctk.CTkEntry(pct_frame, textvariable=self.pct_percent_var)
        pct_entry.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 14))

        ctk.CTkLabel(pct_frame, text="Of value", text_color=self.colors["display_fg"]).grid(
            row=1, column=1, sticky="w", padx=14
        )
        val_entry = ctk.CTkEntry(pct_frame, textvariable=self.pct_value_var)
        val_entry.grid(row=2, column=1, sticky="ew", padx=14, pady=(0, 14))

        self.pct_percent_var.trace_add("write", lambda *a: self._do_percentage())
        self.pct_value_var.trace_add("write", lambda *a: self._do_percentage())

        ctk.CTkLabel(
            pct_frame, textvariable=self.pct_result_var, font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors["display_fg"], anchor="w",
        ).grid(row=2, column=2, sticky="ew", padx=14, pady=(0, 14))

        # Tip calculator
        tip_frame = ctk.CTkFrame(tab, fg_color=self.colors["display_bg"], corner_radius=12)
        tip_frame.grid(row=1, column=0, sticky="new", padx=10, pady=(0, 10))
        for i in range(3):
            tip_frame.grid_columnconfigure(i, weight=1)

        ctk.CTkLabel(
            tip_frame, text="Tip Calculator", font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.colors["display_fg"],
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=14, pady=(14, 6))

        ctk.CTkLabel(tip_frame, text="Bill amount", text_color=self.colors["display_fg"]).grid(
            row=1, column=0, sticky="w", padx=14
        )
        ctk.CTkEntry(tip_frame, textvariable=self.tip_bill_var).grid(
            row=2, column=0, sticky="ew", padx=14, pady=(0, 10)
        )

        ctk.CTkLabel(tip_frame, text="Tip %", text_color=self.colors["display_fg"]).grid(
            row=1, column=1, sticky="w", padx=14
        )
        ctk.CTkEntry(tip_frame, textvariable=self.tip_percent_var).grid(
            row=2, column=1, sticky="ew", padx=14, pady=(0, 10)
        )

        ctk.CTkLabel(tip_frame, text="Split (people)", text_color=self.colors["display_fg"]).grid(
            row=1, column=2, sticky="w", padx=14
        )
        ctk.CTkEntry(tip_frame, textvariable=self.tip_people_var).grid(
            row=2, column=2, sticky="ew", padx=14, pady=(0, 10)
        )

        quick_row = ctk.CTkFrame(tip_frame, fg_color="transparent")
        quick_row.grid(row=3, column=0, columnspan=3, sticky="w", padx=14, pady=(0, 10))
        for pct in [10, 15, 18, 20, 25]:
            ctk.CTkButton(
                quick_row, text=f"{pct}%", width=50,
                fg_color=self.colors["op_btn_bg"], hover_color=self.colors["op_btn_hover"],
                text_color=self.colors["btn_fg"],
                command=lambda p=pct: (self.tip_percent_var.set(str(p)), self._do_tip()),
            ).pack(side="left", padx=4)

        for var in [self.tip_bill_var, self.tip_percent_var, self.tip_people_var]:
            var.trace_add("write", lambda *a: self._do_tip())

        results_row = ctk.CTkFrame(tip_frame, fg_color="transparent")
        results_row.grid(row=4, column=0, columnspan=3, sticky="ew", padx=14, pady=(0, 14))
        for i in range(3):
            results_row.grid_columnconfigure(i, weight=1)

        for i, (label, var) in enumerate([
            ("Tip amount", self.tip_amount_var), ("Total", self.tip_total_var),
            ("Per person", self.tip_per_person_var),
        ]):
            box = ctk.CTkFrame(results_row, fg_color="transparent")
            box.grid(row=0, column=i, sticky="ew")
            ctk.CTkLabel(box, text=label, text_color=self.colors["display_fg"], font=ctk.CTkFont(size=12)).pack(anchor="w")
            ctk.CTkLabel(box, textvariable=var, text_color=self.colors["display_fg"], font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w")

        self._do_percentage()
        self._do_tip()

    def _do_percentage(self):
        try:
            pct = float(self.pct_percent_var.get())
            val = float(self.pct_value_var.get())
            self.pct_result_var.set(f"= {pct / 100 * val:.4g}")
        except ValueError:
            self.pct_result_var.set("Enter valid numbers")

    def _do_tip(self):
        try:
            bill = float(self.tip_bill_var.get())
            pct = float(self.tip_percent_var.get())
            people = max(1, int(float(self.tip_people_var.get() or 1)))
            tip = bill * pct / 100
            total = bill + tip
            per_person = total / people
            self.tip_amount_var.set(f"{tip:.2f}")
            self.tip_total_var.set(f"{total:.2f}")
            self.tip_per_person_var.set(f"{per_person:.2f}")
        except (ValueError, ZeroDivisionError):
            self.tip_amount_var.set("--")
            self.tip_total_var.set("--")
            self.tip_per_person_var.set("--")

    # ------------------------------------------------------------------
    # Theme toggle / rebuild
    # ------------------------------------------------------------------
    def _toggle_theme(self):
        self.current_tab = self.tabview.get()
        idx = THEME_ORDER.index(self.mode)
        self.mode = THEME_ORDER[(idx + 1) % len(THEME_ORDER)]
        ctk.set_appearance_mode("dark" if self.mode == "Dark" else "light")
        self.colors = get_theme(self.mode)
        self._rebuild_ui()

    def _rebuild_ui(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.configure(fg_color=self.colors["bg"])
        self._build_layout()
        self._refresh_history_panel()
        self._plot_graph()

    # ------------------------------------------------------------------
    # Keyboard shortcuts (Calculator tab only; ignored while typing in
    # entries on other tabs)
    # ------------------------------------------------------------------
    def _bind_keys(self):
        for digit in "0123456789.+-*/()":
            self.bind(digit, self._make_key_handler(digit))
        self.bind("<Return>", self._on_enter_key)
        self.bind("<KP_Enter>", self._on_enter_key)
        self.bind("<BackSpace>", self._on_backspace_key)
        self.bind("<Escape>", self._on_escape_key)

    def _is_typing_in_entry(self, event):
        return isinstance(event.widget, tk.Entry)

    def _make_key_handler(self, char):
        def handler(event):
            if self._is_typing_in_entry(event):
                return
            self.expr_var.set(self.expr_var.get() + char)
        return handler

    def _on_enter_key(self, event):
        if self._is_typing_in_entry(event):
            return
        self._calculate()

    def _on_backspace_key(self, event):
        if self._is_typing_in_entry(event):
            return
        self._backspace()

    def _on_escape_key(self, event):
        if self._is_typing_in_entry(event):
            return
        self._clear_entry()
