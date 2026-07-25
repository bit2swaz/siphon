#!/usr/bin/env bash
set -e
for target in up down seed test proto lint; do
  grep -q "^${target}:" Makefile || { echo "FAIL: missing target $target"; exit 1; }
done
echo "PASS: all Makefile targets present"
