#!/bin/bash
set -e

mkdir -p primer3/
cd primer3/
curl -OLs https://github.com/primer3-org/primer3/archive/v2.4.0.tar.gz
tar xfz v2.4.0.tar.gz --strip-components=1
rm v2.4.0.tar.gz
patch -p1 < ../primer3_patch
cd src/
make

echo "Add 'export PRIMER3HOME=\"$(pwd)\"' to your ~/.bashrc"
