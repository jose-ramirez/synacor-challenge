from logger import Logger
from utils import Utils

class Machine:
    def __init__(self):
        self.memory = []
        self.registers = []
        self.stack = []
        self.pc = 0
        self.halt_execution = False
        self.logger = Logger()
        self.instructions = {
            0: self.halt,
            19: self.print_char,
            21: self.no_op
        }

    def print_char(self):
        int_val = self.memory[self.pc + 2]
        value = chr(int_val)
        self.pc += 4
        print(value, end="", flush=True)

    def halt(self):
        print('program halted')
        self.pc += 1
        self.halt_execution = True
        self.logger.stop()

    def no_op(self):
        self.pc += 2
        pass

    def unknown(self, op):
        print(f'unknown instruction code: {op}; pc: {self.pc}, halting')
        self.halt_execution = True
        self.logger.stop()

    def load_program(self, binary_file):
        with open(binary_file, 'rb') as program:
            self.memory = program.read()
        return self

    def start(self):
        while not self.halt_execution:
            op_id = self.memory[self.pc]
            if op_id in self.instructions.keys():
                self.instructions.get(op_id)()
            else:
                self.unknown(op_id)


Machine().load_program('challenge.bin').start()