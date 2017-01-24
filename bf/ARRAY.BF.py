from brainfuck import execute
execute(r'''

Array test
DIM A(8)
array looks like this:
0AB#?#?#?#?#?#?#?#?

>>++++++<+++ B=6:A(B)=3
starts at A
>[>>[-]<<-[>>+<<-]+>>]>[-]<<<[<<]>[>[>>]>+<<<[<<]>-]>-<

#''')

r'''

>> +++++ + 
< +++

>
[
  >> [-]
  << -
  [
    >> +
    << -
  ]
  +
  >>
]
> [-]
<<<
[<<]
>
[
  >
  [>>]
  > +
  <<<
  [<<]
  > -
]
> -
<

#

'''
