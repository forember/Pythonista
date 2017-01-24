# -*- coding: utf-8 -*-

from __future__ import division
import re
from collections import *
from traceback import print_exc
import random, copy, itertools

# = Syntax ===============================

class LambdaSyntaxError (Exception):
	pass

token_re = re.compile(r'[@.()]|[^\s@.()]+')

EXPR = 0
VAR  = 1
APPL = 2
ABST = 3

def parse(s):
	toks = tokenize(s)
	tree = parse_partree(toks)
	return parse_parexpr(tree)
	
def tokenize(s):
	return token_re.findall(s)
		
def parse_partree(toks):
	tree = [EXPR]
	branchdeque = deque()
	branch = tree
	for tok in toks:
		if tok == '(':
			branch.append([EXPR])
			branchdeque.append(branch)
			branch = branch[-1]
		elif tok == ')':
			branch = branchdeque.pop()
		else:
			branch.append(tok)
	return tree
	
def isvar(tok):
	try:
		return bool(re.match(r'[^\s@.()]+$', tok))
	except:
		return False
	
def parse_parexpr(tree):
	if len(tree) == 2:
		if isvar(tree[1]):
			tree[0] = VAR
		else:
			tree[:] = parse_parexpr(tree[1])
	elif tree[1] == '@':
		tree[0] = ABST
		doti = tree.index('.')
		extra_params = tree[3:doti]
		body = [EXPR] + tree[doti+1:]
		tree[1] = tree[2]
		tree[2:] = [None]
		branch = tree
		for param in extra_params:
			if isvar(param):
				branch[2] = [ABST, param, None]
				branch = branch[2]
			else:
				raise LambdaSyntaxError
		branch[2] = parse_parexpr(body)
	else:
		tree[0] = APPL
		if '@' in tree:
			lambdai = tree.index('@')
			tree[lambdai:] = [[ABST] + tree[lambdai:]]
		if len(tree) == 3:
			for i in (1, 2):
				if isvar(tree[i]):
					tree[i] = [VAR, tree[i]]
				else:
					tree[i] = parse_parexpr(tree[i])
		else:
			if isvar(tree[-1]):
				tree[-1] = [VAR, tree[-1]]
			else:
				tree[-1] = parse_parexpr(tree[-1])
			tree[1:-1] = [parse_parexpr([APPL] + tree[1:-1])]
	return tree
	
def unparse(ast):
	s = ''
	type = ast[0]
	if type == VAR:
		s += ast[1]
	elif type == ABST:
		s += '@' + ast[1] + '.' + unparse(ast[2])
	elif type == APPL:
		if ast[1][0] == ABST:
			s += '(' + unparse(ast[1]) + ')'
		else:
			s += unparse(ast[1])
			if ast[2][0] == VAR:
				s += ' '
		if ast[2][0] != VAR:
			s += '(' + unparse(ast[2]) + ')'
		else:
			s += unparse(ast[2])
	elif type == EXPR:
		s += unparse(ast[1])
	return s
	
def repr_ast(ast, indent=''):
	type = ast[0]
	if type == VAR:
		return '{}[VAR, {!r}]'.format(indent, ast[1])
	elif type == ABST:
		return '{indent}[ABST, {!r},\n{}\n{indent}]'.format(ast[1], repr_ast(ast[2], indent + ' '), indent=indent)
	elif type == APPL:
		return '{indent}[APPL,\n{},\n{}\n{indent}]'.format(repr_ast(ast[1], indent + ' '), repr_ast(ast[2], indent + ' '), indent=indent)
	
# = Semantics ============================

class ReductionError (Exception):
	pass
	
class StructureError (ReductionError):
	pass
	
def FV(expr):
	type = expr[0]
	if type == VAR:
		return {expr[1]}
	elif type == ABST:
		return FV(expr[2]) - {expr[1]}
	elif type == APPL:
		return FV(expr[1]) | FV(expr[2])
	
def alpha_convert(abst, new_name):
	if abst[0] != ABST:
		raise StructureError
	abst[2] = substitute(abst[2], abst[1], [VAR, new_name])
	abst[1] = new_name
	return abst
		
def substitute(expr, name, rexpr):
	type = expr[0]
	if type == VAR:
		if name == expr[1]:
			expr[:] = copy.deepcopy(rexpr)
	elif type == APPL:
		for i in (1, 2):
			expr[i] = substitute(expr[i], name, rexpr)
	elif type == ABST:
		param = expr[1]
		if param != name:
			if param in FV(rexpr):
				alpha_convert(expr, param + '_' + format(random.randint(0, 0xffff), '04X'))
			expr[2] = substitute(expr[2], name, rexpr)
	return expr
	
def beta_reduce(appl):
	if appl[0] != APPL or appl[1][0] != ABST:
		raise StructureError
	appl[:] = substitute(appl[1][2], appl[1][1], appl[2])
	return appl
	
def eta_convert(abst):
	if abst[0] != ABST or abst[2][0] != APPL or abst[1] != abst[2][2][1] or abst[1] in FV(abst[2][1]):
		raise StructureError
	abst[:] = abst[2][1]
	return abst
	
def reduce_expr(expr):
	type = expr[0]
	if type == ABST:
		try:
			eta_convert(expr)
			return True
		except ReductionError:
			pass
		return reduce_expr(expr[2])
	elif type == APPL:
		try:
			beta_reduce(expr)
			return True
		except ReductionError:
			pass
		return reduce_expr(expr[1]) or reduce_expr(expr[2])
	else:
		return False

# = Testing ==============================
	
def main():
	expr = parse(r'''
		
		(@y x.y)x
		
	''')
	print unparse(expr)
	while reduce_expr(expr):
		print unparse(expr)
	
if __name__ == '__main__':
	try:
		main()
	except:
		print_exc()
		raise
