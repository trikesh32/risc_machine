.data
input_addr: .word 0x80
output_addr: .word 0x84

.text
.org 0x20
_start:
addi r2, zero, 2
while:
beq r2, zero, end
addi r2, r2, -1
lui r0, %hi(input_addr)
addi r0, r0, %lo(input_addr)
lw r0, 0(r0)
lw r1, 0(r0)
addi r1, r1, 5
lui r0, %hi(output_addr)
addi r0, r0, %lo(output_addr)
lw r0, 0(r0)
sw r1, 0(r0)
j while
end:
halt