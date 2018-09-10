# cython: infer_types=True
# cython: boundscheck=False

import atexit


cdef extern from "blis.h" nogil:
    enum blis_err_t "err_t":
        pass


    cdef struct blis_cntx_t "cntx_t":
        pass


    ctypedef enum blis_trans_t "trans_t":
        BLIS_NO_TRANSPOSE
        BLIS_TRANSPOSE
        BLIS_CONJ_NO_TRANSPOSE
        BLIS_CONJ_TRANSPOSE

    ctypedef enum blis_conj_t "conj_t":
        BLIS_NO_CONJUGATE
        BLIS_CONJUGATE

    ctypedef enum blis_side_t "side_t":
        BLIS_LEFT
        BLIS_RIGHT

    ctypedef enum blis_uplo_t "uplo_t":
        BLIS_LOWER
        BLIS_UPPER
        BLIS_DENSE

    ctypedef enum blis_diag_t "diag_t":
        BLIS_NONUNIT_DIAG
        BLIS_UNIT_DIAG

    char* bli_info_get_int_type_size_str()

    blis_err_t bli_init()
    blis_err_t bli_finalize()


    # BLAS level 3 routines
    void bli_dgemm(
       blis_trans_t transa,
       blis_trans_t transb,
       dim_t   m,
       dim_t   n,
       dim_t   k,
       double*  alpha,
       double*  a, inc_t rsa, inc_t csa,
       double*  b, inc_t rsb, inc_t csb,
       double*  beta,
       double*  c, inc_t rsc, inc_t csc,
    )
    # BLAS level 3 routines
    void bli_sgemm(
       blis_trans_t transa,
       blis_trans_t transb,
       dim_t   m,
       dim_t   n,
       dim_t   k,
       float*  alpha,
       float*  a, inc_t rsa, inc_t csa,
       float*  b, inc_t rsb, inc_t csb,
       float*  beta,
       float*  c, inc_t rsc, inc_t csc,
    )

    void bli_dger(
       blis_conj_t  conjx,
       blis_conj_t  conjy,
       dim_t   m,
       dim_t   n,
       double*  alpha,
       double*  x, inc_t incx,
       double*  y, inc_t incy,
       double*  a, inc_t rsa, inc_t csa,
    )

    void bli_sger(
       blis_conj_t  conjx,
       blis_conj_t  conjy,
       dim_t   m,
       dim_t   n,
       float*  alpha,
       float*  x, inc_t incx,
       float*  y, inc_t incy,
       float*  a, inc_t rsa, inc_t csa,
    )

    void bli_dgemv(
       blis_trans_t transa,
       blis_conj_t  conjx,
       dim_t   m,
       dim_t   n,
       double*  alpha,
       double*  a, inc_t rsa, inc_t csa,
       double*  x, inc_t incx,
       double*  beta,
       double*  y, inc_t incy,
     )

    void bli_sgemv(
       blis_trans_t transa,
       blis_conj_t  conjx,
       dim_t   m,
       dim_t   n,
       float*  alpha,
       float*  a, inc_t rsa, inc_t csa,
       float*  x, inc_t incx,
       float*  beta,
       float*  y, inc_t incy,
     )

    void bli_daxpyv(
       blis_conj_t  conjx,
       dim_t   m,
       double*  alpha,
       double*  x, inc_t incx,
       double*  y, inc_t incy,
     )

    void bli_saxpyv(
       blis_conj_t  conjx,
       dim_t   m,
       float*  alpha,
       float*  x, inc_t incx,
       float*  y, inc_t incy,
     )

    void bli_dscalv(
       blis_conj_t  conjalpha,
       dim_t   m,
       double*  alpha,
       double*  x, inc_t incx,
    )

    void bli_sscalv(
       blis_conj_t  conjalpha,
       dim_t   m,
       float*  alpha,
       float*  x, inc_t incx,
    )

    void bli_ddotv(
       blis_conj_t  conjx,
       blis_conj_t  conjy,
       dim_t   m,
       double*  x, inc_t incx,
       double*  y, inc_t incy,
       double*  rho,
    )

    void bli_sdotv(
       blis_conj_t  conjx,
       blis_conj_t  conjy,
       dim_t   m,
       float*  x, inc_t incx,
       float*  y, inc_t incy,
       float*  rho,
    )

    void bli_snorm1v(
       dim_t n,
       float* x, inc_t incx,
       float* norm,
    )

    void bli_dnorm1v(
       dim_t   n,
       double* x, inc_t incx,
       double* norm,
    )

    void bli_snormfv(
       dim_t   n,
       float*  x, inc_t incx,
       float*  norm,
    )

    void bli_dnormfv(
       dim_t   n,
       double*  x, inc_t incx,
       double*  norm,
    )

    void bli_snormiv(
       dim_t   n,
       float*  x, inc_t incx,
       float*  norm,
    )

    void bli_dnormiv(
       dim_t   n,
       double*  x, inc_t incx,
       double*  norm,
    )

    void bli_srandv(
        dim_t   m,
        float*  x, inc_t incx,
    )

    void bli_drandv(
        dim_t   m,
        double*  x, inc_t incx,
    )

    void bli_ssumsqv(
        dim_t   m,
        float*  x, inc_t incx,
        float*  scale,
        float*  sumsq,
    ) nogil

    void bli_dsumsqv(
        dim_t   m,
        double*  x, inc_t incx,
        double*  scale,
        double*  sumsq,
    ) nogil



bli_init()
def init():
    bli_init()
    assert BLIS_NO_TRANSPOSE == <blis_trans_t>NO_TRANSPOSE
    assert BLIS_TRANSPOSE == <blis_trans_t>TRANSPOSE
    assert BLIS_CONJ_NO_TRANSPOSE == <blis_trans_t>CONJ_NO_TRANSPOSE
    assert BLIS_CONJ_TRANSPOSE == <blis_trans_t>CONJ_TRANSPOSE
    assert BLIS_NO_CONJUGATE == <blis_conj_t>NO_CONJUGATE
    assert BLIS_CONJUGATE == <blis_conj_t>CONJUGATE
    assert BLIS_LEFT == <blis_side_t>LEFT
    assert BLIS_RIGHT == <blis_side_t>RIGHT
    assert BLIS_LOWER == <blis_uplo_t>LOWER
    assert BLIS_UPPER == <blis_uplo_t>UPPER
    assert BLIS_DENSE == <blis_uplo_t>DENSE
    assert BLIS_NONUNIT_DIAG == <blis_diag_t>NONUNIT_DIAG
    assert BLIS_UNIT_DIAG == <blis_diag_t>UNIT_DIAG


def get_int_type_size():
    cdef char* int_size = bli_info_get_int_type_size_str()
    return '%d' % int_size[0]


# BLAS level 3 routines
cdef void gemm(
    trans_t trans_a,
    trans_t trans_b,
    dim_t   m,
    dim_t   n,
    dim_t   k,
    double  alpha,
    reals_ft  a, inc_t rsa, inc_t csa,
    reals_ft  b, inc_t rsb, inc_t csb,
    double  beta,
    reals_ft  c, inc_t rsc, inc_t csc
) nogil:
    cdef float alpha_f = alpha
    cdef float beta_f = beta
    cdef double alpha_d = alpha
    cdef double beta_d = beta
    if reals_ft is floats_t:
        bli_sgemm(
            <blis_trans_t>trans_a, <blis_trans_t>trans_b,
            m, n, k,
            &alpha_f, a, rsa, csa, b, rsb, csb, &beta_f, c, rsc, csc)
    elif reals_ft is doubles_t:
        bli_dgemm(
            <blis_trans_t>trans_a, <blis_trans_t>trans_b,
            m, n, k,
            &alpha_d, a, rsa, csa, b, rsb, csb, &beta_d, c, rsc, csc)
    elif reals_ft is float1d_t:
        bli_sgemm(
            <blis_trans_t>trans_a, <blis_trans_t>trans_b,
            m, n, k,
            &alpha_f, &a[0], rsa, csa, &b[0], rsb, csb, &beta_f, &c[0],
            rsc, csc)
    elif reals_ft is double1d_t:
        bli_dgemm(
            <blis_trans_t>trans_a, <blis_trans_t>trans_b,
            m, n, k,
            &alpha_d, &a[0], rsa, csa, &b[0], rsb, csb, &beta_d, &c[0],
            rsc, csc)
    else:
        # Impossible --- panic?
        pass


cdef void ger(
    conj_t  conjx,
    conj_t  conjy,
    dim_t   m,
    dim_t   n,
    double  alpha,
    reals_ft  x, inc_t incx,
    reals_ft  y, inc_t incy,
    reals_ft  a, inc_t rsa, inc_t csa
) nogil:
    cdef float alpha_f = alpha
    cdef double alpha_d = alpha
    if reals_ft is floats_t:
        bli_sger(
            <blis_conj_t>conjx, <blis_conj_t>conjy,
            m, n,
            &alpha_f,
            x, incx, y, incy, a, rsa, csa)
    elif reals_ft is doubles_t:
        bli_dger(
            <blis_conj_t>conjx, <blis_conj_t>conjy,
            m, n,
            &alpha_d,
            x, incx, y, incy, a, rsa, csa)
    elif reals_ft is float1d_t:
        bli_sger(
            <blis_conj_t>conjx, <blis_conj_t>conjy,
            m, n,
            &alpha_f,
            &x[0], incx, &y[0], incy, &a[0], rsa, csa)
    elif reals_ft is double1d_t:
        bli_dger(
            <blis_conj_t>conjx, <blis_conj_t>conjy,
            m, n,
            &alpha_d,
            &x[0], incx, &y[0], incy, &a[0], rsa, csa)
    else:
        # Impossible --- panic?
        pass


cdef void gemv(
    trans_t transa,
    conj_t  conjx,
    dim_t   m,
    dim_t   n,
    real_ft  alpha,
    reals_ft  a, inc_t rsa, inc_t csa,
    reals_ft  x, inc_t incx,
    real_ft  beta,
    reals_ft  y, inc_t incy
) nogil:
    cdef float alpha_f = alpha
    cdef double alpha_d = alpha
    cdef float beta_f = alpha
    cdef double beta_d = alpha
    if reals_ft is floats_t:
        bli_sgemv(
            <blis_trans_t>transa, <blis_conj_t>conjx,
            m, n,
            &alpha_f, a, rsa, csa,
            x, incx, &beta_f,
            y, incy)
    elif reals_ft is doubles_t:
        bli_dgemv(
            <blis_trans_t>transa, <blis_conj_t>conjx,
            m, n,
            &alpha_d, a, rsa, csa,
            x, incx, &beta_d,
            y, incy)
    elif reals_ft is float1d_t:
        bli_sgemv(
            <blis_trans_t>transa, <blis_conj_t>conjx,
            m, n,
            &alpha_f, &a[0], rsa, csa,
            &x[0], incx, &beta_f,
            &y[0], incy)
    elif reals_ft is double1d_t:
        bli_dgemv(
            <blis_trans_t>transa, <blis_conj_t>conjx,
            m, n,
            &alpha_d, &a[0], rsa, csa,
            &x[0], incx, &beta_d,
            &y[0], incy)
    else:
        # Impossible --- panic?
        pass


cdef void axpyv(
    conj_t  conjx,
    dim_t   m,
    real_ft  alpha,
    reals_ft  x, inc_t incx,
    reals_ft  y, inc_t incy
) nogil:
    cdef float alpha_f = alpha
    cdef double alpha_d = alpha
    if reals_ft is floats_t:
        bli_saxpyv(<blis_conj_t>conjx, m,  &alpha_f, x, incx, y, incy)
    elif reals_ft is doubles_t:
        bli_daxpyv(<blis_conj_t>conjx, m,  &alpha_d, x, incx, y, incy)
    elif reals_ft is float1d_t:
        bli_saxpyv(<blis_conj_t>conjx, m,  &alpha_f, &x[0], incx, &y[0], incy)
    elif reals_ft is double1d_t:
        bli_daxpyv(<blis_conj_t>conjx, m,  &alpha_d, &x[0], incx, &y[0], incy)
    else:
        # Impossible --- panic?
        pass


cdef void scalv(
    conj_t  conjalpha,
    dim_t   m,
    real_ft  alpha,
    reals_ft  x, inc_t incx
) nogil:
    cdef float alpha_f = alpha
    cdef double alpha_d = alpha
    if reals_ft is floats_t:
        bli_sscalv(<blis_conj_t>conjalpha, m, &alpha_f, x, incx)
    elif reals_ft is doubles_t:
        bli_dscalv(<blis_conj_t>conjalpha, m, &alpha_d, x, incx)
    elif reals_ft is float1d_t:
        bli_sscalv(<blis_conj_t>conjalpha, m, &alpha_f, &x[0], incx)
    elif reals_ft is double1d_t:
        bli_dscalv(<blis_conj_t>conjalpha, m, &alpha_d, &x[0], incx)
    else:
        # Impossible --- panic?
        pass


cdef double norm_L1(
    dim_t n,
    reals_ft x, inc_t incx
) nogil:
    cdef double dnorm = 0
    cdef float snorm = 0
    if reals_ft is floats_t:
        bli_snorm1v(n, x, incx, &snorm)
        dnorm = snorm
    elif reals_ft is doubles_t:
        bli_dnorm1v(n, x, incx, &dnorm)
    elif reals_ft is float1d_t:
        bli_snorm1v(n, &x[0], incx, &snorm)
        dnorm = snorm
    elif reals_ft is double1d_t:
        bli_dnorm1v(n, &x[0], incx, &dnorm)
    else:
        # Impossible --- panic?
        pass
    return dnorm


cdef double norm_L2(
    dim_t n,
    reals_ft x, inc_t incx
) nogil:
    cdef double dnorm = 0
    cdef float snorm = 0
    if reals_ft is floats_t:
        bli_snormfv(n, x, incx, &snorm)
        dnorm = snorm
    elif reals_ft is doubles_t:
        bli_dnormfv(n, x, incx, &dnorm)
    elif reals_ft is float1d_t:
        bli_snormfv(n, &x[0], incx, &snorm)
        dnorm = snorm
    elif reals_ft is double1d_t:
        bli_dnormfv(n, &x[0], incx, &dnorm)
    else:
        # Impossible --- panic?
        pass
    return dnorm


cdef double norm_inf(
    dim_t n,
    reals_ft x, inc_t incx
) nogil:
    cdef double dnorm = 0
    cdef float snorm = 0
    if reals_ft is floats_t:
        bli_snormiv(n, x, incx, &snorm)
        dnorm = snorm
    elif reals_ft is doubles_t:
        bli_dnormiv(n, x, incx, &dnorm)
    elif reals_ft is float1d_t:
        bli_snormiv(n, &x[0], incx, &snorm)
        dnorm = snorm
    elif reals_ft is double1d_t:
        bli_dnormiv(n, &x[0], incx, &dnorm)
    else:
        # Impossible --- panic?
        pass
    return dnorm


cdef double dotv(
    conj_t  conjx,
    conj_t  conjy,
    dim_t   m,
    reals_ft x,
    reals_ft y,
    inc_t incx,
    inc_t incy,
) nogil:
    cdef double rho_d = 0.0
    cdef float rho_f = 0.0
    if reals_ft is floats_t:
        bli_sdotv(<blis_conj_t>conjx, <blis_conj_t>conjy, m, x, incx, y, incy, &rho_f)
        return rho_f
    elif reals_ft is doubles_t:
        bli_ddotv(<blis_conj_t>conjx, <blis_conj_t>conjy, m, x, incx, y, incy, &rho_d)
        return rho_d
    elif reals_ft is float1d_t:
        bli_sdotv(<blis_conj_t>conjx, <blis_conj_t>conjy, m, &x[0], incx, &y[0], incy,
                  &rho_f)
        return rho_f
    elif reals_ft is double1d_t:
        bli_ddotv(<blis_conj_t>conjx, <blis_conj_t>conjy, m, &x[0], incx, &y[0], incy,
                  &rho_d)
        return rho_d
    else:
        raise ValueError("Unhandled fused type")


cdef void randv(dim_t m, reals_ft x, inc_t incx) nogil:
    if reals_ft is floats_t:
        bli_srandv(m, x, incx)
    elif reals_ft is float1d_t:
        bli_srandv(m, &x[0], incx)
    if reals_ft is doubles_t:
        bli_drandv(m, x, incx)
    elif reals_ft is double1d_t:
        bli_drandv(m, &x[0], incx)
    else:
        with gil:
            raise ValueError("Unhandled fused type")


cdef void sumsqv(dim_t   m, reals_ft  x, inc_t incx,
        reals_ft scale, reals_ft sumsq) nogil:
    if reals_ft is floats_t:
        bli_ssumsqv(m, &x[0], incx, scale, sumsq)
    elif reals_ft is float1d_t:
        bli_ssumsqv(m, &x[0], incx, &scale[0], &sumsq[0])
    if reals_ft is doubles_t:
        bli_dsumsqv(m, x, incx, scale, sumsq)
    elif reals_ft is double1d_t:
        bli_dsumsqv(m, &x[0], incx, &scale[0], &sumsq[0])
    else:
        with gil:
            raise ValueError("Unhandled fused type")


@atexit.register
def finalize():
    bli_finalize()
