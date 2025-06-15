.macros SP_INIT 1000
.data
input_addr: .word 0x80
output_addr: .word 0x84

.text
add64: ; в r0 хранится адрес возврата!
    lw r1, 0(sp)
    lw r2, 8(sp)

    lw r4, 4(sp)
    lw r5, 12(sp)

    add r3, r1, r2
    add r6, r4, r5
    bgtu r3, r1, add64_do_nothing
    addi r6, r6, 1
    add64_do_nothing:
        sw r3, 16(sp)
        sw r6, 20(sp)
    jr r0

sub64:
    lw r1, 0(sp)    ; arg1_lo
    lw r2, 8(sp)    ; arg2_lo
    lw r4, 4(sp)    ; arg1_hi
    lw r5, 12(sp)   ; arg2_hi

    sub r3, r1, r2  ; res_lo = arg1_lo - arg2_lo
    sub r6, r4, r5  ; res_hi = arg1_hi - arg2_hi (пока без заема)

    ; Проверяем заем (если arg1_lo < arg2_lo)
    bleu r2, r1, sub64_no_borrow
    addi r6, r6, -1 ; учитываем заем
sub64_no_borrow:
    sw r3, 16(sp)   ; сохраняем res_lo
    sw r6, 20(sp)   ; сохраняем res_hi
    jr r0


_start:
    addi sp, zero, SP_INIT ; как там его, инициализация степы
    addi sp, sp, -24 ; выделили место под 6 переменных по 4 байта
    lui r0, %hi(input_addr)
    addi r0, r0, %lo(input_addr)
    lw r0, 0(r0)

    lw r1, 0(r0)
    sw r1, 4(sp)

    lw r1, 0(r0)
    sw r1, 0(sp)

    lw r1, 0(r0)
    sw r1, 12(sp)

    lw r1, 0(r0)
    sw r1, 8(sp)

    jal r0, sub64 ; интересующая функция

    lui r0, %hi(output_addr)
    addi r0, r0, %lo(output_addr)
    lw r0, 0(r0)

    lw r1, 20(sp)
    sw r1, 0(r0)

    lw r1, 16(sp)
    sw r1, 0(r0)
    halt
