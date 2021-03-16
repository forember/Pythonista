import simplexnoise
from PIL import Image

def gen_chunk(area=(0, 0, 0.0625, 0.0625), isize=(16, 16), octaves=16, persistence=0.75, scale=1):
	try:
		w, h = isize
	except:
		w = h = isize
	noise = lambda x, y: int(simplexnoise.scaled_octave_noise_2d(octaves, persistence, scale, 0, 255, (area[2] * x / w) + area[0], (area[3] * y / h) + area[1]))
	img = Image.new('RGB', (w, h))
	pix = img.load()
	for x in range(w):
		for y in range(h):
			pxl = noise(x, y)
			if pxl < 128:
				r = 0
				g = int(0.40625 * pxl)
				b = int(0.78125 * pxl) + 50
			else:
				r = b = 2 * (pxl - 128)
				g = int(1.5 * (pxl - 64))
			pix[x, y] = (r, g, b)
	return img

if __name__ == '__main__':
	img = gen_chunk((0, 0, 1, 1), 64)
	#img.save('Simplex.png')
	img = img.resize((256, 256), Image.ANTIALIAS)
	img.show()
