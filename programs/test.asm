.macros SP_INIT 1000
.data
input_addr: .word 0x80
output_addr: .word 0x84
max_num_elements: .word 50
.org 136
array: .word 0
.text
_start:
    lui r0, %hi(input_addr)
    addi r0, r0, %lo(input_addr)
    lw r0, 0(r0)                        ; r0 - input_addr

    lui r1, %hi(array)
    addi r1, r1, %lo(array)             ; r1 - array pointer, r2, r3 - числа для сравнения, r4 - i, r6 - j

    lui r6, %hi(max_num_elements)
    addi r6, r6, %lo(max_num_elements)
    lw r6, 0(r6)                        ; r6 - максимальное число элементов

    addi r5, zero, 0                    ; r5 - количество элементов

    read_data:
        beq r5, r6, emergency_exit
        lw r2, 0(r0)
        beq r2, zero, read_data_exit
        sw r2, 0(r1)
        addi r1, r1, 4
        addi r5, r5, 1
        j read_data
    read_data_exit:
        addi r4, zero, 1
        sort_loop:
            beq r4, r5, output_array
            bgt r4, r5, output_array
            sub r6, r5, r4
            mv r0, zero
            lui r1, %hi(array)
            addi r1, r1, %lo(array)
            sort_inner_loop:
                beq r0, r6, sort_inner_exit
                lw r2, 0(r1)
                lw r3, 4(r1)
                ble r2, r3, do_nothing
                sw r3, 0(r1)
                sw r2, 4(r1)
                do_nothing:
                    addi r1, r1, 4
                    addi r0, r0, 1
                    j sort_inner_loop
            sort_inner_exit:
                addi r4, r4, 1
                j sort_loop



    output_array:
        mv r4, zero
        lui r1, %hi(array)
        addi r1, r1, %lo(array)
        lui r0, %hi(output_addr)
        addi r0, r0, %lo(output_addr)
        lw r0, 0(r0)
        output_array_while:
            beq r4, r5, exit
            lw r2, 0(r1)
            sw r2, 0(r0)
            addi r1, r1, 4
            addi r4, r4, 1
            j output_array_while

    emergency_exit:
        lui r2, %hi(0xCCCCCCCC)
        addi r2, r2, %lo(0xCCCCCCCC)
        sw r2, 0(r1)
    exit:
        halt