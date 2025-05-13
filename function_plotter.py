import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from sympy import sympify, lambdify, latex, Eq, symbols, solve
import sympy as sp
import os
import shutil
import sys

def check_latex_dependencies():
    """Check if LaTeX, dvipng, and ghostscript are installed and available."""
    missing = []
    if not shutil.which('latex'):
        missing.append('latex')
    if not shutil.which('dvipng'):
        missing.append('dvipng')
    # Ghostscript is 'gs' on Linux/macOS, 'gswin64c' or 'gswin32c' on Windows
    gs_names = ['gs', 'gswin64c', 'gswin32c']
    if not any(shutil.which(gs) for gs in gs_names):
        missing.append('ghostscript (gs)')
    if missing:
        print("Error: The following required LaTeX dependencies are missing:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nPlease install them to enable true LaTeX rendering.\n")
        sys.exit(1)

# Check for LaTeX and configure matplotlib for true LaTeX rendering
check_latex_dependencies()
mpl.rcParams['text.usetex'] = True
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['font.serif'] = ['Computer Modern Roman']
mpl.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'

def validate_function(func_str):
    """Validate if the input string is a valid mathematical function."""
    try:
        # Replace '^' with '**' for proper Python syntax
        func_str = func_str.replace('^', '**')
        sympify(func_str)
        return func_str
    except:
        raise ValueError("Invalid function expression")

def clean_latex_expression(expr):
    """Return a LaTeX string for mathtext rendering."""
    try:
        tex = latex(expr)
        # Remove any $ that might be present
        tex = tex.replace('$', '')
        # Remove \left and \right for matplotlib mathtext compatibility
        tex = tex.replace('\\left', '').replace('\\right', '')
        return tex
    except Exception as e:
        print(f"Warning: LaTeX conversion failed: {e}")
        return str(expr)

def format_text(text, math=True, for_legend=False):
    """Format text for mathtext rendering. Use $...$ only for legend labels."""
    if math and for_legend:
        # Ensure no $ in text, then wrap
        text = text.replace('$', '')
        return r'$' + text + r'$'
    return text

def plot_function(func_str, x_min, x_max, filename="output.svg", format="svg"):
    """Plot the function with true LaTeX rendering and save as SVG or PDF."""
    try:
        # Create symbolic variable and function
        x = sp.Symbol('x')
        expr = sympify(func_str)
        
        # Convert symbolic expression to numpy function
        f = lambdify(x, expr, "numpy")
        
        # Create x values
        x_vals = np.linspace(x_min, x_max, 1000)
        
        # Calculate y values
        y_vals = f(x_vals)
        
        # Get cleaned expression
        tex_expr = clean_latex_expression(expr)
        legend_label = rf'$f(x) = {tex_expr}$'
        
        # Create the plot
        plt.figure(figsize=(10, 6))
        plt.plot(x_vals, y_vals, 'b-', label=legend_label)
        plt.grid(True)
        plt.xlabel(r'$x$')
        plt.ylabel(r'$f(x)$')
        plt.title(rf'$f(x) = {tex_expr}$')
        
        # Adjust legend position based on plot size
        if len(tex_expr) > 30:  # For long expressions
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        else:
            plt.legend(loc='best')
        
        # Add x and y axis
        plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        plt.axvline(x=0, color='k', linestyle='-', alpha=0.3)
        
        # Adjust layout to prevent text cutoff
        plt.tight_layout()
        
        # Save plot with proper settings
        try:
            plt.savefig(filename, format=format, bbox_inches='tight', 
                       pad_inches=0.2, dpi=300)
        except Exception as e:
            print(f"Error saving file: {e}")
            # Try saving with a default filename if the provided one fails
            default_filename = f"output_{hash(func_str) % 10000}.{format}"
            print(f"Attempting to save as {default_filename}")
            plt.savefig(default_filename, format=format, bbox_inches='tight', 
                       pad_inches=0.2, dpi=300)
            filename = default_filename
        
        plt.close()
        return True
        
    except Exception as e:
        print(f"Error plotting function: {e}")
        return False

def plot_equation(equation_str, x_min, x_max, y_min, y_max, filename="output.svg", format="svg"):
    try:
        x, y = symbols('x y')
        # Replace ^ with ** and parse equation
        equation_str = equation_str.replace('^', '**')
        if '=' in equation_str:
            left, right = equation_str.split('=')
            eq = Eq(sympify(left), sympify(right))
            expr = sympify(left) - sympify(right)
        else:
            eq = Eq(sympify(equation_str), 0)
            expr = sympify(equation_str)
        tex_expr = clean_latex_expression(eq)
        # Create grid
        x_vals = np.linspace(x_min, x_max, 400)
        y_vals = np.linspace(y_min, y_max, 400)
        X, Y = np.meshgrid(x_vals, y_vals)
        f_lambdified = lambdify((x, y), expr, "numpy")
        Z = f_lambdified(X, Y)
        plt.figure(figsize=(8, 8))
        plt.contour(X, Y, Z, levels=[0], colors='b')
        plt.grid(True)
        plt.xlabel(r'$x$')
        plt.ylabel(r'$y$')
        plt.title(rf'${latex(eq)}$')
        plt.tight_layout()
        try:
            plt.savefig(filename, format=format, bbox_inches='tight', pad_inches=0.2, dpi=300)
        except Exception as e:
            print(f"Error saving file: {e}")
            default_filename = f"output_{hash(equation_str) % 10000}.{format}"
            print(f"Attempting to save as {default_filename}")
            plt.savefig(default_filename, format=format, bbox_inches='tight', pad_inches=0.2, dpi=300)
            filename = default_filename
        plt.close()
        return True
    except Exception as e:
        print(f"Error plotting equation: {e}")
        return False

def get_output_format():
    """Get the desired output format from user."""
    while True:
        print("\nChoose output format:")
        print("1. SVG")
        print("2. PDF")
        choice = input("Enter your choice (1 or 2): ").strip()
        
        if choice == "1":
            return "svg"
        elif choice == "2":
            return "pdf"
        else:
            print("Invalid choice. Please enter 1 for SVG or 2 for PDF.")

def get_safe_filename(base_filename, format):
    """Generate a safe filename that doesn't already exist."""
    if not base_filename:
        base_filename = "output"
    
    # Ensure the filename ends with the correct extension
    if not base_filename.endswith(f".{format}"):
        base_filename = f"{base_filename}.{format}"
    
    # If the file exists, add a number to make it unique
    counter = 1
    final_filename = base_filename
    while os.path.exists(final_filename):
        name, ext = os.path.splitext(base_filename)
        final_filename = f"{name}_{counter}{ext}"
        counter += 1
    
    return final_filename

def main():
    print("Function Plotter - SVG/PDF Export (True LaTeX Rendering)")
    print("--------------------------------------------------------")
    print("Would you like to plot a function y = f(x) or an equation F(x, y) = 0?")
    print("1. Function (y = f(x))")
    print("2. Equation (F(x, y) = 0)")
    while True:
        try:
            plot_type = input("Enter 1 for function, 2 for equation: ").strip()
            if plot_type not in ('1', '2'):
                print("Invalid choice. Please enter 1 or 2.\n")
                continue
            if plot_type == '1':
                func_str = input("Enter function f(x) = ")
                func_str = validate_function(func_str)
                x_min = float(input("Enter minimum x value: "))
                x_max = float(input("Enter maximum x value: "))
                if x_min >= x_max:
                    raise ValueError("Minimum x value must be less than maximum x value")
                format = get_output_format()
                default_ext = f".{format}"
                filename = input(f"Enter output filename (default: output{default_ext}): ").strip()
                filename = get_safe_filename(filename, format)
                if plot_function(func_str, x_min, x_max, filename, format):
                    print(f"\nFunction plotted successfully and saved as '{filename}'")
                break
            else:
                equation_str = input("Enter equation in x and y (e.g., x^2 + y^2 = 1): ")
                x_min = float(input("Enter minimum x value: "))
                x_max = float(input("Enter maximum x value: "))
                y_min = float(input("Enter minimum y value: "))
                y_max = float(input("Enter maximum y value: "))
                if x_min >= x_max or y_min >= y_max:
                    raise ValueError("Minimum values must be less than maximum values")
                format = get_output_format()
                default_ext = f".{format}"
                filename = input(f"Enter output filename (default: output{default_ext}): ").strip()
                filename = get_safe_filename(filename, format)
                if plot_equation(equation_str, x_min, x_max, y_min, y_max, filename, format):
                    print(f"\nEquation plotted successfully and saved as '{filename}'")
                break
        except ValueError as e:
            print(f"\nError: {e}")
            print("Please try again.\n")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            print("Please try again.\n")

if __name__ == "__main__":
    main() 