import opcode
import pprint
from enum import Enum


class Opcode(str, Enum):
    LUI = 'lui'
    MV = 'mv'
    SW = 'sw'
    LW = 'lw'
    ADDI = 'addi'
    ADD = 'add'
    SUB = 'sub'
    MUL = 'mul'
    MULH = 'mulh'
    DIV = 'div'
    REM = 'rem'
    SLL = 'sll'
    SRL = 'srl'
    SRA = 'sra'
    AND = 'and'
    OR = 'or'
    XOR = 'xor'
    J = 'j'
    JAL = 'jal'
    JR = 'jr'
    BLE = 'ble'
    BLEU = 'bleu'
    BGT = 'bgt'
    BGTU = 'bgtu'
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
    NOT_USED = 'not_used'

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
    Opcode.BLE: 0x13,
    Opcode.BLEU: 0x14,
    Opcode.BGT: 0x15,
    Opcode.BGTU: 0x16,
    Opcode.BEQ: 0x17,
    Opcode.BNE: 0x18,
    Opcode.HALT: 0x19,
    Opcode.SRA: 0x1A
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
    0x13: Opcode.BLE,
    0x14: Opcode.BLEU,
    0x15: Opcode.BGT,
    0x16: Opcode.BGTU,
    0x17: Opcode.BEQ,
    0x18: Opcode.BNE,
    0x19: Opcode.HALT,
    0x1A: Opcode.SRA
}

reg_to_binary = {
    Register.SP: 0x00,
    Register.R0: 0x01,
    Register.R1: 0x02,
    Register.R2: 0x03,
    Register.R3: 0x04,
    Register.R4: 0x05,
    Register.R5: 0x06,
    Register.R6: 0x07,
    Register.ZERO: 0x08
}

binary_to_reg = {
    0x00: Register.SP,
    0x01: Register.R0,
    0x02: Register.R1,
    0x03: Register.R2,
    0x04: Register.R3,
    0x05: Register.R4,
    0x06: Register.R5,
    0x07: Register.R6,
    0x08: Register.ZERO
}


def to_bytes(code):
    binary_bytes = bytearray()
    for instr in code:
        opcode_val = opcode_to_binary[instr["opcode"]]
        binary_instr = opcode_val << 27
        if instr["rd"] != Register.NOT_USED:
            binary_instr |= (reg_to_binary[instr["rd"]]) << 24
        if instr["rs1"] != Register.NOT_USED:
            binary_instr |= (reg_to_binary[instr["rs1"]]) << 20
        if instr["rs2"] != Register.NOT_USED:
            binary_instr |= (reg_to_binary[instr["rs2"]]) << 16
        if instr["k"] != Register.NOT_USED:
            binary_instr |= instr["k"] & 0xFFFF
        binary_bytes.extend([
            (binary_instr >> 24) & 0xFF,
            (binary_instr >> 16) & 0xFF,
            (binary_instr >> 8) & 0xFF,
            binary_instr & 0xFF
        ])
    return bytes(binary_bytes)


def to_signed16(num):
    if num & 0x8000:
        return num - 0x10000
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

        rd_bin = (word >> 24) & 0x7
        rs1_bin = (word >> 20) & 0xF
        rs2_bin = (word >> 16) & 0xF
        k = to_signed16(word & 0xFFFF)
        rd = binary_to_reg[rd_bin].value if rd_bin <= 7 else "UNKNOW"
        rs1 = binary_to_reg[rs1_bin].value if rs1_bin <= 8 else "UNKNOW"
        rs2 = binary_to_reg[rs2_bin].value if rs2_bin <= 8 else "UNKNOW"
        if opcode == Opcode.LUI:
            mnemonic = f"lui {rd}, {k}"
        elif opcode == Opcode.MV:
            mnemonic = f"mv {rd}, {rs1}"
        elif opcode == Opcode.SW:
            mnemonic = f"sw {rs2}, {k}({rs1})"
        elif opcode == Opcode.LW:
            mnemonic = f"lw {rs2}, {k}({rs1})"
        elif opcode == Opcode.ADDI:
            mnemonic = f"addi {rd}, {rs1}, {k}"
        elif opcode == Opcode.ADD:
            mnemonic = f"add {rd}, {rs1}, {rs2}"
        elif opcode == Opcode.SUB:
            mnemonic = f"sub {rd}, {rs1}, {rs2}"
        elif opcode == Opcode.MUL:
            mnemonic = f"mul {rd}, {rs1}, {rs2}"
        elif opcode == Opcode.MULH:
            mnemonic = f"mulh {rd}, {rs1}, {rs2}"
        elif opcode == Opcode.DIV:
            mnemonic = f"div {rd}, {rs1}, {rs2}"
        elif opcode == Opcode.REM:
            mnemonic = f"rem {rd}, {rs1}, {rs2}"
        elif opcode == Opcode.SLL:
            mnemonic = f"sll {rd}, {rs1}, {rs2}"
        elif opcode == Opcode.SRL:
            mnemonic = f"srl {rd}, {rs1}, {rs2}"
        elif opcode == Opcode.AND:
            mnemonic = f"and {rd}, {rs1}, {rs2}"
        elif opcode == Opcode.OR:
            mnemonic = f"or {rd}, {rs1}, {rs2}"
        elif opcode == Opcode.XOR:
            mnemonic = f"xor {rd}, {rs1}, {rs2}"
        elif opcode == Opcode.J:
            mnemonic = f"j {k}"
        elif opcode == Opcode.JAL:
            mnemonic = f"jal {rd}, {k}"
        elif opcode == Opcode.JR:
            mnemonic = f"jr {rs1}"
        elif opcode == Opcode.BLEU:
            mnemonic = f"bleu {rs1}, {rs2}, {k}"
        elif opcode == Opcode.BLE:
            mnemonic = f"ble {rs1}, {rs2}, {k}"
        elif opcode == Opcode.BGT:
            mnemonic = f"bgt {rs1}, {rs2}, {k}"
        elif opcode == Opcode.BGTU:
            mnemonic = f"bgtu {rs1}, {rs2}, {k}"
        elif opcode == Opcode.BNE:
            mnemonic = f"bne {rs1}, {rs2}, {k}"
        elif opcode == Opcode.BEQ:
            mnemonic = f"beq {rs1}, {rs2}, {k}"
        elif opcode == opcode.HALT:
            mnemonic = f"halt"
        elif opcode == opcode.SRA:
            mnemonic = f"sra {rd}, {rs1}, {rs2}"
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

            word = int.from_bytes(bytes_data, "big")
            opcode_bin = word >> 27
            opcode = binary_to_opcode.get(opcode_bin)
            rd_bin = (word >> 24) & 0x7
            rs1_bin = (word >> 20) & 0xF
            rs2_bin = (word >> 16) & 0xF
            k = to_signed16(word & 0xFFFF)
            rd = binary_to_reg.get(rd_bin) if binary_to_reg.get(rd_bin) is not None else Register.NOT_USED
            rs1 = binary_to_reg.get(rs1_bin) if binary_to_reg.get(rs1_bin) is not None else Register.NOT_USED
            rs2 = binary_to_reg.get(rs2_bin) if binary_to_reg.get(rs2_bin) is not None else Register.NOT_USED
            instruction = {
                "opcode": opcode,
                "rd": Register.NOT_USED,
                "rs1": Register.NOT_USED,
                "rs2": Register.NOT_USED,
                "k": Register.NOT_USED
            }
            if opcode == Opcode.LUI:
                instruction["rd"] = rd
                instruction["k"] = k
            elif opcode == Opcode.MV:
                instruction["rd"] = rd
                instruction["rs1"] = rs1
            elif opcode == Opcode.SW:
                instruction["rs1"] = rs1
                instruction["rs2"] = rs2
                instruction["k"] = k
            elif opcode == Opcode.LW:
                instruction["rd"] = rd
                instruction["rs1"] = rs1
                instruction["k"] = k
            elif opcode == Opcode.ADDI:
                instruction["rd"] = rd
                instruction["rs1"] = rs1
                instruction["k"] = k
            elif opcode == Opcode.ADD:
                instruction["rd"] = rd
                instruction["rs1"] = rs1
                instruction["rs2"] = rs2
            elif opcode == Opcode.SUB:
                instruction["rd"] = rd
                instruction["rs1"] = rs1
                instruction["rs2"] = rs2
            elif opcode == Opcode.MUL:
                instruction["rd"] = rd
                instruction["rs1"] = rs1
                instruction["rs2"] = rs2
            elif opcode == Opcode.MULH:
                instruction["rd"] = rd
                instruction["rs1"] = rs1
                instruction["rs2"] = rs2
            elif opcode == Opcode.DIV:
                instruction["rd"] = rd
                instruction["rs1"] = rs1
                instruction["rs2"] = rs2
            elif opcode == Opcode.REM:
                instruction["rd"] = rd
                instruction["rs1"] = rs1
                instruction["rs2"] = rs2
            elif opcode == Opcode.SLL:
                instruction["rd"] = rd
                instruction["rs1"] = rs1
                instruction["rs2"] = rs2
            elif opcode == Opcode.SRL:
                instruction["rd"] = rd
                instruction["rs1"] = rs1
                instruction["rs2"] = rs2
            elif opcode == Opcode.AND:
                instruction["rd"] = rd
                instruction["rs1"] = rs1
                instruction["rs2"] = rs2
            elif opcode == Opcode.OR:
                instruction["rd"] = rd
                instruction["rs1"] = rs1
                instruction["rs2"] = rs2
            elif opcode == Opcode.XOR:
                instruction["rd"] = rd
                instruction["rs1"] = rs1
                instruction["rs2"] = rs2
            elif opcode == Opcode.J:
                instruction["k"] = k
            elif opcode == Opcode.JAL:
                instruction["rd"] = rd
                instruction["k"] = k
            elif opcode == Opcode.JR:
                instruction["rs1"] = rs1
            elif opcode == Opcode.BLEU:
                instruction["rs2"] = rs2
                instruction["rs1"] = rs1
                instruction["k"] = k
            elif opcode == Opcode.BLE:
                instruction["rs2"] = rs2
                instruction["rs1"] = rs1
                instruction["k"] = k
            elif opcode == Opcode.BGT:
                instruction["rs2"] = rs2
                instruction["rs1"] = rs1
                instruction["k"] = k
            elif opcode == Opcode.BGTU:
                instruction["rs2"] = rs2
                instruction["rs1"] = rs1
                instruction["k"] = k
            elif opcode == Opcode.BNE:
                instruction["rs2"] = rs2
                instruction["rs1"] = rs1
                instruction["k"] = k
            elif opcode == Opcode.BEQ:
                instruction["rs2"] = rs2
                instruction["rs1"] = rs1
                instruction["k"] = k
            elif opcode == opcode.HALT:
                pass
            elif opcode == opcode.SRA:
                instruction["rd"] = rd
                instruction["rs1"] = rs1
                instruction["rs2"] = rs2
            code.append(instruction)
    return code


class ALUModes(str, Enum):
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    MULH = "MULH"
    DIV = "DIV"
    REM = "REM"
    SLL = "SLL"
    SRL = "SRL"
    AND = "AND"
    OR = "OR"
    XOR = "XOR"
    SRA = "SRA"

class CondModes(str, Enum):
    EQ = "EQ"
    NE = "NE"
    LE = "LE"
    LEU = "LEU"
    GT = "GT"
    GTU = "GTU"
    TRUE = "TRUE"
    FALSE = "FALSE"

class Selects(int, Enum):
    SEL_A = 0
    SEL_B = 1
    SEL_C = 2
    SEL_D = 3

def get_data_dump(filename):
    res = []
    with open(filename, "rb") as f:
        while True:
            b = f.read(1)
            if not b:
                break
            res.append(int.from_bytes(b, byteorder="little"))
    return res

