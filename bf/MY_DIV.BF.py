from brainfuck import execute
execute(r'''

+++++ ++
> +++

=== === === === === === === === ===
n;r  d   q  rcp dcp rge cp0 cp1 cp2
=0= =1= =2= =3= =4= =5= =6= =7= =8=

> [-]
> [-]
> [-]
> [-] +
> [-]
> [-]
> [-]

TO  5    <<<
WHILE    [
  DEBUG    #
  CLR      [-]
  TO  0    <<<<<
  DUP 3 4  [>>>+>+<<<<-]>>>>[<<<<+>>>>-]
  TO  1    <<<
  DUP 4 5  [>>>+>+<<<<-]>>>>[<<<<+>>>>-]
  GEQ      >>>+ [<<<<[>>+>+<<<-]>>>[<<<+>>>-]+<[>-<[-]]>[>[-]<<<+>>[-]] <<<<[>>>+>+<<<<-]>>>>[<<<<+>>>>-]+<[>-<[-]]>[>[-]<[-]] >[<+<+>>-]<[>+<-]<[<<<->->>-] >>]<<<
  BUP 6 7  [>+>+<<[-]]>>[<<+>>-]
  TO  6    <
  IF       [[-]
    TO  3    <<<
    CLR      [-]
    TO  2    <
    INC 1    +
    TO  1    <
    DUP 3 4  [>>+>+<<<-]>>>[<<<+>>>-]
    TO  3    <
    SUB 0    [<<<->>>-]
    TO  6    >>>
  END      ]
  TO  5    <
END      ]
TO  2    <<<

#

''')

r'''

q = 0
r = n
while r >= d:
	q += 1
	r -= d

'''
