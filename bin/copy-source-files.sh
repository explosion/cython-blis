#!/usr/bin/env bash

blis="$PWD/flame-blis"
headers="$HOME/blis/include/blis"
cyblis="$PWD/blis"

if [ "$1" != "" ]; then
  arches=$1
else
  arches='bulldozer carrizo cortex-a15 cortex-a9 haswell knl piledriver sandybridge reference'
fi

for arch in $arches
do
  echo $arch

  mkdir -p $cyblis/_src/$arch/src
  mkdir -p $cyblis/_src/$arch/include

  cd $blis
  ./configure --disable-threading -i64 $arch
  make
  make install
  cp -r frame/* $cyblis/_src/$arch/src
  cd $cyblis
  cp $headers/* $cyblis/_src/$arch/include
done
