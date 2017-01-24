#include <stdlib.h>
#include <stdint.h>

/* A coloured pixel. */
typedef struct {
    uint8_t red;
    uint8_t green;
    uint8_t blue;
} pixel_t;

/* A picture. */
typedef struct  {
    pixel_t *pixels;
    size_t width;
    size_t height;
} bitmap_t;

/* Given "bitmap", this returns the pixel of bitmap at the point 
   ("x", "y"). */
pixel_t * pixel_at (bitmap_t * bitmap, int x, int y);

/* Write "bitmap" to a PNG file specified by "path"; returns 0 on
   success, non-zero on error. */
int save_png_to_file (bitmap_t *bitmap, const char *path);

/* Given "value" and "max", the maximum value which we expect "value"
   to take, this returns an integer between 0 and 255 proportional to
   "value" divided by "max". */
int pix (int value, int max);
