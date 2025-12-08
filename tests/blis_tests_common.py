# Copyright ExplosionAI GmbH, released under BSD.
import numpy as np

np.random.seed(0)

from hypothesis import settings
from hypothesis.strategies import integers, floats
from hypothesis.extra.numpy import arrays

# Increase this to run more thorough tests
hypothesis_default_profile = settings.register_profile("default", max_examples=100)


def lengths(lo, hi):
    return integers(min_value=lo, max_value=hi)


def ndarrays_of_shape(shape, lo, hi, dtype):
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


def ndarrays(min_len, max_len, min_val, max_val, dtype):
    return lengths(lo=min_len, hi=max_len).flatmap(
        lambda n: ndarrays_of_shape(n, lo=min_val, hi=max_val, dtype=dtype)
    )
