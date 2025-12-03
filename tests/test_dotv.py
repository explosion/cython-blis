# Copyright ExplosionAI GmbH, released under BSD.
import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st
from numpy.testing import assert_allclose

from blis_tests_common import dtypes_tols, ndarrays, run_threaded
from blis.py import dotv


@st.composite
def dotv_arrays(draw):
    """Draw two 1D NumPy arrays of the same size and dtype"""
    size = draw(st.integers(min_value=1, max_value=100))
    dtype, atol, rtol = draw(dtypes_tols)
    arr_st = ndarrays((size,), lo=-100.0, hi=100.0, dtype=dtype)
    return draw(arr_st), draw(arr_st), atol, rtol


def test_incompatible_shape():
    with pytest.raises(ValueError):
        dotv(np.zeros(2), np.zeros(3))


@given(dotv_arrays())
def test_memoryview_noconj(arrays):
    A, B, atol, rtol = arrays
    numpy_result = A.dot(B)
    result = dotv(A, B)
    assert_allclose(result, numpy_result, atol=atol, rtol=rtol)


@given(dotv_arrays())
@pytest.mark.thread_unsafe(reason="Uses run_threaded")
def test_threads_share_input(arrays):
    """Test when multiple threads share the same input arrays."""
    A, B, atol, rtol = arrays
    numpy_result = A.dot(B)

    def f():
        result = dotv(A, B)
        assert_allclose(result, numpy_result, atol=atol, rtol=rtol)

    run_threaded(f)
