#!/usr/bin/env python
import shutil
import os
import os.path
import json
import tempfile
import shutil
import distutils.command.build_ext
from distutils.ccompiler import new_compiler
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

MOD_NAMES = [
    'blis.cy',
    'blis.py'
]

def clean(path):
    if os.path.exists(os.path.join(PWD, 'build')):
        shutil.rmtree(os.path.join(PWD, 'build'))
    for name in MOD_NAMES:
        name = name.replace('.', '/')
        for ext in ['.so', '.html', '.cpp', '.c']:
            file_path = os.path.join(path, name + ext)
            if os.path.exists(file_path):
                os.unlink(file_path)


def locate_windows_llvm():
    # first check if the LLVM_HOME env variable is in use
    if 'LLVM_HOME' in os.environ:
        home = os.environ['LLVM_HOME']
        return os.path.join(home, 'bin', 'clang.exe')
    else:
        # otherwise, search the PATH for NVCC
        clang = find_in_path('clang.exe', os.environ['PATH'])
        if clang is None:
            clang = r"C:\Program Files\LLVM\bin\clang.exe"
        return clang

def find_in_path(name, path):
    "Find a file in a search path"
    #adapted fom http://code.activestate.com/recipes/52224-find-a-file-given-a-search-path/
    for dir in path.split(os.pathsep):
        binpath = os.path.join(dir, name)
        if os.path.exists(binpath):
            return os.path.abspath(binpath)
    return None



# By subclassing build_extensions we have the actual compiler that will be used
# which is really known only after finalize_options
# http://stackoverflow.com/questions/724664/python-distutils-how-to-get-a-compiler-that-is-going-to-be-used
class build_ext_options:
    def build_options(self):
        if hasattr(self.compiler, 'initialize'):
            self.compiler.initialize()
        self.compiler.platform = sys.platform[:6]
        if self.compiler.compiler_type == 'msvc':
            include_dirs = list(self.compiler.include_dirs)
            library_dirs = list(self.compiler.library_dirs)
            self.compiler = new_compiler(plat='nt', compiler='unix')
            self.compiler.platform = 'nt'
            self.compiler.compiler_type = 'msvc'
            self.compiler.compiler = [locate_windows_llvm()]
            self.compiler.compiler_so = list(self.compiler.compiler)
            self.compiler.preprocessor = list(self.compiler.compiler)
            self.compiler.linker = list(self.compiler.compiler) + ['-shared']
            self.compiler.linker_so = list(self.compiler.linker)
            self.compiler.linker_exe = list(self.compiler.linker)
            self.compiler.archiver = ['llvm-ar']
            self.compiler.library_dirs.extend(library_dirs)
            self.compiler.include_dirs = include_dirs
            llvm_home = os.path.dirname(os.path.dirname(self.compiler.compiler[0]))
            lib0 = r"C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\LIB\amd64"
            lib1 = r"C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\ATLMFC\LIB\amd64"
            lib2 = r"C:\Program Files (x86)\Windows Kits\10\lib\10.0.14393.0\ucrt\x64"
            lib3 = r"C:\Program Files (x86)\Windows Kits\NETFXSDK\4.6.1\lib\um\x64" 
            lib4 = r"C:\Program Files (x86)\Windows Kits\10\lib\10.0.14393.0\um\x64"
            for lib in [lib0, lib1, lib2, lib3, lib4]:
                if lib not in self.compiler.library_dirs:
                    self.compiler.library_dirs.append(lib)
            print(os.listdir(llvm_home))
            print(os.listdir(os.path.join(llvm_home, 'libexec')))
            print(os.listdir(os.path.join(llvm_home, 'share')))
            self.compiler.libraries.append('msvcrt')
            self.compiler.libraries.append('ucrt')
            self.compiler.library_dirs.append(os.path.join(llvm_home, 'libexec'))

class ExtensionBuilder(distutils.command.build_ext.build_ext, build_ext_options):
    def build_extensions(self):
        build_ext_options.build_options(self)
        if use_cython:
            subprocess.check_call([sys.executable, 'bin/cythonize.py'],
                                   env=os.environ)
        compiler = self.get_compiler_name()
        arch = self.get_arch_name()
        objects = self.compile_objects(compiler.split('-')[0], arch, OBJ_DIR)
        if compiler == 'msvc':
            platform_name = 'windows'
        else:
            platform_name = 'linux'
        # Work around max line length in Windows, by making a local directory
        # for the objects
        short_dir = 'z'
        os.mkdir(short_dir)
        short_paths = []
        for object_path in objects:
            assert os.path.exists(object_path), object_path
            dir_name, filename = os.path.split(object_path)
            new_path = os.path.join(short_dir, filename)
            shutil.copyfile(object_path, new_path)
            assert os.path.exists(new_path), new_path
            short_paths.append(new_path)
        for e in self.extensions:
            e.include_dirs.append(numpy.get_include())
            e.include_dirs.append(
                os.path.join(INCLUDE, '%s-%s' % (platform_name, arch)))
            e.extra_objects = list(short_paths)
        distutils.command.build_ext.build_ext.build_extensions(self)
        shutil.rmtree(short_dir)
    
    def get_arch_name(self):
        if 'BLIS_ARCH' in os.environ:
            return os.environ['BLIS_ARCH']
        else:
            return 'x86_64'

    def get_compiler_name(self):
        if 'BLIS_COMPILER' in os.environ:
            return os.environ['BLIS_COMPILER']
        elif os.environ.get('TRAVIS_OS_NAME') == "linux":
            return 'gcc-6'
        name = self.compiler.compiler_type
        print(name)
        if name.startswith('msvc'):
            return 'msvc'
        elif name not in ('gcc', 'clang', 'icc'):
            return 'gcc'
        else:
            return name

    def compile_objects(self, py_compiler, py_arch, obj_dir):
        objects = []
        if py_compiler == 'msvc':
            platform_name = 'windows' + '-' + py_arch
        else:
            platform_name = 'linux' + '-' + py_arch

        with open(os.path.join(BLIS_DIR, 'make', '%s.jsonl' % platform_name)) as file_:
            env = {}
            for line in file_:
                spec = json.loads(line)
                if 'environment' in spec:
                    env = spec['environment']
                    print(env)
                    continue
                _, target_name = os.path.split(spec['target'])
                if py_compiler == 'msvc':
                    target_name = target_name.replace('/', '\\')
                    spec['source'] = spec['source'].replace('/', '\\')
                    spec['include'] = [inc.replace('/', '\\') for inc in spec['include']]
                spec['include'].append('-I' + os.path.join(INCLUDE, '%s' % platform_name))

                spec['target'] = os.path.join(obj_dir, target_name)
                spec['source'] = os.path.join(BLIS_DIR, spec['source'])
                objects.append(self.build_object(env=env, **spec))
        return objects

    def build_object(self, compiler, source, target, flags, macros, include,
            env=None):
        if os.path.exists(target):
            return target
        if not os.path.exists(source):
            raise IOError("Cannot find source file: %s" % source)
        command = [compiler, "-c", source, "-o", target]
        command.extend(flags)
        command.extend(macros)
        command.extend(include)
        print(' '.join(command))
        subprocess.check_call(command, cwd=BLIS_DIR)
        return target

PWD = os.path.join(os.path.abspath(os.path.dirname('.')))
SRC = os.path.join(PWD, 'blis') 
BLIS_DIR = os.path.join(SRC, '_src')
INCLUDE = os.path.join(PWD, 'blis', '_src', 'include')
COMPILER = os.environ.get('BLIS_COMPILER', 'gcc')

c_files = [] #get_c_sources(SRC)
 
if len(sys.argv) > 1 and sys.argv[1] == 'clean':
    clean(PWD)

OBJ_DIR = tempfile.mkdtemp()
setup(
    setup_requires=['numpy>=1.15.0'],
    install_requires=['numpy>=1.15.0'],
    ext_modules=[
        Extension('blis.cy', [os.path.join('blis', 'cy.c')]),
        Extension('blis.py', [os.path.join('blis', 'py.c')])
    ],
    cmdclass={'build_ext': ExtensionBuilder},
    package_data={'': ['*.json', '*.jsonl', '*.pyx', '*.pxd', os.path.join(INCLUDE, '*.h')] + c_files},

    name="blis",
    packages=['blis'],
    version="0.0.15",
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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering'
    ],
)
shutil.rmtree(OBJ_DIR)
