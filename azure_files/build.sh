#!usr/bin/env bash
set -e

# https://github.com/conda-forge/blis-feedstock/blob/master/recipe/build.sh
export PREFIX=$BUILD_SOURCESDIRECTORY/flame-blis
export BUILD_PREFIX=$BUILD_SOURCESDIRECTORY/flame-blis
export PATH="$PREFIX/Library/bin:$BUILD_PREFIX/Library/bin:$PATH"
export CC=clang
export RANLIB=echo
export LIBPTHREAD=
export AS=llvm-as
export AR=llvm-ar
export CFLAGS="-MD -I$PREFIX/Library/include"
export LDFLAGS="$LDFLAGS -L$PREFIX/Library/lib"
clang --version
llvm-as --version
llvm-ar --version
./configure --disable-shared --enable-static --prefix=$PREFIX/Library --enable-cblas --enable-threading=pthreads --enable-arg-max-hack x86_64
make -j${CPU_COUNT}
make install
make check -j${CPU_COUNT}

./configure --enable-shared --disable-static --prefix=$PREFIX/Library --enable-cblas --enable-threading=pthreads --enable-arg-max-hack x86_64
make -j${CPU_COUNT}
make install
mv $PREFIX/Library/lib/libblis.lib $PREFIX/Library/lib/blis.lib
mv $PREFIX/Library/lib/libblis.a $PREFIX/Library/lib/libblis.lib
mv $PREFIX/Library/lib/libblis.*.dll $PREFIX/Library/bin/
