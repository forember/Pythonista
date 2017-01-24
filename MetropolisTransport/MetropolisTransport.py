def _makeHistogram(F, histogram, mutations, w, h):
  from random import randint, random
  
  # create an initial sample point
  x0 = randint(0, w-1)
  x1 = randint(0, h-1)
  Fx = F[x0,x1]
  
  # In this example, the tentative transition function T simply chooses
  # a random pixel location, so Txy and Tyx are always equal.
  Txy = 1.0 / (w * h)
  Tyx = 1.0 / (w * h)
  
  # Create a histogram of values using Metropolis sampling.
  for i in xrange(mutations):
    # choose a tentative next sample according to T.
    y0 = randint(0, w-1)
    y1 = randint(0, h-1)
    Fy = F[y0,y1]
    Axy = min(1, (Fy * Txy) / (Fx * Tyx)) # equation 2.
    if random() < Axy:
      x0 = y0
      x1 = y1
      Fx = Fy
    histogram[x0,x1] += 1




def main():
  from PIL import Image
  src_im = Image.open('boat.512.tiff')
  src_im = src_im.resize((128, 128))
  w, h = sz = src_im.size
  dst_im = Image.new(src_im.mode, sz)
  src_pix = src_im.load()
  dst_pix = dst_im.load()
  avgppx = 8
  mutations = w*h * avgppx
  import time
  tt = time.time()
  tc = time.clock()
  _makeHistogram(src_pix, dst_pix, mutations, w, h)
  print time.time() - tt
  print time.clock() - tc
  dst_im = dst_im.point(lambda i: i * 96.0 / avgppx)
  src_im.show()
  dst_im.show()

if __name__ == '__main__':
  main()
