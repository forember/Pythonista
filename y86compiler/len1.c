int List[] = { 1, 2, 3, 4, 0 };

/* Find number of elements in
   null-terminated list */
int len1(int a[])
{
  int len;
  for (len = 0; a[len]; len++)
       ;
  return len;
}

int thelength = -1;

int main()
{
  thelength = len1(List);
  return 0;
}
