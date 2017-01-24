from __future__ import division
from scene import *
import simplexchunks
import os, itertools

class TheScene (Scene):
	def setup(self):
		b = self.bounds
		self.xoffs = 0
		self.yoffs = b.h
		self.chunks = {}
		
	def draw(self):
		background(0, 0, 0)
		b = self.bounds
		xstart = int(-self.xoffs / 16) - 1
		xstop = xstart + int(b.w / 16) + 2
		ystart = int(-self.yoffs / 16) - 1
		ystop = ystart + int(b.h / 16) + 2
		for loc in itertools.product(xrange(xstart, xstop), xrange(ystart, ystop)):
			if loc not in self.chunks:
				self.load_chunk(*loc)
				break
		for (x, y), chunk in self.chunks.items():
			if x < xstart or x >= xstop or y < ystart or y >= ystop:
				del self.chunks[x, y]
				unload_image(chunk)
			else:
				image(chunk, 16 * x + self.xoffs, 16 * y + self.yoffs, 16, 16)
		text('{}, {}'.format(xstart + 1, -31 - ystart), y=b.h, alignment=3)
		
	def load_chunk(self, x, y):
		filename = 'chunks/{x:d}.{y:d}.png'.format(x=x, y=y)
		chunk = load_image_file(filename)
		if not chunk:
			i = 0.0625
			chunk = simplexchunks.gen_chunk((i * x, -i * y, i, i))
			chunk.save(filename)
			chunk = load_image_file(filename)
		self.chunks[x, y] = chunk
		
	def touch_moved(self, touch):
		loc = touch.location
		ploc = touch.prev_location
		self.xoffs += loc.x - ploc.x
		self.yoffs += loc.y - ploc.y
		
if not os.path.exists('chunks'):
	os.mkdir('chunks')
run(TheScene())
