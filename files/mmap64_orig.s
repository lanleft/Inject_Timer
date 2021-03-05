BITS 64 

section .text 

global _start

_start : 
   jmp _far   

main : 
    mov rdi, 0x1000
    mov rsi, 0x1000
    mov rdx, 0x7 
    mov rax, 0x9
    mov r10, 0x22
    xor r8, r8
    xor r9, r9 
    syscall 

    mov rcx, shellcode_len 
    mov rdi, rax 

    pop rsi 
  copy : 
    mov al, byte [rsi]
    mov byte [rdi], al 
    inc rdi 
    inc rsi 
    loop copy 

    mov rax, 0x10000
    jmp rax

_far: 
    call main 
    shellcode db shellcode_obf_ver2
    shellcode_len equ $-shellcode

; nasm -f bin -o mmap_hello.bin mmap.s

; nasm -f elf64 server.asm
; ld -s server.o -o server