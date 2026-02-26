import numpy as np

def adstock(series, rate=0.5):
    result = []
    carry = 0
    for x in series:
        carry = x + carry * rate
        result.append(carry)
    return np.array(result)

def logistic_saturation(x, L=1, k=0.003, x0=5000):
    return L / (1 + np.exp(-k * (x - x0)))
