from brainfuck import execute
execute(r'''++

>[-]>[-]<<[>+>+<<-]>>[<<+>>-]

#''')

r'''

++

> [-]
> [-]
<<
[
  > +
  > +
  << -
]
>>
[
  << +
  >> -
]

#

'''
