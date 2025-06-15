from enum import Enum


class Opcode(str, Enum):
    LUI = "lui"
    MV = "mv"
    SW = "sw"
    LW = "lw"
    ADDI = "addi"
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    MULH = "mulh"
    DIV = "div"
    REM = "rem"
    SLL = "sll"
    SRL = "srl"
    SRA = "sra"
    AND = "and"
    OR = "or"
    XOR = "xor"
    J = "j"
    JAL = "jal"
    JR = "jr"
    BLE = "ble"
    BLEU = "bleu"
    BGT = "bgt"
    BGTU = "bgtu"
    BEQ = "beq"
    BNE = "bne"
    HALT = "halt"

    def __str__(self):
        return str(self.value)


class Register(str, Enum):
    ZERO = "zero"
    R0 = "r0"
    R1 = "r1"
    R2 = "r2"
    R3 = "r3"
    R4 = "r4"
    R5 = "r5"
    R6 = "r6"
    SP = "sp"
    NOT_USED = "not_used"

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
    Opcode.SRA: 0x1A,
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
    0x1A: Opcode.SRA,
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
    Register.ZERO: 0x08,
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
    0x08: Register.ZERO,
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
        binary_bytes.extend(
            [(binary_instr >> 24) & 0xFF, (binary_instr >> 16) & 0xFF, (binary_instr >> 8) & 0xFF, binary_instr & 0xFF]
        )
    return bytes(binary_bytes)


def to_signed16(num):
    if num & 0x8000:
        return num - 0x10000
    return num


def _extract_instruction_fields(word: int) -> tuple:
    opcode_bin = word >> 27
    rd_bin = (word >> 24) & 0x7
    rs1_bin = (word >> 20) & 0xF
    rs2_bin = (word >> 16) & 0xF
    k = to_signed16(word & 0xFFFF)
    return opcode_bin, rd_bin, rs1_bin, rs2_bin, k


def _get_register_name(reg_bin: int, max_valid: int = 8) -> str:
    return binary_to_reg[reg_bin].value if reg_bin <= max_valid else "UNKNOW"


def _generate_mnemonic(opcode: Opcode, rd: str, rs1: str, rs2: str, k: int) -> str:
    mnemonics = {
        Opcode.LUI: f"lui {rd}, {k}",
        Opcode.MV: f"mv {rd}, {rs1}",
        Opcode.SW: f"sw {rs2}, {k}({rs1})",
        Opcode.LW: f"lw {rd}, {k}({rs1})",
        Opcode.ADDI: f"addi {rd}, {rs1}, {k}",
        Opcode.ADD: f"add {rd}, {rs1}, {rs2}",
        Opcode.SUB: f"sub {rd}, {rs1}, {rs2}",
        Opcode.MUL: f"mul {rd}, {rs1}, {rs2}",
        Opcode.MULH: f"mulh {rd}, {rs1}, {rs2}",
        Opcode.DIV: f"div {rd}, {rs1}, {rs2}",
        Opcode.REM: f"rem {rd}, {rs1}, {rs2}",
        Opcode.SLL: f"sll {rd}, {rs1}, {rs2}",
        Opcode.SRL: f"srl {rd}, {rs1}, {rs2}",
        Opcode.AND: f"and {rd}, {rs1}, {rs2}",
        Opcode.OR: f"or {rd}, {rs1}, {rs2}",
        Opcode.XOR: f"xor {rd}, {rs1}, {rs2}",
        Opcode.J: f"j {k}",
        Opcode.JAL: f"jal {rd}, {k}",
        Opcode.JR: f"jr {rs1}",
        Opcode.BLEU: f"bleu {rs1}, {rs2}, {k}",
        Opcode.BLE: f"ble {rs1}, {rs2}, {k}",
        Opcode.BGT: f"bgt {rs1}, {rs2}, {k}",
        Opcode.BGTU: f"bgtu {rs1}, {rs2}, {k}",
        Opcode.BNE: f"bne {rs1}, {rs2}, {k}",
        Opcode.BEQ: f"beq {rs1}, {rs2}, {k}",
        Opcode.HALT: "halt",
        Opcode.SRA: f"sra {rd}, {rs1}, {rs2}",
    }
    return mnemonics.get(opcode, f"UNKNOWN_{opcode.value:02X}")


def to_hex(code: bytes) -> str:
    binary_code = to_bytes(code)
    result = []

    for i in range(0, len(binary_code), 4):
        if i + 3 >= len(binary_code):
            break

        word = (binary_code[i] << 24) | (binary_code[i + 1] << 16) | (binary_code[i + 2] << 8) | binary_code[i + 3]
        opcode_bin, rd_bin, rs1_bin, rs2_bin, k = _extract_instruction_fields(word)

        opcode = binary_to_opcode.get(opcode_bin)
        rd = _get_register_name(rd_bin, max_valid=7)
        rs1 = _get_register_name(rs1_bin)
        rs2 = _get_register_name(rs2_bin)

        mnemonic = _generate_mnemonic(opcode, rd, rs1, rs2, k) if opcode else f"UNKNOWN_{opcode_bin:02X}"
        result.append(f"{i // 4} - {word:08X} - {mnemonic}")

    return "\n".join(result)


def _parse_instruction_word(word: int) -> dict:
    opcode_bin = word >> 27
    return {
        "opcode": binary_to_opcode.get(opcode_bin),
        "rd_bin": (word >> 24) & 0x7,
        "rs1_bin": (word >> 20) & 0xF,
        "rs2_bin": (word >> 16) & 0xF,
        "k": to_signed16(word & 0xFFFF)
    }


def _get_register(reg_bin: int) -> Register:
    return binary_to_reg.get(reg_bin, Register.NOT_USED)


def _build_instruction(fields: dict) -> dict:
    opcode = fields["opcode"]
    if opcode is None:
        return {"opcode": None}

    instruction = {
        "opcode": opcode,
        "rd": Register.NOT_USED,
        "rs1": Register.NOT_USED,
        "rs2": Register.NOT_USED,
        "k": Register.NOT_USED,
    }

    field_mapping = {
        Opcode.LUI: ["rd", "k"],
        Opcode.MV: ["rd", "rs1"],
        Opcode.SW: ["rs1", "rs2", "k"],
        Opcode.LW: ["rd", "rs1", "k"],
        Opcode.ADDI: ["rd", "rs1", "k"],
        Opcode.ADD: ["rd", "rs1", "rs2"],
        Opcode.SUB: ["rd", "rs1", "rs2"],
        Opcode.MUL: ["rd", "rs1", "rs2"],
        Opcode.MULH: ["rd", "rs1", "rs2"],
        Opcode.DIV: ["rd", "rs1", "rs2"],
        Opcode.REM: ["rd", "rs1", "rs2"],
        Opcode.SLL: ["rd", "rs1", "rs2"],
        Opcode.SRL: ["rd", "rs1", "rs2"],
        Opcode.SRA: ["rd", "rs1", "rs2"],
        Opcode.AND: ["rd", "rs1", "rs2"],
        Opcode.OR: ["rd", "rs1", "rs2"],
        Opcode.XOR: ["rd", "rs1", "rs2"],
        Opcode.J: ["k"],
        Opcode.JAL: ["rd", "k"],
        Opcode.JR: ["rs1"],
        Opcode.BLEU: ["rs1", "rs2", "k"],
        Opcode.BLE: ["rs1", "rs2", "k"],
        Opcode.BGT: ["rs1", "rs2", "k"],
        Opcode.BGTU: ["rs1", "rs2", "k"],
        Opcode.BNE: ["rs1", "rs2", "k"],
        Opcode.BEQ: ["rs1", "rs2", "k"],
        Opcode.HALT: []
    }

    for field in field_mapping.get(opcode, []):
        instruction[field] = fields[field]

    return instruction


def from_bytes(input_file_name: str) -> list:
    code = []
    with open(input_file_name, "rb") as f:
        while True:
            bytes_data = f.read(4)
            if len(bytes_data) != 4:
                break

            word = int.from_bytes(bytes_data, "big")
            fields = _parse_instruction_word(word)
            fields.update({
                "rd": _get_register(fields["rd_bin"]),
                "rs1": _get_register(fields["rs1_bin"]),
                "rs2": _get_register(fields["rs2_bin"])
            })

            instruction = _build_instruction(fields)
            if instruction["opcode"] is not None:
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
