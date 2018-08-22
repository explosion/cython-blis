#!/usr/bin/env bash

blis="$PWD/flame-blis"
headers="$HOME/blis/include/blis"
cyblis="$PWD/blis"

if [ "$1" != "" ]; then
  arches=$1
else
  arches='x86_64'
fi

for arch in $arches
do
  echo $arch

  mkdir -p $cyblis/_src/$arch/src
  mkdir -p $cyblis/_src/$arch/include

  cd $blis
  ./configure -i64 $arch
  cp -r frame/* $cyblis/_src/$arch/src
  cd $cyblis
  cp $headers/* $cyblis/_src/$arch/include
done
