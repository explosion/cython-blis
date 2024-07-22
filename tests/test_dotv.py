from __future__ import division
from hypothesis import given, assume
import numpy

from blis_tests_common import *
from blis.py import dotv


@given(
    ndarrays(min_len=10, max_len=100, min_val=-100.0, max_val=100.0, dtype="float64"),
    ndarrays(min_len=10, max_len=100, min_val=-100.0, max_val=100.0, dtype="float64"),
)
def test_memoryview_double_noconj(A, B):
    if len(A) < len(B):
        B = B[: len(A)]
    else:
        A = A[: len(B)]
    assume(A is not None)
    assume(B is not None)
    numpy_result = A.dot(B)
    result = dotv(A, B)
    assert_allclose([numpy_result], result, atol=1e-3, rtol=1e-3)


@given(
    ndarrays(min_len=10, max_len=100, min_val=-100.0, max_val=100.0, dtype="float32"),
    ndarrays(min_len=10, max_len=100, min_val=-100.0, max_val=100.0, dtype="float32"),
)
def test_memoryview_float_noconj(A, B):
    if len(A) < len(B):
        B = B[: len(A)]
    else:
        A = A[: len(B)]
    assume(A is not None)
    assume(B is not None)
    numpy_result = A.dot(B)
    result = dotv(A, B)
    # We want to also know the true(r) answer, if one of them is off.
    A_float64 = A.astype(numpy.float64)
    B_float64 = B.astype(numpy.float64)
    numpy_result64 = A_float64.dot(B_float64)
    blis_result64 = dotv(A_float64, B_float64)
    try:
        assert_allclose(
            [numpy_result],
            result,
            atol=1e-3,
            rtol=1e-3,
        )
    except AssertionError as e:
        # Probably better to make a combined message, but eh
        print(f"Numpy 64bit result: {numpy_result64}")
        print(f"blis 64bit result: {blis_result64}")
        raise e
