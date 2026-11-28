#!/bin/sh
# v7 : le banc OLAP en C++ (C++26), niveau portable (olap_p) et niveau spécialisé (olap_s). Compilateur : clang 23,
# celui de la référence C, avec la bibliothèque standard du système ; MS_CC=gcc : g++ 16.2 (mesure de sensibilité).
set -e
cd "$(dirname "$0")"
case "${MS_CC:-clang}" in
  clang) CXX="clang-23 --driver-mode=g++" ;;
  gcc) CXX=/opt/gcc-16/bin/g++-16 ;;
  *) echo "MS_CC=$MS_CC : compilateur inconnu" >&2; exit 2 ;;
esac
FLAGS="-std=c++26 -O3 -march=native -Wall -Wextra -pthread"
$CXX $FLAGS -o olap_p olap.cpp
$CXX $FLAGS -DSPECIAL -o olap_s olap.cpp
