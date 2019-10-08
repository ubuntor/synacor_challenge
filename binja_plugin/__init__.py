from binaryninja import *
import struct
import os

ARG = 0
REG = 1
CHAR = 2
ADDR = 3

# opcode, operands
opcodes = {
    0: ("halt",  []),
    1: ("set",   [REG, ARG]),
    2: ("push",  [ARG]),
    3: ("pop",   [REG]),
    4: ("eq",    [REG, ARG, ARG]),
    5: ("gt",    [REG, ARG, ARG]),
    6: ("jmp",   [ADDR]),
    7: ("jt",    [ARG, ADDR]),
    8: ("jf",    [ARG, ADDR]),
    9: ("add",   [REG, ARG, ARG]),
    10: ("mult", [REG, ARG, ARG]),
    11: ("mod",  [REG, ARG, ARG]),
    12: ("and",  [REG, ARG, ARG]),
    13: ("or",   [REG, ARG, ARG]),
    14: ("not",  [REG, ARG]),
    15: ("rmem", [REG, ADDR]),
    16: ("wmem", [ADDR, ARG]),
    17: ("call", [ADDR]),
    18: ("ret",  []),
    19: ("out",  [CHAR]),
    20: ("in",   [REG]),
    21: ("nop",  [])
}

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
    intrinsics = {
        "out": IntrinsicInfo([Type.char()], []), # ???
        "in": IntrinsicInfo([], [Type.int(2)])
    }

    def is_literal(self, value):
        return value <= 32767

    def is_register(self, value):
        return 32768 <= value <= 32775

    # instr, ops, length
    def decode_instruction(self, data):
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
        return instr, operands, (len(operands)+1)*2

    def get_instruction_info(self, data, addr):
        instr, operands, length = self.decode_instruction(data)
        if instr is None:
            return None
        result = InstructionInfo()
        result.length = length
        if instr == "jmp":
            target = operands[0][1]
            if self.is_literal(target):
                result.add_branch(BranchType.UnconditionalBranch, 2*target)
            else:
                result.add_branch(BranchType.UnresolvedBranch)
        elif instr in {"jt", "jf"}:
            target = operands[1][1]
            if self.is_literal(target):
                result.add_branch(BranchType.TrueBranch, 2*target)
            else:
                result.add_branch(BranchType.UnresolvedBranch)
            result.add_branch(BranchType.FalseBranch, addr+length)
        elif instr == "call":
            target = operands[0][1]
            if self.is_literal(target):
                result.add_branch(BranchType.CallDestination, 2*target)
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
                if self.is_literal(val):
                    tokens.append(InstructionTextToken(InstructionTextTokenType.IntegerToken, "0x{:04x}".format(val), val))
                elif self.is_register(val):
                    tokens.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, "r{}".format(val-32768)))
                else:
                    tokens.append(InstructionTextTokenType.TextToken, "INVALID")
            elif op_type == REG:
                if self.is_register(val):
                    tokens.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, "r{}".format(val-32768)))
                else:
                    tokens.append(InstructionTextTokenType.TextToken, "INVALID")
            elif op_type == CHAR:
                if self.is_literal(val):
                    tokens.append(InstructionTextToken(InstructionTextTokenType.TextToken, repr(chr(val))))
                elif self.is_register(val):
                    tokens.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, "r{}".format(val-32768)))
                else:
                    tokens.append(InstructionTextTokenType.TextToken, "INVALID")
            elif op_type == ADDR:
                if self.is_literal(val):
                    tokens.append(InstructionTextToken(InstructionTextTokenType.PossibleAddressToken, "2*0x{:04x}".format(val), 2*val))
                elif self.is_register(val):
                    tokens.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, "2*r{}".format(val-32768)))
                else:
                    tokens.append(InstructionTextTokenType.TextToken, "INVALID")
        return tokens

    def get_instruction_text(self, data, addr):
        instr, operands, length = self.decode_instruction(data)
        if instr is None:
            return None
        tokens = []
        tokens.append(InstructionTextToken(InstructionTextTokenType.TextToken, instr))
        tokens.extend(self.get_operand_text(operands))
        return tokens, length

    def get_operand_il(self, il, operand):
        op_type, val = operand
        if op_type in {ARG, CHAR}:
            if self.is_literal(val):
                return il.const(2, val)
            elif self.is_register(val):
                return il.reg(2, "r{}".format(val-32768))
            else:
                return None
        elif op_type == ADDR:
            if self.is_literal(val):
                return il.const_pointer(2, val*2)
            elif self.is_register(val):
                return il.shift_left(2, il.reg(2, "r{}".format(val-32768)), il.const(2, 1))
            else:
                return None
        elif op_type == REG:
            if self.is_register(val):
                return "r{}".format(val-32768)
            else:
                return None

    def get_instruction_low_level_il(self, data, addr, il):
        instr, orig_operands, length = self.decode_instruction(data)
        if instr is None:
            return None
        operands = list(map(lambda x: self.get_operand_il(il, x), orig_operands))
        if None in operands:
            return None
        if instr == "halt":
            il.append(il.no_ret())
        elif instr == "set":
            il.append(il.set_reg(2, operands[0], operands[1]))
        elif instr == "push":
            il.append(il.push(2, operands[0]))
        elif instr == "pop":
            il.append(il.set_reg(2, operands[0], il.pop(2)))
        elif instr == "eq":
            il.append(il.set_reg(2, operands[0], il.compare_equal(2, operands[1], operands[2])))
        elif instr == "gt":
            il.append(il.set_reg(2, operands[0], il.compare_unsigned_greater_than(2, operands[1], operands[2])))
        elif instr == "jmp":
            il.append(il.jump(operands[0]))
        elif instr == "jt":
            true_branch = il.get_label_for_address(il.arch, il[operands[1]].constant)
            false_branch = il.get_label_for_address(il.arch, addr+length)
            il.append(il.if_expr(operands[0], true_branch, false_branch))
        elif instr == "jf":
            true_branch = il.get_label_for_address(il.arch, addr+length)
            false_branch = il.get_label_for_address(il.arch, il[operands[1]].constant)
            il.append(il.if_expr(operands[0], true_branch, false_branch))
        elif instr == "add":
            il.append(il.set_reg(2, operands[0], il.add(2, operands[1], operands[2])))
        elif instr == "mult":
            il.append(il.set_reg(2, operands[0], il.mult(2, operands[1], operands[2])))
        elif instr == "mod":
            il.append(il.set_reg(2, operands[0], il.mod_unsigned(2, operands[1], operands[2])))
        elif instr == "and":
            il.append(il.set_reg(2, operands[0], il.and_expr(2, operands[1], operands[2])))
        elif instr == "or":
            il.append(il.set_reg(2, operands[0], il.or_expr(2, operands[1], operands[2])))
        elif instr == "not":
            il.append(il.set_reg(2, operands[0], il.not_expr(2, operands[1])))
        elif instr == "rmem":
            il.append(il.set_reg(2, operands[0], il.load(2, operands[1])))
        elif instr == "wmem":
            il.append(il.store(2, operands[0], operands[1]))
        elif instr == "call":
            il.append(il.call(operands[0]))
        elif instr == "ret":
            il.append(il.ret(il.pop(2)))
        elif instr == "out":
            il.append(il.intrinsic([], "out", [operands[0]]))
        elif instr == "in":
            il.append(il.intrinsic([il.reg(2, operands[0])], "in", []))
        elif instr == "nop":
            il.append(il.nop())
        else:
            log.log_error("unknown instruction {}".format(instr))
        return length

Synacor.register()
