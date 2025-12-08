# Copyright ExplosionAI GmbH, released under BSD.
from concurrent.futures import ThreadPoolExecutor
from hypothesis import settings
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays

# Increase this to run more thorough tests
hypothesis_default_profile = settings.register_profile("default", max_examples=200)

# (dtype, atol, rtol)
dtypes_tols = st.sampled_from(
    [
        # FIXME huge tolerance needed for float32:
        # https://github.com/explosion/cython-blis/issues/142
        ("float32", 1e-2, 1e-4),
        ("float64", 1e-9, 1e-9),
    ]
)


def ndarrays(shape, lo, hi, dtype):
    """Draw ND NumPy arrays of floats"""
    assert isinstance(dtype, str) and dtype.startswith("float")
    width = int(dtype[5:])
    elements = st.floats(min_value=lo, max_value=hi, width=width)
    return arrays(dtype, shape=shape, elements=elements)


def run_threaded(func, max_workers=8, outer_iterations=2):
    """Runs a function many times in parallel"""
    with ThreadPoolExecutor(max_workers=max_workers) as tpe:
        for _ in range(outer_iterations):
            futures = [tpe.submit(func) for _ in range(max_workers)]
            for f in futures:
                f.result()
