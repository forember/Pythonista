from __future__ import division
from PIL import Image

img = Image.open('Simplex.png')
w, h = img.size
pix = img.load()
for x in xrange(w):
	for y in xrange(h):
		pxl = pix[x, y][0]
		if pxl < 128:
			r = 0
			g = int(0.40625 * pxl)
			b = int(0.78125 * pxl) + 50
		else:
			r = b = 2 * (pxl - 128)
			g = int(1.5 * (pxl - 64))
		pix[x, y] = (r, g, b)
		
img.show()
