"""Root-finding methods on the simulated machine.  YOU WRITE THIS FILE.

Read README.md, sections 4 "Methods" and 5 "Result and errors", before starting.
Every method takes ``f`` (or ``g``) as a string or a parsed Expression and
returns a RootResult. Use Machine operations for every arithmetic step of the
method's formula, in exactly the order given in the README.
"""

from __future__ import annotations

from .result import RootResult
from time import perf_counter
from ._core import  validate, default_eps, check_start, eps_a, build_result , bracketing_set_up , check_bracket
from .expr import parse
from .machine import Machine
from .errors import BracketError ,NumCompError


def bisection(f, xl, xu, *, sig_figs=None, mode="round", eps=None, max_iter=50, true_root=None) -> RootResult:
    """xr = (xl + xu) / 2.
    first the set up : validate the inputs , calculate eps , start the timer , parse  f , initiate machine object and enter xl and xu
    Checks before the loop: xl < xu or a ValueError; an exact zero at either end returns right away; the same-sign BracketError
    The loop : compute xr , then f(xr) , compute the ea , shrink the interval, append the row , then check for a reason for stopping
    After the loop: if you ran out of iterations, the stop reason is "max_iter". Then build the result.
    """
    parsed, m, xl, xu, eps, start_time = bracketing_set_up(f, xl, xu, sig_figs, mode, eps, max_iter, true_root)
    fxl, fxu, early = check_bracket("bisection", parsed, m, xl, xu, sig_figs, true_root, start_time)
    if early is not None:
        return early
    steps = []
    try:
        for i in range(1, max_iter + 1):
            xr = m.div(m.add(xl, xu), m.enter(2))
            fxr = parsed.evaluate(m, xr)
            ea = eps_a(xr, xr_old) if i > 1 else None
            rows = {"i": i, "xl": xl, "f_xl": fxl, "xu": xu, "f_xu": fxu, "xr": xr, "f_xr": fxr, "ea": ea}
            steps.append(rows)
            if fxr == 0:
                return build_result("bisection", xr, steps, "computed_zero", fxr, sig_figs, true_root, start_time)
            if xr >= xu or xr <= xl:
                return build_result("bisection", xr, steps, "stagnated", fxr, sig_figs, true_root, start_time)
            if ea is not None and ea <= eps:
                return build_result("bisection", xr, steps, "tolerance", fxr, sig_figs, true_root, start_time)
            if fxl < 0 and fxr > 0 or fxl > 0 and fxr < 0:
                xu = xr
                fxu = fxr
            else:
                xl = xr
                fxl = fxr
            xr_old = xr
           
    except NumCompError as exc:
        exc.steps = steps
        raise  
    return build_result("bisection", xr, steps, "max_iter", fxr, sig_figs, true_root ,start_time)


def false_position(f, xl, xu, *, sig_figs=None, mode="round", eps=None, max_iter=50, true_root=None) -> RootResult:
    """xr = xu - (f(xu) * (xl - xu)) / (f(xl) - f(xu)).
    first the set up : validate the inputs , calculate eps , start the timer , parse  f , initiate machine object and enter xl and xu
        Checks before the loop: xl < xu or a ValueError; an exact zero at either end returns right away; the same-sign BracketError
        The loop : compute xr , then f(xr) , compute the ea , shrink the interval, append the row , then check for a reason for stopping
        After the loop: if you ran out of iterations, the stop reason is "max_iter". Then build the result.
    """
    parsed, m, xl, xu, eps, start_time = bracketing_set_up(f, xl, xu, sig_figs, mode, eps, max_iter, true_root)
    fxl, fxu, early = check_bracket("false_position", parsed, m, xl, xu, sig_figs, true_root, start_time)
    if early is not None:
        return early
    steps = []
    try:
        for i in range(1, max_iter + 1):
            a = m.sub(xl, xu)
            b = m.sub(fxl, fxu)
            c = m.mul(fxu, a)
            d = m.div(c, b)
            xr = m.sub(xu, d)


            fxr = parsed.evaluate(m, xr)
            ea = eps_a(xr, xr_old) if i > 1 else None
            rows = {"i": i, "xl": xl, "f_xl": fxl, "xu": xu, "f_xu": fxu, "xr": xr, "f_xr": fxr, "ea": ea}
            steps.append(rows)
            if fxr == 0:
                return build_result("false_position", xr, steps, "computed_zero", fxr, sig_figs, true_root ,start_time )
            if xr >= xu or xr <= xl:
                return build_result("false_position", xr, steps, "stagnated", fxr, sig_figs, true_root ,start_time )
            if ea is not None and ea <= eps:
                return build_result("false_position", xr, steps, "tolerance", fxr, sig_figs, true_root ,start_time )
            if fxl < 0 and fxr > 0 or fxl > 0 and fxr < 0:
                xu = xr
                fxu = fxr
            else:
                xl = xr
                fxl = fxr
            xr_old = xr
    except NumCompError as exc:
            exc.steps = steps
            raise
    return build_result("false_position", xr, steps, "max_iter", fxr, sig_figs, true_root ,start_time ) 
    


def fixed_point(g, x0, *, sig_figs=None, mode="round", eps=None, max_iter=50, true_root=None) -> RootResult:
    """x_{i+1} = g(x_i)."""
    raise NotImplementedError


def newton(f, x0, *, sig_figs=None, mode="round", eps=None, max_iter=50, true_root=None) -> RootResult:
    """x_{i+1} = x_i - f(x_i) / f'(x_i)."""
    raise NotImplementedError


def modified_newton(f, x0, *, sig_figs=None, mode="round", eps=None, max_iter=50, true_root=None) -> RootResult:
    """x_{i+1} = x_i - (f f') / (f' f' - f f'')."""
    raise NotImplementedError


def secant(f, x0, x1, *, sig_figs=None, mode="round", eps=None, max_iter=50, true_root=None) -> RootResult:
    """x_{i+1} = x_i - (f(x_i) * (x_{i-1} - x_i)) / (f(x_{i-1}) - f(x_i))."""
    raise NotImplementedError
