import re
import sys

from isa import reg_to_binary, opcode_to_binary, Opcode, Register, to_bytes


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
        return True
    except Exception:
        return False


def parse_data_word(to_parse: str):
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
            raise ValueError("Кривые байтики")
    return list(res)


def parse_data_byte(to_parse: str):
    args = to_parse.strip().replace(",", " ").split()
    res = bytearray()
    for arg in args:
        if is_digit(arg):
            res.extend(int(arg, 0).to_bytes(1, "little"))
        elif arg[0] == "'" and arg[-1] == "'" and arg.count("'") == 2:
            arg = arg[1:-1].encode("ascii")
            res.extend(arg)
        else:
            raise ValueError("Кривые байтики")
    return list(res)


def first_run(lines):
    global data_labels, text_labels, macros
    state = 0
    current_data_address = 0
    current_text_address = 4
    data_dump = {}
    text_dump = {}
    for line in lines:
        line = re.sub(r";.*$", "", line).strip()
        if line == "" or line is None:
            continue
        elif line.startswith(".macros") and state == 0:
            line = line.replace(".macros", "").strip().split()
            if len(line) != 2:
                raise Exception("invalid macro definition")
            macros[line[0]] = line[1]
        elif line.startswith(".data") and state != 1:
            state = 1
        elif line.startswith(".text") and state != 2:
            state = 2
        elif line.startswith(".org") and state == 1:
            line = line.replace(".org", "").strip().split()
            if len(line) != 1:
                raise Exception("invalid org definition")
            current_data_address = int(line[0], 0)
        elif line.startswith(".org") and state == 2:
            pass
        elif ":" in line:
            line = line.split(":")
            if state == 1:
                data_labels[line[0].strip()] = current_data_address
                if line[1] != "":
                    if line[1].strip().startswith(".byte"):
                        line = line[1].replace(".byte", "").strip()
                        res = parse_data_byte(line)
                    elif line[1].strip().startswith(".word"):
                        line = line[1].replace(".word", "").strip()
                        res = parse_data_word(line)
                    else:
                        raise Exception(f"Что такое: {line[1]}")
                    for b in res:
                        data_dump[current_data_address] = b
                        current_data_address += 1
            elif state == 2:
                text_labels[line[0].strip()] = current_text_address
                if line[1] != "":
                    text_dump[current_text_address] = line[1].strip()
                    current_text_address += 4
        else:
            if state == 1:
                if line.strip().startswith(".byte"):
                    line = line.replace(".byte", "").strip()
                    res = parse_data_byte(line)
                elif line.strip().startswith(".word"):
                    line = line.replace(".word", "").strip()
                    res = parse_data_word(line)
                else:
                    raise Exception(f"Что такое: {line}")
                for b in res:
                    data_dump[current_data_address] = b
                    current_data_address += 1
            if state == 2:
                text_dump[current_text_address] = line.strip()
                current_text_address += 4
    return data_dump, text_dump


def second_run(text_dump):  # подставляем лейблы и макросы
    for key, val in text_dump.items():
        for label in text_labels.keys():
            if label in val:
                text_dump[key] = text_dump[key].replace(label, str(text_labels[label] - key - 4))
        for label in data_labels.keys():
            if label in val:
                text_dump[key] = text_dump[key].replace(label, str(data_labels[label]))
        for label in macros.keys():
            if label in val:
                text_dump[key] = text_dump[key].replace(label, str(macros[label]))
    return text_dump


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


def fourth_run(text_dump):
    res = {}
    for key, val in text_dump.items():
        parts = val.replace(",", " ").split()
        opcode_bin = 0
        rd = 0
        rs1 = 0
        rs2 = 0
        k = 0
        if parts[0] in ["lui", "jal"]:
            opcode_bin = opcode_to_binary.get("lui")
            rd = reg_to_binary.get(parts[1])
            k = int(parts[2], 0)
        elif parts[0] == "mv":
            opcode_bin = opcode_to_binary.get("mv")
            rd = reg_to_binary.get(parts[1])
            rs1 = reg_to_binary.get(parts[2])
        elif parts[0] == "sw":
            opcode_bin = opcode_to_binary.get("sw")
            rs2 = reg_to_binary.get(parts[1])
            dop = parts[2].replace("(", " ").split()
            rs1 = reg_to_binary.get(dop[1][:-1])
            k = int(dop[0], 0)
        elif parts[0] == "lw":
            opcode_bin = opcode_to_binary.get("lw")
            rd = reg_to_binary.get(parts[1])
            dop = parts[2].replace("(", " ").split()
            rs1 = reg_to_binary.get(dop[1][:-1])
            k = int(dop[0], 0)
        elif parts[0] == "addi":
            opcode_bin = opcode_to_binary.get("addi")
            rd = reg_to_binary.get(parts[1])
            rs1 = reg_to_binary.get(parts[2])
            k = int(parts[3], 0)
        elif parts[0] in ["add", "sub", "mul", "mulh", "div", "rem", "sll", "srl", "sra", "and", "or", "xor"]:
            opcode_bin = opcode_to_binary.get(parts[0])
            rd = reg_to_binary.get(parts[1])
            rs1 = reg_to_binary.get(parts[2])
            rs2 = reg_to_binary.get(parts[3])
        elif parts[0] == "j":
            opcode_bin = opcode_to_binary.get("j")
            k = int(parts[1], 0)
        elif parts[0] == "jr":
            opcode_bin = opcode_to_binary.get("jr")
            rs1 = reg_to_binary.get(parts[1])
        elif parts[0] in ["bgt", "bgtu", "le", "leu", "beq", "bne"]:
            opcode_bin = opcode_to_binary.get(parts[0])
            rs1 = reg_to_binary.get(parts[1])
            rs2 = reg_to_binary.get(parts[2])
            k = int(parts[3], 0)
        elif parts[0] == "halt":
            opcode_bin = opcode_to_binary.get("halt")
        else:
            raise Exception(f"Неизвестный опкод: {parts[0]}")
        assert rd != 8, "нельзя записывать в zero!"
        assert all(d is not None for d in [opcode_bin, rd, rs1, rs2, k]), f"что-то криво емое {val}"
        res[key] = (opcode_bin << 3) | (rd & 7)
        res[key + 1] = (rs1 << 4) | (rs2 & 0xF)
        res[key + 2] = (k >> 8) & 0xFF
        res[key + 3] = k & 0xFF
    return res


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Использование: python translator.py <input.asm> <code.bin> <data.bin>")
        sys.exit(1)
    with open(sys.argv[1], "r") as f:
        lines = f.readlines()
    first_run(lines)
    data_dump, text_dump = first_run(lines)
    text_dump = second_run(text_dump)
    text_dump = third_run(text_dump)
    text_dump[0] = f"j {text_labels['_start'] - 4}"
    text_dump = fourth_run(text_dump)
    with open(sys.argv[2], "wb+") as f:
        for i in range(max(text_dump.keys()) + 1):
            if i in text_dump.keys():
                f.write(text_dump[i].to_bytes(1, byteorder="little"))
            else:
                f.write(int.to_bytes(0, 1, byteorder="little"))
    with open(sys.argv[3], "wb+") as f:
        for i in range(max(data_dump.keys()) + 1):
            if i in data_dump.keys():
                f.write(data_dump[i].to_bytes(1, byteorder="little"))
            else:
                f.write(int.to_bytes(0, 1, byteorder="little"))
