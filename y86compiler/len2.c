int List[] = { 1, 2, 3, 4, 0 };

/* Find number of elements in
   null-terminated list */
int len2(int a[])
{
  int len = 0;
  while (*a++)
      len++;
  return len;
}

int thelength = -1;

int main()
{
  thelength = len2(List);
  return 0;
}
