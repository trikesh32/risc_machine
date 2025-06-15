.data
    input_addr: .word 0x80
    output_addr: .word 0x84
    greeting: .byte 'What is your name?',0
    .text
    _start:
        lui r0, %hi(output_addr)
        addi r0, r0, %lo(output_addr)
        lw r0, 0(r0) ; r0 - указатель на вывод
        lui r1, %hi(string)
        addi r1, r1, %lo(string) ; r1 - указатель на нынешний элемент строки
        addi r3, zero, 0xFF ; маска для выделения младшего байта
        lw r2, 0(r1)
        and r2, r2, r3
        while:
            beq r2, zero, end
            sw r2, 0(r0)
            addi r1, r1, 1
            lw r2, 0(r1)
            and r2, r2, r3
            j while
        end:
            halt
