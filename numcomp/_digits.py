import math

def digits(error_percent, sig_figs):
    cap = sig_figs if sig_figs is not None else 15

    if error_percent is None:
        return None
    elif error_percent == 0:
        return cap
    elif math.isinf(error_percent):
        return 0
    
    return max(0, min(math.floor(2 - math.log10(2 * error_percent)), cap))