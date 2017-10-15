Cython BLIS: Fast BLAS-like operations from Python and Cython, without the tears
================================================================================

This repository provides the `Blis linear algebra <https://github.com/flame/blis>`_
as a self-contained Python C-extension.

.. image:: https://img.shields.io/pypi/v/blis.svg?style=flat-square
    :target: https://pypi.python.org/pypi/blis
    :alt: pypi Version

You can install the package via pip, optionally specifying your machine's
architecture via an environment variable:

.. code:: bash

    BLIS_ARCH=haswell pip install blis

After installation, run a small matrix multiplication benchmark:

.. code:: bash

    $ python -m blis.benchmark
    Setting up data nO=384 nI=384 batch_size=2000. Running 1000 iterations
    Blis...
    Total: 11032014.6484
    7.35 seconds
    Numpy (Openblas)...
    Total: 11032016.6016
    16.81 seconds
    Blis einsum ab,cb->ca
    8.10 seconds
    Numpy (openblas) einsum ab,cb->ca
    Total: 5510596.19141
    83.18 seconds

This is on a Dell XPS 13 i7-7500U. Running the same benchmark on a 2015 Macbook
Air gives:

.. code:: bash

    Blis...
    Total: 11032014.6484
    8.89 seconds
    Numpy (Accelerate)...
    Total: 11032012.6953
    6.68 seconds

It might be that Openblas is performing poorly on the relatively small
matrices (which are typically the sizes typical for neural network models).

Usage
-----

Two APIs are provided: a high-level Python API, and direct
`Cython <http://cython.org>`_ access. The best part of the Python API is the
`einsum function <https://obilaniu6266h16.wordpress.com/2016/02/04/einstein-summation-in-numpy/>`_,
which works like numpy's, but with some restrictions that allow
a direct mapping to Blis routines. Example usage:

.. code:: python

    from blis.py import einsum
    from numpy import ndarray, zeros

    dim_a = 500
    dim_b = 128
    dim_c = 300
    arr1 = ndarray((dim_a, dim_b))
    arr2 = ndarray((dim_b, dim_c))
    out = zeros((dim_a, dim_c))

    einsum('ab,bc->ac', arr1, arr2, out=out)
    # Change dimension order of output
    out = einsum('ab,bc->ca', arr1, arr2)
    assert out.shape == (dim_a, dim_c)
    # Matrix vector product, with transposed output
    arr2 = ndarray((dim_b,))
    out = einsum('ab,b->ba', arr1, arr2)
    assert out.shape == (dim_b, dim_a)

The Einstein summation format is really awesome, so it's always been
disappointing that it's so much slower than equivalent calls to ``tensordot``
in numpy. The ``blis.einsum`` function gives up the numpy version's generality,
so that calls can be easily mapped to Blis:

* Only two input tensors
* Maximum two dimensions
* Dimensions must be labelled ``a``, ``b`` and ``c``
* The first argument's dimensions must be ``'a'`` (for 1d inputs) or ``'ab'`` (for 2d inputs).

With these restrictions, there are ony 15 valid combinations – which
correspond to all the things you would otherwise do with the ``gemm``, ``gemv``,
``ger`` and ``axpy`` functions. You can therefore forget about all the other
functions and just use the ``einsum``.

We also provide fused-type, nogil Cython bindings to the underlying
Blis linear algebra library. Fused types are a simple template mechanism,
allowing just a touch of compile-time generic programming:

.. code:: python

    cimport blis.cy
    A = <float*>calloc(nN * nI, sizeof(float))
    B = <float*>calloc(nO * nI, sizeof(float))
    C = <float*>calloc(nr_b0 * nr_b1, sizeof(float))
    blis.cy.gemm(blis.cy.NO_TRANSPOSE, blis.cy.NO_TRANSPOSE,
                 nO, nI, nN,
                 1.0, A, nI, 1, B, nO, 1,
                 1.0, C, nO, 1)


Bindings have been added as we've needed them. Please submit pull requests if
the library is missing some functions you require.
