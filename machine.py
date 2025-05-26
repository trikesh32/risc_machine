from encodings.punycode import selective_find


class DataPath:
    zero = None  # инициализируется нулем, при технически можно попытаться переписать, но все равно останется регистром с нулями
    r0 = None  # инициализируется нулем
    r1 = None  # инициализируется нулем
    r2 = None  # инициализируется нулем
    r3 = None  # инициализируется нулем
    r4 = None  # инициализируется нулем
    r5 = None  # инициализируется нулем
    r6 = None  # инициализируется нулем
    sp = None  # инициализируется нулем
    ar = None  # инициализируется нулем
    bus_a = None  # шина первого аргумента
    bus_b = None  # шина второго аргумента
    bus_res = None  # шина результата
    data_memory_module = None
    alu = None
    conditional_module = None

    def __init__(self, input_addr, output_addr, data_memory_size, input_buffer):
        self.zero = 0
        self.r0 = 0
        self.r1 = 0
        self.r2 = 0
        self.r3 = 0
        self.r4 = 0
        self.r5 = 0
        self.r6 = 0
        self.sp = 0
        self.ar = 0
        self.data_memory_module = DataMemoryModule(input_addr, output_addr, data_memory_size, input_buffer)
        self.alu = ALU()
        self.conditional_module = ConditionalModule()

    def latch_zero(self):
        self.zero = 0

    def latch_r0(self):
        self.r0 = self.bus_res

    def latch_r1(self):
        self.r1 = self.bus_res

    def latch_r2(self):
        self.r2 = self.bus_res

    def latch_r3(self):
        self.r3 = self.bus_res

    def latch_r4(self):
        self.r4 = self.bus_res

    def latch_r5(self):
        self.r5 = self.bus_res

    def latch_r6(self):
        self.r6 = self.bus_res

    def latch_sp(self):
        self.sp = self.bus_res

    def latch_ar(self):
        self.ar = self.bus_res

    def load_zero_on_bus_a(self):
        self.bus_a = self.zero

    def load_zero_on_bus_b(self):
        self.bus_b = self.zero

    def load_r0_on_bus_a(self):
        self.bus_a = self.r0

    def load_r0_on_bus_b(self):
        self.bus_b = self.r0

    def load_r1_on_bus_a(self):
        self.bus_a = self.r1

    def load_r1_on_bus_b(self):
        self.bus_b = self.r1

    def load_r2_on_bus_a(self):
        self.bus_a = self.r2

    def load_r2_on_bus_b(self):
        self.bus_b = self.r2

    def load_r3_on_bus_a(self):
        self.bus_a = self.r3

    def load_r3_on_bus_b(self):
        self.bus_b = self.r3

    def load_r4_on_bus_a(self):
        self.bus_a = self.r4

    def load_r4_on_bus_b(self):
        self.bus_b = self.r4

    def load_r5_on_bus_a(self):
        self.bus_a = self.r5

    def load_r5_on_bus_b(self):
        self.bus_b = self.r5

    def load_r6_on_bus_a(self):
        self.bus_a = self.r6

    def load_r6_on_bus_b(self):
        self.bus_b = self.r6

    def load_sp_on_bus_a(self):
        self.bus_a = self.sp

    def load_sp_on_bus_b(self):
        self.bus_b = self.sp


class ControlUnit:
    tick = None # показатель тиков, инициализируется нулем
    microcode_counter = None # счетчик командой для микрокоманд
    microcode_reg = None
    microcode_memory = None
    program_counter = None # счетчик команд для program_memory
    program_memory = None # инициализируется входными данными
    data_path = None
    halted = None # инициализируется False


    def __init__(self, microcode_memory, program, input_addr, output_addr, data_memory_size, input_buffer):
        self.program_counter = 0
        self.program_memory = program
        self.tick = 0
        self.microcode_counter = 0
        self.microcode_reg = None
        self.data_path = DataPath(input_addr, output_addr, data_memory_size, input_buffer)
        self.microcode_memory = microcode_memory
        self.halted = False

    def run_microcode(self):
        while not self.halted:
            self.tick += 1
            self.microcode_reg = self.microcode_memory[self.microcode_counter]
            self.microcode_reg()




class DataMemoryModule:
    input_addr = None
    output_addr = None
    data_memory_size = None
    data_memory = None
    input_buffer = None
    output_buffer = None

    def __init__(self, input_addr, output_addr, data_memory_size, input_buffer):
        self.input_addr = input_addr
        self.output_addr = output_addr
        self.data_memory_size = data_memory_size
        assert data_memory_size > 0, "Размер памяти данных должен быть больше нуля"
        self.data_memory = [0 for _ in range(data_memory_size)]
        self.input_buffer = input_buffer
        self.output_buffer = []

    def read_data(self, address):
        assert address != self.output_addr, "Невозможно считать данные из буфера вывода!"
        if address == self.input_addr:
            assert not self.input_buffer.empty(), "Буфер ввода пустой!"
            res = self.input_buffer[0]
            self.input_buffer = self.input_buffer[1:]
            return res
        return self.data_memory[address]

    def write_data(self, address, value):
        assert address != self.input_addr, "Невозможно записать данные в буфер ввода!"
        if address == self.output_addr:
            self.output_buffer.append(value)
            return
        self.data_memory[address] = value


class ALU:
    def sum(self, a, b):
        return (a + b) & 0xFFFFFFFF

    def sub(self, a, b):
        return (a - b) & 0xFFFFFFFF

    def mul(self, a, b):
        return (a * b) & 0xFFFFFFFF

    def mulh(self, a, b):
        return ((a * b) & 0xFFFFFFFF00000000) >> 32

    def div(self, a, b):
        return (a / b) & 0xFFFFFFFF

    def mod(self, a, b):
        return (a % b) & 0xFFFFFFFF

    def shiftl(self, a, b):
        return (a >> b) & 0xFFFFFFFF

    def shiftr(self, a, b):
        return (a << b) & 0xFFFFFFFF

    def AND(self, a, b):
        return (a & b) & 0xFFFFFFFF

    def OR(self, a, b):
        return (a | b) & 0xFFFFFFFF

    def XOR(self, a, b):
        return (a ^ b) & 0xFFFFFFFF


class ConditionalModule:
    def eq(self, a, b):
        return a == b

    def ne(self, a, b):
        return a != b

    def lt(self, a, b):
        return a < b

    def le(self, a, b):
        return a <= b

    def gt(self, a, b):
        return a > b

    def ge(self, a, b):
        return a >= b


alu = ALU()
print(alu.sub(1, 2))
