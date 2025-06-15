import contextlib
import io
import logging
import os
import tempfile

import machine
import pytest
import translator

MAX_LOGS = 150000


@pytest.mark.golden_test("tests/*.yml")
def test_translator_asm_and_machine(golden, caplog):
    caplog.set_level(logging.DEBUG)
    with tempfile.TemporaryDirectory() as tmpdirname:
        source = os.path.join(tmpdirname, "source.asm")
        input_stream = os.path.join(tmpdirname, "input.txt")
        target = os.path.join(tmpdirname, "target.bin")
        target_data = os.path.join(tmpdirname, "target_data.bin")
        target_hex = os.path.join(tmpdirname, "target.bin.hex")
        input_fmt = golden["input_fmt"]
        with open(source, "w", encoding="utf-8") as file:
            file.write(golden.get("in_source"))
        with open(input_stream, "w", encoding="utf-8") as file:
            file.write(golden["in_stdin"])

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            translator.main(source, target, target_data)
            print("============================================================")
            machine.main(target, target_data, input_stream, input_fmt, target_hex)

        with open(target, "rb") as file:
            code = file.read()
        with open(target_data, "rb") as file:
            data = file.read()
        with open(target_hex, encoding="utf-8") as file:
            code_hex = file.read()

        assert code == golden.out["out_code"]
        assert data == golden.out["out_data"]
        assert code_hex == golden.out["out_code_hex"]
        assert stdout.getvalue() == golden.out["out_stdout"]
        assert caplog.text[0:MAX_LOGS] == golden.out["out_log"]
