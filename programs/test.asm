.macros SP_INIT 1000
.data
input_addr: .word 0x80
output_addr: .word 0x84

.text
check_palindromic: ; в r6 адрес возврата!!
    lw r0, 0(sp)
    mv r1, zero
    addi r2, zero, 10
    while:
        beq r0, zero, while_end
        mul r1, r1, r2
        rem r3, r0, r2
        add r1, r1, r3
        div r0, r0, r2
        j while
    while_end:
        lw r0, 0(sp)
        beq r0, r1, palindromic
        addi r0, zero, 1
        sw r0, 0(sp)
        jr r6
    palindromic:
        sw zero, 0(sp)
        jr r6

_start:
    addi sp, zero, SP_INIT
    addi r3, zero, 99
    addi r1, zero, 999
    mv r5, zero
    loop:
        beq r1, r3, goal
        add r2, zero, r1
        mul r2, r2, r1
        ble r2, r5, goal
        add r2, zero, r1
        inner_loop:
            ble r2, r3, inner_loop_end
            mul r4, r1, r2

            addi sp, sp, -16
            sw r1, 12(sp)
            sw r2, 8(sp)
            sw r3, 4(sp)
            mv r0, r4
            sw r0, 0(sp)
            jal r6, check_palindromic
            lw r0, 0(sp)
            lw r3, 4(sp)
            lw r2, 8(sp)
            lw r1, 12(sp)
            addi sp, sp, 16

            bne r0, zero, non_pal
            ble r4, r5, non_pal
            mv r5, r4
            mv r3, r2
            non_pal:
                addi r2, r2, -1
                j inner_loop
        inner_loop_end:
            addi r1, r1, -1
            j loop
    goal:
        lui r0, %hi(output_addr)
        addi r0, r0, %lo(output_addr)
        lw r0, 0(r0)
        sw r5, 0(r0)
    halt

