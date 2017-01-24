# -*- coding: utf-8 -*-

from __future__ import division
import re
from collections import *
from traceback import print_exc
import random, copy, itertools

# = Syntax ===============================

class LambdaSyntaxError (Exception):
  pass

EXPR = 0
VAR  = 1
APPL = 2
ABST = 3

def parse(s):
  toks = tokenize(s)
  tree = parse_partree(toks)
  return parse_parexpr(tree)
  
token_re = re.compile(r'[@.()]|[^\s@.()]+')
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
  
var_re = re.compile(r'[^\s@.()]+$')
def isvar(tok):
  try:
    return bool(var_re.match(tok))
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
    if tree[1] == '@':
      import importlib
      ext = importlib.import_module('ext_' + extra_params[0])
      ext.ext_parexpr(tree, extra_params, body)
    else:
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
  return s
  
num_re = re.compile( \
  r'(?P<nvb>^|(?<=[\s@.()]))?' \
  r'((?P<op>\()|(?P<start>^))' \
  r'@(?P<f>[^.]+).' \
  r'(' \
    r'(?P<one>(?P=f))' \
  r'|' \
    r'@(?P<x>[^.]+).' \
    r'(?P<fs>' \
      r'(?P<fp>(?P=f)\()*' \
      r'(?(fp)(?P=f) )' \
    r')' \
    r'(?P=x)' \
  r')' \
  r'(?(op)\))' \
  r'(?(fs)(?P<cps>\)*))' \
  r'(?(start)$)' \
  r'(?P<nva>$|(?=[\s@.()]))?' \
  )
def restore_nums(s):
  i = 0
  while True:
    m = num_re.search(s, i)
    if not m:
      break
    #print repr(m.group()), m.groupdict()
    if m.group('one') != None:
      num = 1
      n_cps = 1
    else:
      fp_w = len(m.group('f')) + 1
      num = len(m.group('fs')) // fp_w
      n_cps = len(m.group('cps'))
      if num:
        n_cps += 1
    end_i = m.end()
    if n_cps < num:
      i = end_i
      continue
    elif n_cps == num:
      v_after = m.group('nva') == None
    elif n_cps > num:
      end_i -= n_cps - num
      v_after = False
    start_i = m.start()
    v_before = m.group('nvb') == None
    r_str = (' ' if v_before else '') + str(num) + (' ' if v_after else '')
    s = s[:start_i] + r_str + s[end_i:]
    i += len(r_str)
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
  if abst[0] != ABST or new_name in FV(abst):
    raise StructureError
  abst[2] = substitute(abst[2], abst[1], [VAR, new_name])
  abst[1] = new_name
  return abst
    
def substitute(expr, name, rexpr, rfv=None):
  if rfv == None:
    if expr[0] == APPL and expr[1][0] == ABST and expr[1][1] in ('@b e', '@b b'):
      reduce_full(expr)
    if rexpr[0] == APPL and rexpr[1][0] == ABST and rexpr[1][1] in ('@b', '@b b'):
      reduce_full(rexpr)
    rfv = FV(rexpr)
  type = expr[0]
  if type == VAR:
    if name == expr[1]:
      expr[:] = copy.deepcopy(rexpr)
  elif type == APPL:
    for i in (1, 2):
      expr[i] = substitute(expr[i], name, rexpr, rfv)
  elif type == ABST:
    param = expr[1]
    if param != name:
      if param in rfv:
        alpha_convert(expr, param + '_' + format(random.randint(0, 0xffff), '04X'))
      expr[2] = substitute(expr[2], name, rexpr, rfv)
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
  expr_stack = deque([expr])
  while True:
    try:
      expr = expr_stack.pop()
    except IndexError:
      return False
    type = expr[0]
    if callable(type):
      try:
        type(expr[1])
        return True
      except ReductionError:
        pass
    elif type == ABST:
      expr_stack.extend([expr[2], (eta_convert, expr)])
    elif type == APPL:
      expr_stack.extend([expr[2], expr[1]])
      expr_stack.append((beta_reduce, expr))

cycle_ctr = 0

def reduce_full(expr, ct_cycles=False):
  global cycle_ctr
  if ct_cycles:
    cycle_ctr = 0
  ct = 0
  while reduce_expr(expr):
    ct += 1
    #print '@@churchnums.' + restore_nums(unparse(expr)); print
  cycle_ctr += ct
  if ct_cycles:
    ct = cycle_ctr
    cycle_ctr = 0
    return ct

# = Testing ==============================
  
def main():
  src = r'''

@@ churchnums.

'''
  # .standard
  src += \
  r'''

@@ def ++. (@ n.
  @f x.f (n f x))
@@ def +. (@ m n.
  m ++ n)
@@ def *. (@ m n.
  @f.m (n f))
@@ def **. (@ b e.
  e b)
@@ def --. (@ n.
  @f x.n (@g h.h (g f)) (@u.x) (@u.u))
@@ def -. (@ m n.
  n -- m)

@@ def #t.
  (@t f.t)
@@ def #f.
  (@t f.f)
@@ def &. (@ p q.
  p q p)
@@ def |. (@ p q.
  p p q)
@@ def !. (@ p.
  @a b.p b a)
@@ def ?:. (@ p a b.
  p a b)
@@ def 0?. (@ n.
  n (@x.#f) #t)
@@ def <=. (@ m n.
  0? (- m n))
@@ def >=. (@ m n.
  <= n m)
@@ def >. (@ m n.
  ! (<= m n))
@@ def <. (@ m n.
  ! (>= m n))
@@ def =. (@ m n.
  & (<= m n) (>= m n))

@@ def pair. (@ x y.
  @f.f x y)
@@ def get0. (@ p.
  p #t)
@@ def get1. (@ p.
  p #f)
@@ def #nil.
  (@x.#t)
@@ def nil?. (@ p.
  p @x y.#f)

@@ def Y. (@ g.
  (@x.g (x x)) (@x.g (x x)))
      
@@ def I.(@x.x)
@@ def K.(@x y.x)
@@ def S.(@x y z.x z (y z))
@@ def B.(@x y z.x (y z))
@@ def C.(@x y z.x z y)
@@ def W.(@x y.x y y)
@@ def U.(@x.x x)
@@ def omega.U
@@ def OMEGA.(omega omega)
    
@@ def ^. (@ p q.
  @@ def _not2. (@ p.
    p #f #t)
  p (_not2 q) q)

'''
  # math
  #src += \
  r'''

@@ def //. (@ n d.
  (0? d) #nil
    ((Y @Y_div d q r.
        (>= r d)
          (Y_div d (@@b.++ q) (@@b.- r d))
          (pair q r))
      d 0 n))

@@ def factorial. (Y @Y_fact n.
  (0? n) 1
    (* (Y_fact (@@b.-- n)) n))

'''
  # list
  src += \
  r'''

@@ def list:%ex1.
  (@e.pair 4 (pair 8 (pair 1 (pair 5 (pair 1 (pair 6 e))))))
@@ def list:%ex2.
  (@e.pair 2 (pair 3 (pair 4 (pair 2 e))))


@@ def list:append. (@ list list2.
  @e.list (list2 e))

@@ def list:appendx. (@ list x.
  list:append list (pair x))

@@ def list:del1. (@ list.
  @e.get1 (list e))

@@ def list:deln. (@ list n.
  @e.n get1 (list e))

@@ def list:pop1. (@ list.
  pair (list:del1 list)
    (get0 (list #e)))

@@ def list:popn. (Y @Y_pop list n dst.
  (0? n) (pair list dst)
    ((list:pop1 list) @list1 x.
        (Y_pop (@@b.list1) (@@b.-- n)
          (@@b.list:appendx dst x))))

@@ def list:getSlice. (@ list i n.
  get1 (list:popn
      (@@b.list:deln list i) n 1))

@@ def list:get. (@ list i.
  get0 (list:deln list i #e))
        
@@ def list:setSlice. (@ list i n list2.
  (list:popn list i 1) @sec0 sec1.
    list:append sec1 (list:append list2
        (list:deln sec0 n)))

@@ def list:set. (@ list i x.
  list:setSlice list i 1 (pair x))

@@ def list:delSlice. (@ list i n.
  list:setSlice list i n 1)

@@ def list:del. (@ list i.
  list:delSlice list i 1)

@@ def list:insert. (@ list i list2.
  list:setSlice list i 0 list2)

@@ def list:insertx. (@ list i x.
  list:insert list i (pair x))


@@ def list:repeat. (@ list n.
  n (list:append list) list)

@@ def list:length. (@ list.
  (Y @Y_len p n.
    (nil? p) n
      (Y_len (@@b.get1 p) (@@b.++ n)))
    (list #nil) 0)


@@ def list:applyAll. (@ func list.
  (Y @Y_aA func p.
    (nil? p) func
      (p @p0 p1.Y_aA (func p0) p1))
    func (list #nil))

@@ def list:_print. (@ list.
  list:applyAll [ (@@b.list) ])

'''
  # int
  #src += \
  r'''

@@ def int:%-4.(pair #t 4)
@@ def int:%3.(pair #f 3)

@@ def int:abs. (@ n.
  n @n0.pair #f)

@@ def int:neg. (@ n.
  n @n0.pair (! n0))

@@ def int:inc. (@ n.
  n @n0 n1.(0? n1)
    (pair #f 1)
    (pair n0
      ((n0 -- ++) n1)))

@@ def int:add. (@ m n.
  m @m0 m1.n @n0 n1.pair
    ((<= m1 n1) n0 m0)
    ((^ m0 n0)
      ((<= m1 n1)
        (- n1 m1)
        (- m1 n1))
      (+ m1 n1)))

@@ def int:dec. (@ n.
  n @n0 n1.(0? n1)
    (pair #t 1)
    (pair n0
      ((n0 ++ --) n1)))

@@ def int:sub. (@ m n.
  int:add m (int:neg n))

@@ def int:mul. (@ m n.
  m @m0 m1.n @n0 n1.pair
    (^ m0 n0)
    (* m1 n1))

@@ def int:zero?. (@ n.
  0? (get1 n))
  
@@ def int:neq?. (@ m n.
  m @m0 m1.n @n0 n1.
    (& (0? m1) (0? n1)) #f
      (| (^ m0 n0) (= m1 n1)))

@@ def int:leq?. (@ m n.
  m @m0 m1.n @n0 n1.
    (^ m0 n0)
      ((& (0? m1) (0? n1)) #t m0)
      ((m0 >= <=) m1 n1))

'''
  # uint10 (math, list)
  #src += \
  r'''

@@ def uint10:%243.
  (@e.pair 3 (pair 4 (pair 2 e)))
@@ def uint10:%89.
  (@e.pair 9 (pair 8 e))

@@ def uint10:_extp. (@ p.
  (nil? p) (pair 0 p) p)

@@ def uint10:_norm. (Y @Y_norm p s c.
  (& (nil? p) (0? c)) s
    ((uint10:_extp p) @p0 p1.
      (// (@@b.+ c p0) 10) @q r.
        Y_norm (@@b.p1)
          (@@b.list:appendx s r) q))

@@ def uint10:norm. (@ n.
  uint10:_norm (n #nil) 1 0)

@@ def uint10:inc. (@ n.
  (@e.(n e) @p0 p1.pair (++ p0) p1))

@@ def uint10:add. (@ m n.
  (Y @Y_add pm pn s.
    (& (nil? pm) (nil? pn)) s
      ((uint10:_extp pm) @pm0 pm1.
        (uint10:_extp pn) @pn0 pn1.
          Y_add (@@b.pm1) pn1
            (@@b.list:appendx s
              (@@b.+ pm0 pn0))))
    (m #nil) (n #nil) 1)

'''
  # .exec
  src += \
  r'''
  
list:_print
  (list:setSlice list:%ex1 2 3 list:%ex2)

'''
  expr = parse(src)
  import time
  t = time.time()
  cpu_t = time.clock()
  #print unparse(expr); print
  cycles = reduce_full(expr, True)
  cpu_t = time.clock() - cpu_t
  t = time.time() - t
  print '@@churchnums.' + restore_nums(unparse(expr))
  print '''    calculated in {} cycles
      {} CPU s
      {} s
'''.format(cycles, cpu_t, t)
  
if __name__ == '__main__':
  try:
    main()
    #import cProfile; cProfile.run('main()')
  except:
    print_exc()
    raise
