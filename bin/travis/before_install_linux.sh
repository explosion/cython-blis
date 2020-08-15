#!/usr/bin/env bash

set -e

function before_install {
  local passed=1
  sudo apt-get install python-dev
}
