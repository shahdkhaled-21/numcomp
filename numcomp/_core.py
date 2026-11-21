"""Core helper functions(every method uses them).
    1) validate :Validates sig_figs, mode, eps, max_iter, true_root in that order.
    2) default_eps : Returns the default value of eps based on sig_figs if eps is None.
    3) eps_a : Returns the approximate relative error between x_new and x_old.      
    4) sig_digits : Returns the number of significant digits based on eps and sig_figs.
    5) build_result : builds a RootResult object based on the given parameters.
    6) check_start : Checks if the starting point x is a valid number.
"""
import math
from time import perf_counter
from .expr import parse
from .machine import Machine
from .errors import BracketError
from .result import RootResult


def validate(sig_figs , mode , eps , max_iter , true_root):
    """Validates sig_figs, mode, eps, max_iter, true_root in that order."""
    if isinstance(sig_figs, bool) or (sig_figs is not None and not isinstance(sig_figs, int)):
        raise ValueError("sig_figs must be an integer or None")
    if sig_figs is not None and (sig_figs <= 0 or sig_figs > 12):
        raise ValueError("sig_figs must be a positive integer less than or equal to 12")
    if mode not in ["round", "chop"]:
        raise ValueError("mode must be either 'round' or 'chop'")
    if isinstance(eps, bool) or (eps is not None and not isinstance(eps, (int, float))):
        raise ValueError("eps must be a number(int or float) or None")
    try:
        if eps is not None and (eps <= 0 or not math.isfinite(eps)):
            raise ValueError("eps must be a positive finite number")
    except OverflowError:
        raise ValueError("eps must be a positive finite number")
    if isinstance(max_iter, bool) or not isinstance(max_iter, int) or max_iter <= 0:
        raise ValueError("max_iter must be a positive integer ")         
    if isinstance(true_root, bool) or (true_root is not None and not isinstance(true_root, (int, float))):
        raise ValueError("true_root must be a number(int or float) or None")
    try:
        if true_root is not None and not math.isfinite(true_root):
            raise ValueError("true_root must be a finite number")
    except OverflowError:
        raise ValueError("true_root must be a finite number")

def default_eps(sig_figs, eps):
    """Returns the default value of eps based on sig_figs if eps is None."""
    if eps is not None:
       return eps
    return 0.5 * 10 ** (2-sig_figs) if sig_figs is not None else 0.001

def eps_a(x_new, x_old):
    """Returns the approximate relative error between x_new and x_old."""
    if x_new == 0:
        if x_old == 0:
            return 0.0
        else:
            return math.inf
    
    return abs((x_new - x_old) / x_new)*100


def sig_digits(eps, sig_figs):
    """Returns the number of significant digits based on eps and sig_figs."""
    if sig_figs is not None:
        cap = sig_figs
    else :
        cap = 15
    if eps is not None:
        if eps == 0:
            return cap
        if math.isinf(eps):
            return 0
        return max(0,min(cap, math.floor( 2-math.log10(2*eps)) ))
    return None

def build_result(method, root, steps, stop_reason, residual, sig_figs, true_root, start_time):
    """ builds a RootResult object based on the given parameters."""
    ea = steps[-1]['ea'] if steps else None

    return RootResult(
      method=method,
        root = root,    
        iterations = len(steps),
        ea = ea,
        estimated_sig_figs= sig_digits(ea, sig_figs) if stop_reason != "stagnated" else None,
        true_sig_figs = sig_digits(eps_a(true_root, root), sig_figs) if (true_root is not None and true_root != 0) else None,
        stop_reason = stop_reason,
        residual = residual,
        steps = steps,
        time_s = perf_counter() - start_time,
        g_prime_x0 = None  # fixed point only; None if g' is unavailable (can be removed since it is set as default)
    )

def check_start(x, name):
    """Checks if the starting point x is a valid number."""
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise ValueError(f"{name} must be a number(int or float)")
    try:
        if not math.isfinite(x):
            raise ValueError(f"{name} must be a finite number")
    except OverflowError:
        raise ValueError(f"{name} must be a finite number")

def bracketing_set_up(f, xl, xu, sig_figs, mode, eps, max_iter, true_root):
    """does the initial setup for the bracketing methods, including validate the inputs , calculate eps , start the timer , parse  f , initiate machine object and enter xl and xu"""
    start_time = perf_counter()
    validate(sig_figs, mode, eps, max_iter, true_root)
    eps = default_eps(sig_figs, eps)
    parsed = parse(f)
    m = Machine(sig_figs, mode)
    check_start(xl, "xl")
    xl=m.enter(xl)
    check_start(xu, "xu")
    xu=m.enter(xu)
    if xl >= xu:
        raise ValueError("xl must be less than xu")
    return parsed, m, xl, xu, eps, start_time

def check_bracket(method , parsed, m, xl, xu, sig_figs, true_root, start_time):
    """Checks if the bracket [xl, xu] is valid for the function f."""
    fxl = parsed.evaluate(m, xl)
    fxu = parsed.evaluate(m, xu)
    if fxl == 0:
       return fxl,fxu , build_result(method, xl, [], "computed_zero",0.0, sig_figs,true_root ,start_time )
    if fxu == 0:
        return fxl,fxu , build_result(method, xu, [], "computed_zero",0.0, sig_figs, true_root ,start_time )
    if fxl >0 and fxu >0 or fxl <0 and fxu <0:
        raise BracketError(f"f(xl) = {fxl} and f(xu) = {fxu} have the same sign: [{xl}, {xu}] does not bracket a root")
    return fxl, fxu, None