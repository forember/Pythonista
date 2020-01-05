#!/usr/bin/python3

import sys, re, subprocess

# Number of Temporary Register Slots
TMP_REG_SLOTS = 0

# Error Handling Variables
EXIT_ON_ERROR = False  # if False, continue conversion after an error
RETURNCODE = 0  # the program exit code

# Line Regexes
RE_EMPTY_LINE = re.compile(r'\s*$')
RE_DIRECTIVE = re.compile(r'\t\.(.*)$')
RE_LABEL = re.compile(r'.*:$')
RE_INSTRUCTION = re.compile(r'\t(?P<inst>\w+)(?:\s+(?P<args>.*))?$')

# Misc Regexes
PTN_ARG_LABEL = r'(?P<label1>[a-zA-Z_\.][\w\.]*)' # may need work
RE_ARG_LABEL = re.compile(PTN_ARG_LABEL)

# Address Mode Component Regexes
# Numbers
PTN_NUM = r'\-?(?:0x)?\d*'
RE_NUM = re.compile(PTN_NUM)
# Registers
PTN_REG = r'%e(?:[acdb]x|[sd]i|[sb]p)'
RE_REG = re.compile(PTN_REG)
# Immediates
PTN_IMM = r'\$('+PTN_NUM+'|'+PTN_ARG_LABEL+')'
RE_IMM = re.compile(PTN_IMM)
# Displacement Memory Addressing
PTN_MEM = r'(?:'+PTN_NUM+'|'+PTN_ARG_LABEL+r')?\(('+PTN_REG+r')\)|'+PTN_ARG_LABEL.replace('(?P<label1>', '(?P<label3>')
RE_MEM = re.compile(PTN_MEM)
# Indexed Memory Addressing
PTN_EMEM = '((?:'+PTN_NUM+'|'+PTN_ARG_LABEL+r')?)\(('+PTN_REG+r'),\s*('+PTN_REG+')(?:,\s*([1248]))?\)'
RE_EMEM = re.compile(PTN_EMEM)

def compile_am(ptn1, ptn2):
  '''Compiles two patterns into a std two-arg list regex.
  
  Uses the following pattern:
    r'(?P<arg1>'+ptn1+r'),\s*(?P<arg2>'+ptn2+r')$'
  '''
  # check if input patterns are valid
  re.compile(ptn1)
  re.compile(ptn2)
  # avoid label group name collision
  ptn2 = ptn2.replace('(?P<label1>', '(?P<label2>')
  ptn2 = ptn2.replace('(?P<label3>', '(?P<label4>')
  # compile final regex object
  return re.compile(r'(?P<arg1>'+ptn1+r'),\s*(?P<arg2>'+ptn2+r')$')

# Address Mode Constants
AM_RR = 0  # Register to Register
AM_IR = 1  # Immediate to Register
AM_RM = 2  # Register to Memory (Displacement)  
AM_MR = 3  # Memory (D) to Register
AM_MM = 4  # Memory (D) to Memory (D)
AM_IM = 5  # Immediate to Memory (D)
AM_RE = 6  # Register to Memory (Indexed)
AM_ER = 7  # Memory (I) to Register
AM_EE = 8  # Memory (I) to Memory (I)
AM_IE = 9  # Immediate to Memory (I)
AM_ME = 10 # Memory (D) to Memory (I)
AM_EM = 11 # Memory (I) to Memory (D)
# Address Mode Regexes
AM_DICT = { AM_RR: compile_am(PTN_REG, PTN_REG),
            AM_IR: compile_am(PTN_IMM, PTN_REG),
            AM_RM: compile_am(PTN_REG, PTN_MEM),
            AM_MR: compile_am(PTN_MEM, PTN_REG),
            AM_MM: compile_am(PTN_MEM, PTN_MEM),
            AM_IM: compile_am(PTN_IMM, PTN_MEM),
            AM_RE: compile_am(PTN_REG, PTN_EMEM),
            AM_ER: compile_am(PTN_EMEM, PTN_REG),
            AM_EE: compile_am(PTN_EMEM, PTN_EMEM),
            AM_IE: compile_am(PTN_IMM, PTN_EMEM),
            AM_ME: compile_am(PTN_MEM, PTN_EMEM),
            AM_EM: compile_am(PTN_EMEM, PTN_MEM) }

# Native Movl Address Modes
BUILTIN_MOVL_AM_INSTRUCTIONS = { AM_RR: 'rrmovl',
                                 AM_IR: 'irmovl',
                                 AM_RM: 'rmmovl',
                                 AM_MR: 'mrmovl' }


def address_mode(args):
  '''Detects address mode of given 2-args string.
  
  Returns a tuple of the address mode constant and the regex match object.
  Returns None if the address mode is unrecognized.'''
  for am in AM_DICT:
    m = AM_DICT[am].match(args)
    if m:
      return am, m

def address_mode_error(args):
  '''address_mode with exceptions.
  
  Raises an InstructionError if the address mode is unrecognized.'''
  am_tuple = address_mode(args)
  if am_tuple is None:
    raise InstructionError('unrecognized address mode')
  return am_tuple


# General-Use Registers
GENERAL_REGISTERS = ['%eax', '%ecx', '%edx',
                     '%ebx', '%esi', '%edi']

def get_unbound_registers(args, in_list=GENERAL_REGISTERS):
  '''Gets the unbound registers in args.
  
  Returns the registers in in_list that are not in args.'''
  regs = in_list[:]
  for m in RE_REG.finditer(args):
    reg = m.group()
    try:
      regs.remove(reg)
    except ValueError:
      pass
  return regs


def require_tmp_reg_slots(n):
  if TMP_REG_SLOTS < n:
    globals()['TMP_REG_SLOTS'] = n

def save_tmp_reg(reg, slot):
  '''Get instruction to save a register to a slot'''
  require_tmp_reg_slots(slot)
  return ('rmmovl', reg+', TmpReg'+str(slot))

def load_tmp_reg(reg, slot):
  '''Get instruction to load a register from a slot'''
  require_tmp_reg_slots(slot)
  return ('mrmovl', 'TmpReg'+str(slot)+', '+reg)


class InstructionError (Exception):
  '''Generic exception for the Instructions class.'''
  def __init__(self, *args, must_exit=False):
    Exception.__init__(self, *args)
    self.must_exit = must_exit

class Instructions (object):
  '''Used to convert IA32 instructions into Y86 instructions.'''
  
  @staticmethod
  def _shift_multiply(reg, factor):
    from math import log
    x = log(factor, 2)
    if x % 1 != 0:
      raise InstructionError('non-power-of-2 factor: %d'.format(factor))
    x = int(x)
    return [('addl', reg+', '+reg)]*x
  
  # --[ Move Instructions ]----------------------------------------------------
  @staticmethod
  def INST_movl(args, **kwargs):
    # get address mode and matcher
    am, m = address_mode_error(args)
    if am in BUILTIN_MOVL_AM_INSTRUCTIONS:
      # address mode natively supported
      return [(BUILTIN_MOVL_AM_INSTRUCTIONS[am], args)]
    else:
      # get unbound registers
      unbound_regs = get_unbound_registers(args)
      # separate the arguments
      arg1 = m.group('arg1')
      arg2 = m.group('arg2')
      if am == AM_MM:
        # M4[arg2] <- M4[arg1]
        tmp_reg = unbound_regs.pop(0)
        inst_list = [ save_tmp_reg(tmp_reg, 1),
                      ('mrmovl', arg1+', '+tmp_reg),  # R[tmp] <- M4[arg1]
                      ('rmmovl', tmp_reg+', '+arg2),  # M4[arg2] <- R[tmp]
                      load_tmp_reg(tmp_reg, 1) ]
      elif am == AM_IM:
        # M4[arg2] <- arg1
        tmp_reg = unbound_regs.pop(0)
        inst_list = [ save_tmp_reg(tmp_reg, 1),
                      ('irmovl', arg1+', '+tmp_reg),  # R[tmp] <- arg1
                      ('rmmovl', tmp_reg+', '+arg2),  # M4[arg2] <- R[tmp]
                      load_tmp_reg(tmp_reg, 1) ]
      elif am == AM_ER:
        # R[arg2] <- M4[arg1]
        # arg1 = R[Rb]+S*R[Ri]+D
        print('\t'+args)
        print('\t'+str(m.groups()))
        a1D  = m.group(2)
        print('\ta1D:', a1D)
        a1Rb = m.group(4)
        print('\ta1Rb:', a1Rb)
        a1Ri = m.group(5)
        print('\ta1Ri:', a1Ri)
        print('\ta1S:', m.group(6))
        a1S  = int(m.group(6))
        tmp_reg = unbound_regs.pop(0)
        inst_list = [ save_tmp_reg(tmp_reg, 1),
                      ('rrmovl', a1Ri+', '+tmp_reg) ]          # R[tmp] <- R[a1Ri]
        inst_list.extend(Instructions._shift_multiply(tmp_reg, a1S))# R[tmp] <- a1S*R[tmp]
        inst_lis2 = [ ('addl',   a1Rb+', '+tmp_reg),           # R[tmp] <- R[tmp] + R[a1Rb]
                      ('mrmovl', a1D+'('+tmp_reg+'), '+arg2),  # R[arg2] <- M4[R[tmp]]
                      load_tmp_reg(tmp_reg, 1) ]
        inst_list.extend(inst_lis2)
      else:
        raise InstructionError('unsupported (for now) address mode') #TODO
      return inst_list
  
  @staticmethod
  def cmov_inst(inst, args):
    '''Translates cmov* instructions.'''
    am, m = address_mode_error(args)
    if am == AM_RR:
      return [(inst, args)]
    else:
      raise InstructionError('unsupported (for now) address mode') #TODO
  
  @staticmethod
  def INST_cmovle(args, **kwargs):
    Instructions.cmov_inst('cmovle', args)
  
  @staticmethod
  def INST_cmovl(args, **kwargs):
    Instructions.cmov_inst('cmovl', args)
  
  @staticmethod
  def INST_cmove(args, **kwargs):
    Instructions.cmov_inst('cmove', args)
  
  @staticmethod
  def INST_cmovne(args, **kwargs):
    Instructions.cmov_inst('cmovne', args)
  
  @staticmethod
  def INST_cmovge(args, **kwargs):
    Instructions.cmov_inst('cmovge', args)
  
  @staticmethod
  def INST_cmovg(args, **kwargs):
    Instructions.cmov_inst('cmovg', args)
  # ---------------------------------------------------------------------------
  
  # --[ Builtin ALU Instructions ]---------------------------------------------
  @staticmethod
  def builtin_alu_inst(inst, args):
    '''Translates native ALU instructions (addl, subl, andl, xorl).'''
    # get address mode and matcher
    am, m = address_mode_error(args)
    if am == AM_RR:
      # address mode natively supported
      return [(inst, args)]
    else:
      # get unbound registers
      unbound_regs = get_unbound_registers(args)
      # separate the arguments
      arg1 = m.group('arg1')
      arg2 = m.group('arg2')
      if am == AM_IR:
        # R[arg2] <- R[arg2] OP arg1
        tmp_reg = unbound_regs.pop(0)
        inst_list = [ save_tmp_reg(tmp_reg, 1),
                      ('irmovl', arg1+', '+tmp_reg),  # R[tmp] <- arg1
                      (inst,     tmp_reg+', '+arg2),  # R[arg2] <- R[arg2] OP R[tmp]
                      load_tmp_reg(tmp_reg, 1) ]
      elif am == AM_RM:
        # M4[arg2] <- M4[arg2] OP R[arg1]
        tmp_reg = unbound_regs.pop(0)
        inst_list = [ save_tmp_reg(tmp_reg, 1),
                      ('mrmovl', arg2+', '+tmp_reg),  # R[tmp] <- M4[arg2]
                      (inst,     arg1+', '+tmp_reg),  # R[tmp] <- R[tmp] OP R[arg1]
                      ('rmmovl', tmp_reg+', '+arg2),  # M4[arg2] <- R[tmp]
                      load_tmp_reg(tmp_reg, 1) ]
      elif am == AM_MR:
        # R[arg2] <- R[arg2] OP M4[arg1]
        tmp_reg = unbound_regs.pop(0)
        inst_list = [ save_tmp_reg(tmp_reg, 1),
                      ('mrmovl', arg1+', '+tmp_reg),  # R[tmp] <- M4[arg1]
                      (inst,     tmp_reg+', '+arg2),  # R[arg2] <- R[arg2] OP R[tmp]
                      load_tmp_reg(tmp_reg, 1) ]
      else:
        raise InstructionError('unsupported (for now) address mode') #TODO
      return inst_list
  
  @staticmethod
  def INST_addl(args, **kwargs):
    return Instructions.builtin_alu_inst('addl', args)
  
  @staticmethod
  def INST_subl(args, **kwargs):
    return Instructions.builtin_alu_inst('subl', args)
  
  @staticmethod
  def INST_andl(args, **kwargs):
    return Instructions.builtin_alu_inst('andl', args)
  
  @staticmethod
  def INST_xorl(args, **kwargs):
    return Instructions.builtin_alu_inst('xorl', args)
  # ---------------------------------------------------------------------------
  
  # --[ Jump Instructions ]----------------------------------------------------
  @staticmethod
  def jump_inst(inst, args):
    '''Translates jump instructions.'''
    m = RE_ARG_LABEL.match(args)
    if m:
      return [(inst, args)]
    else:
      # address jumps are not allowed since the addresses are different
      # for the Y86 program than they are for the original IA32
      raise InstructionError('non-label jump (unsupported)')
  
  @staticmethod
  def INST_jmp(args, **kwargs):
    return Instructions.jump_inst('jmp', args)
  
  @staticmethod
  def INST_jle(args, **kwargs):
    return Instructions.jump_inst('jle', args) 
  
  @staticmethod
  def INST_jl(args, **kwargs):
    return Instructions.jump_inst('jl', args) 
  
  @staticmethod
  def INST_je(args, **kwargs):
    return Instructions.jump_inst('je', args) 
  
  @staticmethod
  def INST_jne(args, **kwargs):
    return Instructions.jump_inst('jne', args) 
  
  @staticmethod
  def INST_jge(args, **kwargs):
    return Instructions.jump_inst('jge', args) 
  
  @staticmethod
  def INST_jg(args, **kwargs):
    return Instructions.jump_inst('jg', args) 
  # ---------------------------------------------------------------------------
  
  # --[ Direct Instructions ]--------------------------------------------------
  @staticmethod
  def INST_nop(args, **kwargs):
    return [('nop',)]
  
  @staticmethod
  def INST_call(args, **kwargs):
    return [('call', args)]
  
  @staticmethod
  def INST_ret(args, **kwargs):
    return [('ret',)]
  
  @staticmethod
  def INST_pushl(args, **kwargs):
    return [('pushl', args)]
  
  @staticmethod
  def INST_popl(args, **kwargs):
    return [('popl', args)]
  # ---------------------------------------------------------------------------
  
  # --[ Software Instructions ]------------------------------------------------
  @staticmethod
  def flags_inst(inst, args):
    '''Translates flags instructions (cmpl, testl).'''
    # get address mode and matcher
    am, m = address_mode_error(args)
    # get unbound registers
    unbound_regs = get_unbound_registers(args)
    # split the arguments
    arg1 = m.group('arg1')
    arg2 = m.group('arg2')
    if am == AM_RR:
      # CC <- R[arg2] OP R[arg1]
      tmp_reg = arg2  # tmp == arg2
      inst_list = [ save_tmp_reg(tmp_reg, 1),
                    (inst, args),  # R[tmp] <- R[arg2] OP R[arg1]
                    load_tmp_reg(tmp_reg, 1) ]
    else:
      raise InstructionError('unsupported (for now) address mode') #TODO
    return inst_list
  
  @staticmethod
  def INST_cmpl(args, **kwargs):
    return Instructions.flags_inst('subl', args)
  
  @staticmethod
  def INST_testl(args, **kwargs):
    return Instructions.flags_inst('andl', args)
  
  @staticmethod
  def INST_leave(args, **kwargs):
    return [('rrmovl', '%ebp, %esp'),
            ('popl',   '%ebp')]
  
  @staticmethod
  def INST_rep(args, line_enum=None, **kwargs):
    # Some compilers use rep before ret for hardware reasons.
    # This is NOT an implementation of rep.
    if args == 'ret':
      return [('ret',)]
    must_exit = False
    if line_enum is not None:
      # The line iterator will be advanced, so error is fatal to avoid confusion.
      must_exit = True
      next_i, next_line = next(line_enum, (None, None))
      if next_line == '\tret\n':
        return [('ret',)]
    raise InstructionError('non-rep-ret use of rep', must_exit=must_exit)
  # ---------------------------------------------------------------------------


def handle_error(out_file, line, msg="unknown error:", returncode=1, must_exit=False):
  '''Handles conversion errors.'''
  print('{}\n\t{}'.format(msg, line))
  out_file.writelines(['\t##!!! ERROR: {}  {}'.format(msg, line)])
  globals()['RETURNCODE'] = returncode
  if EXIT_ON_ERROR or must_exit:
    print('!!! FATAL ERROR !!!')
    out_file.writelines(['##!!! FATAL ERROR !!!'])
    raise SystemExit(RETURNCODE)

def convert_asm(line_it, out_file, inst_obj=Instructions()):
  '''Converts IA32 assembly into Y86 assembly.'''
  line_enum = enumerate(line_it, 1)
  for i, line in enumerate(line_it, 1):
    _convert_asm_handle_line(i, line, line_enum, out_file, inst_obj)

def _convert_asm_handle_line(i, line, line_enum, out_file, inst_obj):
    # if empty, write out empty
    if RE_EMPTY_LINE.match(line):
      out_file.writelines(['\n'])
      return
    if RE_LABEL.match(line):
      # replace '.' in labels with '__'
      newlabel = line.replace('.', '__')
      if newlabel.startswith('_'):
        newlabel = 'L' + newlabel
      out_file.writelines([newlabel])
      return
    # check if valid directive format
    m = RE_DIRECTIVE.match(line)
    if m:
      directive = m.group(1)
      # check if directive is supported by Y86
      isy86directive = False
      for startstr in ('long', 'align'):
        if directive.startswith(startstr):
          isy86directive = True
      if isy86directive:
        # write out unchanged if supported
        out_file.writelines([line])
      elif directive == 'zero\t4':
        # convert .zero 4 to .long 0
        out_file.writelines(['\t.long\t0\n'])
      else:
        # comment out unsupported directives
        out_file.writelines(['##'+line])
      return
    #out_file.writelines(['##'+line])
    # check if valid instruction format
    m = RE_INSTRUCTION.match(line)
    if m:
      # get instruction and args
      inst, args = m.group('inst', 'args')
      # get inst_obj member name
      funcname = 'INST_' + inst
      # check if is callable member of inst_obj
      if hasattr(inst_obj, funcname) and callable(getattr(inst_obj, funcname)):
        try:
          # replace '.' in labels with '__'
          if ',' in args:
            am, m = address_mode_error(args)
          else:
            am = None
            m = RE_ARG_LABEL.match(args)
          if m:
            for label_number in range(1, 5):
              label_group = 'label'+str(label_number)
              label = m.groupdict().get(label_group)
              if label and ('.' in label or label.startswith('_')):
                if am is None or am in (AM_IR, AM_RM, AM_MR):
                  newlabel = label.replace('.', '__')
                  if newlabel.startswith('_'):
                    newlabel = 'L' + newlabel
                  args = args[:m.start(label_group)] + newlabel + args[m.end(label_group):]
                else:
                  raise InstructionError('unsupported (for now) use case of labels')
          # call inst_obj member to get tuple list
          inst_func = getattr(inst_obj, funcname)
          inst_out_list = inst_func(args, i=i, line=line, line_enum=line_enum,
                                    out_file=out_file, inst_obj=inst_obj)
          # produce lines from tuple list
          out_lines = []
          for inst_out in inst_out_list:
            out_line = '\t' + ('\t'.join(inst_out)) + '\n'
            out_lines.append(out_line)
          # write lines
          out_file.writelines(out_lines)
        except InstructionError as ie:
          handle_error(out_file, line, '{} on line {}:'.format(ie, i), must_exit=ie.must_exit)
      else:
        # instruction not found in inst_obj or not callable
        handle_error(out_file, line, 'unrecognized instruction "{}" on line {}:'.format(inst, i))
    else:
      # invalid instruction format
      handle_error(out_file, line, 'general syntax error on line {}:'.format(i))
        

def main():
  '''Main method'''
  # handle program arguments
  args = sys.argv[1:]
  argsit = iter(args)
  names_c = []
  name_s = None
  name_ys = None
  do_yas = True
  for arg in argsit:
    if arg == '-o':
      name_ys = next(argsit)
      if name_ys.endswith('.yo'):
        do_yas = True
        name_ys = name_ys.rpartition('.')[0] + '.ys'
      else:
        do_yas = False
      if name_s is None:
        name_s = name_ys.partition('.')[0] + '.s'
    elif arg == '-asm':
      name_s = next(argsit)
      if name_ys is None:
        name_ys = name_s.partition('.')[0] + '.ys'
    else:
      names_c.append(arg)
  # default values for program arguments
  if name_s is None:
    if len(names_c) == 1:
      name_s = names_c[0].partition('.')[0] + '.s'
    else:
      name_s = 'out.s'
  if name_ys is None:
    if len(names_c) == 1:
      name_ys = names_c[0].partition('.')[0] + '.ys'
    else:
      name_ys = 'out.ys'
  # call gcc to generate IA32 assembly
  if names_c:
    gcc_command = ['gcc', '-O2', '-m32', '-fno-asynchronous-unwind-tables', '-S', '-o', name_s]
    gcc_command.extend(names_c)
    try:
      subprocess.check_output(gcc_command)
    except subprocess.CalledProcessError as cpe:
      print(' '.join(gcc_command))
      print(cpe.output)
      return cpe.returncode
  # convert to Y86 assembly
  with open(name_s) as in_file:
    with open(name_ys, 'w') as out_file:
      out_file.writelines(["##\tGenerated by Christopher McKinney's y86c\n",
                           '\t.pos\t0\n', '\tirmovl\tStack, %esp\n', '\tirmovl\tStack, %ebp\n',
                           '\tcall\tmain\n', '\thalt\n', '\n'])
      convert_asm(in_file, out_file)
      out_file.writelines(['\n', '\t.align\t4\n'])
      for slot in range(1, 1+TMP_REG_SLOTS):
        out_file.writelines(['TmpReg'+str(slot)+':\n', '\t.long\t0\n'])
      out_file.writelines(['\n', '\t.pos\t0x1000\n', 'Stack:\n'])
  # stop if an error occurred
  if RETURNCODE or not do_yas:
    return RETURNCODE
  # if yas is not on the path, say so and return
  try:
    subprocess.check_output(['which', 'yas'])
  except subprocess.CalledProcessError as cpe:
    print('"yas" was not found on the path; skipping assembly')
    return cpe.returncode
  # assemble with yas
  yas_command = ['yas', name_ys]
  try:
    subprocess.check_output(yas_command)
  except subprocess.CalledProcessError as cpe:
    print(' '.join(yas_command))
    print(cpe.output)
    return cpe.returncode
  return 0

# call main if running as a script
if __name__ == '__main__':
  RETURNCODE = main()
  # exit with return code
  raise SystemExit(RETURNCODE)
