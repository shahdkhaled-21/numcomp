"""Simulated n-significant-figure decimal machine.  YOU WRITE THIS FILE.

Read README.md, section 2 "The machine", before starting.
Rules: no `decimal`, no built-in `round()`, no `Fraction.__round__`.
`fractions.Fraction` and `math` are allowed.
"""

from __future__ import annotations

from fractions import Fraction

from .errors import DivergenceError  # noqa: F401  (you will raise it)

import math

MODES = ("round", "chop")
MAX_SIG_FIGS = 12


def round_sig(value: float, n: int | None, mode: str = "round") -> float:
    """Round ``value`` to ``n`` significant figures.

    mode "round": half away from zero (2.675 -> 2.68, -2.5 -> -3 at n=1).
    mode "chop":  toward zero (3.1415926535 -> 3.141592 at n=7).
    n None: no decimal rounding, just convert to float (inputs are still
    validated and the result is never -0.0). Raise ValueError for bad n / mode,
    DivergenceError for inf / nan or a result too large for a float.
    """
    if n is not None and (type(n) is not int or n < 1 or n > 12):
        raise ValueError(f"sig_figs must be an int in 1..12 or None, got {n}")

    if mode != "chop" and mode != "round" :
        raise ValueError(f"mode must be 'round' or 'chop', got {mode!r}")

    if isinstance(value, bool):
        raise ValueError("booleans are not numbers here")

    if not isinstance(value, (int, float, Fraction)):
        raise ValueError(f"expected an int, float or Fraction, got {type(value).__name__}")

    if type(value) is float and not math.isfinite(value):
        raise DivergenceError("value is inf or nan")
    
    value = Fraction(repr(value)) if type(value) is float else Fraction(value)

    if n is None:
        try :
            res = float(value)
        except OverflowError:
           raise DivergenceError("result too large for a float")
        if res == 0:
            return float(0)
        else:
            return float(res)
       

    if value == 0:
        return float(0)

    e = 0
    sign = 0
    w_value = value

    if w_value < 0:
        sign = 1
        w_value *= -1

    if w_value >= 1 :
        while w_value >= 10 :
            w_value /= 10
            e += 1
    else :
        while w_value < 1 :
            w_value *= 10
            e -= 1

    if (e - n + 1) < 0:
        scaled = abs(value) * 10**abs(e - n + 1)
    else:
        scaled = abs(value) / 10**abs(e - n + 1)

    num = scaled // Fraction(1)

    if Fraction(scaled - num) >= Fraction(1, 2) and mode == "round":
        num += 1

    if (e - n + 1) < 0:
        f_value = Fraction(num, 10**abs(e - n + 1))
    else:
        f_value = num * 10**abs(e - n + 1)

    try :
        res = float(f_value)
    except OverflowError:
        raise DivergenceError("result too large for a float")

    if res == 0:
        return float(0)
    else:
        return float(-1*res) if sign else float(res)


class Machine:
    """Every method returns a float holding an exact n-digit decimal."""

    def __init__(self, sig_figs: int | None = None, mode: str = "round"):
        round_sig(1, sig_figs, mode)
        self.sig_figs = sig_figs
        self.mode = mode

    def enter(self, value: int | float | Fraction) -> float:
        """Store an input number (literal, constant, initial guess): one rounding."""
        return round_sig(value, self.sig_figs, self.mode)

    def add(self, a: float, b: float) -> float:
        if self.sig_figs is None:
            res = a + b
        else:
            res = Fraction(repr(a)) + Fraction(repr(b))

        return round_sig(res, self.sig_figs, self.mode)

    def sub(self, a: float, b: float) -> float:
        if self.sig_figs is None:
            res = a - b
        else:
            res = Fraction(repr(a)) - Fraction(repr(b))
        
        return round_sig(res, self.sig_figs, self.mode)

    def mul(self, a: float, b: float) -> float:
        if self.sig_figs is None:
            res = a * b
        else:
            res = Fraction(repr(a)) * Fraction(repr(b))
        
        return round_sig(res, self.sig_figs, self.mode)   

    def div(self, a: float, b: float) -> float:
        """Raise ZeroDivisionError when b == 0."""
        if b == 0:
            raise ZeroDivisionError("division by zero")
        
        if self.sig_figs is None:
            res = a / b
        else:
            res = Fraction(repr(a)) / Fraction(repr(b))
        
        return round_sig(res, self.sig_figs, self.mode)   
        

    def pow_int(self, a: float, k: int) -> float:
        """a**k by repeated multiplication from the left, rounding each product.
        k == 0 -> 1; k < 0 -> one rounded reciprocal of a**(-k)."""
        if k == 0:
            return self.enter(1)
        elif k < 0:
            return self.div(self.enter(1), self.pow_int(a, -k))
        else:
            r = a
            for i in range(k - 1):
                r = self.mul(r, a)

            return r

    def call(self, name: str, a: float) -> float:
        """exp, sin, cos, tan, ln, sqrt: computed with `math` in double, then
        rounded once. Let math's ValueError (domain error) propagate; turn
        overflow into DivergenceError."""

        look = {"exp" : math.exp, "sin" : math.sin, "cos" : math.cos,
                "tan" : math.tan, "ln" : math.log, "sqrt" : math.sqrt}

        if name not in look:
            raise ValueError(f"{name} not supported")

        try:
            func = look[name]
            return self.enter(func(a))
        except OverflowError:
            raise DivergenceError("result too large for a float")
