import re
import sys

from isa import opcode_to_binary, reg_to_binary


class InvalidDataFormatError(ValueError):
    def __init__(self):
        super().__init__("Некорректный формат данных")


class InvalidMacroDefinitionError(ValueError):
    def __init__(self):
        super().__init__("Плохое определение макроса")


class InvalidOrgDefinitionError(ValueError):
    def __init__(self):
        super().__init__("Плохое определение .org")


class UnknownInstructionError(ValueError):
    def __init__(self, val):
        super().__init__(f"Что такое: {val}")


class ZeroWriteError(ValueError):
    def __init__(self):
        super().__init__("Нельзя писать в zero!")


def hi(number):
    return (int(number, 0) >> 16) & 0xFFFF


def lo(number):
    return int(number, 0) & 0xFFFF


# state 0 - до сегментов, 1 - сегмент данных, 2 - сегмент текста
data_labels = {}
text_labels = {}
macros = {}


def is_digit(string):
    try:
        int(string, 0)
    except ValueError:
        return False
    else:
        return True


def parse_data_word(to_parse):
    args = to_parse.strip().replace(",", " ").split()
    res = bytearray()
    for arg in args:
        if is_digit(arg):
            res.extend(int(arg, 0).to_bytes(4, "little"))
        elif arg[0] == "'" and arg[-1] == "'" and arg.count("'") == 2:
            arg = arg[1:-1]
            for el in arg:
                res.extend(ord(el).to_bytes(4, "little"))
        else:
            raise InvalidDataFormatError()
    return list(res)


def parse_data_byte(to_parse):
    res = bytearray()
    args = re.findall(r"'[^']*'|[^\s,]+", to_parse.strip().replace(",", " "))
    for arg in args:
        if arg[0] == "'" and arg[-1] == "'" and arg.count("'") == 2:
            arg = arg[1:-1].encode("ascii")
            res.extend(arg)
        elif is_digit(arg):
            res.extend(int(arg, 0).to_bytes(1, "little"))
        else:
            raise InvalidDataFormatError()

    return list(res)


def _process_macro_definition(line):
    parts = line.replace(".macros", "").strip().split()
    if len(parts) != 2:
        raise InvalidMacroDefinitionError()
    macros[parts[0]] = parts[1]


def _process_org_definition(line):
    parts = line.replace(".org", "").strip().split()
    if len(parts) != 1:
        raise InvalidOrgDefinitionError()
    return int(parts[0], 0)


def _process_data_label(line_parts, data_dump, current_addr):
    label, content = line_parts[0].strip(), ":".join(line_parts[1:]).strip()
    data_labels[label] = current_addr
    if content:
        return _process_data_content(content, data_dump, current_addr)
    return current_addr


def _process_text_label(line_parts, text_dump, current_addr):
    label, content = line_parts[0].strip(), ":".join(line_parts[1:]).strip()
    text_labels[label] = current_addr
    if content:
        text_dump[current_addr] = content.strip()
        return current_addr + 4
    return current_addr


def _process_data_content(line, data_dump, current_addr):
    if line.strip().startswith(".byte"):
        data = parse_data_byte(line.replace(".byte", "").strip())
    elif line.strip().startswith(".word"):
        data = parse_data_word(line.replace(".word", "").strip())
    else:
        raise UnknownInstructionError(line)

    for byte in data:
        data_dump[current_addr] = byte
        current_addr += 1
    return current_addr


def _process_label_string(line, data_dump, text_dump, current_text_address, current_data_address, state):
    line_parts = line.split(":")
    if state == 1:
        current_data_address = _process_data_label(line_parts, data_dump, current_data_address)
    elif state == 2:
        current_text_address = _process_text_label(line_parts, text_dump, current_text_address)
    return current_data_address, current_text_address


def _process_first_run_end(state, current_data_address, current_text_address, text_dump, line, data_dump):
    if state == 1:
        current_data_address = _process_data_content(line, data_dump, current_data_address)
    elif state == 2:
        text_dump[current_text_address] = line.strip()
        current_text_address += 4
    return current_data_address, current_text_address, text_dump, line


def _process_directive(line, state, current_data_address):
    res = False
    if line.startswith(".macros") and state == 0:
        _process_macro_definition(line)
        res = True
    if line.startswith(".data") and state != 1:
        state = 1
        res = True
    if line.startswith(".text") and state != 2:
        state = 2
        res = True
    if line.startswith(".org"):
        if state == 1:
            current_data_address = _process_org_definition(line)
        res = True
    return res, state, current_data_address


def first_run(lines):
    global data_labels, text_labels, macros

    state = 0
    current_data_address = 0
    current_text_address = 4
    data_dump = {}
    text_dump = {}

    for line in lines:
        line = re.sub(r";.*$", "", line).strip()
        if not line:
            continue
        res, state, current_data_address = _process_directive(line, state, current_data_address)
        if res:
            continue
        if ":" in line:
            current_data_address, current_text_address = _process_label_string(
                line, data_dump, text_dump, current_text_address, current_data_address, state
            )
            continue
        current_data_address, current_text_address, text_dump, line = _process_first_run_end(
            state, current_data_address, current_text_address, text_dump, line, data_dump
        )
    return data_dump, text_dump


def _replace_labels(text, labels, offset=0):
    sorted_labels = sorted(labels.items(), key=lambda x: len(x[0]), reverse=True)
    for label, address in sorted_labels:
        pattern = r"\b" + re.escape(label) + r"\b"
        text = re.sub(pattern, str(address + offset), text)
    return text


def _replace_macros(text):
    for macro, value in macros.items():
        if macro in text:
            text = text.replace(macro, str(value))
    return text


def second_run(text_dump):
    processed_dump = {}
    for address, instruction in text_dump.items():
        instruction = _replace_labels(instruction, text_labels, -address - 4)
        instruction = _replace_labels(instruction, data_labels)
        instruction = _replace_macros(instruction)
        processed_dump[address] = instruction
    return processed_dump


def third_run(text_dump):  # обрабатываем %hi и %lo
    for key, val in text_dump.items():
        if "%hi" in val:
            matches_full = re.findall(r"%hi\(.+\)", val)
            for match in matches_full:
                num = int(match[4:-1], 0)
                if num & 0x8000:
                    num += 0x00010000
                val = val.replace(match, str((num >> 16) & 0xFFFF))
            text_dump[key] = val
        if "%lo" in val:
            matches_full = re.findall(r"%lo\(.+\)", val)
            for match in matches_full:
                num = int(match[4:-1], 0)
                num &= 0xFFFF
                val = val.replace(match, str(num))
            text_dump[key] = val
    return text_dump


def _parse_instruction(parts):
    opcode = parts[0]
    operands = parts[1:]
    return opcode, operands


def _process_lui_jal(opcode, operands, reg_to_binary, opcode_to_binary):
    rd = reg_to_binary.get(operands[0], 0)
    k = int(operands[1], 0)
    return opcode_to_binary.get(opcode, 0), rd, 0, 0, k


def _process_mv(opcode, operands, reg_to_binary, opcode_to_binary):
    rd = reg_to_binary.get(operands[0], 0)
    rs1 = reg_to_binary.get(operands[1], 0)
    return opcode_to_binary.get(opcode, 0), rd, rs1, 0, 0


def _process_sw_lw(opcode, operands, reg_to_binary, opcode_to_binary):
    rs2_or_rd = reg_to_binary.get(operands[0], 0)
    dop = operands[1].replace("(", " ").split()
    rs1 = reg_to_binary.get(dop[1][:-1], 0)
    k = int(dop[0], 0)
    rd = rs2_or_rd if opcode == "lw" else 0
    rs2 = rs2_or_rd if opcode == "sw" else 0
    return opcode_to_binary.get(opcode, 0), rd, rs1, rs2, k


def _process_addi(opcode, operands, reg_to_binary, opcode_to_binary):
    rd = reg_to_binary.get(operands[0], 0)
    rs1 = reg_to_binary.get(operands[1], 0)
    k = int(operands[2], 0)
    return opcode_to_binary.get(opcode, 0), rd, rs1, 0, k


def _process_arithmetic(opcode, operands, reg_to_binary, opcode_to_binary):
    rd = reg_to_binary.get(operands[0], 0)
    rs1 = reg_to_binary.get(operands[1], 0)
    rs2 = reg_to_binary.get(operands[2], 0)
    return opcode_to_binary.get(opcode, 0), rd, rs1, rs2, 0


def _process_j(opcode, operands, reg_to_binary, opcode_to_binary):
    k = int(operands[0], 0)
    return opcode_to_binary.get(opcode, 0), 0, 0, 0, k


def _process_jr(opcode, operands, reg_to_binary, opcode_to_binary):
    rs1 = reg_to_binary.get(operands[0], 0)
    return opcode_to_binary.get(opcode, 0), 0, rs1, 0, 0


def _process_branch(opcode, operands, reg_to_binary, opcode_to_binary):
    rs1 = reg_to_binary.get(operands[0], 0)
    rs2 = reg_to_binary.get(operands[1], 0)
    k = int(operands[2], 0)
    return opcode_to_binary.get(opcode, 0), 0, rs1, rs2, k


def _process_halt(opcode, operands, reg_to_binary, opcode_to_binary):
    return opcode_to_binary.get(opcode, 0), 0, 0, 0, 0


def _encode_instruction(opcode_bin, rd, rs1, rs2, k, key):
    result = {}
    result[key] = (opcode_bin << 3) | (rd & 7)
    result[key + 1] = (rs1 << 4) | (rs2 & 0xF)
    result[key + 2] = (k >> 8) & 0xFF
    result[key + 3] = k & 0xFF
    return result


def fourth_run(text_dump):
    result = {}
    instruction_handlers = {
        "lui": _process_lui_jal,
        "jal": _process_lui_jal,
        "mv": _process_mv,
        "sw": _process_sw_lw,
        "lw": _process_sw_lw,
        "addi": _process_addi,
        "add": _process_arithmetic,
        "sub": _process_arithmetic,
        "mul": _process_arithmetic,
        "mulh": _process_arithmetic,
        "div": _process_arithmetic,
        "rem": _process_arithmetic,
        "sll": _process_arithmetic,
        "srl": _process_arithmetic,
        "sra": _process_arithmetic,
        "and": _process_arithmetic,
        "or": _process_arithmetic,
        "xor": _process_arithmetic,
        "j": _process_j,
        "jr": _process_jr,
        "bgt": _process_branch,
        "bgtu": _process_branch,
        "ble": _process_branch,
        "bleu": _process_branch,
        "beq": _process_branch,
        "bne": _process_branch,
        "halt": _process_halt,
    }

    for key, value in text_dump.items():
        parts = value.replace(",", " ").split()
        opcode, operands = _parse_instruction(parts)

        handler = instruction_handlers.get(opcode)
        if handler is None:
            raise UnknownInstructionError(opcode)

        opcode_bin, rd, rs1, rs2, k = handler(opcode, operands, reg_to_binary, opcode_to_binary)

        if rd == 8:
            raise ZeroWriteError()
        if any(d is None for d in [opcode_bin, rd, rs1, rs2, k]):
            raise UnknownInstructionError(value)

        result.update(_encode_instruction(opcode_bin, rd, rs1, rs2, k, key))

    return result


def main(input_filename, code_filename, data_filename):
    with open(input_filename) as f:
        lines = f.readlines()
    data_dump, text_dump = first_run(lines)
    text_dump = second_run(text_dump)
    text_dump = third_run(text_dump)
    text_dump[0] = f"j {text_labels['_start'] - 4}"
    text_dump = fourth_run(text_dump)
    with open(code_filename, "wb+") as f:
        for i in range(max(text_dump.keys()) + 1):
            if i in text_dump.keys():
                f.write(text_dump[i].to_bytes(1, byteorder="little"))
            else:
                f.write(int.to_bytes(0, 1, byteorder="little"))
    with open(data_filename, "wb+") as f:
        for i in range(max(data_dump.keys()) + 1):
            if i in data_dump.keys():
                f.write(data_dump[i].to_bytes(1, byteorder="little"))
            else:
                f.write(int.to_bytes(0, 1, byteorder="little"))
    print("Success")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Использование: python translator.py <input.asm> <code.bin> <data.bin>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
