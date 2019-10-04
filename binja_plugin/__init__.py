from binaryninja.architecture import Architecture
from binaryninja.function import RegisterInfo, InstructionInfo, InstructionTextToken
from binaryninja.enums import BranchType, InstructionTextTokenType
from binaryninja import interaction
import struct
import os

ARG = 0
REG = 1
CHAR = 2
ADDR = 3

# opcode, operands
opcodes = {
    0: ("halt", []),
    1: ("set", [REG, ARG]),
    2: ("push", [ARG]),
    3: ("pop", [REG]),
    4: ("eq", [REG, ARG, ARG]),
    5: ("gt", [REG, ARG, ARG]),
    6: ("jmp", [ADDR]),
    7: ("jt", [ARG, ADDR]),
    8: ("jf", [ARG, ADDR]),
    9: ("add", [REG, ARG, ARG]),
    10: ("mult", [REG, ARG, ARG]),
    11: ("mod", [REG, ARG, ARG]),
    12: ("and", [REG, ARG, ARG]),
    13: ("or", [REG, ARG, ARG]),
    14: ("not", [REG, ARG]),
    15: ("rmem", [REG, ADDR]),
    16: ("wmem", [ADDR, ARG]),
    17: ("call", [ADDR]),
    18: ("ret", []),
    19: ("out", [CHAR]),
    20: ("in", [REG]),
    21: ("nop", [])
}

# approach taken from
# https://github.com/jeffball55/ctf_writeups/blob/master/defcon_finals_2017/binja/clemency.py

RAW_DATA = None
FILENAME = None
def get_filename():
  global FILENAME
  if FILENAME == None:
    FILENAME = os.getenv("BINARY_NINJA_FILENAME")
    if FILENAME == None:
      FILENAME = interaction.get_open_filename_input("File to disassemble (please select it again)")
  return FILENAME

def read_data(addr, length):
    global RAW_DATA
    if RAW_DATA == None:
        RAW_DATA = open(get_filename(),"rb").read()
    return RAW_DATA[addr:addr+length]

class Synacor(Architecture):
    name = "Synacor Challenge"
    address_size = 2
    default_int_size = 2
    instr_alignment = 2
    max_instr_length = 8
    regs = {
        "r0": RegisterInfo("r0", 2),
        "r1": RegisterInfo("r1", 2),
        "r2": RegisterInfo("r2", 2),
        "r3": RegisterInfo("r3", 2),
        "r4": RegisterInfo("r4", 2),
        "r5": RegisterInfo("r5", 2),
        "r6": RegisterInfo("r6", 2),
        "r7": RegisterInfo("r7", 2),
        "sp": RegisterInfo("sp", 2)
    }
    stack_pointer = "sp"

    # instr, ops, length
    def decode_instruction(self, addr):
        data = read_data(addr*2, self.max_instr_length)
        if len(data) < 2:
            return None, None, None
        opcode = struct.unpack('<H', data[:2])[0]
        if opcode not in opcodes:
            return None, None, None
        instr, operand_types = opcodes[opcode]
        if len(data) < 2 + len(operand_types):
            return None, None, None
        operand_values = struct.unpack('<{}H'.format(len(operand_types)), data[2:2+2*len(operand_types)])
        operands = list(zip(operand_types, operand_values))
        return instr, operands, len(operands)+1

    def get_instruction_info(self, data, addr):
        instr, operands, length = self.decode_instruction(addr)
        if instr is None:
            return None
        result = InstructionInfo()
        result.length = length
        if instr == "jmp":
            target = operands[0][1]
            if target <= 32767:
                result.add_branch(BranchType.UnconditionalBranch, target)
            else:
                result.add_branch(BranchType.UnresolvedBranch)
        elif instr in {"jt", "jf"}:
            target = operands[1][1]
            if target <= 32767:
                result.add_branch(BranchType.TrueBranch, target)
            else:
                result.add_branch(BranchType.UnresolvedBranch)
            result.add_branch(BranchType.FalseBranch, addr+length)
        elif instr == "call":
            target = operands[0][1]
            if target <= 32767:
                result.add_branch(BranchType.CallDestination, target)
            else:
                result.add_branch(BranchType.UnresolvedBranch)
        elif instr == "ret":
            result.add_branch(BranchType.FunctionReturn)
        elif instr == "halt":
            result.add_branch(BranchType.UnresolvedBranch)
        return result

    def get_operand_text(self, operands):
        tokens = []
        for i, (op_type, val) in enumerate(operands):
            if i == 0:
                tokens.append(InstructionTextToken(InstructionTextTokenType.TextToken, " "))
            else:
                tokens.append(InstructionTextToken(InstructionTextTokenType.TextToken, ", "))
            if op_type == ARG:
                if val <= 32767:
                    tokens.append(InstructionTextToken(InstructionTextTokenType.IntegerToken, "0x{:04x}".format(val), val))
                elif 32768 <= val <= 32775:
                    tokens.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, "r{}".format(val-32768)))
                else:
                    tokens.append(InstructionTextTokenType.TextToken, "INVALID")
            elif op_type == REG:
                if 32768 <= val <= 32775:
                    tokens.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, "r{}".format(val-32768)))
                else:
                    tokens.append(InstructionTextTokenType.TextToken, "INVALID")
            elif op_type == CHAR:
                if val <= 32767:
                    tokens.append(InstructionTextToken(InstructionTextTokenType.TextToken, "'{}'".format(chr(val))))
                elif 32768 <= val <= 32775:
                    tokens.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, "r{}".format(val-32768)))
                else:
                    tokens.append(InstructionTextTokenType.TextToken, "INVALID")
            elif op_type == ADDR:
                if val <= 32767:
                    tokens.append(InstructionTextToken(InstructionTextTokenType.PossibleAddressToken, "0x{:04x}".format(val), val))
                elif 32768 <= val <= 32775:
                    tokens.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, "r{}".format(val-32768)))
                else:
                    tokens.append(InstructionTextTokenType.TextToken, "INVALID")
        return tokens

    def get_instruction_text(self, data, addr):
        instr, operands, length = self.decode_instruction(addr)
        if instr is None:
            return None
        tokens = []
        tokens.append(InstructionTextToken(InstructionTextTokenType.TextToken, instr))
        tokens.extend(self.get_operand_text(operands))
        return tokens, length

    def get_instruction_low_level_il(self, data, addr, il):
        return None

Synacor.register()
