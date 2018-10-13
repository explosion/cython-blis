#!/usr/bin/env bash

sudo -E apt-add-repository -y "ppa:ubuntu-toolchain-r/test"
sudo apt-get update -y
sudo apt-get install -y gcc-6 binutils clang

sed -i 's/"gcc"/"gcc-6"/' blis/_src/make/linux-x86_64.jsonl

export CC="gcc-6"
