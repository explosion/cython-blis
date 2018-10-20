#!/usr/bin/env bash

set -e

if [ "$TRAVIS_OS_NAME" = "linux" ]; then
  sudo -E apt-add-repository -y "ppa:ubuntu-toolchain-r/test"
  sudo apt-get update -y
  sudo apt-get install -y gcc-6 binutils clang
  sed -i 's/"gcc"/"gcc-6"/' blis/_src/make/linux-x86_64.jsonl
  export CC="gcc-6"
fi

if [ "$TRAVIS_OS_NAME" = "osx" ]; then
  mkdir -p blis/_src/include/darwin-x86_64
  ./bin/generate-make-jsonl darwin x86_64
  cp flame-blis/include/x86_64/blis.h blis/_src/include/darwin-x86_64/blis.h
fi

