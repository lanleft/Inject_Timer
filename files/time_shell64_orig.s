BITS 64

SECTION .text
global main

section .text

main:
    push rax         ; save all clobbered registers
    push rcx               
    push rdx
    push rsi
    push rdi
    push r11

    ; timer
    mov rdi, 0
    mov eax, 201
    syscall

    mov ebx, 0x6fbe52fa  ;; 10:12
    cmp eax, ebx
    ja exit 

parent:
    pop r11          ; restore all registers
    pop rdi
    pop rsi
    pop rdx
    pop rcx
    pop rax

    ; push 0x4010d0    ; jump to original entry point
    ret

exit:
    mov rax,1                ; sys_write
    mov rdi,1                ; stdout
    lea rsi,[rel $+defense-$]  ; defense
    mov rdx,23   ; len
    syscall
    
    mov     ebx,0    ; Exit code
    mov     eax,60   ; SYS_EXIT
    syscall

defense: db "Defensed by Nupakachi",33,10
len  : dd 23

;   nasm -f bin -o time_shell.bin time_shell.s