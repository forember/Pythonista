#!/usr/bin/env python3
from simplexchunks_py3 import gen_chunk
from random import random
maxint = 2**31 - 1

def randomarea(areasize=(1, 1), *args, **kwargs):
	try:
		aw, ah = areasize
	except:
		aw = ah = areasize
	area = (maxint * random(), maxint * random(), aw, ah)
	return gen_chunk(area, *args, **kwargs)

randomarea(isize=128*4, octaves=8).show()
