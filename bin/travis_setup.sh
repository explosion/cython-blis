#!/usr/bin/env bash

sudo apt-get install -y gcc-6 binutils-2.26 clang
sudo rm -f /usr/bin/as
sudo ln -s /usr/lib/binutils-2.26/bin/as /usr/bin/as
sudo rm -f /usr/bin/ld
sudo ln -s /usr/lib/binutils-2.26/bin/ld /usr/bin/ld
sed -i 's/"gcc"/"gcc-6"/' blis/_src/make/linux-x86_64.jsonl
