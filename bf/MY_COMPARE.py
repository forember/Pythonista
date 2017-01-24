from brainfuck import execute

op_nop = '', ''
op_leq = '', '+'
op_geq = '+', ''
op_eq1 = '+', '+'
op_cmp_max = '+', '++'
op_cmp_min = '++', '+'
op_lt = '+', '[-]'
op_gt = '++', '>+<[>-<[-]]>[<+>-]<'

al = 0, 1, 2
bl = 1, 1, 1
a_geq_b, b_geq_a = op_geq

def mk_comptest(a, b, a_geq_b, b_geq_a):
	return '+' * a + '>' + '+' * b + '#>[-]>[-]>[-]>[-]+ [#<<<<[>>+>+<<<-]>>>[<<<+>>>-]+<[>-<[-]]>[>[-]<<<' + a_geq_b + '>>[-]]# <<<<[>>>+>+<<<<-]>>>>[<<<<+>>>>-]+<[>-<[-]]>[>[-]<<<' + b_geq_a + '>>[-]]# >[<+<+>>-]<[>+<-]<[<<<->->>-] >>]<<<#'

ai = iter(al)
bi = iter(bl)
try:
	print (a_geq_b, b_geq_a)
	print
	while True:
		a = ai.next()
		b = bi.next()
		try:
			execute(mk_comptest(a, b, a_geq_b, b_geq_a))
		except:
			from traceback import print_exc
			print_exc()
			raise
		print
except StopIteration:
	pass
