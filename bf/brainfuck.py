from __future__ import print_function
from collections import deque
import re
from warnings import warn

ignore_re = re.compile(r'[^><+\-.,[\]#]+')
bracket_re = re.compile(r'[][]')

def execute(instrns):
	instrns = ignore_re.sub('', instrns)
	instrn_ptr = 0
	data = bytearray(1)
	data_ptr = 0
	open_brackets = []
	input_buffer = deque()
	while instrn_ptr < len(instrns):
		instrn = instrns[instrn_ptr]
		instrn_ptr += 1
		if instrn == '>':
			data_ptr += 1
			if data_ptr == len(data):
				data.append(0)
		elif instrn == '<':
			data_ptr -= 1
			if data_ptr == -1:
				raise IndexError, 'negative data pointer'
		elif instrn == '+':
			if data[data_ptr] == 0xff:
				data[data_ptr] = 0
			else:
				data[data_ptr] += 1
		elif instrn == '-':
			if data[data_ptr] == 0:
				data[data_ptr] = 0xff
			else:
				data[data_ptr] -= 1
		elif instrn == '.':
			b = data[data_ptr]
			if b:
				print(unichr(b), sep='', end='')
			del b
		elif instrn == ',':
			if not input_buffer:
				s = raw_input().decode('L1')
				input_buffer.extend(s)
				del s
			if input_buffer:
				c = input_buffer.popleft()
				data[data_ptr] = ord(c)
				del c
		elif instrn == '[':
			if instrn_ptr + 2 <= len(instrns) and instrns[instrn_ptr:instrn_ptr + 2] == '[-]':
				instrn_ptr += 2
				data[data_ptr] = 0
			if data[data_ptr] == 0:
				depth = 1
				for match in bracket_re.finditer(instrns, instrn_ptr):
					c = match.group()
					if c == '[':
						depth += 1
					elif c == ']':
						depth -= 1
					else:
						warn("interpreter warning: bracket_re found a match other than '[' or ']'")
					if depth == 0:
						instrn_ptr = match.end()
						del depth, match, c
						break
				else:
					raise SyntaxError, 'no corresponding ] found'
			else:
				open_brackets.append(instrn_ptr)
		elif instrn == ']':
			if data[data_ptr] == 0:
				del open_brackets[-1]
			else:
				instrn_ptr = open_brackets[-1]
		elif instrn == '#':
			print(data_ptr, '(', *(format(b, '02x') for b in data), end=' )\n')
		else:
			warn('interpreter warning: not all non-instruction characters were removed at startup')
