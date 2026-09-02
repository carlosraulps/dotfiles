#!/usr/bin/env bash
# ==============================================================================
#  macOS Spotlight Pro Scientific Calculator for Rofi
#  Supports Physical & Mathematical Constants, Trigonometry, and Metric Prefixes
# ==============================================================================

theme="$HOME/.config/rofi/themes/spotlight-dark.rasi"
ans=""
expr=""

while true; do
    if [ -z "$ans" ]; then
        prompt="󰍹 Sci-Calc"
        mesg="Type formula (e.g. hbar*c, kb*300, 13.6*eV, G*M/R^2, sin(rad(45))) — Enter to solve"
    else
        prompt="󰍹 Result: $ans"
        mesg="Last: $expr = $ans (Copied to clipboard) — Enter next formula or Esc to exit"
    fi

    # Display interactive Rofi prompt with Spotlight theme
    input=$(rofi -dmenu \
        -p "$prompt" \
        -mesg "$mesg" \
        -theme "$theme" \
        -theme-str 'listview {lines: 0; padding: 0px; margin: 0px; border: 0px;}' \
        -theme-str 'mode-switcher {enabled: false;}' \
        -theme-str 'window {width: 680px;}')

    # Exit on Esc or empty submission
    [ -z "$input" ] && exit 0

    # Calculate expression safely with Python
    result=$(python3 -c "
import sys, math, re

raw = sys.argv[1].strip()
if not raw:
    sys.exit(0)

# Replace human operators and formatting
cleaned = raw.replace('^', '**').replace('×', '*').replace('÷', '/')
cleaned = re.sub(r'(\d+(\.\d+)?)%', r'(\1/100)', cleaned)

# Scientific and Physical Constants (CODATA Recommended Values)
constants = {
    # Speed of light in vacuum (m/s)
    'c': 299792458,
    # Planck constant (J·s)
    'h': 6.62607015e-34,
    # Reduced Planck constant hbar = h / (2*pi) (J·s)
    'hbar': 1.0545718176461565e-34,
    'h_bar': 1.0545718176461565e-34,
    # Boltzmann constant (J/K)
    'k': 1.380649e-23,
    'kb': 1.380649e-23,
    'k_B': 1.380649e-23,
    'boltzmann': 1.380649e-23,
    # Gravitational constant (m^3/(kg·s^2))
    'G': 6.67430e-11,
    'g_const': 6.67430e-11,
    # Standard acceleration due to gravity (m/s^2)
    'g': 9.80665,
    # Elementary charge (C)
    'q_e': 1.602176634e-19,
    'qe': 1.602176634e-19,
    'echarge': 1.602176634e-19,
    # Electronvolt in Joules (J)
    'eV': 1.602176634e-19,
    'keV': 1.602176634e-16,
    'MeV': 1.602176634e-13,
    'GeV': 1.602176634e-10,
    # Vacuum electric permittivity (F/m)
    'eps0': 8.8541878128e-12,
    'eps_0': 8.8541878128e-12,
    'epsilon_0': 8.8541878128e-12,
    # Vacuum magnetic permeability (N/A^2)
    'mu0': 1.25663706212e-6,
    'mu_0': 1.25663706212e-6,
    # Coulomb constant 1 / (4*pi*eps0) (N·m^2/C^2)
    'ke': 8.9875517923e9,
    'k_e': 8.9875517923e9,
    'coulomb': 8.9875517923e9,
    # Masses (kg)
    'me': 9.1093837015e-31,
    'm_e': 9.1093837015e-31,
    'mp': 1.67262192369e-27,
    'm_p': 1.67262192369e-27,
    'mn': 1.67492749804e-27,
    'm_n': 1.67492749804e-27,
    'u': 1.66053906660e-27,
    'amu': 1.66053906660e-27,
    # Chemistry & Thermodynamics
    'Na': 6.02214076e23,
    'N_A': 6.02214076e23,
    'avogadro': 6.02214076e23,
    'R': 8.314462618,
    'sigma': 5.670374419e-8,
    'stefan_boltzmann': 5.670374419e-8,
    'F': 96485.33212,
    'faraday': 96485.33212,
    'atm': 101325,
    # Atomic & Quantum Constants
    'alpha': 7.2973525693e-3,
    'fine_structure': 7.2973525693e-3,
    'R_inf': 10973731.568160,
    'rydberg': 10973731.568160,
    'a0': 5.29177210903e-11,
    'bohr_radius': 5.29177210903e-11,
    # Mathematical Constants
    'pi': math.pi,
    'tau': 2 * math.pi,
    'e': math.e,
    'phi': 1.618033988749895,
    # Metric Prefixes
    'Y': 1e24, 'Z': 1e21, 'E': 1e18, 'P': 1e15, 'T': 1e12,
    'G_prefix': 1e9, 'M': 1e6, 'kilo': 1e3,
    'milli': 1e-3, 'micro': 1e-6, 'nano': 1e-9, 'pico': 1e-12, 'femto': 1e-15, 'atto': 1e-18,
    # Mathematical Functions
    'sqrt': math.sqrt,
    'cbrt': lambda x: x ** (1/3),
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'asin': math.asin,
    'acos': math.acos,
    'atan': math.atan,
    'atan2': math.atan2,
    'sinh': math.sinh,
    'cosh': math.cosh,
    'tanh': math.tanh,
    'asinh': math.asinh,
    'acosh': math.acosh,
    'atanh': math.atanh,
    'log': math.log,
    'ln': math.log,
    'log10': math.log10,
    'log2': math.log2,
    'exp': math.exp,
    'abs': abs,
    'round': round,
    'floor': math.floor,
    'ceil': math.ceil,
    'factorial': math.factorial,
    'gcd': math.gcd,
    'deg': math.degrees,
    'degrees': math.degrees,
    'rad': math.radians,
    'radians': math.radians,
}

env = {'__builtins__': {}, **constants}

try:
    val = eval(cleaned, env)
    if isinstance(val, (int, float, complex)):
        if isinstance(val, float) and val.is_integer():
            print(int(val))
        elif isinstance(val, float):
            # Check for scientific notation necessity
            abs_val = abs(val)
            if abs_val != 0 and (abs_val < 1e-4 or abs_val >= 1e9):
                print(f'{val:.6e}')
            else:
                print(f'{round(val, 8):g}')
        else:
            print(val)
except Exception:
    pass
" "$input" 2>/dev/null)

    if [ -n "$result" ]; then
        ans="$result"
        expr="$input"
        # Copy to clipboard completely in background (non-blocking)
        (echo -n "$result" | xclip -selection clipboard) >/dev/null 2>&1 &
        notify-send -a "Spotlight Calc" "Calculation Complete" "$input = $result\n(Copied to clipboard)" 2>/dev/null &
    else
        notify-send -a "Spotlight Calc" "Invalid Expression" "Could not solve: $input" 2>/dev/null &
    fi
done
