from brainfuck import execute
execute(r'''

[

CLR  =   [-]
ADD  =   [<+>-]<
DUP  =   >[-]>[-]<< [>+>+<<-]>>[<<+>>-]
SWAP =   >[-]< [>+<-]<[>+<-]>>[<<+>>-]<
MUL  =   >[-]>[-]<< <[>[>+>+<<-] >[<+>-] <<-] >>>[<<<+>>>-]<<<
IF   =   [ (your program here) [-]]

]

''')
