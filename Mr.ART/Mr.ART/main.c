#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>

#define MAX_SHELLCODE_SIZE 1024

__attribute__((constructor))
void __constructor__(){
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
}

int main() {
    unsigned char shellcode[MAX_SHELLCODE_SIZE];
    int len = 0;
    int c;
    
    puts("Welcome to the no-syscall shellcode challenge!");
    puts("Send me your shellcode (syscalls are forbidden):");
    
    // Read shellcode byte by byte, stop at newline
    while (len < MAX_SHELLCODE_SIZE) {
        c = getchar();
        if (c == EOF || c == '\n') break;
        shellcode[len++] = (unsigned char)c;
    }
    
    printf("Received %d bytes\n", len);
    
    // Check for valid input
    if (len == 0) {
        puts("No shellcode received!");
        return 1;
    }
    
    // Check for syscall instruction (0x0f 0x05)
    for (int i = 0; i < len - 1; i++) {
        if (shellcode[i] == 0x0f && shellcode[i + 1] == 0x05) {
            puts("Syscall detected! Execution blocked.");
            return 1;
        }
    }
    
    // Allocate executable memory
    void *exec_mem = mmap(NULL, MAX_SHELLCODE_SIZE, 
                          PROT_READ | PROT_WRITE | PROT_EXEC,
                          MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    
    if (exec_mem == MAP_FAILED) {
        puts("Memory allocation failed!");
        return 1;
    }
    
    // Copy shellcode to executable memory
    memcpy(exec_mem, shellcode, len);
    
    puts("Executing shellcode...");
    
    // Execute shellcode
    ((void(*)())exec_mem)();
    
    // Cleanup (may not reach here if shellcode exits)
    munmap(exec_mem, MAX_SHELLCODE_SIZE);
    
    return 0;
}
