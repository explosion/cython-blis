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
import shutil
import distutils.command.build_ext
from distutils.ccompiler import new_compiler
import subprocess
import sys
import platform
import cython
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


# By subclassing build_extensions we have the actual compiler that will be used
# which is really known only after finalize_options
# http://stackoverflow.com/questions/724664/python-distutils-how-to-get-a-compiler-that-is-going-to-be-used
class build_ext_options:
    def build_options(self):
        if hasattr(self.compiler, "initialize"):
            self.compiler.initialize()
        self.compiler.platform = sys.platform[:6]
        print("Build options", self.compiler.platform, self.compiler.compiler_type)

        self.compiler.include_dirs = [numpy.get_include()] + self.compiler.include_dirs

        if self.compiler.compiler_type == "msvc":
            include_dirs = list(self.compiler.include_dirs)
            library_dirs = list(self.compiler.library_dirs)
            self.compiler = new_compiler(plat="nt", compiler="unix")
            self.compiler.platform = "nt"
            self.compiler.compiler_type = "msvc"
            self.compiler.compiler = [locate_windows_llvm()]
            self.compiler.compiler_so = list(self.compiler.compiler)
            self.compiler.preprocessor = list(self.compiler.compiler)
            self.compiler.linker = list(self.compiler.compiler) + ["-shared"]
            self.compiler.linker_so = list(self.compiler.linker)
            self.compiler.linker_exe = list(self.compiler.linker)
            self.compiler.archiver = ["llvm-ar"]
            self.compiler.library_dirs.extend(library_dirs)
            self.compiler.include_dirs = include_dirs


class ExtensionBuilder(distutils.command.build_ext.build_ext, build_ext_options):
    def build_extensions(self):
        build_ext_options.build_options(self)
        subprocess.check_call([sys.executable, "bin/cythonize.py"], env=os.environ)
        arch = self.get_arch_name()
        print("BUILD ARCH:", arch)
        if sys.platform in ("msvc", "win32"):
            platform_name = "windows"
        elif sys.platform == "darwin":
            platform_name = "darwin"
        else:
            platform_name = "linux"
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
        distutils.command.build_ext.build_ext.build_extensions(self)
        shutil.rmtree(short_dir)

    def get_arch_name(self):
        # User-defined
        if "BLIS_ARCH" in os.environ:
            return os.environ["BLIS_ARCH"]
        # Not linux defaults to x86_64
        elif sys.platform != "linux":
            return "x86_64"

        # Linux:
        machine = platform.machine()
        if machine == "aarch64":
            return "cortexa57"
        elif machine == "ppc64le":
            return "power9"
        elif machine != "x86_64":
            return "generic"

        # Try to detect whether compiler flags are available
        has_znver2 = True
        try:
            subprocess.check_call(" ".join(self.compiler.compiler) + " -march=znver2 -E -xc - -o -", stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        except:
            has_znver2 = False
        has_skx = True
        try:
            subprocess.check_call(" ".join(self.compiler.compiler) + " -march=skylake-avx512 -E -xc - -o -", stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        except:
            has_skx = False

        if has_znver2:
            return "x86_64"
        elif has_skx:
            return "x86_64_no_znver2"
        else:
            return "x86_64_no_skx"
    
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
                spec["flags"] = [f for f in spec["flags"]]
                objects.append(self.build_object(env=env, **spec))
        return objects

    def build_object(self, compiler, source, target, flags, macros, include, env=None):
        if os.path.exists(target):
            return target
        if not os.path.exists(source):
            raise IOError("Cannot find source file: %s" % source)
        command = [compiler, "-c", source, "-o", target]
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
BLIS_REALLY_COMPILE = os.environ.get("BLIS_REALLY_COMPILE", 0)

if not BLIS_REALLY_COMPILE:
    try:
        import pip
        version_parts = pip.__version__.split(".")
        major = int(version_parts[0])
        minor = int(version_parts[1])
        if major < 19 or (major == 19 and minor < 3):
            print("WARNING: pip versions <19.3 (currently installed: " + pip.__version__ + ") are unable to detect binary wheel compatibility for blis. To avoid a source install with a very long compilation time, please upgrade pip with `pip install --upgrade pip`.\n\nIf you know what you're doing and you really want to compile blis from source, please set the environment variable BLIS_REALLY_COMPILE=1.")
            sys.exit(1)
    except Exception:
        pass

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
        "cython>=0.25",
        "numpy>=1.15.0",
    ],
    install_requires=["numpy>=1.15.0"],
    ext_modules=[
        Extension(
            "blis.cy", [os.path.join("blis", "cy.c")], extra_compile_args=["-std=c99"]
        ),
        Extension(
            "blis.py", [os.path.join("blis", "py.c")], extra_compile_args=["-std=c99"]
        ),
    ],
    cmdclass={"build_ext": ExtensionBuilder},
    package_data={
        "": ["*.json", "*.jsonl", "*.pyx", "*.pxd"]
    },
    name="blis",
    packages=["blis", "blis.tests"],
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
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Cython",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering",
    ],
)
shutil.rmtree(OBJ_DIR)
