//#include <stdio.h>

int src[8] = { 0, 1, 2, 3, 4, 5, 6, 7 };
int dst[8] = {-1,-1,-1,-1,-1,-1,-1,-1 };

/* $begin ncopy */
/*
 * ncopy - copy src to dst, returning number of positive ints
 * contained in src array.
 */
int ncopy(int *src, int *dst, int len)
{
    int count = 0;
    int val;

    while (len > 0) {
	val = *src++;
	*dst++ = val;
	if (val > 0)
	    count++;
	len--;
    }
    return count;
}
/* $end ncopy */

int count = -1;

int main()
{
    //int i, count;

    /*for (i=0; i<8; i++)
	src[i]= i+1;*/
    count = ncopy(src, dst, 8);
    //printf ("count=%d\n", count);
    //exit(0);
}


