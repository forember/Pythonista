/* 
 * Architecture Lab: Part A 
 * 
 * High level specs for the functions that the students will rewrite
 * in Y86 assembly language
 */

/* $begin examples */
/* linked list element */
typedef struct ELE *list_ptr;
struct ELE {
    int val;
    struct ELE *next;
};

/* sum_list - Sum the elements of a linked list */
int sum_list(list_ptr ls)
{
    int val = 0;
    while (ls) {
	val += ls->val;
	ls = ls->next;
    }
    return val;
}

/* rsum_list - Recursive version of sum_list */
int rsum_list(list_ptr ls)
{
    if (!ls)
	return 0;
    else {
	int val = ls->val;
	int rest = rsum_list(ls->next);
	return val + rest;
    }
}

/* copy_block - Copy src to dest and return xor checksum of src */
int copy_block(int *src, int *dest, int len)
{
    int result = 0;
    while (len > 0) {
	int val = *src++;
	*dest++ = val;
	result ^= val;
	len--;
    }
    return result;
}
/* $end examples */

int thesum = -1;

struct ELE ele3 = { 0xc00, 0 };
struct ELE ele2 = { 0x0b0, &ele3 };
struct ELE ele1 = { 0x00a, &ele2 };
list_ptr list = &ele1;

int main(void)
{
    thesum = sum_list(list);
    return 0;
}
