
.data ; aboba
input_addr: .word   0x80
output_addr: .word  0x84
word_size: .word    0x4
aboba: .byte 'aboba', 0, 25
word_aboba: .word 0xFFFFFFFF

.text
.org 0x88
_start:
    lui r0, %hi(0xFFFFFFFF)
    addi r0, r0, %lo(0xFFFFFFFF)
    lui  r0, %hi(input_addr)
    addi r0, r0, %lo(input_addr)
    lw  r0, 0(r0)
    lw  r0, 0(r0)   ; r0 - слово которое нужно развернуть

    lui r1, %hi(word_size)
    addi r1, r1, %lo(word_size)
    lw  r1, 0(r1)               ; загружеаем размер машинного слова (в байтах)

    addi r2, zero, 8    ; в r2 константа 8
    addi sp, zero, 1000 ; инициализировали стек
    sub sp, sp, r1      ; аллоцировали word_size байт в стеке
    add r4, sp, r1
    addi r4, r4, -1     ; создали в r4 указатель на актуальную ячейку для записи

    add r6, zero, r1    ; в r6 счетчик для цикла

    while:
        addi r6, r6, -1
        jal r5, write_byte
        j while

    end:
        lw r3, 0(sp)
        add sp, sp, r1 ; убираем ранее выделенные 4 байт в стеке

        lui r0, %hi(output_addr)
        addi    r0, r0, %lo(output_addr)
        lw  r0, 0(r0)
        sw  r3, 0(r0)
        halt

write_byte:
    addi r4, r4, -1 ; сдвинули на следующую ячейку для записи
    srl r0, r0, r2
    jr r5

; https://wrench.edu.swampbuds.me/result/f13aa624-c1b0-4516-ad40-ccb848babad7