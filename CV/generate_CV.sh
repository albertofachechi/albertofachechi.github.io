#!/bin/sh
# Rigenera i file del CV dal sito e compila. Opzioni: vedi python3 build_cv.py --help
cd "$(dirname "$0")" && python3 build_cv.py "$@"
