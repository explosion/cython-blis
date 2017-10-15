#!/usr/bin/env bash

blis="$PWD/flame-blis"
headers="$HOME/blis/include/blis"
cyblis="$PWD"

mkdir -p $cyblis/_src/$arch/src
mkdir -p $cyblis/_src/$arch/include


arches='bulldozer carrizo cortex-a15 cortex-a9 haswell knl piledriver sandybridge reference'

for arch in $arches
do
  echo $arch
  cd $blis
  ./configure -i64 $arch
  make
  make install
  cp -r frame/* $cyblis/_src/$arch/src
  cd $cyblis
  cp $headers/* $cyblis/_src/$arch/include
done
