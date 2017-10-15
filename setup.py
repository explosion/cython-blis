#!/usr/bin/env python
import shutil
import os
import os.path
import json
import distutils.command.build_ext
import subprocess
import sys
from setuptools import Extension, setup
import platform

import numpy

try:
    import cython
    use_cython = True
except ImportError:
    use_cython = False


class ExtensionBuilder(distutils.command.build_ext.build_ext):
    def build_extensions(self):
        if use_cython:
            subprocess.check_call([sys.executable, 'bin/cythonize.py'],
                                   env=os.environ)
        compiler = self.get_compiler_name()
        arch = self.get_arch_name()
        cflags, ldflags = self.get_flags(arch=arch, compiler=compiler)
        extensions = []
        e = self.extensions.pop(0)
        blis_dir = os.path.dirname(e.sources[0])
        c_sources = get_c_sources(os.path.join(blis_dir, '_src', arch))
        include_dir = os.path.join(blis_dir, '_src', arch, 'include')
        self.extensions.append(Extension(e.name, e.sources + c_sources))
        for e in self.extensions:
            e.extra_compile_args.extend(cflags)
            e.extra_link_args.extend(ldflags),
            e.include_dirs.append(numpy.get_include())
            e.include_dirs.append(os.path.abspath(include_dir)),
            e.undef_macros.append("FORTIFY_SOURCE")
        distutils.command.build_ext.build_ext.build_extensions(self)
    
    def get_arch_name(self):
        if 'BLIS_ARCH' in os.environ:
            return os.environ['BLIS_ARCH']
        processor = platform.processor()
        if processor == 'x86_64':
            return 'haswell' # Best guess?
        else:
            return 'reference'

    def get_compiler_name(self):
        if 'BLIS_COMPILER' in os.environ:
            return os.environ['BLIS_COMPILER']
        name = self.compiler.compiler_type
        if name.startswith('msvc'):
            return 'msvc'
        elif name not in ('gcc', 'clang', 'icc'):
            return 'gcc'
        else:
            return name
    
    def get_flags(self, arch='haswell', compiler='gcc'):
        flags = json.load(open('blis/compilation_flags.json'))
        if compiler != 'msvc':
            cflags = flags['cflags'].get(compiler, {}).get(arch, [])
            cflags += flags['cflags']['common']
        else:
            cflags = flags['cflags']['msvc']
        if compiler != 'msvc':
            ldflags = flags['ldflags'].get(compiler, [])
            ldflags += flags['ldflags']['common']
        else:
            ldflags = flags['ldflags']['msvc']
        return cflags, ldflags


def get_c_sources(start_dir):
    c_sources = []
    excludes = ['old', 'attic', 'broken', 'tmp', 'test',
                'cblas', 'other']
    for path, subdirs, files in os.walk(start_dir):
        for exc in excludes:
            if exc in path:
                break
        else:
            for name in files:
                if name.endswith('.c'):
                    c_sources.append(os.path.join(path, name))
    return c_sources


PWD = os.path.join(os.path.dirname(__file__))
ARCH = os.environ.get('BLIS_ARCH', 'haswell')
SRC = os.path.join(PWD, 'blis', '_src')
INCLUDE = os.path.join(PWD, 'blis', '_src', ARCH)
COMPILER = os.environ.get('BLIS_COMPILER', 'gcc')

c_files = get_c_sources(SRC)

setup(
    setup_requires=['numpy'],
    ext_modules=[
        Extension('blis.cy', ['blis/cy.c']),
        Extension('blis.py', ['blis/py.c']),

    ],
    cmdclass={'build_ext': ExtensionBuilder},
    package_data={'': ['*.json', '*.pyx', '*.pxd', '_src/*/include/*.h'] + c_files},

    name="blis",
    packages=['blis'],
    version="0.0.13",
    author="Matthew Honnibal",
    author_email="matt@explosion.ai",
    summary="The Blis BLAS-like linear algebra library, as a self-contained C-extension.",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Cython',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering'
    ],
)
