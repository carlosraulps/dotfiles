#!/usr/bin/env python3
"""
macOS Spotlight Instant Scientific Calculator for Rofi Script-Mode
Supports full physical & mathematical constants, non-blocking clipboard copy, and notifications.
"""

import sys
import os
import re
import math
import subprocess

# Full Scientific & Physical Constants (CODATA Recommended Values)
CONSTANTS = {
    # Speed of light in vacuum (m/s)
    'c': 299792458,
    # Planck constants (J·s)
    'h': 6.62607015e-34,
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
    # Standard gravity (m/s^2)
    'g': 9.80665,
    # Elementary charge (C)
    'q_e': 1.602176634e-19,
    'qe': 1.602176634e-19,
    'echarge': 1.602176634e-19,
    # Electronvolt (J)
    'eV': 1.602176634e-19,
    'keV': 1.602176634e-16,
    'MeV': 1.602176634e-13,
    'GeV': 1.602176634e-10,
    # Vacuum permittivity & permeability
    'eps0': 8.8541878128e-12,
    'eps_0': 8.8541878128e-12,
    'epsilon_0': 8.8541878128e-12,
    'mu0': 1.25663706212e-6,
    'mu_0': 1.25663706212e-6,
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
    # Metric Multipliers
    'Y': 1e24, 'Z': 1e21, 'E': 1e18, 'P': 1e15, 'T': 1e12,
    'G_prefix': 1e9, 'M': 1e6, 'kilo': 1e3,
    'milli': 1e-3, 'micro': 1e-6, 'nano': 1e-9, 'pico': 1e-12, 'femto': 1e-15, 'atto': 1e-18,
    # Functions
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

ENV = {'__builtins__': {}, **CONSTANTS}


def evaluate(expr):
    expr = expr.strip()
    if not expr:
        return None
    cleaned = expr.replace('^', '**').replace('×', '*').replace('÷', '/')
    cleaned = re.sub(r'(\d+(\.\d+)?)%', r'(\1/100)', cleaned)
    try:
        val = eval(cleaned, ENV)
        if isinstance(val, (int, float, complex)):
            if isinstance(val, float) and val.is_integer():
                return str(int(val))
            elif isinstance(val, float):
                abs_val = abs(val)
                if abs_val != 0 and (abs_val < 1e-4 or abs_val >= 1e9):
                    return f'{val:.6e}'
                else:
                    return f'{round(val, 8):g}'
            return str(val)
    except Exception:
        return None
    return None


def copy_clipboard_async(text):
    try:
        subprocess.Popen(
            f"(echo -n '{text}' | xclip -selection clipboard) >/dev/null 2>&1 &",
            shell=True,
            start_new_session=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass


def notify_async(title, msg):
    try:
        subprocess.Popen(
            ["notify-send", "-a", "Spotlight Calc", title, msg],
            start_new_session=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass


def main():
    if len(sys.argv) > 1 and sys.argv[1].strip():
        raw_input = sys.argv[1].strip()
        if "=" in raw_input:
            ans = raw_input.split("=")[-1].strip()
            copy_clipboard_async(ans)
            notify_async("Calculator", f"Copied {ans} to clipboard!")
            return

        res = evaluate(raw_input)
        if res is not None:
            copy_clipboard_async(res)
            notify_async("Calculator", f"{raw_input} = {res}\n(Copied to clipboard)")
        return

    # Default examples and quick constants
    examples = [
        "󰍹  hbar = 1.054572e-34 J·s  (Reduced Planck)",
        "󰍹  kb   = 1.380649e-23 J/K  (Boltzmann Constant)",
        "󰍹  c    = 299792458 m/s     (Speed of Light)",
        "󰍹  G    = 6.674300e-11      (Gravitational Constant)",
        "󰍹  eV   = 1.602177e-19 J    (Electronvolt)",
        "󰍹  me   = 9.109384e-31 kg   (Electron Mass)",
        "󰍹  mp   = 1.672622e-27 kg   (Proton Mass)",
        "󰍹  Na   = 6.022141e+23      (Avogadro Number)",
        "󰍹  eps0 = 8.854188e-12 F/m  (Permittivity)",
        "󰍹  mu0  = 1.256637e-06 N/A² (Permeability)",
    ]
    for ex in examples:
        print(ex)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(0)
