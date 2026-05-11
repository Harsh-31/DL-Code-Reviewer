# VHDL Review Guidelines

## Process Sensitivity Lists
- All signals read in a combinational process must be in the sensitivity list
- Use `process(all)` (VHDL-2008) for combinational logic

## Signal vs Variable
- Signals update at end of delta cycle; variables update immediately
- Avoid variables in synthesizable code unless intentional

## Reset
- Be explicit: synchronous (`if rising_edge(clk) then if rst = '1'`) or async
- All registers must have a reset condition

## Common Issues
- Incomplete sensitivity lists causing simulation/synthesis mismatch
- Unresolved signals from multiple drivers
- `std_logic` vs `std_ulogic` misuse
- Inferred latches from incomplete if/case statements
