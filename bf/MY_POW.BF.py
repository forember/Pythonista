from brainfuck import execute
execute(r'''

++
> +++

> [-]
> [-]
> [-]
<<<
[
  >>> +
  <<< -
]
<
[
  > +
  < -
]
+
>>>>
[
  <<<
  MUL  <[>[>+>+<<-] >[<+>-]<<-]
       >>>[<<<+>>>-]
  > -
]
<<<<

#

''')

r'''

VAR 'base' 0
VAR 'exp'  1
VAR 'pow'  2
VAR 'spc0' 3
VAR 'spc1' 4

PUT $base 2
PUT $exp  3


CLRALL $spc0 $spc1
PUT $pow 1
FOR $exp
	MUL $pow $base $spc0 $spc1
	ADD $spc0 $pow
END

'''
