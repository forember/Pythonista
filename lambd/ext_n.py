# -*- coding: utf-8 -*-

'''Parses the body normally

(@@n.expr) -> (expr)
'''

from lambd import *

def ext_parexpr(tree, extra_params, body):
  tree[:] = parse_parexpr(body)
