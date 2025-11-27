# Copyright ExplosionAI GmbH, released under BSD.
import numpy as np

np.random.seed(0)

from hypothesis.strategies import tuples, integers, floats
from hypothesis.extra.numpy import arrays


def lengths(lo=1, hi=10):
    return integers(min_value=lo, max_value=hi)


def ndarrays_of_shape(shape, lo=-1000.0, hi=1000.0, dtype="float64"):
    width = 64 if dtype == "float64" else 32
    return arrays(
        dtype,
        shape=shape,
        elements=floats(
            min_value=lo,
            max_value=hi,
            width=width,
        ),
    )


def ndarrays(
    min_len=0, max_len=10, min_val=-10000000.0, max_val=1000000.0, dtype="float64"
):
    return lengths(lo=min_len, hi=max_len).flatmap(
        lambda n: ndarrays_of_shape(n, lo=min_val, hi=max_val, dtype=dtype)
    )
