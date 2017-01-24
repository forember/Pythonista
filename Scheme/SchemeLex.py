# -*- coding: utf-8 -*-

import re

class LexError (Exception):
	pass

def p_type(typename):
	def f(s, iptr):
		m, iptr = node_types[typename](s, iptr)
		return (typename, m), iptr
	return f
	
def p_re(pattern, flags=re.IGNORECASE):
	compiled_re = re.compile(pattern, flags)
	def f(s, iptr):
		m = compiled_re.match(s, iptr)
		if m:
			return (None, m.group()), m.end()
		raise LexError, iptr
	return f
	
def p_or(*funcs):
	def f(s, iptr):
		for func in funcs:
			try:
				return func(s, iptr)
			except LexError:
				pass
		raise LexError, iptr
	return f
	
def p_chain(*funcs):
	def f(s, iptr):
		ms = []
		for func in funcs:
			m, iptr = func(s, iptr)
			ms.append(m)
		return ('*', ms), iptr
	return f
	
def p_star(func):
	def f(s, iptr):
		ms = []
		try:
			while True:
				m, iptr = func(s, iptr)
				ms.append(m)
		except LexError:
			pass
		return ('*', ms), iptr
	return f
	
def p_plus(func):
	def f(s, iptr):
		m = p_star(func)(s, iptr)
		if m[0][1]:
			return m
		raise LexError, iptr
	return f
	
def p_lookahead(func):
	def f(s, iptr):
		func(s, iptr)
		return (None, ''), iptr
	return f
	
def t_variable(s, iptr):
	try:
		p_type('syntactic keyword')(s, iptr)
	except LexError:
		m, iptr = p_type('identifier')(s, iptr)
		return ('variable', m), iptr
	raise LexError
	
def u_error(s, iptr):
	raise LexError, iptr
	
u_lex = \
	p_chain(
		p_type('intertoken space'),
		p_star(p_chain(
			p_type('token'),
			p_type('intertoken space')
		)),
	)

def lex(s):
	m, iptr = u_lex(s, 0)
	if iptr != len(s):
		raise LexError, iptr
	return m
	
def repr_m(m, indent=0):
	t = m[0]
	if t == None:
		return '{indent}({m[0]!r},\n{indent} {m[1]!r})\n'.format(indent=' ' * indent, m=m)
	elif t == '*':
		msindent = indent + 1
		msrepr = ''.join(repr_m(n, msindent) for n in m[1])
		return '{indent}({t!r}, [\n{msrepr}{indent}])\n'.format(indent=' ' * indent, t=t, msrepr=msrepr)
	else:
		mrepr = repr_m(m[1], indent + 1)
		return '{indent}({t!r},\n{mrepr}{indent})\n'.format(indent=' ' * indent, t=t, mrepr=mrepr)
	return s

def main():
	#print repr_m(lex('(display "Hello World!")'))
	import sys
	execfile(sys.argv[0] + '_main.py')


node_types = {
	'empty':
		p_re(r''),
	
	'token':
		p_or(
			p_type('identifier'),
			p_type('boolean'),
			p_type('number'),
			p_type('character'),
			p_type('string'),
			p_re(r"#\(|,@|[()'`,.]"),
		),
	'delimiter':
		p_or(
			p_type('whitespace'),
			p_re(r'[()";]'),
		),
	'whitespace':
		p_re(r'\s'),
	'comment':
		p_re(r';.*'),
	'atmosphere':
		p_or(
			p_type('whitespace'),
			p_type('comment'),
		),
	'intertoken space':
		p_star(p_type('atmosphere')),
	
	'identifier':
		p_chain(
			p_or(
				p_chain(
					p_type('initial'),
					p_star(p_type('subsequent')),
				),
				p_type('peculiar identifier'),
			),
			p_lookahead(p_type('delimiter')),
		),
	'initial':
		p_or(
			p_type('letter'),
			p_type('special initial'),
		),
	'letter':
		p_re(r'[a-z]'),
	
	'special initial':
		p_re(r'[!$%&*/:<=>?^_~]'),
	'subsequent':
		p_or(
			p_type('initial'),
			p_type('digit'),
			p_type('special subsequent'),
		),
	'digit':
		p_re(r'[0-9]'),
	'special subsequent':
		p_re(r'[+\-.@]'),
	'peculiar identifier':
		p_re(r'\.\.\.|[+\-]'),
		
	'syntactic keyword':
		p_or(
			p_type('expression keyword'),
			p_re(r'else|=>|define|unquote(-splicing)?'),
		),
	'expression keyword':
		p_re(r'quote|lambda|if|set!|begin|cond|and|or|case|let(\*|rec)?|do|delay|quasiquote'),
		
	'variable':
		t_variable,
		
	'boolean':
		p_re(r'#[tf]'),
	'character':
		p_chain(
			p_re(r'#\\'),
			p_or(
				p_re(r'.|\n'),
				p_type('character name'),
			),
			p_lookahead(p_type('delimiter')),
		),
	'character name':
		p_re(r'space|newline'),
		
	'string':
		p_chain(
			p_re(r'"'),
			p_star(p_type('string element')),
			p_re(r'"'),
		),
	'string element':
		p_re(r'[^"\\]|\\["\\]'),
	
	'number':
		p_chain(
			p_or(
				p_type('num 2'),
				p_type('num 8'),
				p_type('num 10'),
				p_type('num 16'),
			),
			p_lookahead(p_type('delimiter')),
		),
}

for r in (2, 8, 10, 16):
	r = str(r)
	num_r = 'num ' + r
	complex_r = 'complex ' + r
	real_r = 'real ' + r
	ureal_r = 'ureal ' + r
	decimal_r = 'decimal ' + r
	uinteger_r = 'uinteger ' + r
	prefix_r = 'prefix ' + r
	radix_r = 'radix ' + r
	digit_r = 'digit ' + r
	node_types.update({
		num_r:
			p_chain(
				p_type(prefix_r),
				p_type(complex_r),
			),
		complex_r:
			p_or(
				p_chain(
					p_type(real_r),
					p_or(
						p_chain(
							p_re(r'@'),
							p_type(real_r),
						),
						p_type('empty'),
					),
				),
				p_chain(
					p_or(
						p_type(real_r),
						p_type('empty'),
					),
					p_re(r'[+\-]'),
					p_or(
						p_type(ureal_r),
						p_type('empty'),
					),
					p_re(r'i'),
				),
			),
		real_r:
			p_chain(
				p_type('sign'),
				p_type(ureal_r),
			),
		ureal_r:
			p_or(
				p_chain(
					p_type(uinteger_r),
					p_or(
						p_chain(
							p_re(r'/'),
							p_type(uinteger_r),
						),
						p_type('empty'),
					),
				),
				p_type(decimal_r),
			),
		decimal_r:
			u_error,
		uinteger_r:
			p_chain(
				p_plus(p_type(digit_r)),
				p_star(p_re(r'#')),
			),
		prefix_r:
			p_or(
				p_chain(
					p_type(radix_r),
					p_type('exactness'),
				),
				p_chain(
					p_type('exactness'),
					p_type(radix_r),
				),
			),
	})

node_types.update({
	'decimal 10':
		p_chain(
			p_chain(
				p_or(
					p_chain(
						p_re(r'\.'),
						p_plus(p_type('digit 10')),
					),
					p_chain(
						p_plus(p_type('digit 10')),
						p_re(r'#+\.#*'),
					),
					p_chain(
						p_plus(p_type('digit 10')),
						p_re(r'\.'),
						p_star(p_type('digit 10')),
					),
				),
				p_star(p_re(r'#')),
			),
			p_type('suffix'),
		),
	
	'suffix':
		p_or(
			p_chain(
				p_type('exponent marker'),
				p_type('sign'),
				p_plus(p_type('digit 10')),
			),
			p_type('empty'),
		),
	'exponent marker':
		p_re(r'[esfdl]'),
	'sign':
		p_re(r'[+\-]?'),
	'exactness':
		p_re(r'(#[ie])?'),
	'radix 2':
		p_re(r'#b'),
	'radix 8':
		p_re(r'#o'),
	'radix 10':
		p_re(r'(#d)?'),
	'radix 16':
		p_re(r'#x'),
	'digit 2':
		p_re(r'[01]'),
	'digit 8':
		p_re(r'[0-7]'),
	'digit 10':
		p_type('digit'),
	'digit 16':
		p_or(
			p_type('digit'),
			p_re(r'[a-f]'),
		),
})

if __name__ == '__main__':
	main()

