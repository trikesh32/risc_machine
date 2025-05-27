import opcode
from enum import Enum

class Opcode(str, Enum):
    LUI = 'lui' # загружает в старшие 23 бита регистра значение
    MV = 'mv' # копирует значение из регистра в регистр
    SW = 'sw' # сохраняет в память слово
    LW = 'lw' # загружает из памяти слово в регистр
    ADDI = 'addi'
    ADD = 'add'
    SUB = 'sub'
    MUL = 'mul'
    MULH = 'mulh'
    DIV = 'div'
    REM = 'rem'
    SLL = 'sll'
    SRL = 'srl'
    AND = 'and'
    OR = 'or'
    XOR = 'xor'
    J = 'j'
    JAL = 'jal'
    JR = 'jr'
    BLT = 'blt'
    BLE = 'ble'
    BGT = 'bgt'
    BGE = 'bge'
    BEQ = 'beq'
    BNE = 'bne'
    HALT = 'halt'

    def __str__(self):
        return str(self.value)


class Register(str, Enum):
    ZERO = 'zero'
    R0 = 'r0'
    R1 = 'r1'
    R2 = 'r2'
    R3 = 'r3'
    R4 = 'r4'
    R5 = 'r5'
    R6 = 'r6'
    SP = 'sp'

    def __str__(self):
        return str(self.value)

opcode_to_binary = {
    Opcode.LUI: 0x00,
    Opcode.MV: 0x01,
    Opcode.SW: 0x02,
    Opcode.LW: 0x03,
    Opcode.ADDI: 0x04,
    Opcode.ADD: 0x05,
    Opcode.SUB: 0x06,
    Opcode.MUL: 0x07,
    Opcode.MULH: 0x08,
    Opcode.DIV: 0x09,
    Opcode.REM: 0x0A,
    Opcode.SLL: 0x0B,
    Opcode.SRL: 0x0C,
    Opcode.AND: 0x0D,
    Opcode.OR: 0x0E,
    Opcode.XOR: 0x0F,
    Opcode.J: 0x10,
    Opcode.JAL: 0x11,
    Opcode.JR: 0x12,
    Opcode.BLT: 0x13,
    Opcode.BLE: 0x14,
    Opcode.BGT: 0x15,
    Opcode.BGE: 0x16,
    Opcode.BEQ: 0x17,
    Opcode.BNE: 0x18,
    Opcode.HALT: 0x19
}

binary_to_opcode = {
    0x00: Opcode.LUI,
    0x01: Opcode.MV,
    0x02: Opcode.SW,
    0x03: Opcode.LW,
    0x04: Opcode.ADDI,
    0x05: Opcode.ADD,
    0x06: Opcode.SUB,
    0x07: Opcode.MUL,
    0x08: Opcode.MULH,
    0x09: Opcode.DIV,
    0x0A: Opcode.REM,
    0x0B: Opcode.SLL,
    0x0C: Opcode.SRL,
    0x0D: Opcode.AND,
    0x0E: Opcode.OR,
    0x0F: Opcode.XOR,
    0x10: Opcode.J,
    0x11: Opcode.JAL,
    0x12: Opcode.JR,
    0x13: Opcode.BLT,
    0x14: Opcode.BLE,
    0x15: Opcode.BGT,
    0x16: Opcode.BGE,
    0x17: Opcode.BEQ,
    0x18: Opcode.BNE,
    0x19: Opcode.HALT
}

reg_to_binary = {
    Register.ZERO: 0x00,
    Register.R0: 0x01,
    Register.R1: 0x02,
    Register.R2: 0x03,
    Register.R3: 0x04,
    Register.R4: 0x05,
    Register.R5: 0x06,
    Register.R6: 0x07,
    Register.SP: 0x08
}

binary_to_reg = {
    0x00: Register.ZERO,
    0x01: Register.R0,
    0x02: Register.R1,
    0x03: Register.R2,
    0x04: Register.R3,
    0x05: Register.R4,
    0x06: Register.R5,
    0x07: Register.R6,
    0x08: Register.SP
}

def to_bytes(code):
    binary_bytes = bytearray()
    for instr in code:
        opcode_val = opcode_to_binary[instr["opcode"]]
        if "arg3" in instr.keys():
            arg1_val = reg_to_binary[instr["arg1"]]
            arg2_val = reg_to_binary[instr["arg2"]]
            arg3_val = reg_to_binary[instr["arg3"]]
            binary_instr = (opcode_val << 27) | (arg1_val << 23) | (arg2_val << 19) | (arg3_val << 15)
        elif "arg2" in instr.keys():
            arg1_val = reg_to_binary[instr["arg1"]]
            arg2_val = reg_to_binary[instr["arg2"]]
            k = instr["k"]
            binary_instr = (opcode_val << 27) | (arg1_val << 23) | (arg2_val << 19) | (k & 0x7FFFF)
        else:
            arg1_val = reg_to_binary[instr["arg1"]]
            k = instr["k"]
            binary_instr = (opcode_val << 27) | (arg1_val << 23) | (k & 0x7FFFFF)
        binary_bytes.extend([
            (binary_instr >> 24) & 0xFF,
            (binary_instr >> 16) & 0xFF,
            (binary_instr >> 8) & 0xFF,
            binary_instr & 0xFF
        ])
    return bytes(binary_bytes)

def to_signed(num):
    if num & 0x40000:
        return num - 0x80000
    return num

def to_hex(code):
    binary_code = to_bytes(code)
    result = []
    for i in range(0, len(binary_code), 4):
        if i + 3 >= len(binary_code):
            break
        word = (binary_code[i] << 24) | (binary_code[i + 1] << 16) | (binary_code[i + 2] << 8) | binary_code[i + 3]
        opcode_bin = word >> 27
        opcode = binary_to_opcode[opcode_bin]

        arg1_bin = (word >> 23) & 0xF
        arg2_bin = (word >> 19) & 0xF
        arg3_bin = (word >> 15) & 0xF
        k_short = to_signed(word & 0x7FFFF)
        k_long = word & 0x7FFFFF
        arg1 = binary_to_reg[arg1_bin].value if arg1_bin <= 8 else "UNKNOW"
        arg2 = binary_to_reg[arg2_bin].value if arg2_bin <= 8 else "UNKNOW"
        arg3 = binary_to_reg[arg3_bin].value if arg3_bin <= 8 else "UNKNOW"
        if opcode == Opcode.LUI:
            mnemonic = f"lui {arg1}, {k_long}"
        elif opcode == Opcode.MV:
            mnemonic = f"mv {arg1}, {arg2}"
        elif opcode == Opcode.SW:
            mnemonic = f"sw {arg1}, {k_short}({arg2})"
        elif opcode == Opcode.LW:
            mnemonic = f"lw {arg1}, {k_short}({arg2})"
        elif opcode == Opcode.ADDI:
            mnemonic = f"addi {arg1}, {arg2}, {k_short}"
        elif opcode == Opcode.ADD:
            mnemonic = f"add {arg1}, {arg2}, {arg3}"
        elif opcode == Opcode.SUB:
            mnemonic = f"sub {arg1}, {arg2}, {arg3}"
        elif opcode == Opcode.MUL:
            mnemonic = f"mul {arg1}, {arg2}, {arg3}"
        elif opcode == Opcode.MULH:
            mnemonic = f"mulh {arg1}, {arg2}, {arg3}"
        elif opcode == Opcode.DIV:
            mnemonic = f"div {arg1}, {arg2}, {arg3}"
        elif opcode == Opcode.REM:
            mnemonic = f"rem {arg1}, {arg2}, {arg3}"
        elif opcode == Opcode.SLL:
            mnemonic = f"sll {arg1}, {arg2}, {arg3}"
        elif opcode == Opcode.SRL:
            mnemonic = f"srl {arg1}, {arg2}, {arg3}"
        elif opcode == Opcode.AND:
            mnemonic = f"and {arg1}, {arg2}, {arg3}"
        elif opcode == Opcode.OR:
            mnemonic = f"or {arg1}, {arg2}, {arg3}"
        elif opcode == Opcode.XOR:
            mnemonic = f"xor {arg1}, {arg2}, {arg3}"
        elif opcode == Opcode.J:
            mnemonic = f"j {k_short}"
        elif opcode == Opcode.JAL:
            mnemonic = f"jal {arg1}, {k_short}"
        elif opcode == Opcode.JR:
            mnemonic = f"jr {arg1}"
        elif opcode == Opcode.BLT:
            mnemonic = f"blt {arg1}, {arg2}, {k_short}"
        elif opcode == Opcode.BLE:
            mnemonic = f"ble {arg1}, {arg2}, {k_short}"
        elif opcode == Opcode.BGT:
            mnemonic = f"bgt {arg1}, {arg2}, {k_short}"
        elif opcode == Opcode.BGE:
            mnemonic = f"bge {arg1}, {arg2}, {k_short}"
        elif opcode == Opcode.BNE:
            mnemonic = f"bne {arg1}, {arg2}, {k_short}"
        elif opcode == Opcode.BEQ:
            mnemonic = f"beq {arg1}, {arg2}, {k_short}"
        elif opcode == opcode.HALT:
            mnemonic = f"halt"
        else:
            mnemonic = f"UNKNOWN_{opcode_bin:02X}"

        result.append(f"{i // 4} - {word:08X} - {mnemonic}")
    return "\n".join(result)


def from_bytes(input_file_name):
    code = []
    with open(input_file_name, "rb") as f:
        while True:
            bytes_data = f.read(4)
            if len(bytes_data) != 4:
                break
            instruction = {}
            word = int.from_bytes(bytes_data, "big")
            opcode_bin = word >> 27
            opcode = binary_to_opcode.get(opcode_bin)
            arg1_bin = (word >> 23) & 0xF
            arg2_bin = (word >> 19) & 0xF
            arg3_bin = (word >> 15) & 0xF
            k_short = to_signed(word & 0x7FFFF)
            k_long = word & 0x7FFFFF
            arg1 = binary_to_reg.get(arg1_bin)
            arg2 = binary_to_reg.get(arg2_bin)
            arg3 = binary_to_reg.get(arg3_bin)
            instruction["opcode"] = opcode
            if opcode == Opcode.LUI:
                instruction["arg1"] = arg1
                instruction["k"] = k_long
            elif opcode == Opcode.MV:
                instruction["arg1"] = arg1
                instruction["arg2"] = arg2
            elif opcode == Opcode.SW:
                instruction["arg1"] = arg1
                instruction["arg2"] = arg2
                instruction["k"] = k_short
            elif opcode == Opcode.LW:
                instruction["arg1"] = arg1
                instruction["arg2"] = arg2
                instruction["k"] = k_short
            elif opcode == Opcode.ADDI:
                instruction["arg1"] = arg1
                instruction["arg2"] = arg2
                instruction["k"] = k_short
            elif opcode == Opcode.ADD:
                instruction["arg1"] = arg1
                instruction["arg2"] = arg2
                instruction["arg3"] = arg3
            elif opcode == Opcode.SUB:
                instruction["arg1"] = arg1
                instruction["arg2"] = arg2
                instruction["arg3"] = arg3
            elif opcode == Opcode.MUL:
                instruction["arg1"] = arg1
                instruction["arg2"] = arg2
                instruction["arg3"] = arg3
            elif opcode == Opcode.MULH:
                instruction["arg1"] = arg1
                instruction["arg2"] = arg2
                instruction["arg3"] = arg3
            elif opcode == Opcode.DIV:
                instruction["arg1"] = arg1
                instruction["arg2"] = arg2
                instruction["arg3"] = arg3
            elif opcode == Opcode.REM:
                instruction["arg1"] = arg1
                instruction["arg2"] = arg2
                instruction["arg3"] = arg3
            elif opcode == Opcode.SLL:
                instruction["arg1"] = arg1
                instruction["arg2"] = arg2
                instruction["arg3"] = arg3
            elif opcode == Opcode.SRL:
                instruction["arg1"] = arg1
                instruction["arg2"] = arg2
                instruction["arg3"] = arg3
            elif opcode == Opcode.AND:
                instruction["arg1"] = arg1
                instruction["arg2"] = arg2
                instruction["arg3"] = arg3
            elif opcode == Opcode.OR:
                instruction["arg1"] = arg1
                instruction["arg2"] = arg2
                instruction["arg3"] = arg3
            elif opcode == Opcode.XOR:
                instruction["arg1"] = arg1
                instruction["arg2"] = arg2
                instruction["arg3"] = arg3
            elif opcode == Opcode.J:
                instruction["k"] = k_short
            elif opcode == Opcode.JAL:
                instruction["arg1"] = arg1
                instruction["k"] = k_short
            elif opcode == Opcode.JR:
                instruction["arg1"] = arg1
            elif opcode == Opcode.BLT:
                instruction["arg1"] = arg1
                instruction["arg2"] = arg2
                instruction["k"] = k_short
            elif opcode == Opcode.BLE:
                instruction["arg1"] = arg1
                instruction["arg2"] = arg2
                instruction["k"] = k_short
            elif opcode == Opcode.BGT:
                instruction["arg1"] = arg1
                instruction["arg2"] = arg2
                instruction["k"] = k_short
            elif opcode == Opcode.BGE:
                instruction["arg1"] = arg1
                instruction["arg2"] = arg2
                instruction["k"] = k_short
            elif opcode == Opcode.BNE:
                instruction["arg1"] = arg1
                instruction["arg2"] = arg2
                instruction["k"] = k_short
            elif opcode == Opcode.BEQ:
                instruction["arg1"] = arg1
                instruction["arg2"] = arg2
                instruction["k"] = k_short
            elif opcode == opcode.HALT:
                pass
            code.append(instruction)
    return code






