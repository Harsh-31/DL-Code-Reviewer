# Verilog / SystemVerilog Review Guidelines

## Blocking vs Non-Blocking Assignments
- Use non-blocking (`<=`) in `always @(posedge clk)` sequential blocks
- Use blocking (`=`) in `always @(*)` combinational blocks
- NEVER mix blocking and non-blocking in the same always block

## Reset Logic
- Prefer synchronous resets for FPGA targets
- Prefer asynchronous resets (`always @(posedge clk or posedge rst)`) for ASIC
- Every register must have a defined reset value

## Sensitivity Lists
- Always use `@(*)` for combinational logic — never enumerate manually
- Missing signals in sensitivity list causes simulation/synthesis mismatches

## Common Pitfalls
- Inferred latches from incomplete `if`/`case` statements (always have a default)
- Integer overflow in arithmetic — check bit widths explicitly
- Undriven outputs (x/z propagation in simulation)
- Clock domain crossing without proper synchronizers
- Signed vs unsigned comparison errors

## Naming Conventions
- Inputs: no prefix or `i_`
- Outputs: `o_`
- Registers: `_r` suffix
- Parameters: ALL_CAPS

## Synthesis Concerns
- `initial` blocks are not synthesizable (simulation only)
- `#delays` are not synthesizable
- `$display` and tasks are simulation-only
