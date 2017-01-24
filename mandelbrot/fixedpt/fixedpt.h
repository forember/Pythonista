#ifndef FIXEDPT_H
#define FIXEDPT_H

#include "stdint.h"
#include <stdio.h>

#define FIXEDPT_N   (32)
#define FIXEDPT_M   (20)

typedef int32_t fx_int_t;
typedef int64_t fx_long_t;
typedef fx_int_t fx_t;
typedef fx_long_t dfx_t;
typedef double fx_float_t;

fx_t float2fx(fx_float_t a);
fx_float_t fx2float(fx_t a);
fx_t int2fx(fx_int_t a);
fx_int_t fxfloor(fx_t a);
fx_int_t fxceil(fx_t a);
fx_int_t fxround(fx_t a);
fx_t fxfrac(fx_t a);
fx_t fxneg(fx_t a);
fx_t fxadd(fx_t a, fx_t b);
fx_t fxsub(fx_t a, fx_t b);
fx_t fxmuli(fx_t a, fx_int_t b);
fx_t fxmul(fx_t a, fx_t b);
fx_t fxdivi(fx_t a, fx_int_t b);
fx_t fxdiv(fx_t a, fx_t b);
fx_int_t fxdiv2int(fx_t a, fx_t b);
fx_t fxcos(fx_t a);
fx_t fxsin(fx_t a);
void fxprint(fx_t a);
int snfxprint(char *dst, size_t size, fx_t a);

#endif
