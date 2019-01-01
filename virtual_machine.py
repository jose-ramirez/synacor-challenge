from struct import unpack
import sys, time

MAX_VALUE = 32768

class Machine:
    def __init__(self):
        self.memory = []
        self.registers = {i: 0 for i in range(MAX_VALUE, MAX_VALUE + 8)}
        self.stack = []
        self.program_pointer = 0
        self.halt_execution = False
        self.instructions = {
            0: self.halt,
            1: self.set,
            2: self.push,
            3: self.pop,
            4: self.eq,
            5: self.gt,
            6: self.jump,
            7: self.jt,
            8: self.jf,
            9: self.add,
            10: self.mult,
            11: self.mod,
            12: self._and,
            13: self._or,
            14: self._not,
            15: self.rmem,
            16: self.wmem,
            17: self.call,
            18: self.ret,
            19: self.out,
            20: self._in,
            21: self.no_op
        }

    def get_mem_value(self, pointer):
        val = self.memory[pointer]
        return val if val < MAX_VALUE else self.registers[val]

    def set_mem(self, pointer, value):
        mem_addr = self.memory[pointer]
        if mem_addr < MAX_VALUE:
            self.memory[mem_addr] = value
        else:
            self.registers[mem_addr] = value

    def halt(self):
        self.halt_execution = True

    def set(self):
        val = self.get_mem_value(self.program_pointer + 2)
        self.set_mem(self.program_pointer + 1, val)
        self.program_pointer += 3

    def push(self):
        a = self.get_mem_value(self.program_pointer + 1)
        self.stack.append(a)
        self.program_pointer += 2

    def pop(self):
        if not self.stack:
            raise Exception('Empty stack')
        else:
            val = self.stack.pop()
            self.set_mem(self.program_pointer + 1, val)
            self.program_pointer += 2

    def eq(self):
        b = self.get_mem_value(self.program_pointer + 2)
        c = self.get_mem_value(self.program_pointer + 3)
        self.set_mem(self.program_pointer + 1, int(b == c))
        self.program_pointer += 4

    def gt(self):
        b = self.get_mem_value(self.program_pointer + 2)
        c = self.get_mem_value(self.program_pointer + 3)
        self.set_mem(self.program_pointer + 1, int(b > c))
        self.program_pointer += 4

    def jump(self):
        addr = self.get_mem_value(self.program_pointer + 1)
        self.program_pointer = addr

    def jt(self):
        test_value = self.get_mem_value(self.program_pointer + 1)
        jump_addr = self.get_mem_value(self.program_pointer + 2)
        if test_value > 0:
            self.program_pointer = jump_addr
        else:
            self.program_pointer += 3

    def jf(self):
        test_value = self.get_mem_value(self.program_pointer + 1)
        jump_addr = self.get_mem_value(self.program_pointer + 2)
        if test_value == 0:
            self.program_pointer = jump_addr
        else:
            self.program_pointer += 3

    def add(self):
        b = self.get_mem_value(self.program_pointer + 2)
        c = self.get_mem_value(self.program_pointer + 3)
        self.set_mem(self.program_pointer + 1, (b + c) % MAX_VALUE)
        self.program_pointer += 4

    def mult(self):
        b = self.get_mem_value(self.program_pointer + 2)
        c = self.get_mem_value(self.program_pointer + 3)
        self.set_mem(self.program_pointer + 1, (b * c) % MAX_VALUE)
        self.program_pointer += 4

    def mod(self):
        b = self.get_mem_value(self.program_pointer + 2)
        c = self.get_mem_value(self.program_pointer + 3)
        self.set_mem(self.program_pointer + 1, (b % c) % MAX_VALUE)
        self.program_pointer += 4

    def _and(self):
        b = self.get_mem_value(self.program_pointer + 2)
        c = self.get_mem_value(self.program_pointer + 3)
        self.set_mem(self.program_pointer + 1, (b & c) % MAX_VALUE)
        self.program_pointer += 4

    def _or(self):
        b = self.get_mem_value(self.program_pointer + 2)
        c = self.get_mem_value(self.program_pointer + 3)
        self.set_mem(self.program_pointer + 1, (b | c) % MAX_VALUE)
        self.program_pointer += 4

    def _not(self):
        b = self.get_mem_value(self.program_pointer + 2)
        self.set_mem(self.program_pointer + 1, MAX_VALUE - 1 - b)
        self.program_pointer += 3

    def rmem(self):
        addr = self.memory[self.program_pointer + 2]
        val = self.memory[addr] if addr < MAX_VALUE else self.memory[self.registers[addr]]
        self.set_mem(self.program_pointer + 1, val)
        self.program_pointer += 3

    def wmem(self):
        a = self.get_mem_value(self.program_pointer + 1)
        b = self.get_mem_value(self.program_pointer + 2)
        self.memory[a] = b
        self.program_pointer += 3

    def call(self):
        a = self.get_mem_value(self.program_pointer + 1)
        self.stack.append(self.program_pointer + 2)
        self.program_pointer = a

    def ret(self):
        if not self.stack:
            raise Exception('Empty stack')
        jump_addr = self.stack.pop()
        self.program_pointer = jump_addr

    def _in(self):
        a = sys.stdin.read(1)
        self.set_mem(self.program_pointer + 1, ord(a))
        self.program_pointer += 2

    def out(self):
        int_val = self.get_mem_value(self.program_pointer + 1)
        value = chr(int_val)
        self.program_pointer += 2
        print(value, end="", flush=True)

    def no_op(self):
        self.program_pointer += 1

    def unknown(self, op):
        print(f'unknown instruction code: {op}; program_pointer: {self.program_pointer}, halting')
        self.halt_execution = True

    def load_program(self, binary_file):
        with open(binary_file, 'rb') as program:
            while True:
                try:
                    self.memory.append(unpack('<H', program.read(2))[0])
                except:
                    break

    def start(self):
        while not self.halt_execution:
            try:
                op_id = self.memory[self.program_pointer]
                if op_id in self.instructions.keys():
                    self.instructions.get(op_id)()
                else:
                    self.unknown(op_id)
            except Exception as e:
                print(f'program exited with an error: {e}')
                break
