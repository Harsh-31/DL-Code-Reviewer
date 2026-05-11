# Assembly Review Guidelines

## Safety
- Verify stack alignment (16-byte alignment required for x86-64 ABI before CALL)
- Check all registers are saved/restored per calling convention (callee-saved: rbx, rbp, r12-r15)
- Ensure no use of uninitialized registers

## Common Issues
- Off-by-one in loop counters
- Missing RET or incorrect return path
- Incorrect operand order (AT&T vs Intel syntax confusion)
- Signed vs unsigned comparison opcodes (JL vs JB, JG vs JA)
- Forgetting to zero-extend when moving 32-bit to 64-bit registers

## Performance
- Avoid unnecessary memory accesses — keep hot values in registers
- Prefer XOR reg,reg for zeroing over MOV reg,0
- Be aware of branch prediction costs on tight loops
