#!/usr/bin/env python
import shutil
import os

# This is maybe not the best place to put this,
# but we need to tell OSX to build for 10.7.
# Otherwise, wheels don't work. We can't use 10.6,
# it doesn't compile.
# if "MACOSX_DEPLOYMENT_TARGET" not in os.environ:
#    os.environ["MACOSX_DEPLOYMENT_TARGET"] = "10.7"

from setuptools import Extension, setup
import contextlib
import io
import os.path
import json
import tempfile
from setuptools.command.build_ext import build_ext, new_compiler
from Cython.Build import cythonize
import subprocess
import sys
import platform
import numpy

MOD_NAMES = ["blis.cy", "blis.py"]

print("BLIS_COMPILER?", os.environ.get("BLIS_COMPILER", "None"))


def clean(path):
    if os.path.exists(os.path.join(PWD, "build")):
        shutil.rmtree(os.path.join(PWD, "build"))
    for name in MOD_NAMES:
        name = name.replace(".", "/")
        for ext in [".so", ".html", ".cpp", ".c"]:
            file_path = os.path.join(path, name + ext)
            if os.path.exists(file_path):
                os.unlink(file_path)


def locate_windows_llvm():
    # first check if the LLVM_HOME env variable is in use
    if "LLVM_HOME" in os.environ:
        home = os.environ["LLVM_HOME"]
        return os.path.join(home, "bin", "clang.exe")
    else:
        # otherwise, search the PATH for clang.exe
        clang = find_in_path("clang.exe", os.environ["PATH"])
        if clang is None:
            clang = r"C:\Program Files\LLVM\bin\clang.exe"
        return clang


def find_in_path(name, path):
    "Find a file in a search path"
    # adapted fom http://code.activestate.com/recipes/52224-find-a-file-given-a-search-path/
    for dir in path.split(os.pathsep):
        binpath = os.path.join(dir, name)
        if os.path.exists(binpath):
            return os.path.abspath(binpath)
    return None


def is_gil_enabled():
    if sys.version_info < (3, 13):
        return True
    return sys._is_gil_enabled()


class ExtensionBuilder(build_ext):
    # By overriding build_extensions we have the actual compiler that will be used
    # which is really known only after finalize_options
    # http://stackoverflow.com/questions/724664/python-distutils-how-to-get-a-compiler-that-is-going-to-be-used
    def build_extensions(self):
        if hasattr(self.compiler, "initialize"):
            self.compiler.initialize()
        self.compiler.platform = sys.platform[:6]
        self.compiler.include_dirs.append(numpy.get_include())

        if self.compiler.compiler_type == "msvc":
            # Replace msvc compiler with unix compiler
            include_dirs = self.compiler.include_dirs[:]
            library_dirs = self.compiler.library_dirs[:]
            llvm_path = locate_windows_llvm()

            self.compiler = new_compiler(plat="nt", compiler="unix")
            self.compiler.platform = "nt"
            self.compiler.compiler_type = "msvc"
            self.compiler.compiler = [llvm_path]
            self.compiler.compiler_so = [llvm_path]
            self.compiler.preprocessor = [llvm_path]
            self.compiler.linker_so = [llvm_path, "-shared"]
            self.compiler.linker_exe = [llvm_path, "-shared"]
            self.compiler.archiver = ["llvm-ar"]
            self.compiler.library_dirs = library_dirs
            self.compiler.include_dirs = include_dirs

            # The official Windows free threaded Python installer doesn't set
            # Py_GIL_DISABLED because its pyconfig.h is shared with the
            # default build, so we need to define it here
            # (see pypa/setuptools#4662).
            # setuptools normally implements a workaround internally, but we
            # need to define it ourselves because we're replacing the compiler.
            if not is_gil_enabled():
                self.compiler.define_macro("Py_GIL_DISABLED", "1")

        if sys.platform in ("msvc", "win32"):
            platform_name = "windows"
        elif sys.platform == "darwin":
            platform_name = "darwin"
        else:
            platform_name = "linux"
        arch = self.get_arch_name(platform_name)
        print("BUILD ARCH:", arch)
        objects = self.compile_objects(platform_name, arch, OBJ_DIR)
        # Work around max line length in Windows, by making a local directory
        # for the objects
        short_dir = "z"
        if not os.path.exists(short_dir):
            os.mkdir(short_dir)
        short_paths = []
        for object_path in objects:
            assert os.path.exists(object_path), object_path
            dir_name, filename = os.path.split(object_path)
            new_path = os.path.join(short_dir, filename)
            shutil.copyfile(object_path, new_path)
            assert os.path.exists(new_path), new_path
            short_paths.append(new_path)
        root = os.path.abspath(os.path.dirname(__file__))
        for e in self.extensions:
            e.include_dirs.append(os.path.join(root, "include"))
            e.include_dirs.append(
                os.path.join(INCLUDE, "%s-%s" % (platform_name, arch))
            )
            e.extra_objects = list(short_paths)

        super().build_extensions()
        shutil.rmtree(short_dir)

    def get_libraries(self, ext):
        libs = super().get_libraries(ext)
        if os.name == "nt" and not is_gil_enabled():
            # Work around https://github.com/pypa/setuptools/issues/5126
            # Replace cmake parameter '-lpython314'  with '-lpython314t'
            libs = [
                lib + "t" if lib.startswith("python") and not lib.endswith("t") else lib
                for lib in libs
            ]
        return libs

    def get_arch_name(self, platform_name):
        # User-defined
        if "BLIS_ARCH" in os.environ:
            return os.environ["BLIS_ARCH"]
        # Darwin: use "generic" (for now) for any non-x86_64
        elif platform_name == "darwin":
            if platform.machine() == "x86_64":
                return "x86_64"
            else:
                return "generic"
        # Windows: use "generic" (for now) for ARM64 and x86_64 for other platforms
        elif platform_name == "windows":
            if platform.machine() == "ARM64":
                return "generic"
            else:
                return "x86_64"

        # Everything else other than linux defaults to x86_64
        elif not platform_name.startswith("linux"):
            return "x86_64"

        # Linux
        machine = platform.machine()
        if machine == "aarch64":
            return "cortexa57"
        elif machine == "ppc64le":
            return "power9"
        elif machine != "x86_64":
            return "generic"

        # Linux x86_64
        # Try to detect which compiler flags are supported
        supports_znver1 = self.check_compiler_flag("znver1")
        supports_znver2 = self.check_compiler_flag("znver2")
        supports_skx = self.check_compiler_flag("skylake-avx512")

        if supports_znver2 and supports_skx:
            return "x86_64"
        elif supports_znver1 and supports_skx:
            return "x86_64_no_zen2"
        elif supports_znver1 and not supports_skx:
            return "x86_64_no_skx"
        else:
            return "generic"

    def check_compiler_flag(self, flag):
        supports_flag = True
        DEVNULL = os.open(os.devnull, os.O_RDWR)
        try:
            subprocess.check_call(
                " ".join(self.compiler.compiler)
                + " -march={flag} -E -xc - -o -".format(flag=flag),
                stdin=DEVNULL,
                stdout=DEVNULL,
                stderr=DEVNULL,
                shell=True,
            )
        except Exception:
            supports_flag = False
        os.close(DEVNULL)
        return supports_flag

    def get_compiler_name(self):
        if "BLIS_COMPILER" in os.environ:
            return os.environ["BLIS_COMPILER"]
        elif "CC" in os.environ:
            return os.environ["CC"]
        else:
            return None

    def compile_objects(self, platform, py_arch, obj_dir):
        objects = []
        platform_arch = platform + "-" + py_arch
        compiler = self.get_compiler_name()
        with open(os.path.join(BLIS_DIR, "make", "%s.jsonl" % platform_arch)) as file_:
            env = {}
            for line in file_:
                spec = json.loads(line)
                if "environment" in spec:
                    env = spec["environment"]
                    print(env)
                    continue
                _, target_name = os.path.split(spec["target"])
                if platform == "windows":
                    target_name = target_name.replace("/", "\\")
                    spec["source"] = spec["source"].replace("/", "\\")
                    spec["include"] = [
                        inc.replace("/", "\\") for inc in spec["include"]
                    ]
                spec["include"].append(
                    "-I" + os.path.join(INCLUDE, "%s" % platform_arch)
                )

                spec["target"] = os.path.join(obj_dir, target_name)
                spec["source"] = os.path.join(BLIS_DIR, spec["source"])
                if compiler is not None:
                    spec["compiler"] = compiler
                if platform == "windows":
                    spec["compiler"] = locate_windows_llvm()
                # Ensure that symbols are visible to aid debugging and profiling.
                spec["flags"] = [
                    f for f in spec["flags"] if "visibility=hidden" not in f
                ]
                # spec["flags"].append(
                #    "-D__cpuid=__cpuid_function"
                # )
                objects.append(self.build_object(env=env, **spec))
        return objects

    def build_object(self, compiler, source, target, flags, macros, include, env=None):
        if os.path.exists(target):
            return target
        if not os.path.exists(source):
            raise IOError("Cannot find source file: %s" % source)
        command = compiler.split()
        command.extend(["-c", source, "-o", target])
        command.extend(flags)
        command.extend(macros)
        command.extend(include)
        print("[COMMAND]", " ".join(command))
        # TODO: change this to subprocess.run etc. once we drop 2.7
        subprocess.check_call(command, cwd=BLIS_DIR)
        return target


@contextlib.contextmanager
def chdir(new_dir):
    old_dir = os.getcwd()
    try:
        os.chdir(new_dir)
        sys.path.insert(0, new_dir)
        yield
    finally:
        del sys.path[0]
        os.chdir(old_dir)


PWD = os.path.join(os.path.abspath(os.path.dirname(".")))
SRC = os.path.join(PWD, "blis")
BLIS_DIR = os.path.join(SRC, "_src")
INCLUDE = os.path.join(PWD, "blis", "_src", "include")
COMPILER = os.environ.get("BLIS_COMPILER", "gcc")

if len(sys.argv) > 1 and sys.argv[1] == "clean":
    clean(PWD)

OBJ_DIR = tempfile.mkdtemp()

root = os.path.abspath(os.path.dirname(__file__))
with chdir(root):
    with open(os.path.join(root, "blis", "about.py")) as f:
        about = {}
        exec(f.read(), about)

    with io.open(os.path.join(root, "README.md"), encoding="utf8") as f:
        readme = f.read()

setup(
    setup_requires=[
        "cython>=3.1,<4.0",
        "numpy>=2.0.0,<3.0.0",
    ],
    install_requires=[
        "numpy>=1.21.2,<3.0.0",
    ],
    ext_modules=cythonize(
        [
            Extension(
                "blis.cy",
                [os.path.join("blis", "cy.pyx")],
                extra_compile_args=["-std=c99"],
            ),
            Extension(
                "blis.py",
                [os.path.join("blis", "py.pyx")],
                extra_compile_args=["-std=c99"],
            ),
        ],
        language_level=3,
    ),
    python_requires=">=3.10,<3.15",
    cmdclass={"build_ext": ExtensionBuilder},
    package_data={"": ["*.json", "*.jsonl", "*.pyx", "*.pxd"]},
    name="blis",
    packages=["blis"],
    author=about["__author__"],
    author_email=about["__email__"],
    version=about["__version__"],
    url=about["__uri__"],
    license=about["__license__"],
    description=about["__summary__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: Free Threading :: 2 - Beta",
        "Topic :: Scientific/Engineering",
    ],
)
shutil.rmtree(OBJ_DIR)
