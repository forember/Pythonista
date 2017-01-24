#!/usr/bin/env python2
# requires PIL (Python Imaging Library)
# http://www.pythonware.com/products/pil/

# Author: Chris McKinney

from __future__ import division


def palette(x):
  if x <= 0.5:
    return (int(510*x),
            int(510*x),
            int(255*(x+0.5)))
  elif x <= 0.75:
    return (255,
            int(765*(0.875-x)),
            int(1020*(0.75-x)))
  elif x <= 0.875:
    return (int(1020*(1-x)),
            int(765*(0.875-x)),
            0)
  else:
    return (int(1020*(1-x)),
            0,
            0)


def escape_time(iw=350, ih=200, left=-2.5, top=1.0, w=3.5, h=2.0, max_iteration=100):
  from PIL import Image
  im = Image.new('RGB', (iw, ih))
  pix = im.load()
  for Px in xrange(iw):
    for Py in xrange(ih):
      x0 = w * Px / iw + left
      y0 = top - h * Py / ih
      x = 0.0
      y = 0.0
      iteration = 0
      while x*x + y*y < 2*2 and iteration < max_iteration:
        x, y = x*x - y*y + x0, 2*x*y + y0
        iteration += 1
      color = palette(iteration / max_iteration)
      pix[Px, Py] = color
  return im


def palette_test():
  from PIL import Image
  im = Image.new('RGB', (1000, 1000))
  im.putdata(1000 * [palette(x / 1000.0) for x in xrange(1000)])
  return im


def main():
  import sys
  if len(sys.argv) == 2 and sys.argv[1] == '--help':
      print('''
Usage:  mandelbrot.py   [iw=350] [ih=200] [left=-2.5] [top=1.0] [w=3.5] [h=2.0]
                        [max_iteration=100]

    Generate an image (mandelbrot.png) with the specified dimensions (iw, ih),
    complex frame (left, top, w, h), and a maximum number of iterations.

        mandelbrot.py   --palette

    Generate a palette test (palette.png).

        mandelbrot.py   --help

    Display this message.
      '''.strip())
      return
  if len(sys.argv) == 2 and sys.argv[1] == '--palette':
      im = palette_test()
      im.save('palette.png')
      im.show()
      return
  args = []
  for i, argi in enumerate(sys.argv[1:8]):
    if i in (0, 1, 6):
      arg = int(argi)
    else:
      arg = float(argi)
    args.append(arg)
  im = escape_time(*args)
  im.save('mandelbrot.png')
  im.show()

if __name__ == '__main__':
  main()
