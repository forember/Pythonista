from brainfuck import execute
execute(r'++++++++++[>+++++++>++++++++++>+++>+>++++<<<<<-]>++.>+.+++++++..+++.>>>++++.<<++.<++++++++.--------.+++.------.--------.>+.>.')

r'''

+++++ +++++             initialize counter (cell #0) to 10
[                       use loop to set the next four cells to 70/100/30/10/40
    > +++++ ++              add  7 to cell #1
    > +++++ +++++           add 10 to cell #2 
    > +++                   add  3 to cell #3
    > +                     add  1 to cell #4
    > ++++                  add 4 to cell #5
    <<<<< -                  decrement counter (cell #0)
]                   
> ++ .                  print 'H'
> + .                   print 'e'
+++++ ++ .              print 'l'
.                       print 'l'
+++ .                   print 'o'
>>> ++++ .              print '\x2c'
<< ++ .                 print ' '
 
< +++++ +++ .           print 'w'
 ----- --- .            print 'o'
+++ .                   print 'r'
----- - .               print 'l'
----- --- .             print 'd'
> + .                   print '!'
> .                     print '\n'

'''

r'''

+++++ +++++
[
  > +++++ ++
  > +++++ +++++
  > +++
  > +
  > ++++
  <<<<< -
]

0 70 100 30 10 40
^

> ++ .        'H'
> + .         'e'
+++++ ++ .    'l'
.             'l'
+++ .         'o'
>>> ++++ .    comma
<< ++ .       ' '
< +++++ +++ . 'w'
----- --- .   'o'
+++ .         'r'
----- - .     'l'
----- --- .   'd'
> + .         '!'
> .           '\n'

'''
