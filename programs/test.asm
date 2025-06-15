    .data
    input_addr: .word 0x80
    output_addr: .word 0x84
    question: .byte 'What is your name?\nHello',44, 0
    after: .byte '!', 0
    .text
    _start:
    lui r0, %hi(output_addr)
    addi r0, r0, %lo(output_addr)
    lw r0, 0(r0) ; r0 - указатель на вывод
    lui r1, %hi(question)
    addi r1, r1, %lo(question) ; r1 - указатель на нынешний элемент строки
    addi r3, zero, 0xFF ; маска для выделения младшего байта
    lui r4, %hi(input_addr)
    addi r4, r4, %lo(input_addr)
    lw r4, 0(r4) ; в r4 input_addr
    lw r2, 0(r1)
    and r2, r2, r3
    while_question:
        beq r2, zero, input_action
        sw r2, 0(r0)
        addi r1, r1, 1
        lw r2, 0(r1)
        and r2, r2, r3
        j while_question
    input_action:
        lw r2, 0(r4)
        beq r2, zero, action_after
        sw r2, 0(r0)
        j input_action
    action_after:
        lui r1, %hi(after)
        addi r1, r1, %lo(after)
    after_action_loop:
        lw r2, 0(r1)
        addi r1, r1, 1
        and r2, r2, r3
        beq r2, zero, end
        sw r2, 0(r0)
        j after_action_loop
    end:
        sw r2, 0(r0)
        halt