# Copyright ExplosionAI GmbH, released under BSD.
import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st
from numpy.testing import assert_allclose

from blis_tests_common import dtypes_tols, ndarrays, run_threaded
from blis.py import gemm


@st.composite
def gemm_arrays(draw):
    """Draw two NumPy arrays with shapes (l, m) and (m, n) of the same dtype"""
    max_size = 100
    l = draw(st.integers(min_value=1, max_value=max_size))  # noqa: E741
    n = draw(st.integers(min_value=1, max_value=max_size))
    m = draw(st.integers(min_value=1, max_value=max_size // max(l, n)))
    dtype, atol, rtol = draw(dtypes_tols)
    A = draw(ndarrays((l, m), lo=-100.0, hi=100.0, dtype=dtype))
    B = draw(ndarrays((m, n), lo=-100.0, hi=100.0, dtype=dtype))
    return A, B, atol, rtol


def test_incompatible_shape():
    with pytest.raises(ValueError):
        gemm(np.zeros((2, 2)), np.zeros((3, 2)))
    with pytest.raises(ValueError):
        gemm(np.zeros((3, 2)), np.zeros((2, 2)), trans1=True)
    with pytest.raises(ValueError):
        gemm(np.zeros((2, 2)), np.zeros((2, 3)), trans2=True)
    with pytest.raises(ValueError):
        gemm(np.zeros((3, 2)), np.zeros((3, 2)), trans1=True, trans2=True)


@given(gemm_arrays())
def test_memoryview_notrans(arrays):
    A, B, atol, rtol = arrays
    numpy_result = A.dot(B)
    C = np.zeros_like(numpy_result)  # (l, n)
    gemm(A, B, out=C)
    assert_allclose(C, numpy_result, atol=atol, rtol=rtol)


@given(gemm_arrays())
@pytest.mark.thread_unsafe(reason="Uses run_threaded")
def test_threads_share_input(arrays):
    """Test when multiple threads share the same input arrays."""
    A, B, atol, rtol = arrays
    numpy_result = A.dot(B)

    def f():
        C = np.zeros_like(numpy_result)  # (l, n)
        gemm(A, B, out=C)
        assert_allclose(C, numpy_result, atol=atol, rtol=rtol)

    run_threaded(f)
