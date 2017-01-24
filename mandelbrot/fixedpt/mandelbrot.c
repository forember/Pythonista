#include "lemodapng.h"
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include <limits.h>

#define USE_FIXED_POINT

#ifdef USE_FIXED_POINT
#include "fixedpt.h"
#endif

#ifdef USE_FIXED_POINT
typedef fx_t real_t;
#define F2INT(T,A)      ((T)fxfloor((A)))
#define INT2F(A)        (int2fx((A)))
#define FLOAT2F(A)      (float2fx((A)))
#define AGN_MUL(A,B)    (fxmul((A),(B)))
#define AGN_DIV(A,B)    (fxdiv((A),(B)))
#define AGN_COS(A)      (fxcos((A)))
#define AGN_SIN(A)      (fxsin((A)))
#else
typedef float real_t;
#define F2INT(T,A)      ((T)(A))
#define INT2F(A)        ((real_t)(A))
#define FLOAT2F(A)      ((real_t)(A))
#define AGN_MUL(A,B)    ((A)*(B))
#define AGN_DIV(A,B)    ((A)/(B))
#define AGN_COS(A)      (cos((A)))
#define AGN_SIN(A)      (sin((A)))
#endif

pixel_t palette(real_t x) {
    pixel_t p;
    if (x <= INT2F(1)/2) {
        p.red   = F2INT(uint8_t, 510 * x);
        p.green = F2INT(uint8_t, 510 * x);
        p.blue  = F2INT(uint8_t, 255 * (x + INT2F(1)/2));
    } else if (x <= INT2F(3)/4) {
        p.red   = 255;
        p.green = F2INT(uint8_t, 680 * (INT2F(7)/8 - x));
        p.blue  = F2INT(uint8_t, 1020 * (INT2F(3)/4 - x));
    } else if (x <= INT2F(7)/8) {
        p.red   = F2INT(uint8_t, 1020 * (INT2F(1) - x));
        p.green = F2INT(uint8_t, 680 * (INT2F(7)/8 - x));
        p.blue  = 0;
    } else {
        p.red   = F2INT(uint8_t, 1020 * (INT2F(1) - x));
        p.green = 0;
        p.blue  = 0;
    }
    return p;
}

bitmap_t alloc_bitmap(size_t width, size_t height) {
    bitmap_t im;
    // Create an image.
    im.width = width;
    im.height = height;
    im.pixels = calloc(sizeof(pixel_t), im.width*im.height);
    return im;
}

bitmap_t palette_test(void) {
    bitmap_t im;
    im = alloc_bitmap(1000, 1000);
    size_t px, py;
    pixel_t color;
    pixel_t *pixel;
    for (py = 0; py < im.height; ++py) {
        for (px = 0; px < im.width; ++px) {
            color = palette(INT2F(px) / 1000);
            pixel = pixel_at(&im, px, py);
            pixel->red   = color.red;
            pixel->green = color.green;
            pixel->blue  = color.blue;
        }
    }
    return im;
}

struct escape_time_r {
    bitmap_t im;
    real_t interest_x;
    real_t interest_y;
};

struct escape_time_r escape_time(size_t iw, size_t ih, real_t left, real_t top,
        real_t w, real_t h, unsigned max_iteration, uint8_t find_interest) {
    bitmap_t im;
    im = alloc_bitmap(iw, ih);
    size_t px, py;
    pixel_t color;
    pixel_t *pixel;
    real_t x0, y0, x, tmpx, y, value, cx, cy, inx, iny, x2, y2;
    unsigned iteration;
    cx = left + w / 2;
    cy = top - h / 2;
    inx = left;
    iny = top;
    for (py = 0; py < im.height; ++py) {
        for (px = 0; px < im.width; ++px) {
            x0 = w * px / iw + left;
            y0 = top - h * py / ih;
            x = 0.0;
            y = 0.0;
            iteration = 0;
            while ((x2 = AGN_MUL(x, x)) + (y2 = AGN_MUL(y, y)) < INT2F(4)
                    && iteration < max_iteration) {
                tmpx = x2 - y2 + x0;
                y = 2 * AGN_MUL(x, y) + y0;
                x = tmpx;
                ++iteration;
            }
            value = INT2F(iteration) / max_iteration;
            if (find_interest && value > INT2F(7)/8 && value != INT2F(1)) {
                real_t dx0, dy0, dinx, diny;
                dx0 = x0 - cx;
                dy0 = y0 - cy;
                dinx = inx - cx;
                diny = iny - cy;
                if (AGN_MUL(dx0,dx0) + AGN_MUL(dy0,dy0) < AGN_MUL(dinx,dinx)
                        + AGN_MUL(diny,diny)) {
                    inx = x0;
                    iny = y0;
                }
            }
            color = palette(value);
            pixel = pixel_at(&im, px, py);
            pixel->red   = color.red;
            pixel->green = color.green;
            pixel->blue  = color.blue;
        }
    }
    struct escape_time_r return_value;
    return_value.im = im;
    if (find_interest) {
        if (inx == left && iny == top) {
            inx = cx;
            iny = cy;
        }
    } else {
        inx = iny = 0;
    }
    return_value.interest_x = inx;
    return_value.interest_y = iny;
    return return_value;
}

void zoom_sequence(size_t iw, size_t ih, real_t left, real_t top,
        real_t w, real_t h, unsigned max_iteration, unsigned n, real_t miiif) {
    bitmap_t im;
    real_t cx, cy;
    struct escape_time_r etr;
    unsigned i;
    int j;
    size_t px, py;
    pixel_t *interest_pixel;
    cx = left + w / 2;
    cy = top - h / 2;
    for (i = 0; i < n; ++i) {
        fprintf(stderr, "%4d/%4d\r", i, n);
        left = cx - w / 2;
        top = cy + h / 2;
        etr = escape_time(iw, ih, left, top, w, h, max_iteration, 1);
        im = etr.im;
        for (j = -5; j < 5; ++j) {
            px = F2INT(size_t, AGN_DIV(iw * (etr.interest_x - left), w));
            py = F2INT(size_t, AGN_DIV(ih * (top - etr.interest_y), h));
            if (j < 0) {
                px += j + 3;
            } else {
                py += j - 2;
            }
            px = (px < 0) ? 0 : (px > iw) ? iw : px;
            py = (py < 0) ? 0 : (py > ih) ? ih : py;
            interest_pixel = pixel_at(&im, px, py);
            interest_pixel->red   = 0;
            interest_pixel->green = 255;
            interest_pixel->blue  = 0;
        }
        char filename[12];
        snprintf(filename, 12, "seq%04d.png", i);
        save_png_to_file(&im, filename);
        cx = (2 * cx + etr.interest_x) / 3;
        cy = (2 * cy + etr.interest_y) / 3;
        w = w * 2 / 3;
        h = h * 2 / 3;
        max_iteration = F2INT(unsigned, max_iteration
                * (INT2F(1) + AGN_DIV(INT2F(1), miiif)));
    }
    fprintf(stderr, "%4d/%4d\n", n, n);
}

int main (int argc, char **argv) {
    if (argc == 2 && strcmp(argv[1], "--palette") == 0) {
        bitmap_t im;
        // Generate the palette test.
        im = palette_test();
        // Write the image to a file 'palette.png'.
        save_png_to_file(&im, "palette.png");
        return 0;
    }
    if (argc >= 8 && argc <= 10) {
        size_t iw, ih;
        real_t left, top, w, h;
        unsigned max_iteration;
        // Parse command-line args.
        iw = strtol(argv[1], 0, 10);
        ih = strtol(argv[2], 0, 10);
        left = FLOAT2F(strtod(argv[3], 0));
        top = FLOAT2F(strtod(argv[4], 0));
        w = FLOAT2F(strtod(argv[5], 0));
        h = FLOAT2F(strtod(argv[6], 0));
        max_iteration = strtol(argv[7], 0, 10);
        bitmap_t im;
        if (argc == 8) {
            // Generate the image.
            im = escape_time(iw, ih, left, top, w, h, max_iteration, 0).im;
            // Write the image to a file 'mandelbrot.png'.
            save_png_to_file(&im, "mandelbrot.png");
        } else {
            unsigned n;
            real_t miiif = INT2F(32);
            n = strtol(argv[8], 0, 10);
            if (argc == 10) miiif = FLOAT2F(strtod(argv[9], 0));
            zoom_sequence(iw, ih, left, top, w, h, max_iteration, n, miiif);
        }
        return 0;
    }
    printf("Usage:  mandelbrot  <iw> <ih> <left> <top> <w> <h> "
            "<max_iteration> [n] [miiif=32.0]\n\n"
            "    Generate an image (mandelbrot.png) with the specified "
            "dimensions (iw, ih),\n    complex frame (left, top, w, h), and a "
            "maximum number of iterations.\n\n"
            "    If n is supplied, generate a sequence of images "
            "(seqXXXX.png) zooming in\n    on points of interest.\n\n"
            "        mandelbrot  --palette\n\n"
            "    Generate a palette test (palette.png).\n\n"
            "        mandelbrot  --help\n\n"
            "    Display this message.\n");
    return 1;
}
