#!/bin/bash
cd "$(dirname "$0")"
tar czf mandelbrot.tar.gz mandelbrot/Cells/mandelbrot_py3.py mandelbrot/fixedpt
