# Function Plotter

A Python script that plots mathematical functions with LaTeX-formatted expressions and exports them as SVG or PDF files.

## Installation

1. Make sure you have Python 3.7 or higher installed
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the script:
```bash
python function_plotter.py
```

The script will prompt you for:
1. A mathematical function using 'x' as the variable
2. The minimum x value for the plot range
3. The maximum x value for the plot range
4. Output format choice (SVG or PDF)
5. The output filename (optional, defaults to 'output.svg' or 'output.pdf')

### Supported Mathematical Functions

You can use various mathematical functions and operators:
- Basic operators: +, -, *, /, ^ (or **)
- Trigonometric functions: sin(x), cos(x), tan(x)
- Exponential and logarithmic: exp(x), log(x)
- Constants: pi, e

### Examples

Here are some example functions you can try:
- `x^2` - Quadratic function
- `sin(x)` - Sine wave
- `exp(-x)` - Exponential decay
- `x^3 - 2*x + 1` - Cubic function
- `log(x)` - Natural logarithm
- `sin(x^2)/(1 + x^2)` - More complex expression

### LaTeX Formatting

The plot includes LaTeX-formatted mathematical expressions for:
- Function in the title
- Function in the legend
- Axis labels
- All mathematical symbols and expressions

This ensures professional-quality typesetting of:
- Fractions
- Exponents
- Greek letters
- Mathematical operators
- Special functions

### Output Formats

1. SVG (Scalable Vector Graphics)
   - Best for web use and scaling without quality loss
   - Can be edited with vector graphics software
   - Smaller file size for simple plots

2. PDF (Portable Document Format)
   - Best for printing and document inclusion
   - Widely supported across different platforms
   - Professional document quality 