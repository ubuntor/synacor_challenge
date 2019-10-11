import struct
import sys

memory = open('challenge.bin','rb').read()

def readmem(i):
    return struct.unpack('<H',memory[2*i:2*i+2])[0]

def writemem(a,b):
    global memory
    w = struct.pack('<H',b)
    memory = memory[:2*a] + w + memory[2*a+2:]

# patch self-test bytes
writemem(0x3a9, 0x15)
writemem(0x3aa, 0x7)

# decrypt memory (fun_06bb)
for i in range(0x17b4, 0x7562):
    x = readmem(i)
    x ^= (i*i) & 32767
    x ^= 0x4154
    writemem(i, x)

open('challenge.patched.bin','wb').write(memory)
