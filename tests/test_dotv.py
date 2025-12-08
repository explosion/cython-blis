# Copyright ExplosionAI GmbH, released under BSD.
from hypothesis import given, assume

from numpy.testing import assert_allclose
from blis_tests_common import ndarrays
from blis.py import dotv


@given(
    ndarrays(min_len=1, max_len=100, min_val=-100.0, max_val=100.0, dtype="float64"),
    ndarrays(min_len=1, max_len=100, min_val=-100.0, max_val=100.0, dtype="float64"),
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
    assert_allclose(result, numpy_result, atol=1e-9, rtol=1e-9)


@given(
    ndarrays(min_len=1, max_len=100, min_val=-100.0, max_val=100.0, dtype="float32"),
    ndarrays(min_len=1, max_len=100, min_val=-100.0, max_val=100.0, dtype="float32"),
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
    assert_allclose(result, numpy_result, atol=1e-2, rtol=1e-4)
