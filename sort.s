@ Insertion sort implementation in ARM assembly
@ KPLKEL001 & STNJOS005
@------------------------------------------
@ Registers:
@   r7      - save step
@   r6      - counter
@   r4      - base address of array
@   r0      - load input, ouutput

.text
.global main
main:
    ldr         r7, =return         @ save location
    str         lr, [r7]            @ link register stores return address
    mov         r6, #0              @ count in r6
    ldr         r4, =array          @ r4 points to array base

input:
    ldr         r0, =input_prompt   @ load input prompt
    bl          puts                @ syscall

    ldr         r0, =input_scan     @ r0 takes input
    ldr         r1, =input_number   @ get number
    bl          scanf               @ syscall

    ldr         r1, =input_number
    ldr         r1, [r1]
    cmp         r1, #0              @ check if negative
    blt         sort

    add         r0, r4, r6, LSL #2  @ move to next index of array
    str         r1, [r0]            @ set array[4*count] = number
    add         r6, r6, #1          @ increase counter
    
    b input

sort:
    mov         r0, r4              @ r4 points to base of array
    mov         r1, r6              @ r1 = count
    mov         r2, #1              @ i = 1

@@@@@@@@@@@@@ Outer i loop @@@@@@@@@@@@@@@@
iloop:
    cmp         r2, r1
    bge         iloopend            @ i >= n
    add         r10, r0, r2, LSL #2 @ move to next array index
    ldr         r10, [r10]
    sub         r3, r2, #1          @j = i-1
    
@@@@@@@@@@@@@ Inner j loop @@@@@@@@@@@@@@@@
    jloop:
        cmp         r3, #0          @ j >= 0?
        blt         jloopend
        add         r9, r0, r3, LSL #2  @ element at next index, put in r9
        ldr         r9, [r9]
        cmp         r10, r9             @ if element is greater than current index
        bge         jloopend
        add         r8, r0, r3, LSL #2  @ get element at following index, put in r8
        add         r8, r8, #4
        str         r9, [r8]        @ swap elements
        sub         r3, r3, #1      @ decrement inner j loop
        b           jloop
    jloopend:
        add         r3, r3, #1       @ increase j by 1
        add         r8, r0, r3, LSL #2  @r8 is next element
        str         r10, [r8]
        add         r2, r2, #1      @ increment i
        b iloop

iloopend:
output:
    ldr         r0, =result_prompt
    bl          puts
    mov         r5, #0      @ new counter = n

ploop:
    cmp         r6, r5
    ble         exit
    add         r3, r4, r5, LSL #2      @ r3 = next index of array
    ldr         r1, [r3]
    ldr         r0, =print_format
    bl          printf
    add         r5, r5, #1      @ increment n
    b           ploop

@@@@@@@@@@@@@@@@@@ EXIT @@@@@@@@@@@@@@@@@@
exit:
    mov         r0, r6              @ r0 = r6 = return ode
    ldr         r1, =return         @ r1 = &return
    ldr         r1, [r1]            @ lr = *return (actual return value)
    bx          lr                  @ exit


@@@@@@@@@@@@@@@@@@ DATA @@@@@@@@@@@@@@@@@@
.data
input_number:   .word   0       @ hold input number
array:          .space  64      @ space for max of 16 ints
return:         .word   0       @ hold return address
input_prompt:   .asciz  "Input up to 16 ints. Enter a negative number to quit.: \n"
result_prompt:  .asciz  "The sorted result is: \n"
input_scan:     .asciz  "%d"
print_format:   .asciz  "%d\n"

/* External */
.global printf
.global scanf
.global puts
