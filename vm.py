import struct
import sys

memory = open('challenge.bin','rb').read()
eip = 0
reg = [0]*8
stack = []
inline = ''

debugprint = [False]*22
ops = ['halt','set','push','pop','eq','gt','jmp','jt','jf','add','mult','mod',
       'and','or','not','rmem','wmem','call','ret','out','in','noop']

def printdebug(op,s):
    if debugprint[op]:
        print(s)

def debugcommand(s):
    global debugprint
    if 'debug' not in s:
        return
    for i in s.split()[1:]:
        if i == 'regs':
            print('Regs: {}'.format(reg))
        elif i == 'stack':
            print('Stack: {}'.format(stack))
        elif 'toggle' in i:
            for j in i.split('-')[1:]:
                ind = ops.index(j)
                debugprint[ind] = not debugprint[ind]

def parseopcode():
    global eip
    r = struct.unpack('<H',memory[2*eip:2*eip+2])[0]
    eip += 1
    return r

def parsearg():
    global eip
    r = struct.unpack('<H',memory[2*eip:2*eip+2])[0]
    eip += 1
    if r <= 32767:
        return r
    elif 32768 <= r <= 32775:
        return reg[r-32768]
    else:
        print("Invalid arg {}!".format(r))
        sys.exit(1)

def parsereg():
    global eip
    r = struct.unpack('<H',memory[2*eip:2*eip+2])[0]
    eip += 1
    return r-32768

def readmem(i):
    return struct.unpack('<H',memory[2*i:2*i+2])[0]

def writemem(a,b):
    global memory
    w = struct.pack('<H',b)
    memory = memory[:2*a] + w + memory[2*a+2:]

def opcode(n):
    global eip, inline
    if n == 0:
        printdebug(0,'{}: halt'.format(eip))
        print('Exiting...')
        sys.exit(0)
    elif n == 1:
        a = parsereg()
        b = parsearg()
        printdebug(1,'{}: set {} {}'.format(eip,a,b))
        reg[a] = b
    elif n == 2:
        a = parsearg()
        printdebug(2,'{}: push {}'.format(eip,a))
        stack.append(a)
    elif n == 3:
        a = parsereg()
        printdebug(3,'{}: pop {}'.format(eip,a))
        reg[a] = stack.pop()
    elif n == 4:
        a = parsereg()
        b = parsearg()
        c = parsearg()
        printdebug(4,'{}: eq {} {} {}'.format(eip,a,b,c))
        if b == c:
            reg[a] = 1
        else:
            reg[a] = 0
    elif n == 5:
        a = parsereg()
        b = parsearg()
        c = parsearg()
        printdebug(5,'{}: gt {} {} {}'.format(eip,a,b,c))
        if b > c:
            reg[a] = 1
        else:
            reg[a] = 0
    elif n == 6:
        a = parsearg()
        printdebug(6,'{}: jmp {}'.format(eip,a))
        eip = a
    elif n == 7:
        a = parsearg()
        b = parsearg()
        printdebug(7,'{}: jt {} {}'.format(eip,a,b))
        if a != 0:
            eip = b
    elif n == 8:
        a = parsearg()
        b = parsearg()
        printdebug(8,'{}: jf {} {}'.format(eip,a,b))
        if a == 0:
            eip = b
    elif n == 9:
        a = parsereg()
        b = parsearg()
        c = parsearg()
        printdebug(9,'{}: add {} {} {}'.format(eip,a,b,c))
        reg[a] = (b+c)%32768
    elif n == 10:
        a = parsereg()
        b = parsearg()
        c = parsearg()
        printdebug(10,'{}: mult {} {} {}'.format(eip,a,b,c))
        reg[a] = (b*c)%32768
    elif n == 11:
        a = parsereg()
        b = parsearg()
        c = parsearg()
        printdebug(11,'{}: mod {} {} {}'.format(eip,a,b,c))
        reg[a] = (b%c)%32768
    elif n == 12:
        a = parsereg()
        b = parsearg()
        c = parsearg()
        printdebug(12,'{}: and {} {} {}'.format(eip,a,b,c))
        reg[a] = b&c
    elif n == 13:
        a = parsereg()
        b = parsearg()
        c = parsearg()
        printdebug(13,'{}: or {} {} {}'.format(eip,a,b,c))
        reg[a] = b|c
    elif n == 14:
        a = parsereg()
        b = parsearg()
        printdebug(14,'{}: not {} {}'.format(eip,a,b))
        reg[a] = (~b)%32768
    elif n == 15:
        a = parsereg()
        b = parsearg()
        printdebug(15,'{}: rmem {} {}'.format(eip,a,b))
        reg[a] = readmem(b)
    elif n == 16:
        a = parsearg()
        b = parsearg()
        printdebug(16,'{}: wmem {} {}'.format(eip,a,b))
        writemem(a,b)
    elif n == 17:
        a = parsearg()
        printdebug(17,'{}: call {}'.format(eip,a))
        stack.append(eip)
        eip = a
    elif n == 18:
        printdebug(18,'{}: ret'.format(eip))
        eip = stack.pop()
    elif n == 19:
        a = parsearg()
        printdebug(19,'{}: out {}'.format(eip,a))
        print(chr(a),end='')
    elif n == 20:
        if inline == '':
            inline = 'debug'
            while 'debug' in inline:
                inline = input()+'\n'
                debugcommand(inline)
        a = parsereg()
        printdebug(20,'{}: in {}'.format(eip,a))
        reg[a] = ord(inline[0])
        inline = inline[1:]
    elif n == 21:
        printdebug(21,'{}: noop'.format(eip))
        pass
    else:
        print("Unknown opcode {}!".format(n))
        sys.exit(1)

while True:
    opcode(parseopcode())    
