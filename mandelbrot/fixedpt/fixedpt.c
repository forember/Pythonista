#include "fixedpt.h"
#include <math.h>

fx_t float2fx(fx_float_t a) {
    return (fx_t)(a * (fx_float_t)(1 << FIXEDPT_M));
}

fx_float_t fx2float(fx_t a) {
    return (fx_float_t)a / (fx_float_t)(1 << FIXEDPT_M);
}

dfx_t fx2dfx(fx_t a) {
    return (dfx_t)a << FIXEDPT_M;
}

fx_t dfx2fx(dfx_t a) {
    return (fx_t)(a >> FIXEDPT_M);
}

fx_t int2fx(fx_int_t a) {
    return a << FIXEDPT_M;
}

fx_int_t fxfloor(fx_t a) {
    return (a >> FIXEDPT_M);
}

fx_int_t fxceil(fx_t a) {
    return fxfloor(a) + 1;
}

fx_int_t fxround(fx_t a) {
    return (a & (1 << (FIXEDPT_M - 1)))
        ? fxceil(a) : fxfloor(a);
}

fx_t fxfrac(fx_t a) {
    return a & (int2fx(1) - 1);
}

fx_t fxneg(fx_t a) {
    return -a;
}

fx_t fxadd(fx_t a, fx_t b) {
    return a + b;
}

fx_t fxsub(fx_t a, fx_t b) {
    return a - b;
}

fx_t fxmuli(fx_t a, fx_int_t b) {
    return a * b;
}

fx_t fxmul(fx_t a, fx_t b) {
    return dfx2fx((dfx_t)a * (dfx_t)b);
}

fx_t fxdivi(fx_t a, fx_int_t b) {
    return a / b;
}

fx_t fxdiv(fx_t a, fx_t b) {
    return (fx_t)(fx2dfx(a) / (dfx_t)b);
}

fx_int_t fxdiv2int(fx_t a, fx_t b) {
    return a / b;
}

fx_t fxcos(fx_t a) {
    return float2fx(cos(fx2float(a)));
}

fx_t fxsin(fx_t a) {
    return float2fx(sin(fx2float(a)));
}

static int quick_pow10(int n)
{
    static int pow10[10] = {1, 10, 100, 1000, 10000, 100000, 1000000,
            10000000, 100000000, 1000000000};
    return pow10[n];
}

void fxprint(fx_t a) {
    printf("%d.", (a<0) ? fxfloor(a)-1 : fxfloor(a));
    fx_int_t frac_digits = FIXEDPT_M * 302 / 1000 + 1;
                // 0.302 > log_10 (2)
    printf("%0*d", frac_digits, ((a<0) ? int2fx(1)-fxfrac(a) : fxfrac(a))
            * quick_pow10(frac_digits) / (1 << FIXEDPT_M));
}

int snfxprint(char *dst, size_t size, fx_t a) {
    int ips = snprintf(dst, size, "%d.", (a<0) ? fxfloor(a)-1 : fxfloor(a));
    if (ips >= size - 1) {
        return ips;
    }
    fx_int_t frac_digits = FIXEDPT_M * 302 / 1000 + 1;
                // 0.302 > log_10 (2)
    char frac_part[size - ips];
    int fps = snprintf(frac_part, size - ips, "%0*d", frac_digits,
            ((a<0) ? int2fx(1)-fxfrac(a) : fxfrac(a))
            * quick_pow10(frac_digits) / (1 << FIXEDPT_M));
    size_t i;
    for (i = ips; i < size; ++i) {
        dst[i] = frac_part[i - ips];
    }
    return ips + fps;
}
