from isa import Opcode, Register, reg_to_binary, binary_to_reg, opcode_to_binary, binary_to_opcode


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

    def alu_sum(self):
        self.bus_res = self.alu.sum(self.bus_a, self.bus_b)

    def alu_sub(self):
        self.bus_res = self.alu.sub(self.bus_a, self.bus_b)

    def alu_mul(self):
        self.bus_res = self.alu.mul(self.bus_a, self.bus_b)

    def alu_mulh(self):
        self.bus_res = self.alu.mulh(self.bus_a, self.bus_b)

    def alu_div(self):
        self.bus_res = self.alu.div(self.bus_a, self.bus_b)

    def alu_mod(self):
        self.bus_res = self.alu.mod(self.bus_a, self.bus_b)

    def alu_shiftl(self):
        self.bus_res = self.alu.shiftl(self.bus_a, self.bus_b)

    def alu_shiftr(self):
        self.bus_res = self.alu.shiftr(self.bus_a, self.bus_b)

    def alu_AND(self):
        self.bus_res = self.alu.AND(self.bus_a, self.bus_b)

    def alu_OR(self):
        self.bus_res = self.alu.OR(self.bus_a, self.bus_b)

    def alu_XOR(self):
        self.bus_res = self.alu.XOR(self.bus_a, self.bus_b)

    def load_data_memory(self):
        self.bus_res = self.data_memory_module.read_word(self.ar)

    def store_data_memory(self):
        self.data_memory_module.write_word(self.ar, self.bus_res)

    def __str__(self):
        s = f"""r0 = {self.r0}. r1 = {self.r1}. r2 = {self.r2}. r3 = {self.r3}. r4 = {self.r4}. r5 = {self.r6}. 
        """
        return s


class ControlUnit:
    tick = None # показатель тиков, инициализируется нулем
    microcode_counter = None # счетчик командой для микрокоманд
    microcode_reg = None
    microcode_memory = None
    program_counter = None # счетчик команд для program_memory
    program_memory = None # инициализируется входными данными
    program_register = None
    data_path = None
    halted = None # инициализируется False


    def __init__(self, microcode_memory, program, input_addr, output_addr, data_memory_size, input_buffer):
        self.program_counter = 0
        self.program_memory = program
        self.tick = 0
        self.microcode_counter = 0
        self.microcode_reg = None
        self.program_register = None
        self.data_path = DataPath(input_addr, output_addr, data_memory_size, input_buffer)
        self.microcode_memory = microcode_memory
        self.halted = False

    def run_microcode(self):
        while not self.halted:
            self.tick += 1
            self.microcode_reg = self.microcode_memory[self.microcode_counter]
            self.microcode_reg(self)
            print(self.data_path)

    def fetch_command(self):
        self.program_register = self.program_memory[self.program_counter]
        self.program_counter += 1
        self.microcode_counter = opcode_to_binary[self.program_register["opcode"]] + 1

    def lui_microcode(self):
        self.data_path.bus_b = 23
        self.data_path.bus_a = self.program_register["k"]
        self.data_path.alu_shiftl()
        getattr(self.data_path, f"latch_{self.program_register['arg1'].value}")()
        self.microcode_counter = 0x0


    def mv_microcode(self):
        getattr(self.data_path, f"load_{self.program_register['arg2'].value}_on_bus_a")()
        self.data_path.load_zero_on_bus_b()
        self.data_path.alu_sum()
        getattr(self.data_path, f"latch_{self.program_register['arg1'].value}")()
        self.microcode_counter = 0

    def sw_microcode_1(self):
        getattr(self.data_path, f"load_{self.program_register['arg2'].value}_on_bus_a")()
        self.data_path.bus_b = self.program_register["k"]
        self.data_path.alu_sum()
        self.data_path.latch_ar()
        self.microcode_counter = 32

    def sw_microcode_2(self):
        getattr(self.data_path, f"load_{self.program_register['arg1'].value}_on_bus_a")()
        self.data_path.load_zero_on_bus_b()
        self.data_path.alu_sum()
        self.data_path.store_data_memory()
        self.microcode_counter = 0

    def lw_microcode_1(self):
        getattr(self.data_path, f"load_{self.program_register['arg2'].value}_on_bus_a")()
        self.data_path.bus_b = self.program_register["k"]
        self.data_path.alu_sum()
        self.data_path.latch_ar()
        self.microcode_counter = 33

    def lw_microcode_2(self):
        self.data_path.load_data_memory()
        getattr(self.data_path, f"latch_{self.program_register['arg1'].value}")()
        self.microcode_counter = 0

    def halt_microcode(self):
        self.halted = True

microcode_memory = {
    0: ControlUnit.fetch_command,
    1: ControlUnit.lui_microcode,
    2: ControlUnit.mv_microcode,
    3: ControlUnit.sw_microcode_1,
    4: ControlUnit.lw_microcode_1,
    26: ControlUnit.halt_microcode,
    32: ControlUnit.sw_microcode_2,
    33: ControlUnit.lw_microcode_2
}


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

    def read_word(self, address):
        assert address != self.output_addr, "Невозможно считать данные из буфера вывода!"
        if address == self.input_addr:
            assert len(self.input_buffer) != 0, "Буфер ввода пустой!"
            res = int.from_bytes((self.input_buffer[0].to_bytes(4, byteorder="little")), "little")
            self.input_buffer = self.input_buffer[1:]
            return res
        a = self.data_memory[address]
        b = self.data_memory[address + 1]
        c = self.data_memory[address + 2]
        d = self.data_memory[address + 3] # TODO разобраться с блядскими restricted zones
        res = (d << 24) | (c << 16) | (b << 8) | a
        return res

    def write_word(self, address, value):
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
        return (a << b) & 0xFFFFFFFF

    def shiftr(self, a, b):
        return (a >> b) & 0xFFFFFFFF

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


code = [
    {
        "opcode": Opcode.LUI,
        "arg1": Register.R0,
        "k": 4
    },
    {
        "opcode": Opcode.MV,
        "arg1": Register.R1,
        "arg2": Register.R0
    },
    {
        "opcode": Opcode.LW,
        "arg1": Register.R0,
        "arg2": Register.ZERO,
        "k": 0x80
    },
    {
        "opcode": Opcode.LW,
        "arg1": Register.R1,
        "arg2": Register.ZERO,
        "k": 0x80
    },
    {
        "opcode": Opcode.HALT,
    }
]
control_unit = ControlUnit(microcode_memory, code, 0x80, 0x84, 256, [ord('a'), ord('b')])
control_unit.run_microcode()
