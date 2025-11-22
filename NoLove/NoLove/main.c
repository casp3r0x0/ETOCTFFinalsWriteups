#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>

#define MAX_SHELLCODE_SIZE 11

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
    
    puts("Welcome to the NO Love.....");
    puts("Send me your shellcode (max 11 bytes):");
    
    // Read shellcode byte by byte, stop at newline or when we exceed 12 bytes
    while (len < MAX_SHELLCODE_SIZE) {
        c = getchar();
        if (c == EOF || c == '\n') break;
        shellcode[len++] = (unsigned char)c;
        
        // Stop early if we already exceeded 12 bytes
        if (len > 11) break;
    }
    
    printf("Received %d bytes\n", len);
    
    // Check if shellcode exceeds 12 bytes
    if (len > 11) {
        puts("Shellcode too long! Maximum 11 bytes allowed.");
        return 1;
    }
    
    // Check for valid input
    if (len == 0) {
        puts("No shellcode received!");
        return 1;
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
