import struct
import sys

import networkx as nx

memory = open('challenge.patched.bin','rb').read()

def readmem(i):
    return struct.unpack('<H',memory[2*i:2*i+2])[0]

def writemem(a,b):
    global memory
    w = struct.pack('<H',b)
    memory = memory[:2*a] + w + memory[2*a+2:]

def ptr_to_list(addr):
    l = readmem(addr)
    s = []
    for i in range(addr+1, addr+1+l):
        s.append(readmem(i))
    return s

def puts_xor(addr, key):
    l = ptr_to_list(addr)
    return ''.join(map(lambda x: chr(x^key), l))

def puts(addr):
    l = ptr_to_list(addr)
    return ''.join(map(chr, l))

def hh(x):
    return "0x{:04x}".format(x)

visited = set()

names = {}
G = nx.DiGraph()

#q = [0x090d]
q = [0x0a3f]
while len(q) > 0:
    room = q.pop()
    if room in visited:
        continue
    name = readmem(room)
    names[room] = "{} {}".format(hh(room), puts(name))
    G.add_node(names[room])
    visited.add(room)
    exit_ptrs = ptr_to_list(readmem(room+3))
    for p in exit_ptrs:
        q = [p]+q

for room in sorted(visited):
    name = readmem(room)
    desc = readmem(room+1)
    exit_names = ptr_to_list(readmem(room+2))
    exit_ptrs = ptr_to_list(readmem(room+3))
    print("{} {}".format(hh(room), puts(name)))
    print("  "+repr(puts(desc)))
    print("Exits:")
    for n,p in zip(exit_names, exit_ptrs):
        G.add_edge(names[room], names[p])
        print("  {} {}".format(hh(p), puts(n)))
        q = [p]+q
    print()

print(puts_xor(0x6de7, 0x7578))

#import matplotlib.pyplot as plt
#nx.draw(G)
#plt.show()

