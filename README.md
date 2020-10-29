<a href="https://explosion.ai"><img src="https://explosion.ai/assets/img/logo.svg" width="125" height="125" align="right" /></a>

# Cython BLIS: Fast BLAS-like operations from Python and Cython, without the tears

This repository provides the [Blis linear algebra](https://github.com/flame/blis)
routines as a self-contained Python C-extension.

Currently, we only supports single-threaded execution, as this is actually best for our workloads (ML inference).

[![Azure Pipelines](https://img.shields.io/azure-devops/build/explosion-ai/public/6/master.svg?logo=azure-pipelines&style=flat-square)](https://dev.azure.com/explosion-ai/public/_build?definitionId=6)
[![pypi Version](https://img.shields.io/pypi/v/blis.svg?style=flat-square&logo=pypi&logoColor=white)](https://pypi.python.org/pypi/blis)
[![conda](https://img.shields.io/conda/vn/conda-forge/cython-blis.svg?style=flat-square&logo=conda-forge&logoColor=white)](https://anaconda.org/conda-forge/cython-blis)
[![Python wheels](https://img.shields.io/badge/wheels-%E2%9C%93-4c1.svg?longCache=true&style=flat-square&logo=python&logoColor=white)](https://github.com/explosion/wheelwright/releases)

## Installation

You can install the package via pip, first making sure that `pip`, `setuptools`,
and `wheel` are up-to-date:

```bash
pip install -U pip setuptools wheel
pip install blis
```

Wheels should be available, so installation should be fast. If you want to install from source and you're on Windows, you'll need to install LLVM.

### Building BLIS for alternative architectures

The provided wheels should work on x86_86 architectures. Unfortunately we do not currently know a way to provide different wheels for alternative architectures, and we cannot provide a single binary that works everywhere. So if the wheel doesn't work for your CPU, you'll need to specify source distribution, and tell Blis your CPU architecture using the `BLIS_ARCH` environment variable.

#### a) Installing with generic arch support

```bash
BLIS_ARCH="generic" pip install spacy --no-binary blis
```

#### b) Building specific support

In order to compile Blis, `cython-blis` bundles makefile scripts for specific architectures, that are compiled by running the Blis build system and logging the commands. We do not yet have logs for every architecture, as there are some architectures we have not had access to.

[See here](https://github.com/flame/blis/blob/0.5.1/config_registry) for list of
architectures. For example, here's how to build support for the ARM architecture `cortexa57`:

```bash
git clone https://github.com/explosion/cython-blis && cd cython-blis
git pull && git submodule init && git submodule update && git submodule status
python3 -m venv env3.6
source env3.6/bin/activate
pip install -r requirements.txt
./bin/generate-make-jsonl linux cortexa57
BLIS_ARCH="cortexa57" python setup.py build_ext --inplace
BLIS_ARCH="cortexa57" python setup.py bdist_wheel
```

Fingers crossed, this will build you a wheel that supports your platform. You
could then [submit a PR](https://github.com/explosion/cython-blis/pulls) with
the `blis/_src/make/linux-cortexa57.jsonl` and
`blis/_src/include/linux-cortexa57/blis.h` files so that you can run:

```bash
BLIS_ARCH=cortexa57 pip install --no-binary=blis
```

## Usage

Two APIs are provided: a high-level Python API, and direct
[Cython](http://cython.org) access, which provides fused-type, nogil
Cython bindings to the underlying Blis linear algebra library. Fused
types are a simple template mechanism, allowing just a touch of
compile-time generic programming:

```python
cimport blis.cy
A = <float*>calloc(nN * nI, sizeof(float))
B = <float*>calloc(nO * nI, sizeof(float))
C = <float*>calloc(nr_b0 * nr_b1, sizeof(float))
blis.cy.gemm(blis.cy.NO_TRANSPOSE, blis.cy.NO_TRANSPOSE,
             nO, nI, nN,
             1.0, A, nI, 1, B, nO, 1,
             1.0, C, nO, 1)
```

Bindings have been added as we've needed them. Please submit pull requests if
the library is missing some functions you require.

## Development

To build the source package, you should run the following command:

```bash
./bin/copy-source-files.sh
```

This populates the `blis/_src` folder for the various architectures, using the
`flame-blis` submodule.

## Updating the build files

In order to compile the Blis sources, we use jsonl files that provide the
explicit compiler flags. We build these jsonl files by running Blis's build
system, and then converting the log. This avoids us having to replicate the
build system within Python: we just use the jsonl to make a bunch of subprocess
calls. To support a new OS/architecture combination, we have to provide the
jsonl file and the header.

### Linux

The Linux build files need to be produced from within the manylinux1 docker
container, so that they will be compatible with the wheel building process.

First, install docker. Then do the following to start the container:

    sudo docker run -it quay.io/pypa/manylinux1_x86_64:latest

Once within the container, the following commands should check out the repo and
build the jsonl files for the generic arch:

    mkdir /usr/local/repos
    cd /usr/local/repos
    git clone https://github.com/explosion/cython-blis && cd cython-blis
    git pull && git submodule init && git submodule update && git submodule
    status
    /opt/python/cp36-cp36m/bin/python -m venv env3.6
    source env3.6/bin/activate
    pip install -r requirements.txt
    ./bin/generate-make-jsonl linux generic --export
    BLIS_ARCH=generic python setup.py build_ext --inplace
    # N.B.: don't copy to /tmp, docker cp doesn't work from there.
    cp blis/_src/include/linux-generic/blis.h /linux-generic-blis.h
    cp blis/_src/make/linux-generic.jsonl /

Then from a new terminal, retrieve the two files we need out of the container:

    sudo docker ps -l # Get the container ID
    # When I'm in Vagrant, I need to go via cat -- but then I end up with dummy
    # lines at the top and bottom. Sigh. If you don't have that problem and
    # sudo docker cp just works, just copy the file.
    sudo docker cp aa9d42588791:/linux-generic-blis.h - | cat > linux-generic-blis.h
    sudo docker cp aa9d42588791:/linux-generic.jsonl - | cat > linux-generic.jsonl
