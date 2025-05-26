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
    data_memory_size = None  # размер подается при создании
    data_memory = None  # инициализируется нулями

    def __init__(self, data_memory_size):
        self.r0 = 0
        self.r1 = 0
        self.r2 = 0
        self.sp = 0
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
        assert data_memory_size > 0, "Размер памяти данных должен быть больше нуля"
        self.data_memory_size = data_memory_size
        self.data_memory = [0 for _ in range(data_memory_size)]

    def aboba(self):
        setattr(self, self.regs[0], 4)
        print(self.r0)


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



datapath = DataPath()
datapath.aboba()
