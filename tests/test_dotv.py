from __future__ import division
from hypothesis import given, assume, reproduce_failure
from math import sqrt, floor

from blis_tests_common import *
from blis.py import dotv
from blis.cy import NO_CONJUGATE, CONJUGATE


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


@reproduce_failure(
    "6.103.5", b"AXicY2AAggaXUAauVetzGBiBHMYGBjBgZATyGCFshhRGJgY4SGFkBmmCKmNAAgAMFQS/"
)
@reproduce_failure(
    "6.103.5", b"AXicE2NAAGsxRiDJCOUpMzIipJQZWYDkQY6POYVSFz8h6WEAAGinBSs="
)
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
    assert_allclose([numpy_result], result, atol=1e-2, rtol=1e-2)
