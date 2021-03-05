BITS 64 

section .text 

global _start

_start : 
   jmp _far   

main : 
    mov edi, 0x1000
    mov esi, 0x1000
    mov edx, 0x7 
    mov eax, 0x9
    mov r10, 0x22 ;;
    xor r8, r8
    xor r9, r9 
    syscall 

    mov rcx, shellcode_len 
    mov edi, eax 

    pop esi 
  copy : 
    mov al, byte [esi]
    mov byte [edi], al 
    inc edi 
    inc esi 
    loop copy 

    mov eax, 0x10000
    jmp eax

_far: 
    call main 
    shellcode db shellcode_obf_ver2
    shellcode_len equ $-shellcode

; nasm -f bin -o mmap_hello.bin mmap.s

; nasm -f elf64 server.asm
; ld -s server.o -o server