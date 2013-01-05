# -*- coding: utf-8 -*-

import re
import sys

## 256 words of memory (can be anything, string, number, object or int)
MEMSIZE = 256
## 4 general purpose registers
REGISTERS = 4
## Denotes the end of program
END_OF_PROGRAM = 'halt'
## Signals memory load address change
CHANGE_ADDRESS = 'change_address'
## Signals label declaration
DECLARE_LABEL = 'declare_label'
## For parsing code lines
SPACE = re.compile('\s+')

class ParseException(Exception):
    pass

class RuntimeException(Exception):
    pass

class Getable(object):
    '''Base class for special memory mapped values, read only
    using assembler. These type of values can't be created in
    memory using assembler.'''
    def __init__(self, value):
        self.value = value
    def get(self):
        return self.value
    def __str__(self):
        return repr(self)
    def __repr__(self):
        return 'Getable(' + repr(self.value) + ')'

class Setable(Getable):
    '''Base class for special memory mapped values, read/write
    using assembler. These type of values can't be created in
    memory using assembler.'''
    def set(self, value):
        self.value = value
    def __repr__(self):
        return 'Setable(' + repr(self.value) + ')'

class Cpu(object):
    '''
    A simulated CPU, supporting a simple asm syntax:

    @<address>
        Moves the loading scope to a specific address

    <label>:
        Gives the memory address a name for variable access or jump/call name

    =<value>
        Loads a value at this space in memory. Should be used when using labels
        for variables to reserve a memory spot

    copy <target> <value>
        Sets a value somewhere
        <target> is R<num> register, @<address> memory reference
        <value> is number, string, R<num> register, @<address> memory reference
        address can be a label, a register or a plain integer

    compute <target> <func> <value> [<value> ...]
        Computes a value using function func applied to the values and sets it
        in target.
        <func> is any of + - * /
            +, -, * and / works as if inserted between all values,
                thus / 1 2 3 is the same as 1/2/3 (0.1667)
                thus - 1 2 3 is the same as 1-2-3 (-4)

    test <value> <op> <value>
        Sets the test flag true or false
        <op> is any of < > != >= <= =

    jump <label>
        Jumps to a label without first pushing any program counter or registers on the stack.

    jumpif <label>
        Jumps to a label if the if flag is true. No regs or PC is pushed before.

    call <label>
        Jumps to a label after pushing the return program counter.

    callif <label>
        Jumps to a label if the if flag is true. The PC is pushed before.

    back
        Returns from a method by popping the program counter and the registers from the stack.

    push <value>
        Pushes a value onto the stack

    pop <target>
        Pops a value from the stack into a target

    trace
        Turns on program trace

    traceoff
        Turns off program trace

    debug <value> [<value> ...]
        Outputs debug information and listed values

    longdebug <value> [<value> ...]
        Outputs a lot of debug information and listed values

'''
    def __init__(self, name):
        self.name = name
        self.memory = [None for _ in xrange(MEMSIZE)]
        self.registers = [None for _ in xrange(REGISTERS)]
        self.program_counter = 0
        self.stack = []
        self.labels = {}
        self.test_flag = False
        self.trace_flag = False

    @classmethod
    def ez_run(cls, program_string):
        """
        Creates a CPU, splits program_string by newlines, loads and runs the program and returns the Cpu.
        >>> Cpu.ez_run("halt")
        Cpu.ez_run('''@0
        halt''')
        """
        res = Cpu('test')
        res.load(program_string.split('\n'))
        res.run()
        return res

    def load(self, lines, start_address=0):
        """
        Loads a program from a line-by-line iterable.

        >>> cpu = Cpu('load test 1')
        >>> cpu.load(['halt'])

        An example loading all supported instructions:
        Note: The double escape of newlines is to satisfy doctest.

        >>> cpu = Cpu('load test 2')
        >>> cpu.load('''
        ... jump @main
        ... hello:
        ... ='Hello'
        ... world:
        ... ='World'
        ... @10
        ... main:
        ... copy @hello @world
        ... compute R0 * 1 2 3 4 5
        ... test R0 = 120
        ... jumpif good
        ... debug 'BAD'
        ... good:
        ... push R0
        ... call sub
        ... trace
        ... pop R0
        ... test R0 = 120
        ... callif sub
        ... traceoff
        ... jump pastsub
        ... sub:
        ... copy 0 R0
        ... back
        ... pastsub:
        ... longdebug
        ... halt'''.split('\\n'))
        """
        addr = start_address
        lineno = 0
        try:
            for line in lines:
                lineno += 1
                parsed = self.parse(line)
                if parsed is None:
                    continue
                if isinstance(parsed, tuple):
                    if parsed[0] is CHANGE_ADDRESS:
                        addr = parsed[1]
                        continue
                    if parsed[0] is DECLARE_LABEL:
                        if parsed[1] in self.labels:
                            raise ParseException('Redeclaration of ' + parsed[1])
                        self.labels[parsed[1]] = addr
                        continue
                if addr >= MEMSIZE:
                    raise ParseException('Out of memory parsing program')
                if self.memory[addr] is not None:
                    raise ParseException('Memory not None at ' + str(addr))
                self.memory[addr] = parsed
                addr += 1
        except ParseException as e:
            sys.stderr.write('%s: ERROR: %s\n' % (lineno, line))
            sys.stderr.write('%s: ERROR: %s\n' % (lineno, e))
            raise e

    def parse(self, line):
        line = line.strip()
        if not line or line[0] == '#':
            return None
        if line[0] == '@':
            return (CHANGE_ADDRESS, int(line[1:]))
        elif line[0] == '=':
            return eval(line[1:])
        elif line[-1] == ':':
            return (DECLARE_LABEL, line[:-1])

        cols = SPACE.split(line)
        i = len(cols) - 1
        while i >= 0:
            # Put strings back together again
            # TODO: Fix case where strings have multiple spaces in them
            if cols[i][-1] == "'":
                j = i
                while cols[i][0] != "'":
                    i -= 1
                    if i < 0:
                        raise ParseException('Unstarted apostrophe')
                cols[i] = ' '.join(cols[i:j+1])
                del cols[i+1:j+1]
            i -= 1
        if not cols[0]:
            cols = cols[1:]
        cmd = cols[0]
        args = cols[1:]
        if cmd == 'halt':
            return END_OF_PROGRAM
        try:
            return (getattr(self, cmd), args)
        except AttributeError:
            raise ParseException('Unsupported command ' + cmd)

    def run(self):
        try:
            while True:
                if self.trace_flag:
                    sys.stdout.write('> ')
                    print self.disassemble([self.memory[self.program_counter]], self.program_counter)
                instr = self.memory[self.program_counter]
                if instr is END_OF_PROGRAM:
                    break
                method, args = instr
                if not method(*args):
                    self.program_counter += 1
        except RuntimeException as e:
            sys.stderr.write('System halted: ' + str(e))
            raise e

    def get_address(self, address):
        try:
                addr = int(address)
        except:
            try:
                addr = self.labels[address]
            except:
                if target[1] == 'R':
                    addr = self.registers[int(address[1:])]
        if addr > MEMSIZE or addr < 0:
            raise RuntimeException('Address ' + address + ' out of bounds (' + addr + ')')
        return addr

    def set_value(self, target, value):
        if target[0] == '@':
            addr = self.get_address(target[1:])
            if isinstance(self.memory[addr], Setable):
                self.memory[addr].set(value)
            else:
                self.memory[addr] = value
        elif target[0] == 'R':
            self.registers[int(target[1:])] = value
        else:
            raise RuntimeException('Invalid target reference ' + target)

    def get_value(self, value):
        if not value:
            return None
        if value[0] == '@':
            return self.memory[self.get_address(value[1:])]
        if value[0] == 'R':
            return self.registers[int(value[1:])]
        if len(value) >= 2 and value[0] == "'" and value[-1] == "'":
            return value[1:-1]
        try:
            return int(value)
        except:
            return float(value)
        raise RuntimeException('Invalid value reference ' + value)

    def copy(self, target, value):
        self.set_value(target, self.get_value(value))

    def test(self, left, op, right):
        left = self.get_value(left)
        right = self.get_value(right)
        if op == '<':
            self.test_flag = left < right
        elif op == '>':
            self.test_flag = left > right
        elif op == '<=':
            self.test_flag = left <= right
        elif op == '>=':
            self.test_flag = left >= right
        elif op == '!=':
            self.test_flag = left != right
        elif op == '=':
            self.test_flag = left = right

    def compute(self, target, func, *values):
        values = [self.get_value(value) for value in values]
        res = values[0]
        del values[0]
        if func == '+':
            res += sum(values)
        elif func == '-':
            res -= sum(values)
        elif func == '*':
            for val in values:
                res *= val
        elif func == '/':
            for val in values:
                res /= val
        else:
            raise RuntimeException('Unsupported func ' + func)
        self.set_value(target, res)

    def pop(self, target):
        self.set_value(target, self.stack.pop())

    def push(self, value):
        self.stack.append(self.get_value(value))

    def jump(self, label):
        self.program_counter = self.labels[label]
        return True

    def jumpif(self, label):
        if self.test_flag:
            return self.jump(label)

    def call(self, label):
        self.stack.append(self.program_counter)
        self.program_counter = self.get_address(label)
        return True

    def callif(self, label):
        if self.test_flag:
            return self.call(label)

    def back(self):
        self.program_counter = int(tmp)

    def trace(self):
        self.trace_flag = True

    def traceoff(self):
        self.trace_flag = False

    def debug(self, *values):
        print "----==| DEBUG |==----"
        print "NAME:", self.name, "TEST:", self.test_flag, "PC:", self.program_counter, \
            "REGISTERS:", self.registers, "STACK:", self.stack, "INSTRUCTION:"
        try:
            print str(self.disassemble([self.memory[self.program_counter]], self.program_counter))
        except:
            print "PROGRAM COUNTER OUTSIDE MEMORY"
        debug = []
        for value in values:
            try:
                debug.append(str(self.get_value(value)))
            except:
                debug.append('**' + str(value))
        print "DEBUG:", ', '.join(debug)

    def longdebug(self, *values):
        self.debug(*values)
        for key, addr in sorted(self.labels.iteritems()):
            try:
                print key, '=', self.memory[addr]
            except:
                print key, '=', '@' + str(addr)
        print 'Memory disassembled'
        print self.disassemble(self.memory)

    def disassemble(self, mem, start_address=0):
        res = []
        def output(data):
            if skipped_last:
                res.append('@' + str(addr))
            res.append(str(data))
        skipped_last = len(mem) > 1
        addr = start_address - 1
        rev_labels = {a:label for label, a in self.labels.iteritems()}
        for instr in mem:
            addr += 1
            if addr in rev_labels:
                output(rev_labels[addr] + ':')
                skipped_last = False
            if instr is None:
                skipped_last = True
            else:
                if instr is END_OF_PROGRAM:
                    output('halt')
                elif isinstance(instr, tuple) and isinstance(instr[0], type(self.disassemble)):
                    method, args = instr
                    name = method.__name__
                    output('    ' + name + ' ' + ' '.join(args))
                else:
                    output('=' + repr(instr))
                skipped_last = False
        return '\n'.join(res)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "Cpu.ez_run('''" + self.disassemble(self.memory) + "''')"

if __name__ == '__main__':
    print "CPU TEST"
    program = '''
# Declare some variables at address 200 and up
@200
polka:
=0
tango:
=5
philip:
=2

# Program start
@0
    copy @200 1
    debug @200
    trace
    copy R0 'polka'
    copy R1 1.23
    copy @200 R0
    copy @polka 'tango'
loop:
    compute @tango - @tango 1
    test @tango > 0
    traceoff
    jumpif loop
    trace
    copy R0 1000
    call meth
    longdebug 'end of program'
    halt
meth:
    copy R0 0
    debug 'Check out the stack'
    back
'''
    cpu = Cpu('test')
    cpu.load(program.split('\n'))
    cpu.run()
