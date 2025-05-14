import matplotlib
matplotlib.use('TkAgg')  # Set backend before importing pyplot
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sympy import sympify, lambdify, latex, Eq, symbols
import sympy as sp
import os
import shutil
import sys
import re

# --- LaTeX dependency check (reuse from function_plotter.py) ---
def check_latex_dependencies():
    missing = []
    if not shutil.which('latex'):
        missing.append('latex')
    if not shutil.which('dvipng'):
        missing.append('dvipng')
    gs_names = ['gs', 'gswin64c', 'gswin32c']
    if not any(shutil.which(gs) for gs in gs_names):
        missing.append('ghostscript (gs)')
    if missing:
        msg = "Error: The following required LaTeX dependencies are missing:\n" + \
              "\n".join(f"  - {dep}" for dep in missing) + \
              "\n\nPlease install them to enable true LaTeX rendering.\n"
        return False, msg
    return True, ""

# --- Matplotlib LaTeX config ---
latex_ok, latex_msg = check_latex_dependencies()
if latex_ok:
    mpl.rcParams['text.usetex'] = True
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = ['Computer Modern Roman']
    mpl.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'
# Set matplotlib figure and axes background to white
mpl.rcParams['figure.facecolor'] = 'white'
mpl.rcParams['axes.facecolor'] = 'white'

# --- Utility functions ---
def clean_latex_expression(expr):
    try:
        tex = latex(expr)
        tex = tex.replace('$', '')
        tex = tex.replace('\\left', '').replace('\\right', '')
        return tex
    except Exception as e:
        return str(expr)

def get_safe_filename(base_filename, ext):
    if not base_filename:
        base_filename = "output"
    if not base_filename.endswith(f".{ext}"):
        base_filename = f"{base_filename}.{ext}"
    counter = 1
    final_filename = base_filename
    while os.path.exists(final_filename):
        name, ext2 = os.path.splitext(base_filename)
        final_filename = f"{name}_{counter}{ext2}"
        counter += 1
    return final_filename

def get_color_from_slider(slider_value, cmap_name="rainbow"):
    cmap = plt.get_cmap(cmap_name)
    color = cmap(slider_value / 100.0)
    return color

def is_valid_hex_color(s):
    return bool(re.fullmatch(r"#([0-9a-fA-F]{6})", s.strip()))

# --- Plotting functions ---
def plot_function_gui(func_str, x_min, x_max, color, legend_loc):
    x = sp.Symbol('x')
    expr = sympify(func_str.replace('^', '**'))
    f = lambdify(x, expr, "numpy")
    x_vals = np.linspace(x_min, x_max, 1000)
    y_vals = f(x_vals)
    tex_expr = clean_latex_expression(expr)
    legend_label = rf'$f(x) = {tex_expr}$'
    fig, ax = plt.subplots(figsize=(7, 4), facecolor='white')
    ax.plot(x_vals, y_vals, color=color, label=legend_label)
    ax.grid(True)
    ax.set_xlabel(r'$x$')
    ax.set_ylabel(r'$f(x)$')
    ax.set_title(rf'$f(x) = {tex_expr}$')
    if legend_loc == "auto":
        if len(tex_expr) > 30:
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        else:
            ax.legend(loc='best')
    else:
        ax.legend(loc=legend_loc)
    ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
    fig.tight_layout()
    return fig

def plot_equation_gui_preview(equation_str, x_min, x_max, y_min, y_max):
    x, y = symbols('x y')
    equation_str = equation_str.replace('^', '**')
    if '=' in equation_str:
        left, right = equation_str.split('=')
        eq = Eq(sympify(left), sympify(right))
        expr = sympify(left) - sympify(right)
    else:
        eq = Eq(sympify(equation_str), 0)
        expr = sympify(equation_str)
    tex_expr = clean_latex_expression(eq)
    x_vals = np.linspace(x_min, x_max, 400)
    y_vals = np.linspace(y_min, y_max, 400)
    X, Y = np.meshgrid(x_vals, y_vals)
    f_lambdified = lambdify((x, y), expr, "numpy")
    Z = f_lambdified(X, Y)
    fig, ax = plt.subplots(figsize=(6, 6), facecolor='white')
    ax.contour(X, Y, Z, levels=[0], colors='b')
    ax.grid(True)
    ax.set_xlabel(r'$x$')
    ax.set_ylabel(r'$y$')
    ax.set_title(rf'${latex(eq)}$')
    fig.tight_layout()
    return fig

def export_current_figure(fig, filename, format_):
    try:
        fig.savefig(filename, format=format_, bbox_inches='tight', pad_inches=0.2, dpi=300, facecolor='white')
        return True, f"Plot exported as '{filename}'"
    except Exception as e:
        return False, f"Error exporting plot: {e}"

# --- GUI ---
class PlotterGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Function/Equation Plotter (LaTeX)")
        self.geometry("950x550")
        self.resizable(False, False)
        self.configure(bg="white")
        self.style = ttk.Style(self)
        self.style.theme_use('default')
        self.style.configure('.', background='white')
        self.style.configure('TLabel', background='white')
        self.style.configure('TFrame', background='white')
        self.style.configure('TEntry', fieldbackground='white', background='white')
        self.style.configure('TCombobox', fieldbackground='white', background='white')
        self.style.configure('TButton', background='white')
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)
        self.create_function_tab()
        self.create_equation_tab()

    def create_function_tab(self):
        tab = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(tab, text="Function y = f(x)")
        ttk.Label(tab, text="f(x) = ").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.func_entry = ttk.Entry(tab, width=40)
        self.func_entry.grid(row=0, column=1, columnspan=3, sticky='w', padx=5, pady=5)
        ttk.Label(tab, text="x min:").grid(row=1, column=0, sticky='e', padx=5)
        self.xmin_entry = ttk.Entry(tab, width=10)
        self.xmin_entry.grid(row=1, column=1, sticky='w', padx=5)
        ttk.Label(tab, text="x max:").grid(row=1, column=2, sticky='e', padx=5)
        self.xmax_entry = ttk.Entry(tab, width=10)
        self.xmax_entry.grid(row=1, column=3, sticky='w', padx=5)
        ttk.Label(tab, text="Output format:").grid(row=2, column=0, sticky='e', padx=5)
        self.func_format = ttk.Combobox(tab, values=["svg", "pdf"], width=8, state="readonly")
        self.func_format.set("svg")
        self.func_format.grid(row=2, column=1, sticky='w', padx=5)
        ttk.Label(tab, text="Output filename:").grid(row=2, column=2, sticky='e', padx=5)
        self.func_filename = ttk.Entry(tab, width=15)
        self.func_filename.grid(row=2, column=3, sticky='w', padx=5)
        ttk.Label(tab, text="Legend position:").grid(row=3, column=0, sticky='e', padx=5)
        self.func_legend_pos = ttk.Combobox(tab, values=[
            "auto", "best", "upper right", "upper left", "lower left", "lower right", "right", "center left", "center right", "lower center", "upper center", "center"
        ], width=15, state="readonly")
        self.func_legend_pos.set("auto")
        self.func_legend_pos.grid(row=3, column=1, sticky='w', padx=5)
        ttk.Label(tab, text="Color:").grid(row=3, column=2, sticky='e', padx=5)
        self.func_color_slider = tk.Scale(tab, from_=0, to=100, orient=tk.HORIZONTAL, showvalue=0, length=120, command=self.update_func_color_preview, bg="white", highlightbackground="white")
        self.func_color_slider.set(0)
        self.func_color_slider.grid(row=3, column=3, sticky='w', padx=5)
        ttk.Label(tab, text="Hex:").grid(row=3, column=4, sticky='e', padx=2)
        self.func_color_hex = ttk.Entry(tab, width=8)
        self.func_color_hex.grid(row=3, column=5, sticky='w', padx=2)
        self.func_color_hex.bind('<KeyRelease>', self.update_func_color_preview)
        self.func_color_preview = tk.Label(tab, width=2, height=1, bg="#0000ff", relief="sunken")
        self.func_color_preview.grid(row=3, column=6, padx=5)
        self.func_generate_btn = ttk.Button(tab, text="Generate", command=self.generate_function_plot)
        self.func_generate_btn.grid(row=4, column=0, columnspan=2, pady=10)
        self.func_export_btn = ttk.Button(tab, text="Export", command=self.export_function_plot, state="disabled")
        self.func_export_btn.grid(row=4, column=2, columnspan=2, pady=10)
        self.func_status = ttk.Label(tab, text="", foreground="blue")
        self.func_status.grid(row=5, column=0, columnspan=7, pady=5)
        self.func_canvas = None
        self.func_fig = None
        self.func_canvas_frame = ttk.Frame(tab, style='TFrame')
        self.func_canvas_frame.grid(row=6, column=0, columnspan=7, sticky='nsew', padx=5, pady=5)
        tab.rowconfigure(6, weight=1)
        tab.columnconfigure(0, weight=1)

    def update_func_color_preview(self, val=None):
        hex_code = self.func_color_hex.get().strip()
        if is_valid_hex_color(hex_code):
            color = hex_code
        else:
            color = get_color_from_slider(self.func_color_slider.get())
            rgb = tuple(int(255 * c) for c in color[:3])
            color = '#%02x%02x%02x' % rgb
        self.func_color_preview.config(bg=color)

    def get_func_plot_color(self):
        hex_code = self.func_color_hex.get().strip()
        if is_valid_hex_color(hex_code):
            return hex_code
        else:
            color = get_color_from_slider(self.func_color_slider.get())
            rgb = tuple(int(255 * c) for c in color[:3])
            return '#%02x%02x%02x' % rgb

    def generate_function_plot(self):
        if not latex_ok:
            self.func_status.config(text=latex_msg, foreground="red")
            return
        func_str = self.func_entry.get().strip()
        x_min = self.xmin_entry.get().strip()
        x_max = self.xmax_entry.get().strip()
        color = self.get_func_plot_color()
        legend_loc = self.func_legend_pos.get()
        try:
            x_min = float(sympify(x_min))
            x_max = float(sympify(x_max))
            if x_min >= x_max:
                raise ValueError("x min must be less than x max")
            try:
                fig = plot_function_gui(func_str, x_min, x_max, color, legend_loc)
            except Exception as e:
                self.func_status.config(text=f"Error generating plot: {e}", foreground="red")
                self.func_export_btn.config(state="disabled")
                if self.func_canvas:
                    self.func_canvas.get_tk_widget().destroy()
                    self.func_canvas = None
                    self.func_fig = None
                return
            if self.func_canvas:
                self.func_canvas.get_tk_widget().destroy()
            self.func_fig = fig
            self.func_canvas = FigureCanvasTkAgg(fig, master=self.func_canvas_frame)
            self.func_canvas.draw()
            self.func_canvas.get_tk_widget().pack(fill='both', expand=True)
            self.func_status.config(text="Plot generated. Click Export to save.", foreground="green")
            self.func_export_btn.config(state="normal")
        except Exception as e:
            self.func_status.config(text=f"Error: {e}", foreground="red")
            self.func_export_btn.config(state="disabled")
            if self.func_canvas:
                self.func_canvas.get_tk_widget().destroy()
                self.func_canvas = None
                self.func_fig = None

    def export_function_plot(self):
        if not self.func_fig:
            self.func_status.config(text="No plot to export.", foreground="red")
            return
        format_ = self.func_format.get()
        filename = self.func_filename.get().strip()
        filename = get_safe_filename(filename, format_)
        ok, msg = export_current_figure(self.func_fig, filename, format_)
        self.func_status.config(text=msg, foreground="green" if ok else "red")

    def create_equation_tab(self):
        tab = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(tab, text="Equation F(x, y) = 0")
        ttk.Label(tab, text="Equation (e.g., x^2 + y^2 = 1):").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.eqn_entry = ttk.Entry(tab, width=40)
        self.eqn_entry.grid(row=0, column=1, columnspan=3, sticky='w', padx=5, pady=5)
        ttk.Label(tab, text="x min:").grid(row=1, column=0, sticky='e', padx=5)
        self.eqn_xmin = ttk.Entry(tab, width=10)
        self.eqn_xmin.grid(row=1, column=1, sticky='w', padx=5)
        ttk.Label(tab, text="x max:").grid(row=1, column=2, sticky='e', padx=5)
        self.eqn_xmax = ttk.Entry(tab, width=10)
        self.eqn_xmax.grid(row=1, column=3, sticky='w', padx=5)
        ttk.Label(tab, text="y min:").grid(row=2, column=0, sticky='e', padx=5)
        self.eqn_ymin = ttk.Entry(tab, width=10)
        self.eqn_ymin.grid(row=2, column=1, sticky='w', padx=5)
        ttk.Label(tab, text="y max:").grid(row=2, column=2, sticky='e', padx=5)
        self.eqn_ymax = ttk.Entry(tab, width=10)
        self.eqn_ymax.grid(row=2, column=3, sticky='w', padx=5)
        ttk.Label(tab, text="Output format:").grid(row=3, column=0, sticky='e', padx=5)
        self.eqn_format = ttk.Combobox(tab, values=["svg", "pdf"], width=8, state="readonly")
        self.eqn_format.set("svg")
        self.eqn_format.grid(row=3, column=1, sticky='w', padx=5)
        ttk.Label(tab, text="Output filename:").grid(row=3, column=2, sticky='e', padx=5)
        self.eqn_filename = ttk.Entry(tab, width=15)
        self.eqn_filename.grid(row=3, column=3, sticky='w', padx=5)
        self.eqn_generate_btn = ttk.Button(tab, text="Generate", command=self.generate_equation_plot)
        self.eqn_generate_btn.grid(row=4, column=0, columnspan=2, pady=10)
        self.eqn_export_btn = ttk.Button(tab, text="Export", command=self.export_equation_plot, state="disabled")
        self.eqn_export_btn.grid(row=4, column=2, columnspan=2, pady=10)
        self.eqn_status = ttk.Label(tab, text="", foreground="blue")
        self.eqn_status.grid(row=5, column=0, columnspan=4, pady=5)
        self.eqn_canvas = None
        self.eqn_fig = None
        self.eqn_canvas_frame = ttk.Frame(tab, style='TFrame')
        self.eqn_canvas_frame.grid(row=6, column=0, columnspan=4, sticky='nsew', padx=5, pady=5)
        tab.rowconfigure(6, weight=1)
        tab.columnconfigure(0, weight=1)

    def generate_equation_plot(self):
        if not latex_ok:
            self.eqn_status.config(text=latex_msg, foreground="red")
            return
        eqn_str = self.eqn_entry.get().strip()
        x_min = self.eqn_xmin.get().strip()
        x_max = self.eqn_xmax.get().strip()
        y_min = self.eqn_ymin.get().strip()
        y_max = self.eqn_ymax.get().strip()
        try:
            x_min = float(sympify(x_min))
            x_max = float(sympify(x_max))
            y_min = float(sympify(y_min))
            y_max = float(sympify(y_max))
            if x_min >= x_max or y_min >= y_max:
                raise ValueError("min must be less than max for both x and y")
            try:
                fig = plot_equation_gui_preview(eqn_str, x_min, x_max, y_min, y_max)
            except Exception as e:
                self.eqn_status.config(text=f"Error generating plot: {e}", foreground="red")
                self.eqn_export_btn.config(state="disabled")
                if self.eqn_canvas:
                    self.eqn_canvas.get_tk_widget().destroy()
                    self.eqn_canvas = None
                    self.eqn_fig = None
                return
            if self.eqn_canvas:
                self.eqn_canvas.get_tk_widget().destroy()
            self.eqn_fig = fig
            self.eqn_canvas = FigureCanvasTkAgg(fig, master=self.eqn_canvas_frame)
            self.eqn_canvas.draw()
            self.eqn_canvas.get_tk_widget().pack(fill='both', expand=True)
            self.eqn_status.config(text="Plot generated. Click Export to save.", foreground="green")
            self.eqn_export_btn.config(state="normal")
        except Exception as e:
            self.eqn_status.config(text=f"Error: {e}", foreground="red")
            self.eqn_export_btn.config(state="disabled")
            if self.eqn_canvas:
                self.eqn_canvas.get_tk_widget().destroy()
                self.eqn_canvas = None
                self.eqn_fig = None

    def export_equation_plot(self):
        if not self.eqn_fig:
            self.eqn_status.config(text="No plot to export.", foreground="red")
            return
        format_ = self.eqn_format.get()
        filename = self.eqn_filename.get().strip()
        filename = get_safe_filename(filename, format_)
        ok, msg = export_current_figure(self.eqn_fig, filename, format_)
        self.eqn_status.config(text=msg, foreground="green" if ok else "red")

if __name__ == "__main__":
    app = PlotterGUI()
    app.mainloop() 