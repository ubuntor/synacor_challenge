# Synacor Challenge Stuff
Interpreter: run [vm.py](vm.py) with `python3`.

Binary ninja plugin in [binja_plugin](binja_plugin).
(WIP: works, but lack of support for addresses that refer to something other
than 1 byte makes reasoning about addresses hard. Ghidra has `wordsize` which
fixes this.)

Ghidra processor in [ghidra_processor](ghidra_processor). (WIP)

## `vm.py` debug commands
- `debug regs` dumps regs.
- `debug stack` dumps stack.
- `debug toggle [opcode(s) ...]` toggles breaks on opcode(s).

## TODO for `vm.py`
- Breakpoints
- Disassembly (from eip or address)
- Ctrl-C to enter debug mode?
