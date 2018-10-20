#!/usr/bin/env bash

set -e

if [ "$TRAVIS_OS_NAME" = "linux" ]; then
  sleep 5
  sudo -E apt-add-repository -y "ppa:ubuntu-toolchain-r/test"
  sleep 5
  sudo apt-get update -y
  sleep 5
  sudo apt-get install -y gcc-6 binutils clang
  sed -i 's/"gcc"/"gcc-6"/' blis/_src/make/linux-x86_64.jsonl
  export CC="gcc-6"
fi

#if [ "$TRAVIS_OS_NAME" = "osx" ]; then

#fi

