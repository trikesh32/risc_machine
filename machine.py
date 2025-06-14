import sys

from isa import (
    Opcode,
    Register,
    reg_to_binary,
    binary_to_reg,
    opcode_to_binary,
    binary_to_opcode,
    to_hex,
    to_signed16,
    ALUModes,
    CondModes,
    Selects,
    from_bytes,
    get_data_dump,
)


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
    data_memory_module = None

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
        # далее это не регистры, это провода и мультиплексоры
        self.res = 0
        self.file_mux = 0
        self.rs1_mux = 0
        self.rs2_mux = 0
        self.op1_mux = 0
        self.op2_mux = 0
        self.imm = 0
        self.mc_const = 0
        self.pc = 0

    def alu(self, mode):
        a = self.op1_mux
        b = self.op2_mux
        if mode == ALUModes.ADD:
            self.res = (a + b) & 0xFFFFFFFF
        elif mode == ALUModes.SUB:
            self.res = (a - b) & 0xFFFFFFFF
        elif mode == ALUModes.MUL:
            self.res = (a * b) & 0xFFFFFFFF
        elif mode == ALUModes.MULH:
            self.res = ((a * b) & 0xFFFFFFFF00000000) >> 32
        elif mode == ALUModes.DIV:
            self.res = (a // b) & 0xFFFFFFFF
        elif mode == ALUModes.REM:
            self.res = (a % b) & 0xFFFFFFFF
        elif mode == ALUModes.SLL:
            self.res = (a << b) & 0xFFFFFFFF
        elif mode == ALUModes.SRL:
            self.res = (a & 0xFFFFFFFF >> b) & 0xFFFFFFFF
        elif mode == ALUModes.AND:
            self.res = (a & b) & 0xFFFFFFFF
        elif mode == ALUModes.OR:
            self.res = (a | b) & 0xFFFFFFFF
        elif mode == ALUModes.XOR:
            self.res = (a ^ b) & 0xFFFFFFFF
        elif mode == ALUModes.SRA:
            self.res = (a >> b) & 0xFFFFFFFF
        else:
            self.res = 0

    def cond(self, mode):
        a = self.rs1_mux
        b = self.rs2_mux
        if mode == CondModes.EQ:
            return to_signed16(a) == to_signed16(b)
        elif mode == CondModes.NE:
            return to_signed16(a) != to_signed16(b)
        elif mode == CondModes.LE:
            return to_signed16(a) <= to_signed16(b)
        elif mode == CondModes.LEU:
            return a <= b
        elif mode == CondModes.GT:
            return to_signed16(a) > to_signed16(b)
        elif mode == CondModes.GTU:
            return a > b
        elif mode == CondModes.TRUE:
            return True
        elif mode == CondModes.FALSE:
            return False
        else:
            return None

    def latch_file(self, rd):
        setattr(self, rd.value, self.file_mux)

    def read(self, sel):
        if sel.value == 0:
            self.file_mux = self.res
        if sel.value == 1:
            self.file_mux = self.data_memory_module.read_word(self.ar)

    def write(self):
        self.data_memory_module.write_word(self.ar, self.res)

    def latch_ar(self):
        self.ar = self.res

    def rs1(self, sel):
        if sel == Register.NOT_USED:
            self.rs1_mux = self.zero
        else:
            self.rs1_mux = getattr(self, sel.value)

    def rs2(self, sel):
        if sel == Register.NOT_USED:
            self.rs2_mux = self.zero
        else:
            self.rs2_mux = getattr(self, sel.value)

    def op1_sig(self, sel):
        if sel.value == 0:
            self.op1_mux = self.rs1_mux
        if sel.value == 1:
            self.op1_mux = self.mc_const
        if sel.value == 2:
            self.op1_mux = self.pc
        if sel.value == 3:
            self.op1_mux = self.imm

    def op2_sig(self, sel):
        if sel.value == 0:
            self.op2_mux = self.rs2_mux
        if sel.value == 1:
            self.op2_mux = self.mc_const
        if sel.value == 2:
            self.op2_mux = self.pc
        if sel.value == 3:
            self.op2_mux = self.imm

    def __str__(self):
        s = f"r0: {self.r0}. r1: {self.r1}. r2: {self.r2}. r3: {self.r3}. r4: {self.r4}. r5: {self.r5}, r6: {self.r6}, sp: {self.sp}, ar: {self.ar}"
        return s


class ControlUnit:
    tick = None  # показатель тиков, инициализируется нулем
    microcode_counter = None  # счетчик командой для микрокоманд
    microcode_reg = None
    microcode_memory = None
    program_counter = None  # счетчик команд для program_memory
    program_memory = None  # инициализируется входными данными
    program_register = None
    data_path = None
    halted = None  # инициализируется False
    LUT = None  # инициализируется входными данными конструктора

    def __init__(self, microcode_memory, program, input_addr, output_addr, data_memory_size, input_buffer, LUT):
        self.program_counter = 0
        self.program_memory = program
        self.tick = 0
        self.microcode_counter = 0
        self.microcode_reg = None
        self.program_register = None
        self.data_path = DataPath(input_addr, output_addr, data_memory_size, input_buffer)
        self.microcode_memory = microcode_memory
        self.LUT = LUT
        self.halted = False
        # мультиплексоры
        self.pc_mux = 0
        self.mc_mux = 0

    def m_signal(self, sel):
        if sel.value == 0:
            self.microcode_counter = self.microcode_counter + 1
        if sel.value == 1:
            self.microcode_counter = self.LUT[self.program_register["opcode"]]
        if sel.value == 2:
            self.microcode_counter = 0

    def latch_pc(self):
        self.program_counter = self.pc_mux

    def pc_mux_sel(self, mode):
        if self.data_path.cond(mode):
            self.pc_mux = self.data_path.res
        else:
            self.pc_mux = self.program_counter

    def latch_pr(self):
        self.program_register = self.program_memory[self.program_counter // 4]

    def debug_output(self, microcode_name):
        s = f"TICK: {self.tick}, {microcode_name}, PC: {self.program_counter} " + str(self.data_path)
        print(s)

    def run_microcode(self):
        while not self.halted:
            self.tick += 1
            self.microcode_reg = self.microcode_memory[self.microcode_counter]
            microcode_name = self.microcode_reg(self)
            self.debug_output(microcode_name)

    def fetch_command(self):
        self.latch_pr()
        self.data_path.mc_const = 4
        self.data_path.op1_sig(Selects.SEL_B)
        self.data_path.op2_sig(Selects.SEL_C)
        self.data_path.alu(ALUModes.ADD)
        self.pc_mux_sel(CondModes.TRUE)
        self.latch_pc()
        self.m_signal(Selects.SEL_A)
        self.data_path.imm = self.program_register["k"]
        self.data_path.pc = self.program_counter
        return "FETCH"

    def decode_command(self):
        self.m_signal(Selects.SEL_B)
        return "DECODE"

    def lui_microcode(self):
        self.data_path.mc_const = 16
        self.data_path.op1_sig(Selects.SEL_D)
        self.data_path.op2_sig(Selects.SEL_B)
        self.data_path.alu(ALUModes.SLL)
        self.data_path.read(Selects.SEL_A)
        self.data_path.latch_file(self.program_register["rd"])
        self.m_signal(Selects.SEL_C)
        return "LUI"

    def mv_microcode(self):
        self.data_path.mc_const = 0
        self.data_path.rs1(self.program_register["rs1"])
        self.data_path.op1_sig(Selects.SEL_A)
        self.data_path.op2_sig(Selects.SEL_B)
        self.data_path.alu(ALUModes.ADD)
        self.data_path.read(Selects.SEL_A)
        self.data_path.latch_file(self.program_register["rd"])
        self.m_signal(Selects.SEL_C)
        return "MV"

    def sw_microcode_1(self):
        self.data_path.rs1(self.program_register["rs1"])
        self.data_path.op1_sig(Selects.SEL_A)
        self.data_path.op2_sig(Selects.SEL_D)
        self.data_path.alu(ALUModes.ADD)
        self.data_path.latch_ar()
        self.m_signal(Selects.SEL_A)
        return "SW_1"

    def sw_microcode_2(self):
        self.data_path.mc_const = 0
        self.data_path.rs2(self.program_register["rs2"])
        self.data_path.op1_sig(Selects.SEL_B)
        self.data_path.op2_sig(Selects.SEL_A)
        self.data_path.alu(ALUModes.ADD)
        self.data_path.write()
        self.m_signal(Selects.SEL_C)
        return "SW_2"

    def lw_microcode_1(self):
        self.data_path.rs1(self.program_register["rs1"])
        self.data_path.op1_sig(Selects.SEL_A)
        self.data_path.op2_sig(Selects.SEL_D)
        self.data_path.alu(ALUModes.ADD)
        self.data_path.latch_ar()
        self.m_signal(Selects.SEL_A)
        return "LW_1"

    def lw_microcode_2(self):
        self.data_path.read(Selects.SEL_B)
        self.data_path.latch_file(self.program_register["rd"])
        self.m_signal(Selects.SEL_C)
        return "LW_2"

    def halt_microcode(self):
        self.halted = True
        return "HALT"

    def addi_microcode(self):
        self.data_path.rs1(self.program_register["rs1"])
        self.data_path.op1_sig(Selects.SEL_A)
        self.data_path.op2_sig(Selects.SEL_D)
        self.data_path.alu(ALUModes.ADD)
        self.data_path.read(Selects.SEL_A)
        self.data_path.latch_file(self.program_register["rd"])
        self.m_signal(Selects.SEL_C)
        return "ADDI"

    def add_microcode(self):
        self.data_path.rs1(self.program_register["rs1"])
        self.data_path.rs2(self.program_register["rs2"])
        self.data_path.op1_sig(Selects.SEL_A)
        self.data_path.op2_sig(Selects.SEL_A)
        self.data_path.alu(ALUModes.ADD)
        self.data_path.read(Selects.SEL_A)
        self.data_path.latch_file(self.program_register["rd"])
        self.m_signal(Selects.SEL_C)
        return "ADD"

    def sub_microcode(self):
        self.data_path.rs1(self.program_register["rs1"])
        self.data_path.rs2(self.program_register["rs2"])
        self.data_path.op1_sig(Selects.SEL_A)
        self.data_path.op2_sig(Selects.SEL_A)
        self.data_path.alu(ALUModes.SUB)
        self.data_path.read(Selects.SEL_A)
        self.data_path.latch_file(self.program_register["rd"])
        self.m_signal(Selects.SEL_C)
        return "SUB"

    def mul_microcode(self):
        self.data_path.rs1(self.program_register["rs1"])
        self.data_path.rs2(self.program_register["rs2"])
        self.data_path.op1_sig(Selects.SEL_A)
        self.data_path.op2_sig(Selects.SEL_A)
        self.data_path.alu(ALUModes.MUL)
        self.data_path.read(Selects.SEL_A)
        self.data_path.latch_file(self.program_register["rd"])
        self.m_signal(Selects.SEL_C)
        return "MUL"

    def mulh_microcode(self):
        self.data_path.rs1(self.program_register["rs1"])
        self.data_path.rs2(self.program_register["rs2"])
        self.data_path.op1_sig(Selects.SEL_A)
        self.data_path.op2_sig(Selects.SEL_A)
        self.data_path.alu(ALUModes.MULH)
        self.data_path.read(Selects.SEL_A)
        self.data_path.latch_file(self.program_register["rd"])
        self.m_signal(Selects.SEL_C)
        return "MULH"

    def div_microcode(self):
        self.data_path.rs1(self.program_register["rs1"])
        self.data_path.rs2(self.program_register["rs2"])
        self.data_path.op1_sig(Selects.SEL_A)
        self.data_path.op2_sig(Selects.SEL_A)
        self.data_path.alu(ALUModes.DIV)
        self.data_path.read(Selects.SEL_A)
        self.data_path.latch_file(self.program_register["rd"])
        self.m_signal(Selects.SEL_C)
        return "DIV"

    def rem_microcode(self):
        self.data_path.rs1(self.program_register["rs1"])
        self.data_path.rs2(self.program_register["rs2"])
        self.data_path.op1_sig(Selects.SEL_A)
        self.data_path.op2_sig(Selects.SEL_A)
        self.data_path.alu(ALUModes.REM)
        self.data_path.read(Selects.SEL_A)
        self.data_path.latch_file(self.program_register["rd"])
        self.m_signal(Selects.SEL_C)
        return "REM"

    def sll_microcode(self):
        self.data_path.rs1(self.program_register["rs1"])
        self.data_path.rs2(self.program_register["rs2"])
        self.data_path.op1_sig(Selects.SEL_A)
        self.data_path.op2_sig(Selects.SEL_A)
        self.data_path.alu(ALUModes.SLL)
        self.data_path.read(Selects.SEL_A)
        self.data_path.latch_file(self.program_register["rd"])
        self.m_signal(Selects.SEL_C)
        return "SLL"

    def srl_microcode(self):
        self.data_path.rs1(self.program_register["rs1"])
        self.data_path.rs2(self.program_register["rs2"])
        self.data_path.op1_sig(Selects.SEL_A)
        self.data_path.op2_sig(Selects.SEL_A)
        self.data_path.alu(ALUModes.SRL)
        self.data_path.read(Selects.SEL_A)
        self.data_path.latch_file(self.program_register["rd"])
        self.m_signal(Selects.SEL_C)
        return "SRL"

    def sra_microcode(self):
        self.data_path.rs1(self.program_register["rs1"])
        self.data_path.rs2(self.program_register["rs2"])
        self.data_path.op1_sig(Selects.SEL_A)
        self.data_path.op2_sig(Selects.SEL_A)
        self.data_path.alu(ALUModes.SRA)
        self.data_path.read(Selects.SEL_A)
        self.data_path.latch_file(self.program_register["rd"])
        self.m_signal(Selects.SEL_C)
        return "SRA"

    def and_microcode(self):
        self.data_path.rs1(self.program_register["rs1"])
        self.data_path.rs2(self.program_register["rs2"])
        self.data_path.op1_sig(Selects.SEL_A)
        self.data_path.op2_sig(Selects.SEL_A)
        self.data_path.alu(ALUModes.AND)
        self.data_path.read(Selects.SEL_A)
        self.data_path.latch_file(self.program_register["rd"])
        self.m_signal(Selects.SEL_C)
        return "AND"

    def or_microcode(self):
        self.data_path.rs1(self.program_register["rs1"])
        self.data_path.rs2(self.program_register["rs2"])
        self.data_path.op1_sig(Selects.SEL_A)
        self.data_path.op2_sig(Selects.SEL_A)
        self.data_path.alu(ALUModes.OR)
        self.data_path.read(Selects.SEL_A)
        self.data_path.latch_file(self.program_register["rd"])
        self.m_signal(Selects.SEL_C)
        return "OR"

    def xor_microcode(self):
        self.data_path.rs1(self.program_register["rs1"])
        self.data_path.rs2(self.program_register["rs2"])
        self.data_path.op1_sig(Selects.SEL_A)
        self.data_path.op2_sig(Selects.SEL_A)
        self.data_path.alu(ALUModes.XOR)
        self.data_path.read(Selects.SEL_A)
        self.data_path.latch_file(self.program_register["rd"])
        self.m_signal(Selects.SEL_C)
        return "XOR"

    def jal_microcode(self):
        self.data_path.mc_const = 0
        self.data_path.op1_sig(Selects.SEL_C)
        self.data_path.op2_sig(Selects.SEL_B)
        self.data_path.alu(ALUModes.ADD)
        self.data_path.read(Selects.SEL_A)
        self.data_path.latch_file(self.program_register["rd"])
        self.m_signal(Selects.SEL_A)
        self.data_path.pc = self.program_counter
        return "JAL"

    def j_microcode(self):
        self.data_path.op1_sig(Selects.SEL_C)
        self.data_path.op2_sig(Selects.SEL_D)
        self.data_path.alu(ALUModes.ADD)
        self.pc_mux_sel(CondModes.TRUE)
        self.latch_pc()
        self.m_signal(Selects.SEL_C)
        self.data_path.pc = self.program_counter
        return "J"

    def jr_microcode(self):
        self.data_path.mc_const = 0
        self.data_path.rs1(self.program_register["rs1"])
        self.data_path.op1_sig(Selects.SEL_A)
        self.data_path.op2_sig(Selects.SEL_B)
        self.data_path.alu(ALUModes.ADD)
        self.pc_mux_sel(CondModes.TRUE)
        self.latch_pc()
        self.m_signal(Selects.SEL_C)
        self.data_path.pc = self.program_counter
        return "JR"

    def bgt_microcode(self):
        self.data_path.rs1(self.program_register["rs1"])
        self.data_path.rs2(self.program_register["rs2"])
        self.data_path.op1_sig(Selects.SEL_C)
        self.data_path.op2_sig(Selects.SEL_D)
        self.data_path.alu(ALUModes.ADD)
        self.pc_mux_sel(CondModes.GT)
        self.latch_pc()
        self.m_signal(Selects.SEL_C)
        self.data_path.pc = self.program_counter
        return "BGT"

    def bgtu_microcode(self):
        self.data_path.rs1(self.program_register["rs1"])
        self.data_path.rs2(self.program_register["rs2"])
        self.data_path.op1_sig(Selects.SEL_C)
        self.data_path.op2_sig(Selects.SEL_D)
        self.data_path.alu(ALUModes.ADD)
        self.pc_mux_sel(CondModes.GTU)
        self.latch_pc()
        self.m_signal(Selects.SEL_C)
        self.data_path.pc = self.program_counter
        return "BGTU"

    def ble_microcode(self):
        self.data_path.rs1(self.program_register["rs1"])
        self.data_path.rs2(self.program_register["rs2"])
        self.data_path.op1_sig(Selects.SEL_C)
        self.data_path.op2_sig(Selects.SEL_D)
        self.data_path.alu(ALUModes.ADD)
        self.pc_mux_sel(CondModes.LE)
        self.latch_pc()
        self.m_signal(Selects.SEL_C)
        self.data_path.pc = self.program_counter
        return "BLE"

    def bleu_microcode(self):
        self.data_path.rs1(self.program_register["rs1"])
        self.data_path.rs2(self.program_register["rs2"])
        self.data_path.op1_sig(Selects.SEL_C)
        self.data_path.op2_sig(Selects.SEL_D)
        self.data_path.alu(ALUModes.ADD)
        self.pc_mux_sel(CondModes.LEU)
        self.latch_pc()
        self.m_signal(Selects.SEL_C)
        self.data_path.pc = self.program_counter
        return "BLEU"

    def beq_microcode(self):
        self.data_path.rs1(self.program_register["rs1"])
        self.data_path.rs2(self.program_register["rs2"])
        self.data_path.op1_sig(Selects.SEL_C)
        self.data_path.op2_sig(Selects.SEL_D)
        self.data_path.alu(ALUModes.ADD)
        self.pc_mux_sel(CondModes.EQ)
        self.latch_pc()
        self.m_signal(Selects.SEL_C)
        self.data_path.pc = self.program_counter
        return "BEQ"

    def bne_microcode(self):
        self.data_path.rs1(self.program_register["rs1"])
        self.data_path.rs2(self.program_register["rs2"])
        self.data_path.op1_sig(Selects.SEL_C)
        self.data_path.op2_sig(Selects.SEL_D)
        self.data_path.alu(ALUModes.ADD)
        self.pc_mux_sel(CondModes.NE)
        self.latch_pc()
        self.m_signal(Selects.SEL_C)
        self.data_path.pc = self.program_counter
        return "BNE"


microcode_memory = {
    0: ControlUnit.fetch_command,
    1: ControlUnit.decode_command,
    2: ControlUnit.lui_microcode,
    3: ControlUnit.halt_microcode,
    4: ControlUnit.mv_microcode,
    5: ControlUnit.sw_microcode_1,
    6: ControlUnit.sw_microcode_2,
    7: ControlUnit.lw_microcode_1,
    8: ControlUnit.lw_microcode_2,
    9: ControlUnit.addi_microcode,
    10: ControlUnit.add_microcode,
    11: ControlUnit.sub_microcode,
    12: ControlUnit.mul_microcode,
    13: ControlUnit.mulh_microcode,
    14: ControlUnit.div_microcode,
    15: ControlUnit.rem_microcode,
    16: ControlUnit.sll_microcode,
    17: ControlUnit.srl_microcode,
    18: ControlUnit.sra_microcode,
    19: ControlUnit.and_microcode,
    20: ControlUnit.or_microcode,
    21: ControlUnit.xor_microcode,
    22: ControlUnit.jal_microcode,
    23: ControlUnit.j_microcode,
    24: ControlUnit.jr_microcode,
    25: ControlUnit.bgt_microcode,
    26: ControlUnit.bgtu_microcode,
    27: ControlUnit.ble_microcode,
    28: ControlUnit.bleu_microcode,
    29: ControlUnit.beq_microcode,
    30: ControlUnit.bne_microcode,
}

LUT = {
    Opcode.LUI: 2,
    Opcode.HALT: 3,
    Opcode.MV: 4,
    Opcode.SW: 5,
    Opcode.LW: 7,
    Opcode.ADDI: 9,
    Opcode.ADD: 10,
    Opcode.SUB: 11,
    Opcode.MUL: 12,
    Opcode.MULH: 13,
    Opcode.DIV: 14,
    Opcode.REM: 15,
    Opcode.SLL: 16,
    Opcode.SRL: 17,
    Opcode.SRA: 18,
    Opcode.AND: 19,
    Opcode.OR: 20,
    Opcode.XOR: 21,
    Opcode.JAL: 22,
    Opcode.J: 23,
    Opcode.JR: 24,
    Opcode.BGT: 25,
    Opcode.BGTU: 26,
    Opcode.BLE: 27,
    Opcode.BLEU: 28,
    Opcode.BEQ: 29,
    Opcode.BNE: 30,
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
        assert (
            address <= self.output_addr - 4 or address >= self.output_addr + 4
        ), "Невозможно считать данные из буфера вывода!"
        assert (
            address <= self.input_addr - 4 or address == self.input_addr or address >= self.input_addr + 4
        ), "Кривое обращение по адресу ввода!"
        assert address <= self.data_memory_size - 4, "Выход за пределы памяти!"
        if address == self.input_addr:
            assert len(self.input_buffer) != 0, "Буфер ввода пустой!"
            res = int.from_bytes((self.input_buffer[0].to_bytes(4, byteorder="little")), "little")
            self.input_buffer = self.input_buffer[1:]
            return res
        a = self.data_memory[address]
        b = self.data_memory[address + 1]
        c = self.data_memory[address + 2]
        d = self.data_memory[address + 3]
        res = (d << 24) | (c << 16) | (b << 8) | a
        return res

    def write_word(self, address, value):
        assert (
            address <= self.input_addr - 4 or address >= self.input_addr + 4
        ), "Невозможно записать данные в буфер ввода!"
        assert (
            address <= self.output_addr - 4 or address == self.output_addr or address >= self.output_addr + 4
        ), "Кривое обращение по адресу вывода!"
        assert address <= self.data_memory_size - 4, "Выход за пределы памяти!"
        if address == self.output_addr:
            self.output_buffer.append(value)
            return
        value_bytes = value.to_bytes(4, byteorder="little")
        self.data_memory[address] = value_bytes[0]
        self.data_memory[address + 1] = value_bytes[1]
        self.data_memory[address + 2] = value_bytes[2]
        self.data_memory[address + 3] = value_bytes[3]

    def load_dump(self, data_dump):
        for i in range(len(data_dump)):
            self.data_memory[i] = data_dump[i]


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Использование: python machine.py <program_dump> <data_dump> <input_file> <input_fmt> (num | str)")
        exit(1)
    if sys.argv[4] == "num":
        input_buffer = list(map(int, open(sys.argv[3]).readlines()))
    else:
        input_buffer = list(map(ord, open(sys.argv[3]).readline()))
        input_buffer[-1] = 0
    code = from_bytes(sys.argv[1])
    control_unit = ControlUnit(microcode_memory, code, 0x80, 0x84, 1024, input_buffer, LUT)
    control_unit.data_path.data_memory_module.load_dump(get_data_dump(sys.argv[2]))
    control_unit.run_microcode()
    print(control_unit.data_path.data_memory_module.output_buffer)
    print("".join(map(chr, control_unit.data_path.data_memory_module.output_buffer)))
