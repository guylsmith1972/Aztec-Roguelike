import numpy as np
import scipy.signal


def find_before(lst, num):
    i = lst.index(num)
    return lst[i - 1] if i > 0 else lst[0]

def find_after(lst, num):
    i = lst.index(num)
    return lst[i + 1] if i < len(lst) - 1 else lst[-1]
